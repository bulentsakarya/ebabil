# ebabil

Video hazırlarken sık gereken iki işi komut satırından yapan, ücretsiz ve
açık kaynak bir Windows aracı:

| Komut | Ne yapar |
|---|---|
| `ebabil ses` | SRT alt yazı dosyasını **Türkçe seslendirir**. Her satır SRT'deki zamanında başlar, ses videoyla eş gider. İsterseniz sesi doğrudan videoya ekler. |
| `ebabil birlestir` | Videoları **uç uca birleştirir**. Aynı biçimdeki videoları saniyeler içinde, kalite kaybı olmadan birleştirir. |

Her şey bilgisayarınızda çalışır. Ekran kartı, hesap, API anahtarı ya da
ücretli bir servis gerekmez. Kurulumdan sonra internet de gerekmez.

---

## İçindekiler

- [Ne kullanıyor?](#ne-kullanıyor)
- [Gereksinimler](#gereksinimler)
- [Kurulum](#kurulum)
- [Hızlı başlangıç](#hızlı-başlangıç)
- [Seslendirme: `ebabil ses`](#seslendirme-ebabil-ses)
- [Video birleştirme: `ebabil birlestir`](#video-birleştirme-ebabil-birlestir)
- [Örnek iş akışı](#örnek-iş-akışı)
- [Nasıl çalışıyor?](#nasıl-çalışıyor)
- [İyi sonuç için ipuçları](#iyi-sonuç-için-ipuçları)
- [Sorun giderme](#sorun-giderme)
- [Klasör yapısı](#klasör-yapısı)
- [Lisans ve teşekkür](#lisans-ve-teşekkür)

---

## Ne kullanıyor?

| Parça | Görevi |
|---|---|
| **Python 3.11–3.13** | Programın dili. |
| **[Ahenk Cep](https://huggingface.co/ozgurguler/ahenk-cep-tr)** | Türkçe metinden ses üreten yapay zekâ modeli. 8,6 milyon parametreli, ~35 MB. İşlemcide (CPU) çalışır. Tek bir kadın sesi vardır ("f022", gerçek bir kişiye ait değildir). |
| **[trnorm](https://github.com/ozguradmin/ahenk-turkish-tts)** | Türkçe metni okunuş hâline çevirir: `1.250 TL` → "bin iki yüz elli lira", `14.10.2026` → tarih okunuşu vb. |
| **[PyTorch](https://pytorch.org) (CPU)** | Modeli çalıştıran motor. Yalnız işlemci sürümü kurulur, ekran kartı sürücüsü gerekmez. |
| **[FFmpeg](https://ffmpeg.org)** | Sesi videoya ekleme, müziği kısma ve video birleştirme işleri. |
| **soundfile, numpy** | Sesi okuma, yazma ve satırları zamanına yerleştirme. |
| **huggingface_hub** | Modeli ilk çalıştırmada Hugging Face'ten indirir. |

## Gereksinimler

- **Windows 10 / 11**
- **Python 3.11, 3.12 ya da 3.13**: [python.org/downloads](https://www.python.org/downloads/)
  (kurarken "Add python.exe to PATH" kutusunu işaretleyin)
- **Git**: [git-scm.com](https://git-scm.com) ya da `winget install Git.Git`
- **~1,5 GB boş disk** (PyTorch, model ve FFmpeg)
- **4 GB RAM** yeterli. Ekran kartı gerekmez. Bu araç 4 GB RAM'li, i3
  işlemcili bir dizüstünde geliştirilip denendi.

FFmpeg'i ayrıca kurmanız gerekmez: yoksa `kur.bat` winget ile kurar.

## Kurulum

**1. Depoyu indirin**

```
git clone https://github.com/bulentsakarya/ebabil C:\ebabil
```

Başka bir klasöre de indirebilirsiniz. Bu belgedeki örnekler `C:\ebabil`
kullanır.

**2. Kurulumu çalıştırın**

```
C:\ebabil\kur.bat
```

`kur.bat` şunları yapar:

1. Git ve Python'u bulur (3.13 → 3.12 → 3.11 sırasıyla dener).
2. Klasörün içine ayrı bir Python ortamı (`.venv`) kurar. Bilgisayardaki ana
   Python'a dokunmaz.
3. Gerekli paketleri `requirements.txt`'ten kurar (PyTorch'un CPU sürümü dahil).
4. FFmpeg yoksa winget ile kurar.
5. Ses modelini indirir (~35 MB, Hugging Face önbelleğine).

Birkaç dakika sürer. Tekrar çalıştırmak zararsızdır: kurulu olanı atlar.

**3. PATH'e ekleyin**

Her klasörden yalnızca `ebabil` yazabilmek için PowerShell'de bir kez
çalıştırın:

```
[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path','User') + ';C:\ebabil', 'User')
```

Ardından **terminali kapatıp yeniden açın**. Açık pencereler yeni PATH'i
görmez. VS Code içindeki terminal için VS Code'u yeniden başlatın.

Denemek için:

```
ebabil
```

Komut listesi görünürse kurulum tamam.

> PATH'e eklemek istemezseniz her seferinde tam yolu yazabilirsiniz:
> `C:\ebabil\ebabil.bat ses dosya.srt`

## Hızlı başlangıç

```
ebabil ses tanitim.srt                         # tanitim.wav üretir
ebabil ses tanitim.srt --video tanitim.mp4     # tanitim-sesli.mp4 üretir
ebabil birlestir bolum1.mp4 bolum2.mp4         # birlesik.mp4 üretir
```

Her komutun ayrıntılı yardımı için: `ebabil ses -h`, `ebabil birlestir -h`

---

## Seslendirme: `ebabil ses`

```
ebabil ses <dosya.srt> [seçenekler]
```

SRT'deki her satırı ayrı ayrı seslendirir ve SRT'deki başlangıç zamanına
yerleştirir. Sonuç, videonun alt yazılarıyla birebir eş giden tek bir ses
dosyasıdır.

### Seçenekler

| Seçenek | Varsayılan | Açıklama |
|---|---|---|
| `-o`, `--cikti <dosya.wav>` | SRT ile aynı ad | Ses dosyasının adı ve yeri. |
| `--video <dosya.mp4>` | — | Sesi bu videoya ekler, videonun yanına `<ad>-sesli.mp4` yazar. |
| `--muzik-seviye <sayı>` | `0.8` | Videoda müzik varsa genel seviyesi (`0.5` daha kısık, `1.0` olduğu gibi). |
| `--muzigi-sil` | kapalı | Videodaki mevcut sesi atar, yalnız seslendirme kalır. |
| `--stil <ad>` | `normal` | Ses tonu: `normal`, `sakin`, `neseli`, `empatik`, `uzgun`, `saskin`, `kizgin`. |
| `--adim <sayı>` | `16` | Kalite adımı. `8` yaklaşık iki kat hızlıdır, kalite biraz düşer. |
| `--hiz-sinir <sayı>` | `1.35` | Bir satırın sesi kendi aralığına sığmazsa en fazla bu oranda hızlandırılır. |

### Örnekler

```
# Yalnız ses dosyası
ebabil ses video.srt

# Ses dosyasını başka bir yere/adla kaydet
ebabil ses video.srt -o D:\sesler\anlatim.wav

# Sesi videoya ekle (videodaki müzik korunur, konuşmada kısılır)
ebabil ses video.srt --video video.mp4

# Müzik daha kısık olsun
ebabil ses video.srt --video video.mp4 --muzik-seviye 0.5

# Videonun kendi sesini at, yalnız anlatım kalsın
ebabil ses video.srt --video video.mp4 --muzigi-sil

# Daha sakin bir ton, hızlı deneme
ebabil ses video.srt --stil sakin --adim 8
```

### Ekranda ne görürsünüz?

```
[1/9]  3.3 sn  Noma temasının header bölümü. Tüm özellikleri kısaca.
[2/9]  5.0 sn  En üstte duyuru çubuğu. Telefonda mesajlar sırayla döner...
[3/9]  3.4 sn (hız x1.12)  Logonun hemen altında, her zaman görünen...
...
Hazır: video.wav  (62.2 sn, 25 sn sürdü)
Video: video-sesli.mp4  (müzik konuşmada kısılarak korundu)
```

`hız x1.12` gibi bir not, o satırın aralığına sığması için hafifçe
hızlandırıldığını gösterir. Bir satır en fazla hızda da sığmazsa sonda
uyarı çıkar (bkz. [Sorun giderme](#sorun-giderme)).

### Çıktı

- **Ses**: 48 kHz, 16 bit, mono WAV. Her montaj programına doğrudan
  aktarılabilir.
- **Video** (`--video` ile): görüntü **yeniden kodlanmaz**, birebir
  kopyalanır, kalite değişmez. Ses AAC 192 kbps. Video süresi orijinalle aynı
  kalır.

Orijinal dosyaların üzerine hiçbir zaman yazılmaz.

---

## Video birleştirme: `ebabil birlestir`

```
ebabil birlestir <video1> <video2> [...] [-o cikti.mp4]
ebabil birlestir <klasör>
```

### Seçenekler

| Seçenek | Varsayılan | Açıklama |
|---|---|---|
| `-o`, `--cikti <dosya>` | ilk videonun klasöründe `birlesik.mp4` | Birleşik videonun adı ve yeri. |

### Örnekler

```
# Verdiğiniz sırayla birleştir
ebabil birlestir giris.mp4 bolum1.mp4 bolum2.mp4 kapanis.mp4

# Klasördeki tüm videoları ada göre sırala ve birleştir
ebabil birlestir D:\videolar\seri

# Çıktıya ad ver
ebabil birlestir a.mp4 b.mp4 -o D:\yayin\tam-video.mp4
```

Klasör verildiğinde `.mp4`, `.mov`, `.mkv`, `.m4v` ve `.webm` dosyaları
**ada göre** sıralanır. Sırayı garanti etmek için dosya adlarının başına
numara koyun: `01-giris.mp4`, `02-bolum.mp4`, …

### İki çalışma biçimi

ebabil önce her videonun biçimine bakar (çözünürlük, fps, kodek, ses) ve
listeler:

```
    64.3 sn  1080x1920  sesli  01-header.mp4
    55.1 sn  1080x1920  sesli  02-slider.mp4
    48.7 sn  1080x1920  sesli  03-kategoriler.mp4
Biçimler aynı: yeniden kodlamadan birleştiriliyor...
```

- **Biçimler aynıysa**: videolar yeniden kodlanmadan uç uca eklenir.
  Birkaç saniye sürer, kalite birebir korunur. Aynı programla ya da aynı
  ayarlarla dışa aktarılmış videolar genelde bu yoldan gider.
- **Biçimler farklıysa** (ör. dikey + kare video, farklı fps, sesi olmayan
  bir video): hepsi **ilk videonun** boyutuna ve fps'ine göre yeniden
  kodlanır. Boyu tutmayan videonun kenarlarına siyah boşluk eklenir, sesi
  olmayan videoya sessizlik konur. Kalite yüksek tutulur (H.264, CRF 18), ama
  bu yol yavaştır: sıradan bir dizüstünde 1 dakikalık video ~1,5 dakikada
  kodlanır.

---

## Örnek iş akışı

Bir tanıtım serisi için üç kısa video ve her birinin SRT'si olduğunu
düşünelim:

```
D:\seri\
  01-giris.mp4      01-giris.srt
  02-ozellik.mp4    02-ozellik.srt
  03-kapanis.mp4    03-kapanis.srt
```

**1. Her videoyu seslendirin**

```
cd D:\seri
ebabil ses 01-giris.srt   --video 01-giris.mp4
ebabil ses 02-ozellik.srt --video 02-ozellik.mp4
ebabil ses 03-kapanis.srt --video 03-kapanis.mp4
```

Her biri için `-sesli.mp4` oluşur.

**2. Dinleyin, gerekirse düzeltin**

Yanlış okunan bir kelime ya da sığmayan bir satır varsa SRT'yi düzenleyip
aynı komutu tekrar çalıştırın. Çıktının üzerine yazılır.

**3. Sesli videoları birleştirin**

```
ebabil birlestir 01-giris-sesli.mp4 02-ozellik-sesli.mp4 03-kapanis-sesli.mp4 -o seri-tam.mp4
```

**4. Yayınlarken kaynak satırını ekleyin** (bkz.
[Lisans ve teşekkür](#lisans-ve-teşekkür)).

---

## Nasıl çalışıyor?

### Seslendirme

1. **SRT okunur.** Sıra numaraları atlanır, çok satırlı alt yazılar
   birleştirilir, `<i>` gibi biçim etiketleri temizlenir.
2. **Her satır ayrı seslendirilir.** Metin önce trnorm ile okunuş hâline
   çevrilir, sonra Ahenk Cep sesi üretir. Baştaki ve sondaki sessizlik
   kırpılır.
3. **Satırın yeri hesaplanır.** Bir satırın kullanabileceği süre, kendi
   başlangıcından bir sonraki satırın başlangıcına kadardır (araya küçük bir
   nefes payı bırakılır).
4. **Sığmazsa hızlandırılır.** Ses bu süreden uzunsa satır, sığacak kadar
   hızlı yeniden okunur (en fazla `--hiz-sinir`, varsayılan ×1,35). Hız
   değişimi modelin kendisinde yapılır, ses tizleşmez.
5. **Yerleştirilir.** Her satır SRT'deki başlangıç anına konur. Yine de
   taşan bir satır olursa bir sonraki satır onun bitişine kadar itilir.
   Satırlar asla üst üste binmez.
6. **WAV yazılır.** Tepe seviye kırpılmayacak şekilde ayarlanır.

### Videoya ekleme (`--video`)

- Videoda ses yoksa seslendirme doğrudan eklenir.
- Videoda ses (müzik) varsa **ducking** uygulanır: seslendirme bir
  sidechain kompresörü tetikler, konuşma başladığında müzik otomatik kısılır,
  bitince yumuşakça eski seviyesine döner. Sonra iki ses karıştırılır ve
  bozulma olmaması için sınırlayıcıdan geçirilir.
- Görüntü kopyalanır (`-c:v copy`), video süresi korunur.

### Birleştirme

- Biçimler aynıysa FFmpeg'in concat demuxer'ı ile akışlar kopyalanır.
- Farklıysa concat filtresiyle her video ölçeklenir, boşlukla doldurulur,
  fps ve ses (48 kHz stereo) eşitlenir, sonra H.264 + AAC ile kodlanır.

### Model nerede duruyor?

İlk çalıştırmada model Hugging Face önbelleğine iner:
`%USERPROFILE%\.cache\huggingface\hub\models--ozgurguler--ahenk-cep-tr`.
Sonraki çalıştırmalar internete çıkmaz.

---

## İyi sonuç için ipuçları

- **Sayıları rakamla yazabilirsiniz.** `%25`, `1.250 TL`, `14.10.2026`,
  `3. sıra` gibi ifadeler doğru okunur.
- **Özel ad ve markaları okunduğu gibi yazın.** Model yabancı ya da uydurma
  kelimeleri Türkçe kurallarıyla okur. Yanlış okunan bir marka için SRT'de
  okunuşa yakın yazın (ör. `cift.click` → `çift klik`). Ekrandaki alt yazıyı
  ayrı tutmak istiyorsanız seslendirme için ayrı bir SRT kopyası kullanın.
- **Kısaltmalar zayıf noktadır.** `THY`, `TBMM` gibi kısaltmaları açık yazın
  ya da harf harf yazın (`te ha ye`).
- **Soru cümlelerinde "mı/mi" kullanın.** Ses yalnız soru ekiyle yükselir,
  "Hazır?" gibi eksiz sorular düz okunur.
- **Satırlara nefes payı bırakın.** Uzun cümleyi kısa bir aralığa koymak
  hızlandırmaya, aşırısı da uyarıya yol açar. Yaklaşık olarak saniyede 2,5–3
  kelime rahat okunur.
- **Önce hızlı deneme yapın.** Metni ve zamanlamayı `--adim 8` ile
  denetleyin, son çıktıyı varsayılan kaliteyle alın.

---

## Sorun giderme

**`ebabil` tanınmıyor**
PATH'e eklemeden sonra terminali (ya da VS Code'u) yeniden açın. Hâlâ
olmuyorsa PATH'i denetleyin:
`[Environment]::GetEnvironmentVariable('Path','User')` çıktısında
`C:\ebabil` olmalı. Geçici çözüm: `$env:Path += ';C:\ebabil'`.

**`ebabil kurulu degil. Once kur.bat dosyasini calistirin.`**
`.venv` klasörü yok. `kur.bat`'ı çalıştırın.

**`kur.bat`: "Python bulunamadi"**
Python 3.11–3.13 kurun. Python kurulu olduğu hâlde `python` yazınca
"Python bulunamadı" çıkıyorsa bu, Windows'un Microsoft Store kısayoludur:
*Ayarlar → Uygulamalar → Gelişmiş uygulama ayarları → Uygulama yürütme
takma adları* bölümünde `python.exe` ve `python3.exe`'yi kapatın.
(`kur.bat` `py` başlatıcısını kullandığı için çoğu zaman bu sorundan
etkilenmez.)

**`ffmpeg bulunamadı`**
`winget install Gyan.FFmpeg` ile kurun ya da [ffmpeg.org](https://ffmpeg.org)
adresinden indirip PATH'e ekleyin. ebabil, winget'in kurduğu FFmpeg'i PATH
güncellenmemiş olsa da bulur.

**`N. satır yerine sığmadı`**
O satırın metni, SRT'deki aralığı için fazla uzun. Seçenekler: metni
kısaltın, SRT'de satırın aralığını genişletin ya da `--hiz-sinir 1.5` ile
daha fazla hızlanmaya izin verin. Ses yine de üretilir, yalnız sonraki
satırlar biraz kayar.

**Bir kelime yanlış okunuyor**
SRT'de okunduğu gibi yazın (bkz. [ipuçları](#iyi-sonuç-için-ipuçları)).

**"unauthenticated requests to the HF Hub" uyarısı**
Zararsızdır, yalnız ilk model indirmesinde görünür. Görmezden gelebilirsiniz.

**Birleştirme çok yavaş**
Videoların biçimi farklı olduğu için yeniden kodlanıyordur. Ekrandaki
listede çözünürlükleri ve ses durumunu karşılaştırın. Videoları aynı
ayarlarla dışa aktarırsanız birleştirme saniyeler sürer.

**Seslendirme yavaş**
`--adim 8` deneyin. İlk çalıştırma, modeli indirdiği için daha uzun sürer.

---

## Klasör yapısı

```
ebabil\
  ebabil.bat         komut: ebabil <ses|birlestir> ...
  ebabil.py          alt komutları dağıtan giriş noktası
  ses.py             SRT → seslendirme (+ videoya ekleme)
  birlestir.py       video birleştirme
  kur.bat            tek seferlik kurulum
  requirements.txt   Python paketleri
  .venv\             kur.bat'ın oluşturduğu Python ortamı (depoda yok)
```

---

## Lisans ve teşekkür

**ebabil**'in kodu [MIT lisansı](LICENSE) ile dağıtılır: ücretsiz kullanın,
değiştirin, paylaşın.

Seslendirme, Özgür Güler'in **[Ahenk Cep](https://huggingface.co/ozgurguler/ahenk-cep-tr)**
modeliyle yapılır. Model ağırlıkları **CC BY 4.0** lisanslıdır. Ürettiğiniz
sesi yayınlarken kaynak belirtmeniz gerekir. Örneğin video açıklamasına:

> Seslendirme: Ahenk Cep (ozgurguler/ahenk-cep-tr, CC BY 4.0)

Ayrıca teşekkürler:

- [EMA Lightning](https://pypi.org/project/ema-lightning/): Ahenk Cep'in
  dayandığı model mimarisi (Apache-2.0)
- [trnorm / ahenk-turkish-tts](https://github.com/ozguradmin/ahenk-turkish-tts):
  Türkçe metin normalleştirme
- [FFmpeg](https://ffmpeg.org): ses ve video işleme
- [PyTorch](https://pytorch.org)
