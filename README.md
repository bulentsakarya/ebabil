# ebabil

Video hazırlarken iki işi komut satırından halleden küçük bir araç:

- **ses**: SRT alt yazı dosyasını Türkçe seslendirir. Her satır SRT'deki
  zamanında başlar, ses videoyla eş gider. İstenirse doğrudan videoya ekler.
- **birlestir**: Videoları uç uca birleştirir.

Tamamen yerelde çalışır; ekran kartı, hesap ya da API anahtarı gerekmez.

## Kurulum (Windows)

Gerekenler: Python 3.11–3.13 ve Git.

```
git clone https://github.com/bulentsakarya/ebabil C:\ebabil
C:\ebabil\kur.bat
```

`kur.bat` Python ortamını (`.venv`) kurar, ffmpeg yoksa winget ile kurar ve
ses modelini (~35 MB) indirir. Her klasörden `ebabil` yazabilmek için
`C:\ebabil` klasörünü PATH'e ekleyin.

## Seslendirme

```
ebabil ses dosya.srt                    # dosya.wav SRT'nin yanına yazılır
ebabil ses dosya.srt -o cikti.wav
ebabil ses dosya.srt --stil sakin       # normal, sakin, neseli, empatik, uzgun, saskin, kizgin
ebabil ses dosya.srt --adim 8           # daha hızlı, biraz daha düşük kalite
ebabil ses dosya.srt --hiz-sinir 1.5    # sığmayan satırı en fazla bu kadar hızlandır

ebabil ses dosya.srt --video dosya.mp4                     # dosya-sesli.mp4 üretir
ebabil ses dosya.srt --video dosya.mp4 --muzik-seviye 0.5  # müzik daha kısık
ebabil ses dosya.srt --video dosya.mp4 --muzigi-sil        # yalnız seslendirme
```

- Bir satırın sesi kendi aralığına sığmazsa en fazla `--hiz-sinir` kadar
  (varsayılan 1,35) hızlandırılarak yeniden okunur. Yine sığmazsa sonraki
  satırı biraz iter ve sonda uyarı verir.
- `--video` verilince videodaki müzik korunur ve konuşma olan yerlerde
  otomatik kısılır. Görüntü yeniden kodlanmaz, kalite aynı kalır.
- Sayılar, tarihler, para birimleri okunuşa kendiliğinden çevrilir.
  Özel adlar ya da marka adları yanlış okunursa SRT'de okunduğu gibi yazın.
- Çıktı: 48 kHz, 16 bit WAV. Ortalama bir bilgisayarda 1 dakikalık metin
  yaklaşık 1 dakikada seslenir.

## Video birleştirme

```
ebabil birlestir a.mp4 b.mp4 c.mp4      # a'nın klasöründe birlesik.mp4
ebabil birlestir klasor\                # klasördeki videolar ada göre sırayla
ebabil birlestir a.mp4 b.mp4 -o sonuc.mp4
```

Videolar aynı biçimdeyse (çözünürlük, fps, kodek, ses) yeniden kodlanmadan
birkaç saniyede birleşir. Farklıysa ilk videonun boyutuna göre yeniden
kodlanır: boyu tutmayan videonun kenarlarına siyah boşluk eklenir, sesi
olmayan videoya sessizlik konur. Bu yol daha yavaştır.

## Ses motoru ve lisans

ebabil'in kodu MIT lisanslıdır (bkz. [LICENSE](LICENSE)).

Seslendirme için [Ahenk Cep](https://huggingface.co/ozgurguler/ahenk-cep-tr)
modeli kullanılır (Özgür Güler; 8,6M parametre, işlemcide çalışır). Model
ağırlıkları **CC BY 4.0** lisanslıdır: üretilen sesi yayınlarken kaynak
belirtin, örneğin video açıklamasına:

> Seslendirme: Ahenk Cep (ozgurguler/ahenk-cep-tr, CC BY 4.0)

Video işlemleri için [FFmpeg](https://ffmpeg.org) kullanılır.
