r"""Videoları uç uca birleştirir.

Kullanım:
    ebabil birlestir a.mp4 b.mp4 c.mp4       -> a klasöründe birlesik.mp4
    ebabil birlestir klasor\                 -> klasördeki videolar ada göre sırayla
    ebabil birlestir a.mp4 b.mp4 -o sonuc.mp4

Videolar aynı biçimdeyse (çözünürlük, fps, kodek, ses) yeniden kodlanmadan
birkaç saniyede birleşir. Biçimler farklıysa ilk videonun boyutuna ve fps'ine
göre yeniden kodlanır (daha uzun sürer).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VIDEO_UZANTI = {".mp4", ".mov", ".mkv", ".m4v", ".webm"}


def arac_bul(ad):
    yol = shutil.which(ad)
    if yol:
        return yol
    aday = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links" / f"{ad}.exe"
    if aday.is_file():
        return str(aday)
    sys.exit(f"{ad} bulunamadı. Kurmak için: winget install Gyan.FFmpeg")


FFMPEG, FFPROBE = arac_bul("ffmpeg"), arac_bul("ffprobe")


def incele(yol: Path):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(yol)],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        sys.exit(f"Okunamadı: {yol}")
    j = json.loads(r.stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    if v is None:
        sys.exit(f"Videoda görüntü yok: {yol}")
    return {
        "sure": float(j["format"].get("duration", 0)),
        "v": (v["codec_name"], v.get("profile"), v["width"], v["height"], v.get("pix_fmt"), v.get("r_frame_rate")),
        "a": (a["codec_name"], a.get("sample_rate"), a.get("channels")) if a else None,
        "w": v["width"], "h": v["height"], "fps": v.get("r_frame_rate", "30/1"),
    }


def dosyalari_topla(girdiler):
    liste = []
    for g in girdiler:
        p = Path(g)
        if p.is_dir():
            liste += sorted(f for f in p.iterdir() if f.suffix.lower() in VIDEO_UZANTI)
        elif p.is_file():
            liste.append(p)
        else:
            sys.exit(f"Bulunamadı: {g}")
    return liste


def kopya_birlestir(dosyalar, cikti):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        for d in dosyalar:
            f.write("file '" + str(d.resolve()).replace("'", r"'\''") + "'\n")
        liste = f.name
    try:
        r = subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
                            "-i", liste, "-c", "copy", "-movflags", "+faststart", str(cikti)])
    finally:
        os.unlink(liste)
    return r.returncode == 0


def kodlayarak_birlestir(dosyalar, bilgiler, cikti):
    w, h, fps = bilgiler[0]["w"], bilgiler[0]["h"], bilgiler[0]["fps"]
    komut = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-stats"]
    for d in dosyalar:
        komut += ["-i", str(d)]
    filtre, girisler = [], ""
    for i, b in enumerate(bilgiler):
        filtre.append(f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
                      f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},format=yuv420p[v{i}]")
        if b["a"]:
            filtre.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}]")
        else:  # sesi olmayan videoya sessizlik
            filtre.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{b['sure']}[a{i}]")
        girisler += f"[v{i}][a{i}]"
    filtre.append(f"{girisler}concat=n={len(dosyalar)}:v=1:a=1[v][a]")
    komut += ["-filter_complex", ";".join(filtre), "-map", "[v]", "-map", "[a]",
              "-c:v", "libx264", "-crf", "18", "-preset", "medium",
              "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(cikti)]
    return subprocess.run(komut).returncode == 0


def main():
    ap = argparse.ArgumentParser(description="Videoları uç uca birleştirir.")
    ap.add_argument("girdiler", nargs="+", help="video dosyaları ya da klasör (sırayla)")
    ap.add_argument("-o", "--cikti", type=Path, help="çıktı dosyası (varsayılan: birlesik.mp4)")
    a = ap.parse_args()

    dosyalar = dosyalari_topla(a.girdiler)
    if len(dosyalar) < 2:
        sys.exit("Birleştirmek için en az iki video gerekli.")
    cikti = a.cikti or dosyalar[0].parent / "birlesik.mp4"
    dosyalar = [d for d in dosyalar if d.resolve() != cikti.resolve()]

    bilgiler = [incele(d) for d in dosyalar]
    for d, b in zip(dosyalar, bilgiler):
        print(f"  {b['sure']:6.1f} sn  {b['w']}x{b['h']}  {'sesli' if b['a'] else 'sessiz'}  {d.name}")

    ayni = all(b["v"] == bilgiler[0]["v"] and b["a"] == bilgiler[0]["a"] for b in bilgiler)
    if ayni:
        print("Biçimler aynı: yeniden kodlamadan birleştiriliyor...")
        ok = kopya_birlestir(dosyalar, cikti)
    else:
        print(f"Biçimler farklı: {bilgiler[0]['w']}x{bilgiler[0]['h']} olarak yeniden kodlanıyor (uzun sürebilir)...")
        ok = kodlayarak_birlestir(dosyalar, bilgiler, cikti)
    if not ok:
        sys.exit("Birleştirme başarısız.")
    print(f"\nHazır: {cikti}  ({incele(cikti)['sure']:.1f} sn, toplam {sum(b['sure'] for b in bilgiler):.1f} sn)")


if __name__ == "__main__":
    main()
