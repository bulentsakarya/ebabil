"""ebabil — SRT'den seslendirme ve video birleştirme.

    ebabil ses dosya.srt [--video dosya.mp4]
    ebabil birlestir a.mp4 b.mp4 ...
"""

import importlib
import sys

KOMUTLAR = {
    "ses": "SRT dosyasını seslendirir (istenirse videoya ekler)",
    "birlestir": "videoları uç uca birleştirir",
}


def yardim():
    print("Kullanım: ebabil <komut> [seçenekler]\n\nKomutlar:")
    for k, aciklama in KOMUTLAR.items():
        print(f"  {k:<10} {aciklama}")
    print("\nAyrıntı için: ebabil <komut> -h")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "yardim"):
        yardim()
        return
    komut = sys.argv[1]
    if komut not in KOMUTLAR:
        print(f"Bilinmeyen komut: {komut}\n")
        yardim()
        sys.exit(2)
    sys.argv = [f"ebabil {komut}"] + sys.argv[2:]
    importlib.import_module(komut).main()


if __name__ == "__main__":
    main()
