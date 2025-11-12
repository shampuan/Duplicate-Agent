#!/usr/bin/env python3

import sys
import os
import hashlib
import shutil
import stat
from datetime import datetime
import getpass
from urllib.parse import quote
import subprocess
import platform
import json
import configparser 

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QListWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QCheckBox, QProgressBar,
    QAbstractItemView, QFileDialog, QMessageBox, QTextEdit,
    QRadioButton, QButtonGroup, QAbstractButton, QTabWidget,
    QFileIconProvider, QMenu, QScrollArea # QScrollArea eklendi
)
from PySide6.QtCore import Qt, Signal, Slot, QThread, QLocale, QSize, QFileInfo
from PySide6.QtGui import QColor, QBrush, QIcon, QPixmap, QFont

# --- GNOME/Qt Platform Plugin Fix ---
os.environ['QT_QPA_PLATFORM'] = 'xcb' 
# --- Bu ayarı GNOME ortamında sıkıntı çıkmaması için ekliyorum. Aklı veren: YZ :)
# ------------------------------------

# --- GLOBAL DİL VERİLERİ ve PROGRAM ADI GÜNCELLEMESİ ---
DEFAULT_LANG = "en"
CURRENT_LANG = DEFAULT_LANG

# "Gözlerimizi kapayıp yalnız yaşadığımızı varsayamayız. Ülkemizi bir çember içine alıp dünya ile ilgilenmeksizin yaşayamayız. Tersine gelişmiş uygarl aşmış bir ulus olarak uygarlık alanının üzerinde yaşayacağız: bu yaşam ancak bilim ve fenle olur. Bilim ve fen nerede ise oradan alacağız ve ulusun her bireyinin kafasına koyacağız. Bilim ve fen için bağ ve koşul yoktur." M. Kemal ATATÜRK.

# Dil verileri için global değişken
_texts = {}

# FİLTRE SABİTLERİ Burası sayesinde kullanıcıya uzantı seçtirebiliyoruz. Şimdilik burası sorunsuz çalışıyor görünüyor. Olmazsa Fatihe bir sorayım. 
EXTENSION_FILTERS = {
    "all": [],
    "audio": [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"],
    "video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".ico", ".raw"],
    "text": [".txt", ".log", ".md", ".json", ".xml", ".ini", ".conf", ".cfg", ".sh", ".py", ".html", ".css", ".js"],
    "office": [".doc", ".docx", ".odt", ".xls", ".xlsx", ".ods", ".ppt", ".pptx", ".odp", ".rtf"],
    "pdf": [".pdf"],
    "archive": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz"],
    "custom": []
}

def load_language_files():
    """INI dosyalarından dil verilerini dinamik olarak yükler."""
    global _texts
    _texts = {}
    
    # Dil dosyalarının bulunabileceği yollar
    script_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        script_dir,  # Ana dosyanın bulunduğu dizin
        os.path.join(script_dir, 'languages'),  # languages alt dizini
        os.path.join(script_dir, 'lang'),  # lang alt dizini
        '/usr/share/DuplicateAgent/lang',  # Sistem dizini
        os.path.expanduser('~/.duplicateagent/lang')  # Kullanıcı dizini
    ]
    
    # Her yolda .ini dosyalarını dinamik olarak tara
    for path in possible_paths:
        if not os.path.exists(path):
            continue
            
        try:
            # Dizindeki tüm .ini dosyalarını bul
            for filename in os.listdir(path):
                if filename.lower().endswith('.ini'):
                    lang_path = os.path.join(path, filename)
                    
                    # Dosya adından dil kodunu çıkar (örn: Turkish.ini -> tr, English.ini -> en)
                    lang_name = os.path.splitext(filename)[0].lower()
                    
                    # Yaygın dil adlarını kodlara çevir
                    lang_mapping = {
                        'english': 'en',
                        'turkish': 'tr', 
                        'turkce': 'tr',
                        'deutsch': 'de',
                        'german': 'de',
                        'french': 'fr',
                        'francais': 'fr',
                        'spanish': 'es',
                        'espanol': 'es',
                        'italian': 'it',
                        'italiano': 'it',
                        'portuguese': 'pt',
                        'russian': 'ru',
                        'chinese': 'zh',
                        'japanese': 'ja',
                        'korean': 'ko',
                        'arabic': 'ar'
                    }
                    
                    lang_code = lang_mapping.get(lang_name, lang_name[:2] if len(lang_name) >= 2 else lang_name)
                    
                    try:
                        config = configparser.ConfigParser()
                        config.read(lang_path, encoding='utf-8')
                        
                        # INI dosyasındaki tüm bölümleri birleştir
                        lang_data = {}
                        for section in config.sections():
                            for key, value in config.items(section):
                                lang_data[key] = value
                        
                        _texts[lang_code] = lang_data
                        print(f"Dil dosyası yüklendi: {filename} -> {lang_code}")
                        
                    except Exception as e:
                        print(f"Dil dosyası yüklenirken hata: {lang_path} - {e}")
                        
        except Exception as e:
            print(f"Dizin taranırken hata: {path} - {e}")
    
    # En az İngilizce yüklenmişse başarılı
    if not _texts:
        print("UYARI: Hiç dil dosyası yüklenemedi!")
        _texts['en'] = {}  # Boş İngilizce sözlük oluştur

def get_available_languages():
    """Yüklenen tüm dillerin listesini döndürür."""
    return list(_texts.keys())

def get_text(key, lang=None):
    """Belirtilen anahtar için çeviriyi döndürür."""
    if lang is None:
        lang = CURRENT_LANG
    
    if lang in _texts and key in _texts[lang]:
        return _texts[lang][key]
    
    # Fallback: İngilizce'yi dene
    if lang != 'en' and 'en' in _texts and key in _texts['en']:
        return _texts['en'][key]
    
    # Son çare: anahtar adını döndür
    return f"[{key}]"

def save_language_preference(lang):
    """Kullanıcının dil tercihini kaydeder."""
    config_dir = os.path.expanduser('~/.duplicateagent')
    config_file = os.path.join(config_dir, 'settings.ini') #kullanıcnın son ayarladığı dili her açılışta geçerli yapıyoruz. 
    
    try:
        os.makedirs(config_dir, exist_ok=True)
        config = configparser.ConfigParser()
        config['PREFERENCES'] = {'language': lang}
        
        with open(config_file, 'w', encoding='utf-8') as f:
            config.write(f)
    except Exception as e:
        print(f"Dil tercihi kaydedilemedi: {e}")

def load_language_preference():
    """Kaydedilen dil tercihini yükler."""
    config_file = os.path.join(os.path.expanduser('~/.duplicateagent'), 'settings.ini')
    
    if os.path.exists(config_file):
        try:
            config = configparser.ConfigParser()
            config.read(config_file, encoding='utf-8')
            
            if 'PREFERENCES' in config and 'language' in config['PREFERENCES']:
                return config['PREFERENCES']['language']
        except Exception as e:
            print(f"Dil tercihi yüklenemedi: {e}")
    
    return DEFAULT_LANG

# ----------------------------------------------------------------------
# 0. YARDIMCI FONKSİYONLAR
# ----------------------------------------------------------------------

def _find_icon_path(icon_name="dup.png"):
    current_working_dir = os.getcwd()
    path_in_cwd = os.path.join(current_working_dir, icon_name)
    if os.path.exists(path_in_cwd):
        return path_in_cwd

    system_path = os.path.join("/usr/share/DuplicateAgent/", icon_name)
    if os.path.exists(system_path):
        return system_path

    return None

def open_path_in_os(path):
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(['start', '', path], shell=True, check=True)
        elif system == "Darwin":
            subprocess.run(['open', path], check=True)
        elif system == "Linux":
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

# <<< YENİ METOT: DOSYANIN BULUNDUĞU DİSKİ (MOUNT NOKTASINI) BULMA >>>
def get_mount_point(path):
    """Verilen dosya yolunun bağlı olduğu mount noktasını bulur. 
    Linux/Unix sistemlerde temel olarak os.path.ismount() kullanır.
    Diğer sistemlerde basitçe kök dizini veya sürücü harfini döndürür.
    """
    path = os.path.abspath(path)
    if platform.system() == "Linux" or platform.system() == "Darwin":
        while not os.path.ismount(path):
            parent = os.path.dirname(path)
            if parent == path: # Kök dizine ulaştık
                break
            path = parent
        return path
    elif platform.system() == "Windows":
        # Windows'ta sürücü harfini döndür (örn: C:\, D:\)
        drive, tail = os.path.splitdrive(path)
        if drive:
            return drive + os.path.sep
        return path # Fallback
    else:
        # Genel fallback
        return os.path.abspath(os.path.sep)
# <<< YENİ METOT SONU >>>

# "İnsanların hayatına, faaliyetine egemen olan kuvvet, yaratma icat yeteneğidir." M. Kemal ATATÜRK

# ----------------------------------------------------------------------
# 1. HASH VE TARAMA MANTIĞI
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
# MD5 neden gerekli: kullanıcı dosya adını değiştirdi ama içerik aynı. Bunu programın akıllı biçimde göstermesi gerekir. 

class WorkerThread(QThread):
    progress_updated = Signal(int)
    status_message = Signal(str)
    scan_finished = Signal(list)

    def __init__(self, target_dirs, options, parent=None):
        super().__init__(parent)
        self.target_dirs = target_dirs
        self.options = options
        self._is_running = True

    def run(self):
        # --- FİLTRELEME İŞLEMİNİN HAZIRLANMASI BAŞLANGICI ---
        file_filters = self.options["filter"]
        allowed_extensions = set()
        custom_extensions_raw = file_filters.get("custom_extensions", "").strip()

        selected_filter_key = "all"
        filter_keys = ["audio", "video", "image", "text", "office", "pdf", "archive", "custom"]
        if file_filters.get("all") == True:
            selected_filter_key = "all"
        else:
            for key in filter_keys:
                if file_filters.get(key) == True:
                    selected_filter_key = key
                    break
        
        if selected_filter_key != "all" and selected_filter_key != "custom":
            allowed_extensions.update(EXTENSION_FILTERS.get(selected_filter_key, []))
            
        if selected_filter_key == "custom" and custom_extensions_raw:
            for ext in custom_extensions_raw.lower().replace(" ", "").split(','):
                if ext:
                    if not ext.startswith('.'):
                        ext = '.' + ext
                    allowed_extensions.add(ext)

        allowed_extensions = {ext.lower() for ext in allowed_extensions}
        is_filtering_active = selected_filter_key != "all" and bool(allowed_extensions)
        # --- FİLTRELEME İŞLEMİNİN HAZIRLANMASI SONU --- Buraya şimdilik ellemeyelim düzgün çalışıyor.

        self.status_message.emit(get_text("status_scanning"))
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

                    # --- UZANTI FİLTRELEME UYGULAMASI ---
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
            self.status_message.emit(get_text("status_finished_none").format(total_files))
            self.scan_finished.emit([])
            return

        self.status_message.emit(get_text("status_hashing").format(total_candidates))

        files_by_hash = {}
        processed_count = 0

        for size, file_paths in candidate_groups.items():
            for file_path in file_paths:
                if not self._is_running: return

                processed_count += 1
                progress = int((processed_count / total_candidates) * 100)
                self.progress_updated.emit(progress)
                self.status_message.emit(get_text("status_hashing_file").format(os.path.basename(file_path)))

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
                        "size_bytes": file_size_bytes, 
                        "size": format_size(file_size_bytes),
                        "files": file_paths
                    })
                except:
                    continue

        self.status_message.emit(get_text("status_finished").format(len(final_duplicates)))

        self.progress_updated.emit(100)
        self.scan_finished.emit(final_duplicates)

    def stop(self):
        self._is_running = False

# ----------------------------------------------------------------------
# 2. FAKE TRASH YÖNETİM SINIFI 
# Sistem trash ile ilgili sorunları çözemeyince başka çarem kalmadı ve fake trash geliştirdim. 
# "Akıl ve mantığın çözümleyemeyeceği mesele yoktur." M. Kemal ATATÜRK
# ----------------------------------------------------------------------

class FakeTrashManager:
    """Sahte Çöp Kutusu dizinlerini ve metadata dosyasını DİSK BAZLI yönetir."""

    def __init__(self):
        # Artık global bir çöp dizini yönetmiyoruz. Sadece yapılandırma dosya tabanını tutalım.
        self.base_config_dir = os.path.join(os.path.expanduser('~'), '.duplicateagent')

    def _get_trash_paths(self, filepath):
        """Dosyanın bulunduğu diske (mount noktasına) göre çöp dizini ve metadata yollarını döndürür."""
        
        # Dosyanın ait olduğu mount noktasını bul
        mount_point = get_mount_point(filepath) 
        
        # Mount noktasında gizli bir çöp dizini oluştur (.Trash-DuplicateAgent)
        trash_dir = os.path.join(mount_point, '.Trash-DuplicateAgent')
        
        # Meta veri dosyası da aynı dizinde olacak
        metadata_path = os.path.join(trash_dir, 'trashdata.json')
        
        return trash_dir, metadata_path

    def _setup_disk_dirs(self, trash_dir):
        """Belirtilen diske ait çöp dizinini ve metadata dosyasını oluşturur."""
        metadata_path = os.path.join(trash_dir, 'trashdata.json')
        try:
            os.makedirs(trash_dir, exist_ok=True)
            if not os.path.exists(metadata_path):
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=4)
        except Exception as e:
            print(f"HATA: Disk Bazlı Fake Trash dizinleri oluşturulamadı: {e}")

    def _load_metadata(self, metadata_path):
        """Belirtilen metadata dosyasını okur ve JSON listesi döndürür."""
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_metadata(self, data, metadata_path):
        """Metadata listesini belirtilen dosyaya yazar."""
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"HATA: Metadata yazılamadı: {e}")
            return False

    def move_to_trash(self, filepath, file_size_bytes):
        """Dosyayı kendi diskindeki FakeTrash'a taşır ve metadata kaydını oluşturur."""
        original_path = os.path.abspath(filepath)
        
        # 1. Disk yollarını al ve dizini kur
        trash_dir, metadata_path = self._get_trash_paths(original_path)
        self._setup_disk_dirs(trash_dir) # Dizin ve metadata dosyasını oluşturur
        
        target_filename = os.path.basename(original_path)
        
        # Benzersiz dosya adı oluşturma 
        counter = 0
        name, ext = os.path.splitext(target_filename)
        postfix = int(datetime.now().timestamp() * 1000) 
        trash_filename = f"{name}_{postfix}{ext}"

        while os.path.exists(os.path.join(trash_dir, trash_filename)):
            counter += 1
            trash_filename = f"{name}_{postfix}_{counter}{ext}"

        target_path = os.path.join(trash_dir, trash_filename)
        
        try:
            # Aynı diskte olduğu için hızlı taşıma
            shutil.move(original_path, target_path)

            # Metadata güncelle
            metadata = self._load_metadata(metadata_path)
            new_entry = {
                "trash_filename": trash_filename,
                "original_path": original_path,
                "deletion_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "size": format_size(file_size_bytes),
                "size_bytes": file_size_bytes,
                "trash_dir": trash_dir # Hangi çöp dizininde olduğunu saklayalım.
            }
            metadata.append(new_entry)
            self._save_metadata(metadata, metadata_path)
            
            return True
        except Exception as e:
            print(f"Taşıma Hatası (Disk Bazlı): {e}")
            return False

    def get_trash_files(self):
        """Bu metod artık kullanılmayacak veya FakeTrashApp tarafından yönetilecek."""
        raise NotImplementedError("Disk bazlı yönetim nedeniyle bu metot artık DuplicateFinderApp tarafından yönetilmelidir.")

    def restore_file(self, trash_filename, original_path, trash_dir):
        """Dosyayı FakeTrash'tan orijinal konumuna geri yükler (trash_dir parametresi eklendi)."""
        trash_file_path = os.path.join(trash_dir, trash_filename)
        metadata_path = os.path.join(trash_dir, 'trashdata.json')
        
        if not os.path.exists(trash_file_path):
            return False 

        try:
            # Orijinal klasör yolunu kontrol et ve oluştur
            original_dir = os.path.dirname(original_path)
            os.makedirs(original_dir, exist_ok=True)

            # Dosyayı geri taşı
            shutil.move(trash_file_path, original_path)

            # Metadata kaydını sil
            metadata = self._load_metadata(metadata_path)
            metadata = [item for item in metadata if not (item["trash_filename"] == trash_filename and item["original_path"] == original_path)]
            self._save_metadata(metadata, metadata_path)
            
            return True
        except Exception as e:
            print(f"Geri Yükleme Hatası: {e}")
            return False

    def purge_file(self, trash_filename, original_path, trash_dir):
        """Dosyayı FakeTrash'tan kalıcı olarak siler (diskten siler)."""
        trash_file_path = os.path.join(trash_dir, trash_filename)
        metadata_path = os.path.join(trash_dir, 'trashdata.json')
        
        try:
            if os.path.exists(trash_file_path):
                os.remove(trash_file_path)

            # Metadata kaydını sil
            metadata = self._load_metadata(metadata_path)
            metadata = [item for item in metadata if not (item["trash_filename"] == trash_filename and item["original_path"] == original_path)]
            self._save_metadata(metadata, metadata_path)
            
            return True
        except Exception as e:
            print(f"Kalıcı Silme Hatası: {e}")
            return False


# ----------------------------------------------------------------------
# 3. ANA PENCERE (DuplicateFinderApp)
# ----------------------------------------------------------------------

class DuplicateFinderApp(QMainWindow):

    GROUP_COLORS = [QColor("#3cb5ff"), QColor("#d7b981")]

    def __init__(self):
        global CURRENT_LANG
        super().__init__()

        self.icon_path = _find_icon_path()
        self.trash_manager = FakeTrashManager() 
        self.duplicate_data = [] # Tarama sonuçlarını tutmak için
        
        # VİNŞ: Yeni başlangıç boyutu, ekran taşmasını engellemek için daha optimize edildi.
        self.setGeometry(100, 100, 900, 650) 
        self.worker_thread = None

        if self.icon_path:
            self.setWindowIcon(QIcon(self.icon_path))
        else:
            self.setWindowIcon(QIcon(":/qt-project.org/qmessagebox/images/information.png"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self._setup_ui()
        self._setup_dir_management() # Dizin yönetimi sinyalleri
        self._connect_signals()      # Ana pencere sinyalleri
        
        # Fake Trash sekmesini başlangıçta yükle
        # Artık başlangıçta sadece arayüz hazırlanır, tab change event'inde yükleme yapılır.
        # self.update_trash_tab() çağrısı kaldırıldı veya _handle_tab_change'e bırakıldı.
        
        # Dil dosylarını yükle
        load_language_files()
        
        # Kaydedilen dil tercihini yükle
        saved_lang = load_language_preference()
        self._update_gui_texts(saved_lang) 

    # <<< YENİ METOT: DOSYA İKONUNU GETİRME >>>
    def _get_file_icon(self, file_path):
        """Dosya yoluna göre sistemin varsayılan dosya ikonunu döndürür."""
        # QFileInfo, dosya hakkındaki bilgileri almak için kullanılır.
        file_info = QFileInfo(file_path)
        # QFileIconProvider, QFileInfo'ya göre sistem ikonunu döndürür.
        provider = QFileIconProvider()
        return provider.icon(file_info)
    # <<< YENİ METOT SONU >>>
# "Allah dünya üzerinde yarattığı bu kadar nimetleri bu kadar güzellikleri insanlar istifade etsin varlık içinde yaşasın diye yaratmıştır ve azamî derecede faydalanabilmek için de bütün yaratıklardan esirgediği zekâyı akıllı insanlara vermiştir." M. Kemal ATATÜRK

    def _update_gui_texts(self, lang):
        global CURRENT_LANG
        CURRENT_LANG = lang

        try:
            self.setWindowTitle(get_text("title", lang))

            # Logoyu yerleştiriyoruz (64x64 piksel olsun)
            if self.icon_path:
                scaled_size = 64
                pixmap = QPixmap(self.icon_path)
                self.logo_icon_label.setPixmap(pixmap.scaled(scaled_size, scaled_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.logo_icon_label.setVisible(True)
            else:
                 self.logo_icon_label.setVisible(False)
            self.logo_text_label.setText(get_text("title", lang))

            # Tarama Ayarları
            self.dir_group.setTitle(get_text("dirs_group", lang))
            self.add_dir_btn.setText(get_text("add_dir", lang))
            self.remove_dir_btn.setText(get_text("remove_selected", lang))
            self.match_group.setTitle(get_text("match_group", lang))
            self.match_content.setText(get_text("match_content", lang))
            self.match_size.setText(get_text("match_size", lang))
            self.match_name.setText(get_text("match_name", lang))
            self.match_extension.setText(get_text("match_extension", lang))
            self.ignore_group.setTitle(get_text("ignore_group", lang))
            self.ignore_zero_byte.setText(get_text("ignore_zero_byte", lang))
            self.ignore_system_hidden.setText(get_text("ignore_system_hidden", lang))
            self.filter_group.setTitle(get_text("filter_group", lang))
            self.filter_all.setText(get_text("filter_all", lang))
            self.filter_audio.setText(get_text("filter_audio", lang))
            self.filter_video.setText(get_text("filter_video", lang))
            self.filter_image.setText(get_text("filter_image", lang))
            self.filter_text.setText(get_text("filter_text", lang))
            self.filter_office.setText(get_text("filter_office", lang))
            self.filter_pdf.setText(get_text("filter_pdf", lang))
            self.filter_archive.setText(get_text("filter_archive", lang))
            self.custom_ext_label.setText(get_text("filter_custom", lang))

            # Sekmeler
            self.tab_widget.setTabText(0, get_text("tab_scan", lang))
            self.tab_widget.setTabText(1, get_text("tab_trash", lang))
            
            # --- Sahte Çöp Kutusu Sekmesi Başlığını Kırmızı Yaptık ---
            trash_tab_text = get_text("tab_trash", lang)
            self.tab_widget.setTabText(1, trash_tab_text)
            self.tab_widget.tabBar().setTabTextColor(1, QColor("red"))

            # Sonuçlar Tablosu
            self.found_label.setText(get_text("found_duplicates", lang))
            self.results_table.setHorizontalHeaderLabels([get_text("col_delete", lang), get_text("col_filename", lang), get_text("col_path", lang), get_text("col_size", lang)])
            self.delete_button.setText(get_text("delete_selected", lang))

            # Fake Trash Tablosu
            self.trash_table.setHorizontalHeaderLabels(["", get_text("trash_col_file", lang), get_text("trash_col_original_path", lang), get_text("trash_col_deletion_date", lang)])
            self.restore_button.setText(get_text("trash_restore", lang))
            self.purge_button.setText(get_text("trash_purge", lang))
            self.select_all_trash_button.setText(get_text("select_all", lang))
            self.unselect_all_trash_button.setText(get_text("unselect_all", lang))


            # Tarama Butonu ve Durum
            is_scanning = self.worker_thread and self.worker_thread.isRunning()
            current_text_is_rescan = self.start_button.text() == get_text("rescan", "tr") or self.start_button.text() == get_text("rescan", "en")

            if is_scanning:
                 self.start_button.setText(get_text("cancel_scan", lang))
                 self.start_button.setStyleSheet("background-color: #FFA500; color: white; font-weight: bold; height: 35px;")
            elif current_text_is_rescan:
                 self.start_button.setText(get_text("rescan", lang))
                 self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 35px;")
            else:
                 self.start_button.setText(get_text("start_scan", lang))
                 self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 35px;")

            self.language_button.setText(get_text("language", lang))
            self.about_button.setText(get_text("about", lang))

            # Durum Etiketi Düzeltmesi - Dil değiştiğinde de güncelle
            current_status = self.status_label.text()
            if current_status == "" or "Ready to scan" in current_status or "Taramaya hazır" in current_status:
                 self.status_label.setText(f'{get_text("status_prefix", lang)}: {get_text("status_ready", lang)}')
            elif ":" in current_status:
                # Mevcut durum mesajını koruyarak sadece prefix'i güncelle
                status_parts = current_status.split(":", 1)
                if len(status_parts) == 2:
                    self.status_label.setText(f'{get_text("status_prefix", lang)}:{status_parts[1]}')
                else:
                    self.status_label.setText(f'{get_text("status_prefix", lang)}: {get_text("status_ready", lang)}')

        except AttributeError:
            pass

    @Slot()
    def _show_language_menu(self):
        menu = QMenu(self)
        available_langs = get_available_languages()
        
        # Dil adları mapping
        lang_names = {
            'en': 'English',
            'tr': 'Türkçe',
            'de': 'Deutsch',
            'fr': 'Français',
            'es': 'Español',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'zh': '中文',
            'ja': '日本語',
            'ko': '한국어',
            'ar': 'العربية'
        }
        
        for lang_code in available_langs:
            lang_name = lang_names.get(lang_code, lang_code.upper())
            action = menu.addAction(lang_name)
            action.setData(lang_code)
            if lang_code == CURRENT_LANG:
                action.setCheckable(True)
                action.setChecked(True)
        
        action = menu.exec(self.language_button.mapToGlobal(self.language_button.rect().bottomLeft()))
        if action:
            selected_lang = action.data()
            save_language_preference(selected_lang)
            self._update_gui_texts(selected_lang)

    def _setup_dir_management(self):
        # Dizin yönetimi butonları sinyal bağlantıları (init'ten taşındı)
        self.add_dir_btn.clicked.connect(self._open_dir_dialog)
        self.remove_dir_btn.clicked.connect(self._remove_selected_dir)

    @Slot()
    def _open_dir_dialog(self):
        dialog_title = get_text("add_dir").replace("...", "").strip()
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
        
        # --- SOL PANEL (AYARLAR) ---
        
        # Ayarların yerleştirileceği container widget'ı
        settings_container_widget = QWidget()
        settings_layout = QVBoxLayout(settings_container_widget)
        # settings_panel.setFixedWidth(350) kaldırıldı, ScrollArea'ya eklenecek.

        # LOGO VE BAŞLIK
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

        # TARANACAK DİZİNLER
        self.dir_group = QGroupBox()
        dir_layout = QVBoxLayout(self.dir_group)
        self.dir_list = QListWidget()
        self.dir_list.setMaximumHeight(100)
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

        # EŞLEŞTİRME KRİTERLERİ
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

        # HARİÇ TUTMA KURALLARI
        self.ignore_group = QGroupBox()
        ignore_layout = QVBoxLayout(self.ignore_group)
        self.ignore_zero_byte = QCheckBox()
        self.ignore_system_hidden = QCheckBox()
        self.ignore_zero_byte.setChecked(True)
        self.ignore_system_hidden.setChecked(True)
        ignore_layout.addWidget(self.ignore_zero_byte)
        ignore_layout.addWidget(self.ignore_system_hidden)
        settings_layout.addWidget(self.ignore_group)

        # DOSYA TİPİ FİLTRESİ
        self.filter_group = QGroupBox()
        filter_layout = QVBoxLayout(self.filter_group)
        self.filter_button_group = QButtonGroup(self)
        self.filter_all = QRadioButton()
        self.filter_audio = QRadioButton()
        self.filter_video = QRadioButton()
        self.filter_image = QRadioButton()
        self.filter_text = QRadioButton()
        self.filter_office = QRadioButton()
        self.filter_pdf = QRadioButton()
        self.filter_archive = QRadioButton()
        self.filter_custom_radio = QRadioButton()
        self.filter_all.setChecked(True)
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
        custom_ext_layout = QHBoxLayout()
        self.custom_ext_label = QLabel()
        self.custom_ext_input = QLineEdit()
        self.custom_ext_input.setPlaceholderText(".mp4,.exe,.dat")
        custom_ext_layout.addWidget(self.filter_custom_radio)
        custom_ext_layout.addWidget(self.custom_ext_label)
        custom_ext_layout.addWidget(self.custom_ext_input)
        filter_layout.addLayout(custom_ext_layout)
        settings_layout.addWidget(self.filter_group)

        # BAŞLATMA BUTONLARI
        self.start_button = QPushButton()
        action_buttons_layout = QHBoxLayout()
        self.language_button = QPushButton()
        self.about_button = QPushButton()
        action_buttons_layout.addWidget(self.language_button)
        action_buttons_layout.addWidget(self.about_button)
        settings_layout.addWidget(self.start_button)
        settings_layout.addLayout(action_buttons_layout)
        settings_layout.addStretch(1) # Stretch settings_container_widget'ın içinde kalır

        # --- QScrollArea Oluşturulması ve Ayarların Eklenmesi ---
        settings_scroll_area = QScrollArea()
        settings_scroll_area.setWidgetResizable(True)
        settings_scroll_area.setFixedWidth(350) 
        settings_scroll_area.setWidget(settings_container_widget)
        
        # --- SAĞ PANEL (SEKMELER) ---
        
        # Sekme Widget'ı
        self.tab_widget = QTabWidget() 
        
        # 1. TARAMA SONUÇLARI SEKME İÇERİĞİ
        scan_results_page = QWidget()
        results_layout = QVBoxLayout(scan_results_page)
        self.found_label = QLabel()
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Seçilenleri Sahte Çöpe Gönder butonu (Tarama Ayarları_Sonuçlar sekmesinin içine alındı)
        self.delete_button = QPushButton()
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; height: 30px;")

        results_layout.addWidget(self.found_label)
        results_layout.addWidget(self.results_table)
        results_layout.addWidget(self.delete_button) 

        
        # 2. FAKE TRASH SEKME İÇERİĞİ
        fake_trash_page = QWidget()
        trash_layout = QVBoxLayout(fake_trash_page)
        self.trash_table = QTableWidget()
        self.trash_table.setColumnCount(4)
        self.trash_table.setHorizontalHeaderLabels(["", "Çöp Dosya Adı", "Orijinal Yolu", "Silinme Tarihi"])
        self.trash_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.trash_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.trash_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.trash_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.trash_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Tümünü Seç/Kaldır butonları (Renklendirildi)
        select_buttons_layout = QHBoxLayout()
        self.select_all_trash_button = QPushButton()
        self.unselect_all_trash_button = QPushButton()
        
        # <<< BUTON RENKLENDİRMELERİ BAŞLANGIÇ >>>
        self.select_all_trash_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 30px;")
        self.unselect_all_trash_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; height: 30px;")
        # <<< BUTON RENKLENDİRMELERİ SONU >>>

        select_buttons_layout.addWidget(self.select_all_trash_button)
        select_buttons_layout.addWidget(self.unselect_all_trash_button)

        trash_buttons_layout = QHBoxLayout()
        self.restore_button = QPushButton()
        self.purge_button = QPushButton()
        self.restore_button.setEnabled(False)
        self.purge_button.setEnabled(False)
        self.restore_button.setStyleSheet("background-color: #3f51b5; color: white; font-weight: bold; height: 30px;") 
        self.purge_button.setStyleSheet("background-color: #e53935; color: white; font-weight: bold; height: 30px;") 
        
        trash_buttons_layout.addWidget(self.restore_button)
        trash_buttons_layout.addWidget(self.purge_button)
        
        trash_layout.addLayout(select_buttons_layout)
        trash_layout.addWidget(self.trash_table)
        trash_layout.addLayout(trash_buttons_layout)
        
        # Sekmeleri Tab Widget'a ekle
        self.tab_widget.addTab(scan_results_page, get_text("tab_scan")) 
        self.tab_widget.addTab(fake_trash_page, get_text("tab_trash"))
        
        # Durum ve İlerleme Çubuğu (Ortak Alt Alan)
        status_layout_widget = QWidget()
        status_layout = QVBoxLayout(status_layout_widget)
        
        status_label_layout = QHBoxLayout()
        self.status_label = QLabel()
        self.status_label.setMinimumWidth(300)

        status_label_layout.addWidget(self.status_label, 1)

        progress_bar_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)

        progress_bar_layout.addWidget(self.progress_bar)

        status_layout.addLayout(status_label_layout)
        status_layout.addLayout(progress_bar_layout)
        
        # Ana Düzenin SON KEZ Kurulumu
        # "Eğer bir gün, benim sözlerim bilimle ters düşerse, bilimi seçin." M. Kemal ATATÜRK
        
        main_v_layout = QVBoxLayout()
        main_v_layout.addWidget(self.tab_widget)
        main_v_layout.addWidget(status_layout_widget)
        
        new_main_layout = QHBoxLayout()
        new_main_layout.addWidget(settings_scroll_area) # BURASI DEĞİŞTİ: settings_panel yerine settings_scroll_area
        new_main_layout.addLayout(main_v_layout, 1)
        
        self.central_widget.setLayout(new_main_layout) 


    def _connect_signals(self):
        self.start_button.clicked.connect(self._start_scan)
        self.delete_button.clicked.connect(self._delete_files_to_fake_trash) 
        self.language_button.clicked.connect(self._show_language_menu)
        self.about_button.clicked.connect(self._show_about)
        self.results_table.cellDoubleClicked.connect(self._handle_double_click) 
        self.filter_button_group.buttonClicked.connect(self._handle_filter_selection)
        self.custom_ext_input.setEnabled(False)
        
        # YENİ BAĞLANTILAR: Fake Trash Sekmesi
        self.tab_widget.currentChanged.connect(self._handle_tab_change)
        self.restore_button.clicked.connect(self._restore_selected_files)
        self.purge_button.clicked.connect(self._purge_selected_files)
        self.select_all_trash_button.clicked.connect(self._select_all_trash_files) 
        self.unselect_all_trash_button.clicked.connect(self._unselect_all_trash_files) 
        
        # Trash tablosunda çift tıklama ile orijinal yolu açma
        self.trash_table.cellDoubleClicked.connect(self._handle_trash_double_click)

    @Slot(int)
    def _handle_tab_change(self, index):
        """Sekme değiştiğinde Fake Trash sekmesini günceller."""
        if self.tab_widget.tabText(index) == get_text("tab_trash"):
            self.update_trash_tab()

    @Slot(QAbstractButton)
    def _handle_filter_selection(self, button):
        if button == self.filter_custom_radio:
            self.custom_ext_input.setEnabled(True)
            self.custom_ext_input.setFocus()
        else:
            self.custom_ext_input.setEnabled(False)

    @Slot(int, int)
    def _handle_double_click(self, row, column):
        """Tarama Sonuçları tablosunda çift tıklama."""
        try:
            if column == 1 or column == 2:
                file_name_item = self.results_table.item(row, 1)
                folder_path_item = self.results_table.item(row, 2)
                
                if not file_name_item or not folder_path_item: return

                file_name = file_name_item.text()
                folder_path = folder_path_item.text()
                full_path = os.path.join(folder_path, file_name)

                if column == 1:
                    path_to_open = full_path
                    self.status_label.setText(f'{get_text("status_prefix")}: {get_text("status_opening_file")}: {file_name}')
                elif column == 2:
                    path_to_open = folder_path.rstrip(os.path.sep) 
                    self.status_label.setText(f'{get_text("status_prefix")}: {get_text("status_opening_folder")}: {folder_path}')

                if open_path_in_os(path_to_open):
                    self.status_label.setText(f'{get_text("status_prefix")}: {get_text("status_ready")}')
                else:
                    self.status_label.setText(f'{get_text("status_prefix")}: {get_text("status_error_open")}: \'{os.path.basename(path_to_open)}\'')
                    
        except Exception as e:
            self.status_label.setText(f'{get_text("status_prefix")}: {get_text("status_error_general")}: {get_text("status_error_double_click")}. ({e})')
            
    @Slot(int, int)
    def _handle_trash_double_click(self, row, column):
        """Fake Trash tablosunda çift tıklama (Orijinal Klasör Yolu açılır)."""
        try:
            if column == 2: # Orijinal Yol sütunu
                original_path_item = self.trash_table.item(row, 2)
                if not original_path_item: return

                original_path = original_path_item.text()
                
                # Açılacak yer: orijinal dosyanın klasörü
                folder_path_to_open = os.path.dirname(original_path).rstrip(os.path.sep)

                if open_path_in_os(folder_path_to_open):
                    self.status_label.setText(f'{get_text("status_prefix")}: {get_text("status_ready")}')
                else:
                    self.status_label.setText(f'{get_text("status_prefix")}: {get_text("status_error_open")}: \'{folder_path_to_open}\'')
                    
        except Exception as e:
            self.status_label.setText(f'{get_text("status_prefix")}: {get_text("status_error_general")}: {get_text("status_error_trash_double_click")}. ({e})')


    @Slot()
    def _show_about(self):
        about_dialog = QMessageBox(self)
        about_dialog.setWindowTitle(get_text("about"))

        if self.icon_path:
            about_dialog.setIconPixmap(QPixmap(self.icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            about_dialog.setIcon(QMessageBox.Information)

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
        <h3>{get_text("about_title")}</h3>
        <ul>
            <li><b>{get_text("about_version")}:</b> 0.9.2 (beta)</li>
            <li><b>{get_text("about_license")}:</b> GPLv3</li>
            <li><b>{get_text("about_lang")}:</b> Python3</li>
            <li><b>{get_text("about_dev")}:</b> A. Serhat KILIÇOĞLU (shampuan)</li>
            <li><b>Github:</b> <a href="https://www.github.com/shampuan">www.github.com/shampuan</a></li>
        </ul>
        <hr>
        <p>{get_text("about_purpose")}</p>
        <p><b>{get_text("about_warranty")}</b></p>
        <p>{get_text("about_copyright")} &copy; 2025 A. Serhat KILIÇOĞLU</p>
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
            self.start_button.setText(get_text("start_scan"))
            self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 35px;")
            self.status_label.setText(f'{get_text("status_prefix")}: {get_text("status_canceled")}')
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

        options = {"match": match_options, "ignore": ignore_options, "filter": filter_options}

        target_dirs = [self.dir_list.item(i).text() for i in range(self.dir_list.count())]

        if not target_dirs:
            self.status_label.setText(f'{get_text("status_prefix")}: {get_text("status_error_dir")}')
            return

        self.results_table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.delete_button.setEnabled(False)
        self.start_button.setText(get_text("cancel_scan"))
        self.start_button.setStyleSheet("background-color: #FFA500; color: white; font-weight: bold; height: 35px;")

        self.worker_thread = WorkerThread(target_dirs, options)
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
        # Durum Etiketi Düzeltmesi: "Durum:" ifadesi çeviriye eklendi
        self.status_label.setText(f'{get_text("status_prefix")}: {message}')

    @Slot()
    def _scan_finished_cleanup(self):
        self.start_button.setText(get_text("rescan"))
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 35px;")

    @Slot(list)
    def _display_results(self, duplicate_groups):
        
        self.results_table.setRowCount(0)
        row_count = 0

        # Sonuçları, hash, boyut ve dosyalarla birlikte saklamak için yeni bir yapı
        self.duplicate_data = duplicate_groups 

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
                # <<< YENİ: İKON EKLEME >>>
                file_icon = self._get_file_icon(file_path)
                name_item.setIcon(file_icon) 
                # <<< YENİ: İKON EKLEME SONU >>>

                path_item = QTableWidgetItem(folder_path)
                size_item = QTableWidgetItem(group["size"]) # Okunabilir boyut

                # QTableWidgetItem'e boyut (bytes) ve hash verisini saklamak için özel veri set ediyoruz
                path_item.setData(Qt.UserRole, group["size_bytes"]) 
                path_item.setData(Qt.UserRole + 1, group["hash"])

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
        self.tab_widget.setCurrentIndex(0) 

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
            
    # <<< FAKE TRASH KULLANIMI >>>
    @Slot()
    def _delete_files_to_fake_trash(self):
        """Seçilen dosyaları Sahte Çöp Kutusu'na taşır."""
        selected_files = []
        for row in range(self.results_table.rowCount()):
            item = self.results_table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                folder_path = self.results_table.item(row, 2).text()
                file_name = self.results_table.item(row, 1).text()
                # size_bytes'ı UserRole'dan al
                size_bytes = self.results_table.item(row, 2).data(Qt.UserRole)
                full_path = os.path.join(folder_path, file_name)
                selected_files.append({"path": full_path, "size_bytes": size_bytes})

        if not selected_files:
            self.status_label.setText(f'{get_text("status_prefix")}: {get_text("trash_error_select")}')
            return

        reply = QMessageBox.question(
            self,
            get_text("delete_confirm_title"),
            get_text("delete_confirm_text").format(len(selected_files)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            self.status_label.setText(f'{get_text("status_prefix")}: {get_text("trash_canceled")}')
            return

        moved_count = 0
        error_count = 0
        moved_paths = []

        self.status_label.setText(f'{get_text("status_prefix")}: {get_text("delete_selected")}')

        for file_data in selected_files:
            if self.trash_manager.move_to_trash(file_data["path"], file_data["size_bytes"]):
                moved_count += 1
                moved_paths.append(file_data["path"])
            else:
                error_count += 1

        self._remove_deleted_rows(moved_paths)
        self.update_trash_tab() 

        if error_count == 0:
            final_message = get_text("trash_success").format(moved_count)
            QMessageBox.information(self, get_text("delete_confirm_title"), final_message)
        else:
            final_message = get_text("trash_error").format(moved_count, error_count)
            QMessageBox.warning(self, get_text("delete_confirm_title"), final_message)

        self.status_label.setText(f'{get_text("status_prefix")}: {final_message}')
        
    # <<< FAKE TRASH SEKMESİ YÖNETİMİ >>>
    @Slot()
    def update_trash_tab(self):
        """Fake Trash sekmesindeki tabloyu günceller (DİSK BAZLI)."""
        all_trash_data = []

        # 1. Taranan dizinlerden ve ev dizininden tüm benzersiz mount noktalarını topla
        target_dirs = [self.dir_list.item(i).text() for i in range(self.dir_list.count())]
        target_dirs.append(os.path.expanduser('~')) # Ev dizini mount noktasını ekle

        known_mount_points = set()
        for d in target_dirs:
            try:
                known_mount_points.add(get_mount_point(d))
            except Exception as e:
                print(f"Mount noktası alınırken hata: {d} - {e}")
                continue

        # 2. Her mount noktasındaki metadata dosyasını oku ve birleştir
        for mount_point in known_mount_points:
            # Disk bazlı çöp dizin yolu
            trash_dir = os.path.join(mount_point, '.Trash-DuplicateAgent')
            metadata_path = os.path.join(trash_dir, 'trashdata.json')

            if os.path.exists(metadata_path):
                # FakeTrashManager'ın yeni _load_metadata metodunu kullan
                disk_trash_data = self.trash_manager._load_metadata(metadata_path)
                
                # Her öğeye trash_dir bilgisini ekleyelim (Güvenlik katmanı)
                for item in disk_trash_data:
                    if "trash_dir" not in item:
                         item["trash_dir"] = trash_dir
                    all_trash_data.append(item)

        trash_data = all_trash_data
        self.trash_table.setRowCount(0)
        row_count = 0

        for item in trash_data:
            self.trash_table.insertRow(row_count)
            
            # 0. Sütun: CheckBox
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.CheckState.Unchecked)
            self.trash_table.setItem(row_count, 0, check_item)
            
            # 1. Çöp Dosya Adı
            trash_filename = item.get("trash_filename", "")
            trash_dir = item.get("trash_dir", "") # Yeni: trash_dir'i meta veriden al
            trash_name_item = QTableWidgetItem(trash_filename)

            # İKON EKLEME
            trash_file_path = os.path.join(trash_dir, trash_filename)
            file_icon = self._get_file_icon(trash_file_path)
            trash_name_item.setIcon(file_icon)

            self.trash_table.setItem(row_count, 1, trash_name_item)
            
            # 2. Orijinal Yolu
            original_path = item.get("original_path", "")
            original_path_item = QTableWidgetItem(original_path)
            
            # UserRole'a trash_filename'i ve UserRole + 1'e trash_dir'i sakla
            original_path_item.setData(Qt.UserRole, trash_filename)
            original_path_item.setData(Qt.UserRole + 1, trash_dir) # <<< ÖNEMLİ: Disk bazlı çöp yolunu sakla

            self.trash_table.setItem(row_count, 2, original_path_item)
            
            # 3. Silinme Tarihi
            date_item = QTableWidgetItem(item.get("deletion_date", ""))
            self.trash_table.setItem(row_count, 3, date_item)
            
            row_count += 1
            
        self.trash_table.setRowCount(row_count)
        is_any_file = row_count > 0
        self.restore_button.setEnabled(is_any_file)
        self.purge_button.setEnabled(is_any_file)
        
    @Slot()
    def _select_all_trash_files(self):
        """Çöp tablosundaki tüm dosyaları işaretler."""
        for row in range(self.trash_table.rowCount()):
            item = self.trash_table.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Checked)

    @Slot()
    def _unselect_all_trash_files(self):
        """Çöp tablosundaki tüm dosyaların işaretini kaldırır."""
        for row in range(self.trash_table.rowCount()):
            item = self.trash_table.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Unchecked)


    @Slot()
    def _get_selected_trash_items(self):
        """Çöp tablosunda seçilen dosyaların listesini döndürür (trash_filename, original_path, trash_dir)."""
        selected_items = []
        for row in range(self.trash_table.rowCount()):
            check_item = self.trash_table.item(row, 0)
            if check_item and check_item.checkState() == Qt.CheckState.Checked:
                # 1. Sütun (Çöp Dosya Adı) veya 2. Sütun (Orijinal Yol) kullanılabilir. 
                # Tutarlılık için 1. sütundan alalım.
                trash_filename = self.trash_table.item(row, 1).text() 
                original_path_item = self.trash_table.item(row, 2)
                
                if original_path_item:
                    original_path = original_path_item.text()
                    # UserRole + 1'den trash_dir bilgisini al
                    trash_dir = original_path_item.data(Qt.UserRole + 1) # <<< ÖNEMLİ: trash_dir'i al
                    
                    selected_items.append({
                        "trash_filename": trash_filename, 
                        "original_path": original_path,
                        "trash_dir": trash_dir # <<< ÖNEMLİ
                    })
        return selected_items

    @Slot()
    def _restore_selected_files(self):
        """Seçili dosyaları orijinal konumuna geri yükler."""
        selected_files = self._get_selected_trash_items()
        if not selected_files:
            QMessageBox.warning(self, get_text("restore_confirm_title"), get_text("restore_error_select"))
            return

        reply = QMessageBox.question(
            self,
            get_text("restore_confirm_title"),
            get_text("restore_confirm_text").format(len(selected_files)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No: return

        restored_count = 0
        error_count = 0

        self.status_label.setText(f'{get_text("status_prefix")}: {get_text("status_restoring_files")}')
        for file_data in selected_files:
            # trash_dir parametresini ekle
            if self.trash_manager.restore_file(file_data["trash_filename"], file_data["original_path"], file_data["trash_dir"]):
                restored_count += 1
            else:
                error_count += 1

        self.update_trash_tab()
        
        if error_count == 0:
            final_message = get_text("restore_success").format(restored_count)
            QMessageBox.information(self, get_text("restore_confirm_title"), final_message)
        else:
            final_message = get_text("restore_error").format(restored_count, error_count)
            QMessageBox.warning(self, get_text("restore_confirm_title"), final_message)

        self.status_label.setText(f'{get_text("status_prefix")}: {final_message}')


    @Slot()
    def _purge_selected_files(self):
        """Seçili dosyaları diskten kalıcı olarak siler."""
        selected_files = self._get_selected_trash_items()
        if not selected_files:
            QMessageBox.warning(self, get_text("purge_confirm_title"), get_text("purge_error_select"))
            return

        reply = QMessageBox.question(
            self,
            get_text("purge_confirm_title"),
            get_text("purge_confirm_text").format(len(selected_files)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No: return

        purged_count = 0
        error_count = 0

        self.status_label.setText(f'{get_text("status_prefix")}: {get_text("status_purging_files")}')
        for file_data in selected_files:
            # trash_dir parametresini ekle
            if self.trash_manager.purge_file(file_data["trash_filename"], file_data["original_path"], file_data["trash_dir"]):
                purged_count += 1
            else:
                error_count += 1

        self.update_trash_tab()

        if error_count == 0:
            final_message = get_text("purge_success").format(purged_count)
            QMessageBox.information(self, get_text("purge_confirm_title"), final_message)
        else:
            final_message = get_text("purge_error").format(purged_count, error_count)
            QMessageBox.warning(self, get_text("purge_confirm_title"), final_message)

        self.status_label.setText(f'{get_text("status_prefix")}: {final_message}')

# "Geldikleri gibi giderler..." M. Kemal ATATÜRK (Geldikleri gibi gittiler). 

# Teşekkürler Fatih ÖNDER. Teşekkürler Yapay Zeka. 

# --- White Rabbit ---
#One pill makes you larger
#And one pill makes you small
#And the ones that mother gives you
#Don't do anything at all
#Go ask Alice
#When she's ten feet tall
#And if you go chasing rabbits
#And you know you're going to fall
#Tell 'em a hookah-smoking caterpillar
#Has given you the call
#He called Alice
#When she was just small
#When the men on the chessboard
#Get up and tell you where to go
#And you've just had some kind of mushroom
#And your mind is moving low
#Go ask Alice
#I think she'll know
#When logic and proportion
#Have fallen sloppy dead
#And the White Knight is talking backwards
#And the Red Queen's off with her head
#Remember what the dormouse said
#Feed your head
#Feed your head
# ---Jafferson Airplane---

# 4. UYGULAMA BAŞLANGICI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Dil dosyalarını yükle
    load_language_files()
    
    window = DuplicateFinderApp()
    window.show()
    sys.exit(app.exec())
