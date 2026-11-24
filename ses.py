"""SRT dosyasını seslendirir: her alt yazı satırı kendi başlangıç zamanına oturur.

Kullanım:
    ebabil ses dosya.srt                     -> dosya.wav (SRT'nin yanına)
    ebabil ses dosya.srt -o cikti.wav
    ebabil ses dosya.srt --stil sakin --hiz-sinir 1.4
    ebabil ses dosya.srt --video dosya.mp4   -> dosya-sesli.mp4

Ses motoru: Ahenk Cep (ozgurguler/ahenk-cep-tr, CC BY 4.0), işlemcide çalışır.
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

import numpy as np

MODEL_REPO = "ozgurguler/ahenk-cep-tr"
STILLER = {
    "normal": "neutral", "sakin": "calm", "neseli": "cheerful", "empatik": "empathetic",
    "uzgun": "sad", "saskin": "surprised", "kizgin": "angry",
}


def zaman(s: str) -> float:
    h, m, rest = s.strip().replace(".", ",").split(":")
    sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def srt_oku(yol: Path):
    metin = yol.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    satirlar = []
    for blok in re.split(r"\n\s*\n", metin.strip()):
        parcalar = blok.strip().split("\n")
        i = next((k for k, p in enumerate(parcalar) if "-->" in p), None)
        if i is None:
            continue
        bas, son = parcalar[i].split("-->")
        yazi = " ".join(p.strip() for p in parcalar[i + 1:] if p.strip())
        yazi = re.sub(r"<[^>]+>", "", yazi)  # <i> gibi etiketler
        if yazi:
            satirlar.append((zaman(bas), zaman(son), yazi))
    return sorted(satirlar)


def sessizlik_kirp(a: np.ndarray, sr: int, esik=0.01, pay=0.04):
    idx = np.where(np.abs(a) > esik)[0]
    if len(idx) == 0:
        return a
    p = int(pay * sr)
    return a[max(0, idx[0] - p): min(len(a), idx[-1] + p)]


def model_yukle():
    from huggingface_hub import snapshot_download
    desen = ["*.pt", "ahenk_cep.py", "config.json"]
    try:
        d = snapshot_download(MODEL_REPO, allow_patterns=desen, local_files_only=True)
    except Exception:
        print("Model indiriliyor (ilk sefer, ~35 MB)...")
        d = snapshot_download(MODEL_REPO, allow_patterns=desen)
    sys.path.insert(0, d)
    import torch
    torch.set_num_threads(os.cpu_count() or 2)
    from ahenk_cep import AhenkCep
    return AhenkCep(f"{d}/student.pt", f"{d}/decoder.pt")


def ffmpeg_bul(ad="ffmpeg"):
    import shutil
    yol = shutil.which(ad)
    if yol:
        return yol
    aday = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links" / f"{ad}.exe"
    if aday.is_file():
        return str(aday)
    sys.exit(f"{ad} bulunamadı. Kurmak için: winget install Gyan.FFmpeg")


def videoya_ekle(video: Path, ses: Path, cikti: Path, muzik_sil: bool, muzik_seviye: float):
    import subprocess
    ffmpeg, ffprobe = ffmpeg_bul("ffmpeg"), ffmpeg_bul("ffprobe")
    sesli = subprocess.run(
        [ffprobe, "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
         "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout.strip() != ""

    if sesli and not muzik_sil:
        # Videodaki müzik: konuşma olan yerlerde otomatik kısılır (ducking).
        filtre = (
            f"[0:a]volume={muzik_seviye}[m];"
            "[1:a]apad,asplit=2[v1][v2];"
            "[m][v1]sidechaincompress=threshold=0.02:ratio=10:attack=30:release=500[md];"
            "[md][v2]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]"
        )
    else:
        filtre = "[1:a]apad[a]"
    komut = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(video), "-i", str(ses),
             "-filter_complex", filtre, "-map", "0:v", "-map", "[a]",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
             "-movflags", "+faststart", str(cikti)]
    r = subprocess.run(komut)
    if r.returncode != 0:
        sys.exit("ffmpeg videoyu oluşturamadı.")
    return sesli and not muzik_sil


def main():
    ap = argparse.ArgumentParser(description="SRT dosyasını seslendirir.")
    ap.add_argument("srt", type=Path)
    ap.add_argument("-o", "--cikti", type=Path, help="çıktı .wav (varsayılan: SRT'nin yanına)")
    ap.add_argument("--stil", default="normal", choices=STILLER.keys())
    ap.add_argument("--hiz-sinir", type=float, default=1.35,
                    help="satır yerine sığmazsa en fazla bu kadar hızlandır (varsayılan 1.35)")
    ap.add_argument("--adim", type=int, default=16, help="kalite adımı (8 hızlı, 16 varsayılan)")
    ap.add_argument("--video", type=Path,
                    help="seslendirmeyi bu videoya ekle -> <video>-sesli.mp4")
    ap.add_argument("--muzigi-sil", action="store_true",
                    help="videodaki mevcut sesi (müziği) at, yalnız seslendirme kalsın")
    ap.add_argument("--muzik-seviye", type=float, default=0.8,
                    help="videodaki müziğin genel seviyesi (varsayılan 0.8)")
    a = ap.parse_args()

    if not a.srt.is_file():
        sys.exit(f"Dosya yok: {a.srt}")
    if a.video and not a.video.is_file():
        sys.exit(f"Video yok: {a.video}")
    cikti = a.cikti or a.srt.with_suffix(".wav")
    satirlar = srt_oku(a.srt)
    if not satirlar:
        sys.exit("SRT içinde satır bulunamadı.")

    import soundfile as sf

    t0 = time.time()
    tts = model_yukle()
    stil = STILLER[a.stil]

    parcalar = []  # (başlangıç sn, ses)
    sr = None
    uyarilar = []
    for i, (bas, son, yazi) in enumerate(satirlar):
        sonraki = satirlar[i + 1][0] if i + 1 < len(satirlar) else son + 1.0
        yer = max(sonraki - bas - 0.15, son - bas)
        ses, sr = tts.say(yazi, style=stil, steps=a.adim)
        ses = sessizlik_kirp(np.asarray(ses, dtype=np.float32), sr)
        sure = len(ses) / sr
        hiz = 1.0
        if sure > yer:
            hiz = min(sure / yer * 1.03, a.hiz_sinir)
            ses, sr = tts.say(yazi, style=stil, steps=a.adim, speed=hiz)
            ses = sessizlik_kirp(np.asarray(ses, dtype=np.float32), sr)
            sure = len(ses) / sr
            if sure > yer + 0.05:
                uyarilar.append(f"  {i + 1}. satır yerine sığmadı: {sure:.1f} sn ses, {yer:.1f} sn yer")
        parcalar.append((bas, ses))
        not_ = f" (hız x{hiz:.2f})" if hiz > 1 else ""
        print(f"[{i + 1}/{len(satirlar)}] {sure:4.1f} sn{not_}  {yazi[:60]}")

    # Satırları zamanlarına yerleştir; taşan satır bir sonrakini iter.
    toplam = max(satirlar[-1][1], max(b + len(s) / sr for b, s in parcalar)) + 0.5
    buf = np.zeros(int(toplam * sr) + sr, dtype=np.float32)
    imlec = 0
    for bas, ses in parcalar:
        k = max(int(bas * sr), imlec)
        buf[k:k + len(ses)] += ses
        imlec = k + len(ses) + int(0.05 * sr)
    buf = buf[: max(imlec, int(toplam * sr))]
    tepe = np.abs(buf).max()
    if tepe > 0.99:
        buf *= 0.99 / tepe

    sf.write(cikti, buf, sr, subtype="PCM_16")
    print(f"\nHazır: {cikti}  ({len(buf) / sr:.1f} sn, {time.time() - t0:.0f} sn sürdü)")
    if a.video:
        vcikti = a.video.with_name(a.video.stem + "-sesli.mp4")
        karisik = videoya_ekle(a.video, cikti, vcikti, a.muzigi_sil, a.muzik_seviye)
        print(f"Video: {vcikti}" + ("  (müzik konuşmada kısılarak korundu)" if karisik else ""))
    if uyarilar:
        print("Uyarı — metni kısaltmak ya da --hiz-sinir'i artırmak gerekebilir:")
        print("\n".join(uyarilar))


if __name__ == "__main__":
    main()
