# 📦 .deb Paketi Oluşturma Kılavuzu

## 🎯 Hızlı Başlangıç

### Yöntem 1: Basit Script ile (Önerilen)

```bash
# Scripti çalıştır
./build_deb.sh

# Oluşan paketi kur
sudo dpkg -i duplicate-agent_0.9.1-1_all.deb

# Eksik bağımlılıkları düzelt
sudo apt --fix-broken install
```

### Yöntem 2: Debuild ile (Profesyonel)

```bash
# Gerekli araçları yükle
sudo apt install debhelper dh-python python3-all python3-setuptools devscripts

# Paketi oluştur
debuild -us -uc -b

# Üst dizinde .deb dosyası oluşur
cd ..
sudo dpkg -i duplicate-agent_0.9.1-1_all.deb
```

---

## 📋 Gereksinimler

### Build Araçları
```bash
sudo apt install \
    dpkg-dev \
    debhelper \
    dh-python \
    python3-all \
    python3-setuptools \
    devscripts \
    build-essential
```

### Runtime Bağımlılıklar
```bash
sudo apt install \
    python3 \
    python3-pyside6.qtwidgets \
    python3-pyside6.qtcore \
    python3-pyside6.qtgui \
    python3-watchdog \
    python3-schedule \
    python3-pil \
    python3-imagehash
```

---

## 📁 Debian Paket Yapısı

```
duplicate-agent/
├── debian/
│   ├── control          # Paket metadata
│   ├── changelog        # Sürüm geçmişi
│   ├── rules            # Build kuralları
│   ├── compat           # Debhelper uyumluluk seviyesi
│   ├── copyright        # Lisans bilgisi
│   ├── install          # Kurulum dosyaları
│   ├── postinst         # Kurulum sonrası script
│   ├── prerm            # Kaldırma öncesi script
│   └── postrm           # Kaldırma sonrası script
└── build_deb.sh         # Otomatik build scripti
```

---

## 🔧 Özelleştirme

### Versiyon Güncelleme

`debian/changelog` dosyasını düzenle:
```bash
dch -v 0.9.2-1 "Yeni özellikler eklendi"
```

### Bağımlılık Ekleme

`debian/control` dosyasında `Depends:` satırını düzenle:
```
Depends: python3 (>= 3.8), python3-pyside6.qtwidgets, ...
```

### Script Ekleme

Kurulum sonrası işlemler için `debian/postinst`:
```bash
#!/bin/bash
# Özel işlemler buraya
```

---

## ✅ Paket Doğrulama

### Lintian ile Kontrol
```bash
lintian duplicate-agent_0.9.1-1_all.deb
```

### Paket İçeriğini Görüntüle
```bash
dpkg-deb --contents duplicate-agent_0.9.1-1_all.deb
```

### Paket Bilgisi
```bash
dpkg-deb --info duplicate-agent_0.9.1-1_all.deb
```

---

## 📦 Kurulum ve Kaldırma

### Kurulum
```bash
# Paketi kur
sudo dpkg -i duplicate-agent_0.9.1-1_all.deb

# Bağımlılıkları otomatik kur
sudo apt --fix-broken install
```

### Kaldırma
```bash
# Programı kaldır (ayarlar kalır)
sudo apt remove duplicate-agent

# Tamamen kaldır (ayarlar dahil)
sudo apt purge duplicate-agent
```

### Kontrol
```bash
# Kurulu mu kontrol et
dpkg -l | grep duplicate-agent

# Kurulum bilgisi
apt show duplicate-agent
```

---

## 🚀 Çalıştırma

### Terminal'den
```bash
duplicate-agent
```

### Applications Menüsünden
- Utilities → Duplicate Agent
- System Tools → Duplicate Agent

### Desktop İkonu
Masaüstünüze sürükleyip bırakın.

---

## 🐛 Sorun Giderme

### Bağımlılık Hatası
```bash
# Eksik paketleri kur
sudo apt --fix-broken install

# Manuel kurulum
sudo apt install python3-pyside6.qtwidgets python3-watchdog
```

### İzin Hatası
```bash
# Scripte izin ver
chmod +x build_deb.sh
chmod +x debian/rules
```

### Build Hatası
```bash
# Temizlik yap
rm -rf build_deb/
debuild clean

# Tekrar dene
./build_deb.sh
```

---

## 📊 Paket İçeriği

Kurulum sonrası dosyalar:

```
/usr/bin/duplicate-agent                          # Launcher
/usr/share/DuplicateAgent/duplicateagent0.9.1.py  # Ana program
/usr/share/DuplicateAgent/src/                    # Modüller
/usr/share/DuplicateAgent/languages/              # Dil dosyaları
/usr/share/applications/duplicate-agent.desktop   # Desktop entry
/usr/share/pixmaps/duplicate-agent.png            # İkon
/usr/share/doc/duplicate-agent/                   # Dokümantasyon
```

---

## 🎁 PPA'ya Yükleme (Gelişmiş)

### Launchpad PPA Oluştur
```bash
# PPA oluştur (launchpad.net'te)
# GPG anahtarı oluştur
gpg --gen-key

# Paketi imzala
debsign duplicate-agent_0.9.1-1_source.changes

# PPA'ya yükle
dput ppa:kullaniciadi/duplicate-agent duplicate-agent_0.9.1-1_source.changes
```

### Kullanıcılar İçin
```bash
sudo add-apt-repository ppa:kullaniciadi/duplicate-agent
sudo apt update
sudo apt install duplicate-agent
```

---

## 📝 Test Listesi

- [ ] Paket başarıyla oluşturuldu
- [ ] Kurulum hatasız tamamlandı
- [ ] Program çalışıyor
- [ ] Desktop entry görünüyor
- [ ] İkon doğru gösteriliyor
- [ ] Tüm diller yüklü
- [ ] Kaldırma sorunsuz
- [ ] Bağımlılıklar otomatik kuruldu

---

## 💡 İpuçları

1. **Test Ortamı**: İlk denemeyi sanal makinede yapın
2. **Versiyon**: Her değişiklikte versiyonu artırın
3. **Changelog**: Her değişikliği kaydedin
4. **Bağımlılıklar**: Minimum versiyon belirtin
5. **Temizlik**: Build sonrası temizlik yapın

---

## 🆘 Yardım

### Resmi Kaynaklar
- [Debian New Maintainers' Guide](https://www.debian.org/doc/manuals/maint-guide/)
- [Debian Policy Manual](https://www.debian.org/doc/debian-policy/)
- [Ubuntu Packaging Guide](https://packaging.ubuntu.com/)

### Hata Raporlama
GitHub Issues: https://github.com/shampuan/Duplicate-Agent/issues

---

**İyi şanslar! 🚀**
