#!/usr/bin/env python3
import sys
import os
import hashlib
import shutil
import stat
from datetime import datetime
import getpass
from urllib.parse import quote
import subprocess # <<< YENİ EKLEME: İşletim sistemi komutlarını çalıştırmak için
import platform   # <<< YENİ EKLEME: İşletim sistemini tespit etmek için

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QListWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QCheckBox, QProgressBar,
    QAbstractItemView, QFileDialog, QMessageBox, QTextEdit,
    QRadioButton, QButtonGroup, QAbstractButton
)
from PySide6.QtCore import Qt, Signal, Slot, QThread, QLocale, QSize
from PySide6.QtGui import QColor, QBrush, QIcon, QPixmap

# --- GNOME/Qt Platform Plugin Fix ---
# Burası gnome ortamında qtnin sıkıntı çıkarmaması için.
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''
os.environ['QT_PLUGIN_PATH'] = ''
# ------------------------------------

# --- GLOBAL DİL VERİLERİ ve PROGRAM ADI GÜNCELLEMESİ ---
DEFAULT_LANG = "en"
CURRENT_LANG = DEFAULT_LANG

# --- YENİ FİLTRE SABİTLERİ VE EŞLEŞTİRMELERİ ---
# Uzantı filtreleri
EXTENSION_FILTERS = {
    "all": [], # Hepsi
    "audio": [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"],
    "video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".ico", ".raw"],
    "text": [".txt", ".log", ".md", ".json", ".xml", ".ini", ".conf", ".cfg", ".sh", ".py", ".html", ".css", ".js"],
    "office": [".doc", ".docx", ".odt", ".xls", ".xlsx", ".ods", ".ppt", ".pptx", ".odp", ".rtf"],
    "pdf": [".pdf"],
    "archive": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz"],
    "custom": [] # Kullanıcı tarafından girilenler
}

_texts = {
    "en": {
        "title": "Duplicate Agent (beta)", "dirs_group": "Directories to Scan", "add_dir": "Add Directory...",
        "remove_selected": "Remove Selected", "match_group": "Matching Criteria", "match_content": "Match by File Content (Hash) (Recommended)",
        "match_size": "Match by File Size", "match_name": "Match by File Name (Optional)", "match_extension": "Match by File Extension (Optional)",
        "ignore_group": "Exclusion Rules", "ignore_zero_byte": "Exclude Zero-Byte Files", "ignore_system_hidden": "Exclude System/Hidden Files",
        "filter_group": "File Type Filter", "filter_all": "All File Types", "filter_audio": "Audio Files",
        "filter_video": "Video Files", "filter_image": "Image Files", "filter_text": "Text-Based Files",
        "filter_office": "Office Files (DOC, XLS, PPT etc.)", "filter_pdf": "PDF Files", "filter_archive": "Archive Files (ZIP, RAR, TAR etc.)",
        "filter_custom": "Custom Extension (e.g., .exe, .dat):", "start_scan": "⚡ Start Scan", "cancel_scan": "🛑 Cancel Scan", "rescan": "⚡ Rescan", "language": "Language",
        "about": "About", "found_duplicates": "Found Duplicate Files:", "col_delete": "Delete", "col_filename": "File Name",
        "col_path": "Folder Path", "col_size": "Size", "delete_selected": "Move Selected to Trash", "status_ready": "Ready. Start scanning.",
        "status_error_dir": "ERROR: Please add at least one directory to scan.", "status_canceled": "Scan Canceled. Restart.",
        "status_scanning": "1/2: Scanning file system...", "status_hashing": "2/2: Hashing {0} candidate files...",
        "status_hashing_file": "Hashing: {0}", "status_finished_none": "Scan Completed. {0} files checked, no duplicates found.",
        "status_finished": "Scan Completed. {0} duplicate groups found.", "trash_confirm_title": "Trash Confirmation",
        "trash_confirm_text": "Are you sure you want to move **{0}** files to the trash?\n(You can restore them from the trash.)",
        "trash_success": "Success: {0} files moved to trash.", "trash_error": "WARNING: {0} files moved, but {1} files failed (Permissions/Access etc.).",
        "trash_error_select": "Error: Please select files to move to trash.", "trash_canceled": "File moving canceled by user.",
        # --- HAKKINDA ÇEVİRİSİ ---
        "about_title": "About Duplicate Agent",
        "about_version": "Version", "about_license": "License", "about_lang": "Programming Language", "about_dev": "Developer",
        "about_purpose": "This program helps you find and delete files that were accidentally created multiple times on your system.",
        "about_warranty": "This program comes with no warranty.",
        "about_copyright": "Copyright",
    },
    "tr": {
        "title": "Kopya Ajanı (beta)", "dirs_group": "Taranacak Dizinler", "add_dir": "Dizin Ekle...",
        "remove_selected": "Seçileni Kaldır", "match_group": "Eşleştirme Kriterleri", "match_content": "Dosya İçeriği (Hash) ile Eşleştir (Önerilen)",
        "match_size": "Dosya Boyutu Eşleşmeli", "match_name": "Dosya Adı Eşleşmeli (Opsiyonel)", "match_extension": "Dosya Uzantısı Eşleşmeli (Opsiyonel)",
        "ignore_group": "Hariç Tutma Kuralları", "ignore_zero_byte": "Sıfır Bayt Dosyalarını Hariç Tut", "ignore_system_hidden": "Sistem/Gizli Dosyaları Hariç Tut",
        "filter_group": "Dosya Tipi Filtresi", "filter_all": "Tüm Dosya Tipleri", "filter_audio": "Ses Dosyaları",
        "filter_video": "Video Dosyaları", "filter_image": "Resim Dosyaları", "filter_text": "Metin Tabanlı Dosyalar",
        "filter_office": "Ofis Dosyaları (DOC, XLS, PPT vb.)", "filter_pdf": "PDF Dosyaları", "filter_archive": "Arşiv Dosyaları (ZIP, RAR, TAR vb.)",
        "filter_custom": "Özel Uzantı Girin (Örn: .exe, .dat):", "start_scan": "⚡ Taramayı Başlat", "cancel_scan": "🛑 Taramayı İptal Et", "rescan": "⚡ Yeniden Tara", "language": "Language",
        "about": "Hakkında", "found_duplicates": "Bulunan Kopya Dosyalar:", "col_delete": "Sil", "col_filename": "Dosya Adı",
        "col_path": "Klasör Yolu", "col_size": "Boyut", "delete_selected": "Seçilenleri Çöp Kutusuna Taşı", "status_ready": "Hazır. Taramayı Başlatın.",
        "status_error_dir": "HATA: Lütfen taramak istediğiniz en az bir dizin ekleyin.", "status_canceled": "Tarama İptal Edildi. Yeniden Başlatın.",
        "status_scanning": "1/2: Dosya sistemini tarıyor...", "status_hashing": "2/2: {0} aday dosya için Hash hesaplanıyor...",
        "status_hashing_file": "Hash hesaplanıyor: {0}", "status_finished_none": "Tarama Tamamlandı. {0} dosya kontrol edildi, kopya adayı bulunamadı.",
        "status_finished": "Tarama Tamamlandı. {0} kopya grubu bulundu.", "trash_confirm_title": "Çöp Kutusuna Taşıma Onayı",
        "trash_confirm_text": "Seçili **{0}** dosyayı çöp kutusuna taşımak istediğinizden emin misiniz?\n(Çöp kutusundan geri yükleyebilirsiniz.)",
        "trash_success": "Başarılı: {0} dosya çöp kutusuna taşındı.", "trash_error": "UYARI: {0} dosya taşındı, ancak {1} dosyada hata oluştu (İzinler/Erişim vb.).",
        "trash_error_select": "Hata: Lütfen çöp kutusuna taşımak istediğiniz dosyaları işaretleyin.", "trash_canceled": "Dosya taşıma işlemi kullanıcı tarafından iptal edildi.",
        # --- HAKKINDA ÇEVİRİSİ ---
        "about_title": "Kopya Ajanı Hakkında",
        "about_version": "Sürüm", "about_license": "Lisans", "about_lang": "Programlama Dili", "about_dev": "Geliştirici",
        "about_purpose": "Bu program, sisteminizdeki yanlışlıkla birden fazla kez oluşturulmuş dosyaları tespit ederek silmenizi sağlar.",
        "about_warranty": "Bu program hiçbir garanti getirmez.",
        "about_copyright": "Telif Hakkı",
    }
}

# ----------------------------------------------------------------------
# 0. BURASI SİMGE YÖNETİMİ VE YARDIMCI FONKSİYONLAR
# ----------------------------------------------------------------------

def _find_icon_path(icon_name="dup.png"):
    """
    Simgesi dosyasını arar: Önce çalışan dizin, sonra sistem yolu.
    """
    # 1. Çalışan dizin (py dosyasının bulunduğu yer)
    # script_dir = os.path.dirname(os.path.abspath(__file__)) # Bu bazen __main__ ile çalışmayabilir.
    current_working_dir = os.getcwd()
    path_in_cwd = os.path.join(current_working_dir, icon_name)
    if os.path.exists(path_in_cwd):
        return path_in_cwd

    # 2. Sistem yolu
    system_path = os.path.join("/usr/share/Duplicate Agent/", icon_name)
    if os.path.exists(system_path):
        return system_path

    return None # Bulunamadı

# <<< YENİ EKLEME: İŞLETİM SİSTEMİ İLE DOSYA/KLASÖR AÇMA FONKSİYONU BAŞLANGICI >>>

def open_path_in_os(path):
    """
    Belirtilen yolu (dosya veya klasör) işletim sisteminin varsayılan uygulamasıyla açar.
    """
    system = platform.system()
    try:
        if system == "Windows":
            # Windows'ta Explorer'ı veya varsayılan programı kullan
            subprocess.run(['start', '', path], shell=True, check=True)
        elif system == "Darwin":
            # macOS'te 'open' komutunu kullan
            subprocess.run(['open', path], check=True)
        elif system == "Linux":
            # Linux'ta platformlar arası 'xdg-open'ı kullan
            subprocess.run(['xdg-open', path], check=True)
        else:
            return False
        return True
    except subprocess.CalledProcessError as e:
        print(f"HATA: Dosya/Klasör açılamadı: {e}")
        return False
    except FileNotFoundError:
        print(f"HATA: İşletim sistemi komutu bulunamadı.")
        return False

# <<< YENİ EKLEME: İŞLETİM SİSTEMİ İLE DOSYA/KLASÖR AÇMA FONKSİYONU SONU >>>


# ----------------------------------------------------------------------
# 1. BURASI HASH VE TARAMA MANTIĞI
# ----------------------------------------------------------------------

def calculate_md5(filepath, chunk_size=4096):
    """Büyük dosyalar için belleği yormadan MD5 hash'ini hesaplar."""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except IOError:
        return None

def format_size(size):
    """Bayt cinsinden boyutu okunabilir formata çevirir."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:3.1f} {unit}"
        size /= 1024.0
    return f"{size:3.1f} PB"


class WorkerThread(QThread):
# ... (WorkerThread sınıfı) ...
    progress_updated = Signal(int)
    status_message = Signal(str) # Doğru sinyal
    scan_finished = Signal(list)

    def __init__(self, target_dirs, options, parent=None):
        super().__init__(parent)
        self.target_dirs = target_dirs
        self.options = options
        self._is_running = True

    def run(self):

        # --- FİLTRELEME İŞLEMİNİN HAZIRLANMASI BAŞLANGICI (YENİ EKLEME) ---
        # Filtreleme seçeneklerini al
        file_filters = self.options["filter"]
        allowed_extensions = set()

        # Özel uzantı girişi
        custom_extensions_raw = file_filters.get("custom_extensions", "").strip()

        # Radyo düğmelerinden seçilen uzantı grubunu belirle
        selected_filter_key = "all"
        # EXTENSION_FILTERS keys'ini sırayla kontrol et
        filter_keys = ["audio", "video", "image", "text", "office", "pdf", "archive", "custom"]
        if file_filters.get("all") == True:
            selected_filter_key = "all"
        else:
            for key in filter_keys:
                if file_filters.get(key) == True:
                    selected_filter_key = key
                    break
        
        # Seçilen uzantı grubunu al
        if selected_filter_key != "all" and selected_filter_key != "custom":
            allowed_extensions.update(EXTENSION_FILTERS.get(selected_filter_key, []))
            
        # Özel uzantıları işle ve ekle
        if selected_filter_key == "custom" and custom_extensions_raw:
            # Kullanıcıdan gelen uzantıları virgülle ayırıp temizle ve '.önek' ekle
            for ext in custom_extensions_raw.lower().replace(" ", "").split(','):
                if ext:
                    if not ext.startswith('.'):
                        ext = '.' + ext
                    allowed_extensions.add(ext)

        # Uzantı setini büyük/küçük harf duyarsız arama için sadece küçük harfe çevir
        allowed_extensions = {ext.lower() for ext in allowed_extensions}

        # Filtreleme yapılacak mı kontrol et
        is_filtering_active = selected_filter_key != "all" and bool(allowed_extensions)
        # --- FİLTRELEME İŞLEMİNİN HAZIRLANMASI SONU ---


        self.status_message.emit(_texts[CURRENT_LANG]["status_scanning"])
        all_files_by_size = {}
        total_files = 0

        for base_dir in self.target_dirs:
            if not self._is_running: return

            for root, dirs, files in os.walk(base_dir):
                if not self._is_running: return

                for file_name in files:
                    full_path = os.path.join(root, file_name)

                    try:
                        file_stats = os.stat(full_path)
                        file_size = file_stats.st_size
                    except:
                        continue

                    if self.options["ignore"]["ignore_zero_byte"] and file_size == 0:
                        continue
                    if self.options["ignore"]["ignore_system_hidden"] and file_name.startswith('.'):
                        continue

                    # --- UZANTI FİLTRELEME UYGULAMASI BAŞLANGICI ---
                    if is_filtering_active:
                        file_ext = os.path.splitext(file_name)[1].lower()
                        if file_ext not in allowed_extensions:
                            continue
                    # --- UZANTI FİLTRELEME UYGULAMASI SONU ---

                    if file_size not in all_files_by_size:
                        all_files_by_size[file_size] = []
                    all_files_by_size[file_size].append(full_path)
                    total_files += 1

        candidate_groups = {size: paths for size, paths in all_files_by_size.items() if len(paths) > 1}
        total_candidates = sum(len(paths) for paths in candidate_groups.values())

        if total_candidates == 0:
            self.status_message.emit(_texts[CURRENT_LANG]["status_finished_none"].format(total_files))
            self.scan_finished.emit([])
            return

        self.status_message.emit(_texts[CURRENT_LANG]["status_hashing"].format(total_candidates))

        files_by_hash = {}
        processed_count = 0

        for size, file_paths in candidate_groups.items():
            for file_path in file_paths:
                if not self._is_running: return

                processed_count += 1
                progress = int((processed_count / total_candidates) * 100)
                self.progress_updated.emit(progress)
                self.status_message.emit(_texts[CURRENT_LANG]["status_hashing_file"].format(os.path.basename(file_path)))

                file_hash = calculate_md5(file_path)

                if not file_hash:
                    continue

                if self.options["match"]["name"]:
                    file_hash = f"{file_hash}-{os.path.basename(file_path)}"

                if self.options["match"]["extension"]:
                    file_name, file_ext = os.path.splitext(os.path.basename(file_path))
                    file_hash = f"{file_hash}-{file_ext.lower()}"

                if file_hash:
                    if file_hash not in files_by_hash:
                        files_by_hash[file_hash] = []
                    files_by_hash[file_hash].append(file_path)

        final_duplicates = []
        for file_hash, file_paths in files_by_hash.items():
            if len(file_paths) > 1:
                try:
                    file_size_bytes = os.stat(file_paths[0]).st_size
                    final_duplicates.append({
                        "hash": file_hash,
                        "size": format_size(file_size_bytes),
                        "files": file_paths
                    })
                except:
                    continue

        # <<< HATA DÜZELTİLDİ: status_label yerine status_message kullanıldı >>>
        self.status_message.emit(_texts[CURRENT_LANG]["status_finished"].format(len(final_duplicates)))

        self.progress_updated.emit(100)
        self.scan_finished.emit(final_duplicates)

    def stop(self):
        self._is_running = False

# ----------------------------------------------------------------------
# 2. ANA PENCERE (DuplicateFinderApp)
# ----------------------------------------------------------------------

# --- Çöp Kutusu Yönetimi (Thunar/XFCE KRİTİK DÜZELTME DAHİL) ---
# ... (_get_trash_base ve _move_to_trash fonksiyonları olduğu gibi kalır)

def _get_trash_base(filepath):
    """Dosyanın ait olduğu sistem/partisyon için çöp kutusunun kök dizinini bulur."""

    try:
        uid = os.getuid()
    except AttributeError:
        uid = 1000

    home_dir = os.path.expanduser('~')

    # 1. Standart HOME dizininden temizlik yapılırken geçerli çöp kuralını burası yönetir
    if os.path.abspath(filepath).startswith(home_dir):
        return os.path.join(home_dir, '.local', 'share', 'Trash')

    # 2. Harici Disk/Partisyondan temizlik yapıyorsak çöp kuralını burası yönetir
    else:
        current_path = os.path.abspath(filepath)
        current_dir = os.path.dirname(current_path)

        while True:
            parent_dir = os.path.dirname(current_dir)
            if os.path.ismount(current_dir) or parent_dir == current_dir:
                break
            current_dir = parent_dir

        return os.path.join(current_dir, f'.Trash-{uid}')

def _move_to_trash(filepath):
    """Dosyayı uygun çöp kutusu dizinine taşır ve Freedesktop uyumlu meta veri (info) dosyasını oluşturur."""
# Hadi inşallah bakalım
# Olmuyo amk kafayı yicem
    original_path = os.path.abspath(filepath)
    trash_base = _get_trash_base(original_path)

    trash_files_dir = os.path.join(trash_base, 'files')
    trash_info_dir = os.path.join(trash_base, 'info')

    try:
        os.makedirs(trash_files_dir, exist_ok=True)
        os.makedirs(trash_info_dir, exist_ok=True)

        if not original_path.startswith(os.path.expanduser('~')):
            # Harici disklerde .Trash-UID'nin iznini ayarla
            os.chmod(trash_base, 0o700)

    except Exception as e:
        # Hata yönetimi (örneğin dosya yazma izni yok)
        print(f"HATA: Çöp kutusu dizinleri oluşturulamadı: {e}")
        return False

    try:
        # Dosya Adını Çakışma Olmadan Taşıma
        target_filename = os.path.basename(original_path)

        counter = 1
        trash_filename = target_filename

        while os.path.exists(os.path.join(trash_files_dir, trash_filename)):
            name, ext = os.path.splitext(target_filename)
            name_part = name.split('.')[0]
            trash_filename = f"{name_part}.{counter}{ext}"
            counter += 1

        target_path = os.path.join(trash_files_dir, trash_filename)

        # Dosyayı taşı
        shutil.move(original_path, target_path)

        # Meta Veri (Info) Dosyasını Oluştur.
        info_filename = trash_filename + '.trashinfo'
        info_path = os.path.join(trash_info_dir, info_filename)

        deletion_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        # <<<<<<< KRİTİK THUNAR DÜZELTMESİ BAŞLANGICI >>>>>>>
        # Buraya ilerde bakıcam sıyırmak üzereyim.
        path = original_path
        home_dir = os.path.expanduser('~')

        # 1. Yolu URI kodla (Boşlukları, Türkçe karakterleri kodla, '/' ve ':' hariç)
        encoded_path = quote(path, safe='/:')

        # 2. KRİTİK KOŞUL: Eğer dosya Home dizinindeyse (veya aynı partisyondaysa),
        # Thunar'ın yaptığı gibi 'file:///' şemasını ATLA. Sadece kodlanmış mutlak yolu kullan.
        if original_path.startswith(home_dir):
            # Path=/home/serhat/Masa%C3%BCst%C3%BC/... formatı
            uri_path = encoded_path
        else:
            # Harici disklerde/partisyonlarda standart olan 'file:///' şemasını kullan.
            # file:///mnt/disk/dosya formatı
            uri_path = "file://" + encoded_path

        # <<<<<<< KRİTİK THUNAR DÜZELTMESİ SONU >>>>>>>

        trash_info_content = f"""
[Trash Info]
Path={uri_path}
DeletionDate={deletion_date}
"""

        with open(info_path, 'w', encoding='utf-8') as f:
            f.write(trash_info_content.strip())

        return True

    except Exception as e:
        print(f"Taşıma/Meta Veri Hatası: {e}")
        return False
# -----------------------------

class DuplicateFinderApp(QMainWindow):

    GROUP_COLORS = [QColor("#3cb5ff"), QColor("#d7b981")]

    def __init__(self):
        global CURRENT_LANG
        super().__init__()

        self.icon_path = _find_icon_path() # Simge yolunu bul

        self._update_gui_texts(DEFAULT_LANG)

        self.setGeometry(100, 100, 1000, 750) # << PENCERE YÜKSEKLİĞİ ARTIRILDI (650 -> 750)
        self.worker_thread = None

        # Pencere simgesini ayarla
        if self.icon_path:
            self.setWindowIcon(QIcon(self.icon_path))
        else:
            # Yedek simge (eğer bulunamazsa)
            self.setWindowIcon(QIcon(":/qt-project.org/qmessagebox/images/information.png"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self._setup_ui()
        self._connect_signals()
        self._setup_dir_management()

    # ... (Diğer metodlar aynı kalır) ...
    def _update_gui_texts(self, lang):
        global CURRENT_LANG
        CURRENT_LANG = lang
        texts = _texts[lang]

        try:
            self.setWindowTitle(texts["title"])

            # Logo ve Başlık Label'ları güncelleme
            if self.icon_path:
                scaled_size = 64
                pixmap = QPixmap(self.icon_path)
                self.logo_icon_label.setPixmap(pixmap.scaled(scaled_size, scaled_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.logo_icon_label.setVisible(True) # İkonu göster
            else:
                 self.logo_icon_label.setVisible(False) # İkon bulunamazsa gizle

            # Logo text (Yazılım Adı) güncelleme
            self.logo_text_label.setText(texts["title"])

            self.dir_group.setTitle(texts["dirs_group"])
            self.add_dir_btn.setText(texts["add_dir"])
            self.remove_dir_btn.setText(texts["remove_selected"])

            self.match_group.setTitle(texts["match_group"])
            self.match_content.setText(texts["match_content"])
            self.match_size.setText(texts["match_size"])
            self.match_name.setText(texts["match_name"])
            self.match_extension.setText(texts["match_extension"])

            self.ignore_group.setTitle(texts["ignore_group"])
            self.ignore_zero_byte.setText(texts["ignore_zero_byte"])
            self.ignore_system_hidden.setText(texts["ignore_system_hidden"])

            # --- YENİ FİLTRELEMELERİN ÇEVİRİSİ BAŞLANGICI ---
            self.filter_group.setTitle(texts["filter_group"])
            self.filter_all.setText(texts["filter_all"])
            self.filter_audio.setText(texts["filter_audio"])
            self.filter_video.setText(texts["filter_video"])
            self.filter_image.setText(texts["filter_image"])
            self.filter_text.setText(texts["filter_text"])
            self.filter_office.setText(texts["filter_office"])
            self.filter_pdf.setText(texts["filter_pdf"])
            self.filter_archive.setText(texts["filter_archive"])
            self.custom_ext_label.setText(texts["filter_custom"])
            # --- YENİ FİLTRELEMELERİN ÇEVİRİSİ SONU ---

            # Tarama durumu mesajları için dinamik güncelleme
            is_scanning = self.worker_thread and self.worker_thread.isRunning()
            current_text_is_rescan = self.start_button.text() == _texts["tr"]["rescan"] or self.start_button.text() == _texts["en"]["rescan"]

            if is_scanning:
                 self.start_button.setText(texts["cancel_scan"])
                 self.start_button.setStyleSheet("background-color: #FFA500; color: white; font-weight: bold; height: 35px;")
            elif current_text_is_rescan:
                 self.start_button.setText(texts["rescan"])
                 self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 35px;")
            else:
                 self.start_button.setText(texts["start_scan"])
                 self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 35px;")

            self.language_button.setText(texts["language"])
            self.about_button.setText(texts["about"])

            self.found_label.setText(texts["found_duplicates"])
            self.results_table.setHorizontalHeaderLabels([texts["col_delete"], texts["col_filename"], texts["col_path"], texts["col_size"]])
            self.delete_button.setText(texts["delete_selected"])

            # Hazır durumu mesajını güncelle
            if not self.status_label.text().startswith("Durum:") and not self.status_label.text().startswith("Status:"):
                 self.status_label.setText(texts["status_ready"])

        except AttributeError:
            # UI öğeleri henüz oluşturulmamışsa (init sırasında) hata vermemek için
            pass

    @Slot()
    def _toggle_language(self):
        new_lang = "tr" if CURRENT_LANG == "en" else "en"
        self._update_gui_texts(new_lang)

    def _setup_dir_management(self):
        self.add_dir_btn.clicked.connect(self._open_dir_dialog)
        self.remove_dir_btn.clicked.connect(self._remove_selected_dir)

    @Slot()
    def _open_dir_dialog(self):
        dialog_title = _texts[CURRENT_LANG]["add_dir"].replace("...", "").strip()
        # Varsayılan başlangıç dizini olarak kullanıcının HOME dizinini belirle
        home_dir = os.path.expanduser('~')
        selected_dir = QFileDialog.getExistingDirectory(self, dialog_title, home_dir)
        if selected_dir and selected_dir not in [self.dir_list.item(i).text() for i in range(self.dir_list.count())]:
            self.dir_list.addItem(selected_dir)
            self.dir_input.setText(selected_dir)

    @Slot()
    def _remove_selected_dir(self):
        for item in self.dir_list.selectedItems():
            self.dir_list.takeItem(self.dir_list.row(item))

    def _setup_ui(self):

        settings_panel = QWidget()
        settings_layout = QVBoxLayout(settings_panel)
        settings_panel.setFixedWidth(350)

        # --- LOGO VE BAŞLIK DÜZENLEMESİ ---
        logo_title_layout = QHBoxLayout()
        logo_title_layout.setAlignment(Qt.AlignLeft)

        self.logo_icon_label = QLabel()
        self.logo_icon_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.logo_icon_label.setStyleSheet("margin-right: 5px;")

        self.logo_text_label = QLabel()
        self.logo_text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.logo_text_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #0078D4;")

        logo_title_layout.addWidget(self.logo_icon_label)
        logo_title_layout.addWidget(self.logo_text_label)
        logo_title_layout.addStretch(1)

        settings_layout.addLayout(logo_title_layout)

        # --- TARANACAK DİZİNLER ---
        self.dir_group = QGroupBox()
        dir_layout = QVBoxLayout(self.dir_group)
        self.dir_list = QListWidget()
        self.dir_list.setMaximumHeight(100) # << Dizin listesi kutucuğunun yüksekliği azaltıldı
        self.dir_input = QLineEdit()

        dir_buttons_layout = QHBoxLayout()
        self.add_dir_btn = QPushButton()
        self.remove_dir_btn = QPushButton()

        dir_buttons_layout.addWidget(self.add_dir_btn)
        dir_buttons_layout.addWidget(self.remove_dir_btn)

        dir_layout.addWidget(self.dir_input)
        dir_layout.addLayout(dir_buttons_layout)
        dir_layout.addWidget(self.dir_list)
        settings_layout.addWidget(self.dir_group)

        # --- EŞLEŞTİRME KRİTERLERİ ---
        self.match_group = QGroupBox()
        match_layout = QVBoxLayout(self.match_group)
        self.match_content = QCheckBox()
        self.match_content.setChecked(True)
        self.match_size = QCheckBox()
        self.match_size.setChecked(True)
        self.match_name = QCheckBox()
        self.match_extension = QCheckBox()

        match_layout.addWidget(self.match_content)
        match_layout.addWidget(self.match_size)
        match_layout.addWidget(self.match_name)
        match_layout.addWidget(self.match_extension)
        settings_layout.addWidget(self.match_group)

        # --- HARİÇ TUTMA KURALLARI ---
        self.ignore_group = QGroupBox()
        ignore_layout = QVBoxLayout(self.ignore_group)

        self.ignore_zero_byte = QCheckBox()
        self.ignore_system_hidden = QCheckBox()

        self.ignore_zero_byte.setChecked(True)
        self.ignore_system_hidden.setChecked(True)

        ignore_layout.addWidget(self.ignore_zero_byte)
        ignore_layout.addWidget(self.ignore_system_hidden)

        settings_layout.addWidget(self.ignore_group)

        # --- YENİ DOSYA TİPİ FİLTRESİ BAŞLANGICI ---
        self.filter_group = QGroupBox()
        filter_layout = QVBoxLayout(self.filter_group)
        self.filter_button_group = QButtonGroup(self) # Radyo düğmeleri için grup oluştur

        self.filter_all = QRadioButton()
        self.filter_audio = QRadioButton()
        self.filter_video = QRadioButton()
        self.filter_image = QRadioButton()
        self.filter_text = QRadioButton()
        self.filter_office = QRadioButton()
        self.filter_pdf = QRadioButton()
        self.filter_archive = QRadioButton()
        self.filter_custom_radio = QRadioButton()

        self.filter_all.setChecked(True) # Varsayılan olarak hepsi seçili

        # Radyo düğmelerini gruba ve düzene ekle
        self.filter_button_group.addButton(self.filter_all, 0)
        self.filter_button_group.addButton(self.filter_audio, 1)
        self.filter_button_group.addButton(self.filter_video, 2)
        self.filter_button_group.addButton(self.filter_image, 3)
        self.filter_button_group.addButton(self.filter_text, 4)
        self.filter_button_group.addButton(self.filter_office, 5)
        self.filter_button_group.addButton(self.filter_pdf, 6)
        self.filter_button_group.addButton(self.filter_archive, 7)
        self.filter_button_group.addButton(self.filter_custom_radio, 8)

        filter_layout.addWidget(self.filter_all)
        filter_layout.addWidget(self.filter_audio)
        filter_layout.addWidget(self.filter_video)
        filter_layout.addWidget(self.filter_image)
        filter_layout.addWidget(self.filter_text)
        filter_layout.addWidget(self.filter_office)
        filter_layout.addWidget(self.filter_pdf)
        filter_layout.addWidget(self.filter_archive)

        # Özel uzantı girişi (Radyo düğmesi + LineEdit)
        custom_ext_layout = QHBoxLayout()
        self.custom_ext_label = QLabel()
        self.custom_ext_input = QLineEdit()
        self.custom_ext_input.setPlaceholderText(".mp4,.exe,.dat") # Örnek metin

        custom_ext_layout.addWidget(self.filter_custom_radio)
        custom_ext_layout.addWidget(self.custom_ext_label)
        custom_ext_layout.addWidget(self.custom_ext_input)

        filter_layout.addLayout(custom_ext_layout)

        settings_layout.addWidget(self.filter_group)
        # --- YENİ DOSYA TİPİ FİLTRESİ SONU ---

        self.start_button = QPushButton()
        # Stil, _update_gui_texts içinde ayarlanacak

        action_buttons_layout = QHBoxLayout()
        self.language_button = QPushButton()
        self.about_button = QPushButton()

        action_buttons_layout.addWidget(self.language_button)
        action_buttons_layout.addWidget(self.about_button)

        settings_layout.addWidget(self.start_button)
        settings_layout.addLayout(action_buttons_layout)

        settings_layout.addStretch(1) # Geri kalan boşluğu doldurur
        self.main_layout.addWidget(settings_panel)

        results_panel = QWidget()
        results_layout = QVBoxLayout(results_panel)

        self.found_label = QLabel()
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)

        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        results_layout.addWidget(self.found_label)
        results_layout.addWidget(self.results_table)

        status_label_layout = QHBoxLayout()
        self.status_label = QLabel()
        self.status_label.setMinimumWidth(300)
        self.delete_button = QPushButton()
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; height: 30px;")

        status_label_layout.addWidget(self.status_label, 1)
        status_label_layout.addWidget(self.delete_button)

        progress_bar_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)

        progress_bar_layout.addWidget(self.progress_bar)

        results_layout.addLayout(status_label_layout)
        results_layout.addLayout(progress_bar_layout)

        self.main_layout.addWidget(results_panel)

        self._update_gui_texts(DEFAULT_LANG)

    def _connect_signals(self):
        self.start_button.clicked.connect(self._start_scan)
        self.delete_button.clicked.connect(self._delete_files_to_trash)
        self.language_button.clicked.connect(self._toggle_language)
        self.about_button.clicked.connect(self._show_about)
        
        # YENİ BAĞLANTI: Çift tıklama olayını bağla
        self.results_table.cellDoubleClicked.connect(self._handle_double_click) 
        
        # Filtreleme seçenekleri etkileşimi (YENİ EKLEME)
        self.filter_button_group.buttonClicked.connect(self._handle_filter_selection)
        # Başlangıçta custom girişi pasif yap
        self.custom_ext_input.setEnabled(False)

    @Slot(QAbstractButton) # << HATA GİDERİLDİ: QAbstractButton kullanıldı
    def _handle_filter_selection(self, button):
        # Eğer "Custom" radyo düğmesi seçiliyse, LineEdit'i etkinleştir.
        if button == self.filter_custom_radio:
            self.custom_ext_input.setEnabled(True)
            self.custom_ext_input.setFocus()
        else:
            self.custom_ext_input.setEnabled(False)

    # <<< YENİ EKLEME: ÇİFT TIKLAMA İŞLEVİ BAŞLANGICI >>>
    @Slot(int, int) # Satır ve sütun indeksi alır
    def _handle_double_click(self, row, column):
        """
        Sonuç tablosunda çift tıklama olayını işler.
        Sütun 1 (Dosya Adı) çift tıklanırsa dosyayı açar.
        Sütun 2 (Klasör Yolu) çift tıklanırsa klasörü açar.
        """
        try:
            # Sütun 1: Dosya Adı, Sütun 2: Klasör Yolu
            if column == 1 or column == 2:
                # 1. Dosya Adı ve Klasör Yolu sütunlarından bilgileri al
                file_name_item = self.results_table.item(row, 1)
                folder_path_item = self.results_table.item(row, 2)
                
                if not file_name_item or not folder_path_item:
                    return

                file_name = file_name_item.text()
                folder_path = folder_path_item.text()
                
                # 2. Tam yolu oluştur
                full_path = os.path.join(folder_path, file_name)

                # 3. Hangi eylemin yapılacağına karar ver
                if column == 1: # Dosya Adı sütununa çift tıklandı
                    path_to_open = full_path
                    self.status_label.setText(f"Durum: Dosya açılıyor: {file_name}")
                elif column == 2: # Klasör Yolu sütununa çift tıklandı
                    # Klasörü açmak için yolun dizin kısmını al (Zaten folder_path doğru yolu içerir)
                    path_to_open = folder_path.rstrip(os.path.sep) 
                    self.status_label.setText(f"Durum: Klasör açılıyor: {folder_path}")

                # 4. İşletim sistemi komutuyla aç
                if open_path_in_os(path_to_open):
                    # Başarılı mesajı, eğer dosya/klasör açma başarılı olursa durum mesajını sıfırlar
                    self.status_label.setText(_texts[CURRENT_LANG]["status_ready"])
                else:
                    self.status_label.setText(f"Durum: HATA: '{os.path.basename(path_to_open)}' açılamadı.")
                    
        except Exception as e:
            self.status_label.setText(f"Durum: Genel HATA: Çift tıklama işlenemedi. ({e})")
    # <<< YENİ EKLEME: ÇİFT TIKLAMA İŞLEVİ SONU >>>


    @Slot()
    def _show_about(self):
        texts = _texts[CURRENT_LANG]
        about_dialog = QMessageBox(self)
        about_dialog.setWindowTitle(texts["about"])

        # İkonu ayarla: Varsayılan ikonu kaldırıp kendi ikonumuzu kullan
        if self.icon_path:
            about_dialog.setIconPixmap(QPixmap(self.icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            about_dialog.setIcon(QMessageBox.Information) # Eğer ikon bulunamazsa varsayılanı kullan

        about_text = f"""
        <html>
        <head>
            <style>
                h3 {{ color: #0078D4; }}
                ul {{ list-style-type: none; padding-left: 0; }}
                li {{ margin-bottom: 5px; }}
            </style>
        </head>
        <body>
        <h3>{texts["about_title"]}</h3>
        <ul>
            <li><b>{texts["about_version"]}:</b> 0.3.0 (beta)</li>
            <li><b>{texts["about_license"]}:</b> GPLv3</li>
            <li><b>{texts["about_lang"]}:</b> Python3</li>
            <li><b>{texts["about_dev"]}:</b> A. Serhat KILIÇOĞLU (shampuan)</li>
            <li><b>Github:</b> <a href="https://www.github.com/shampuan">www.github.com/shampuan</a></li>
        </ul>
        <hr>
        <p>{texts["about_purpose"]}</p>
        <p><b>{texts["about_warranty"]}</b></p>
        <p>{texts["about_copyright"]} &copy; 2025 A. Serhat KILIÇOĞLU</p>
        </body>
        </html>
        """

        about_dialog.setText(about_text)
        about_dialog.exec()

    @Slot()
    def _start_scan(self):

        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop()
            self.worker_thread.wait()
            self.start_button.setText(_texts[CURRENT_LANG]["start_scan"])
            self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 35px;")
            self.status_label.setText(_texts[CURRENT_LANG]["status_canceled"])
            return

        match_options = {
            "content": self.match_content.isChecked(),
            "size": self.match_size.isChecked(),
            "name": self.match_name.isChecked(),
            "extension": self.match_extension.isChecked(),
        }

        ignore_options = {
            "ignore_zero_byte": self.ignore_zero_byte.isChecked(),
            "ignore_system_hidden": self.ignore_system_hidden.isChecked(),
        }
        
        # --- FİLTRELEME SEÇENEKLERİNİN TOPLANMASI BAŞLANGICI (YENİ EKLEME) ---
        filter_options = {
            "all": self.filter_all.isChecked(),
            "audio": self.filter_audio.isChecked(),
            "video": self.filter_video.isChecked(),
            "image": self.filter_image.isChecked(),
            "text": self.filter_text.isChecked(),
            "office": self.filter_office.isChecked(),
            "pdf": self.filter_pdf.isChecked(),
            "archive": self.filter_archive.isChecked(),
            "custom": self.filter_custom_radio.isChecked(),
            "custom_extensions": self.custom_ext_input.text()
        }
        # --- FİLTRELEME SEÇENEKLERİNİN TOPLANMASI SONU ---

        options = {"match": match_options, "ignore": ignore_options, "filter": filter_options}

        target_dirs = [self.dir_list.item(i).text() for i in range(self.dir_list.count())]

        if not target_dirs:
            self.status_label.setText(_texts[CURRENT_LANG]["status_error_dir"])
            return

        self.results_table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.delete_button.setEnabled(False)
        self.start_button.setText(_texts[CURRENT_LANG]["cancel_scan"])
        self.start_button.setStyleSheet("background-color: #FFA500; color: white; font-weight: bold; height: 35px;")

        self.worker_thread = WorkerThread(target_dirs, options)
        # Sinyal bağlantıları
        self.worker_thread.progress_updated.connect(self._update_progress)
        self.worker_thread.status_message.connect(self._update_status)
        self.worker_thread.scan_finished.connect(self._display_results)
        self.worker_thread.finished.connect(self._scan_finished_cleanup)
        self.worker_thread.start()

    @Slot(int)
    def _update_progress(self, value):
        self.progress_bar.setValue(value)

    @Slot(str)
    def _update_status(self, message):
        # Durum mesajları için status_label kullanıyoruz.
        self.status_label.setText(f"Durum: {message}")

    @Slot()
    def _scan_finished_cleanup(self):
        self.start_button.setText(_texts[CURRENT_LANG]["rescan"])
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 35px;")

    @Slot(list)
    def _display_results(self, duplicate_groups):

        self.results_table.setRowCount(0)
        row_count = 0

        for group_index, group in enumerate(duplicate_groups):

            group_color = self.GROUP_COLORS[group_index % len(self.GROUP_COLORS)]

            for file_index, file_path in enumerate(group["files"]):
                self.results_table.insertRow(row_count)

                file_name = os.path.basename(file_path)
                folder_path = os.path.dirname(file_path) + os.path.sep

                check_item = QTableWidgetItem()
                check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)

                if file_index == 0:
                    check_item.setCheckState(Qt.CheckState.Unchecked)
                else:
                    check_item.setCheckState(Qt.CheckState.Checked)

                self.results_table.setItem(row_count, 0, check_item)

                name_item = QTableWidgetItem(file_name)
                path_item = QTableWidgetItem(folder_path)
                size_item = QTableWidgetItem(group["size"])

                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row_count, col)
                    if not item:
                         item = QTableWidgetItem()
                         self.results_table.setItem(row_count, col, item)

                    item.setBackground(QBrush(group_color))

                self.results_table.setItem(row_count, 1, name_item)
                self.results_table.setItem(row_count, 2, path_item)
                self.results_table.setItem(row_count, 3, size_item)

                row_count += 1

        self.results_table.setRowCount(row_count)
        self.delete_button.setEnabled(row_count > 0)

    def _remove_deleted_rows(self, deleted_files_paths):

        deleted_set = set(deleted_files_paths)

        for row in range(self.results_table.rowCount() - 1, -1, -1):
            folder_path = self.results_table.item(row, 2).text()
            file_name = self.results_table.item(row, 1).text()
            full_path = os.path.join(folder_path, file_name)

            if full_path in deleted_set:
                self.results_table.removeRow(row)

        if self.results_table.rowCount() == 0:
            self.delete_button.setEnabled(False)

    @Slot()
    def _delete_files_to_trash(self):

        selected_files = []
        for row in range(self.results_table.rowCount()):
            item = self.results_table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                folder_path = self.results_table.item(row, 2).text()
                file_name = self.results_table.item(row, 1).text()
                full_path = os.path.join(folder_path, file_name)
                selected_files.append(full_path)

        if not selected_files:
            self.status_label.setText(_texts[CURRENT_LANG]["trash_error_select"])
            return

        reply = QMessageBox.question(
            self,
            _texts[CURRENT_LANG]["trash_confirm_title"],
            _texts[CURRENT_LANG]["trash_confirm_text"].format(len(selected_files)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            self.status_label.setText(_texts[CURRENT_LANG]["trash_canceled"])
            return

        moved_count = 0
        error_count = 0
        moved_paths = []

        self.status_label.setText("Seçilen dosyalar çöp kutusuna taşınıyor...")

        for file_path in selected_files:
            if _move_to_trash(file_path):
                moved_count += 1
                moved_paths.append(file_path)
            else:
                error_count += 1

        self._remove_deleted_rows(moved_paths)

        if error_count == 0:
            final_message = _texts[CURRENT_LANG]["trash_success"].format(moved_count)
            QMessageBox.information(self, "Taşıma Başarılı", final_message)
        else:
            final_message = _texts[CURRENT_LANG]["trash_error"].format(moved_count, error_count)
            QMessageBox.warning(self, "Taşıma Hatalı", final_message)

        self.status_label.setText(final_message)

# 3. BURASI UYGULAMA BAŞLANGICI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DuplicateFinderApp()
    window.show()
    sys.exit(app.exec())
