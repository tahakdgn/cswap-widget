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
   # uv ile:
   uv tool install claude-swap

   # veya pipx ile:
   pipx install claude-swap
   ```
   > Hesap eklemek için: `cswap add` veya `cswap add-token <TOKEN>` komutlarını kullanabilirsiniz.

### 2. Projeyi İndirme ve Bağımlılıkları Yükleme

```bash
git clone https://github.com/tahakdgn/cswap-widget.git
cd cswap-widget
pip install -r requirements.txt
```

---

## 🎮 Kullanım

### Widget'ı Başlatma

- **Komut Satırından:**
  ```bash
  python widget.py
  ```
- **Arka Planda Konsolsuz Başlatma:**
  `başlat.bat` dosyasına çift tıklayarak veya `pythonw widget.py` komutuyla başlatabilirsiniz.

### Masaüstü Kısayolu Oluşturma

Tek tıkla masaüstünüze kısayol eklemek için:
```bash
python make_shortcut.py
```
Masaüstünüzde `cswap Widget` adında doğrudan başlatılabilir bir kısayol oluşturulacaktır.

---

## 🏗️ Proje Yapısı

```
cswap-widget/
├── widget.py          # PyQt6 tabanlı ana arayüz, tema sistemi ve tray yönetimi
├── parser.py          # cswap CLI komutlarını çalıştıran ve çıktıyı ayrıştıran motor
├── make_shortcut.py   # Windows için otomatik masaüstü kısayolu oluşturucu
├── başlat.bat         # Konsolsuz hızlı başlatma betiği
├── requirements.txt   # Gerekli Python paketleri
├── LICENSE            # MIT Lisansı
└── README.md          # Proje dökümantasyonu
```

---

## 🔗 Referanslar & Teşekkür

Bu proje aşağıdaki açık kaynaklı projelerden ve yaklaşımlardan ilham alınarak ve üzerine inşa edilerek geliştirilmiştir:

- **[realiti4/claude-swap](https://github.com/realiti4/claude-swap)**: Claude Code için çoklu hesap yönetimi ve rotasyon sağlayan mükemmel CLI motoru. `cswap Widget`, arka plan işlemlerinde `claude-swap` komutlarını kullanır.
- **[tahakdgn/claude-account-switcher](https://github.com/tahakdgn/claude-account-switcher)**: Çoklu Claude hesapları için Chrome profil yönetimi ve kota takip masaüstü aracı.

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
