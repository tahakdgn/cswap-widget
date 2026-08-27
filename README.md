# cswap Widget 🎛️

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Powered By](https://img.shields.io/badge/Powered%20By-claude--swap-blueviolet?style=for-the-badge)

**Claude Code CLI için şık, modern ve yarı saydam masaüstü kota takip & hızlı hesap geçiş widget'ı.**

[Özellikler](#-özellikler) • [Kurulum](#-kurulum) • [Kullanım](#-kullanım) • [Referanslar & Teşekkür](#-referanslar--teşekkür) • [Lisans](#-lisans)

</div>

---

## 📌 Genel Bakış

`cswap Widget`, birden fazla Claude / Anthropic hesabı kullanan geliştiriciler için geliştirilmiş, masaüstünde her an elinizin altında duran estetik ve hafif bir arayüz aracıdır.

Arka planda popüler açık kaynaklı CLI aracı **`claude-swap` (cswap)** ile entegre çalışarak:
- Tüm hesaplarınızın **5 saatlik (5h)** ve **7 günlük (7d)** token limitlerini / kotalarını anlık gösterir.
- Kotaların ne zaman ve ne kadar süre sonra sıfırlanacağını canlı olarak takip eder.
- Tek tıklamayla en uygun/en yüksek kotaya sahip hesaba (`--strategy best`) veya seçtiğiniz hesaba geçiş yapmanızı sağlar.

---

## ✨ Özellikler

- 📊 **Canlı Kota Görselleştirmesi:** Her hesabın 5 saatlik ve 7 günlük kullanım yüzdeleri renkli ilerleme çubukları (%0-%50 Yeşil, %50-%80 Sarı, %80+ Kırmızı) ile gösterilir.
- ⚡ **Tek Tıkla Akıllı Geçiş:** *"En İyi Hesaba Geç"* butonu ile arka planda otomatik en boş hesaba geçiş yapılır.
- 🎯 **Doğrudan Hesap Seçimi:** Her hesap kartındaki *"Geçiş Yap"* butonu ile istenen hesaba anında geçilebilir.
- 🎨 **Dark / Light Glassmorphism Teması:** Yarı saydam pencereler, yumuşak gölgeler ve koyu/açık mod geçişi (☀️ / 🌙).
- 📌 **Always-On-Top (Üstte Sabitleme):** Kodlama yaparken veya Claude Code terminalinde çalışırken widget'ı ekranda sabit tutabilme (📌).
- 🪟 **Sürüklenebilir & Konum Hatırlama:** Pencere ekranın istenen yerine sürüklenebilir; kapatılıp açıldığında konum ve tema ayarlarını hatırlar.
- 🔔 **Sistem Tepsisi (System Tray):** Görev çubuğuna küçültülebilir, tepsi menüsü üzerinden durum yenileme ve geçiş yapılabilir.
- ⏱️ **Otomatik & Manuel Yenileme:** Saat başı otomatik kota kontrolü ve geri sayım sayacı, istenirse anlık *"↻ Yenile"* desteği.

---

## 🚀 Kurulum

### 1. Ön Koşullar

1. **Python 3.9+** kurulu olmalıdır.
2. **`claude-swap` (cswap)** CLI aracı kurulu ve hesaplar eklenmiş olmalıdır:
   ```bash
   # uv ile (Önerilen):
   uv tool install claude-swap

   # veya pipx ile:
   pipx install claude-swap
   ```
   > Hesap eklemek için: `cswap add` veya `cswap add-token <TOKEN>` komutlarını kullanabilirsiniz.

### 2. Projeyi İndirme ve Yükleme

```bash
git clone https://github.com/tahakdgn/cswap-widget.git
cd cswap-widget

# Bağımlılıkları yükleyin:
pip install -r requirements.txt

# veya paketi yerel olarak geliştirme modunda kurun (CLI komutu `cswap-widget` ekler):
pip install -e .
```

---

## 🎮 Kullanım

### Widget'ı Başlatma

- **Kök Dizinden (Kolay Başlatıcı):**
  ```bash
  python run.py
  ```
- **Modül Olarak Başlatma:**
  ```bash
  python -m cswap_widget
  ```
- **Paket Olarak Kurulduğunda:**
  ```bash
  cswap-widget
  ```
- **Arka Planda Konsolsuz Başlatma (Windows):**
  `scripts/start.bat` dosyasına çift tıklayarak veya `pythonw run.py` komutuyla arka planda açabilirsiniz.

### Masaüstü Kısayolu Oluşturma

Tek tıkla masaüstünüze kısayol oluşturmak için:
```bash
python scripts/make_shortcut.py
```
Masaüstünüzde `cswap Widget` adında doğrudan çalıştırılabilir bir kısayol oluşturulacaktır.

---

## 🏗️ Proje Mimarisi

```text
cswap-widget/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI (Syntax, Lint & Build)
├── src/
│   └── cswap_widget/
│       ├── __init__.py          # Paket versiyonu ve meta veriler
│       ├── __main__.py          # `python -m cswap_widget` desteği
│       ├── main.py              # Uygulama lifecycle ve QApplication başlatıcı
│       ├── core/                # Çekirdek mantık ve veri modelleri
│       │   ├── __init__.py
│       │   ├── models.py        # AccountStatus veri yapısı
│       │   ├── parser.py        # cswap CLI regex ayrıştırıcı
│       │   └── executor.py      # Subprocess çağrıları ve komut yürütücü
│       ├── ui/                  # Arayüz bileşenleri ve stil sistemi
│       │   ├── __init__.py
│       │   ├── themes.py        # Koyu/Açık tema tokenları ve renk hesapları
│       │   ├── card.py          # Hesap kartı (AccountCard) bileşeni
│       │   ├── widget.py        # Ana pencere (CSwapWidget) ve sürükleme mantığı
│       │   └── tray.py          # Sistem tepsisi (System Tray) menüsü
│       └── utils/               # Yardımcı araçlar
│           ├── __init__.py
│           └── shortcut.py      # Dinamik masaüstü kısayol oluşturucu
├── scripts/
│   ├── start.bat                # Windows arka plan başlatma scripti
│   └── make_shortcut.py         # Kısayol oluşturma aracı
├── pyproject.toml               # PEP 517/621 modern Python paket standardı
├── requirements.txt             # Bağımlılıklar (PyQt6)
├── run.py                       # Hızlı başlatıcı giriş noktası
├── .gitignore                   # Git temizleme kuralları
├── LICENSE                      # MIT Lisansı
└── README.md                    # Proje dökümantasyonu
```

---

## 🔗 Referanslar & Teşekkür

Bu proje aşağıdaki açık kaynaklı projelerden ve yaklaşımlardan ilham alınarak ve üzerine inşa edilerek geliştirilmiştir:

- **[realiti4/claude-swap](https://github.com/realiti4/claude-swap)**: Claude Code için çoklu hesap yönetimi ve rotasyon sağlayan mükemmel CLI motoru. `cswap Widget`, arka plan işlemlerinde `claude-swap` komutlarını kullanır.
- **[tahakdgn/claude-account-switcher](https://github.com/tahakdgn/claude-account-switcher)**: Çoklu Claude hesapları için Chrome profil yönetimi ve kota takip masaüstü aracı.

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
