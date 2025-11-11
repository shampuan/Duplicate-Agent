#!/usr/bin/env python3
"""
Dosya Sistemi İzleyici (Watchdog)
Gerçek zamanlı duplicate tespit sistemi
"""

import os
import time
import logging
from typing import List, Callable, Optional
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

logger = logging.getLogger(__name__)


class DuplicateWatchdogHandler(FileSystemEventHandler):
    """Dosya sistemi değişikliklerini izleyen handler"""
    
    def __init__(self, 
                 on_file_created: Optional[Callable] = None,
                 on_file_modified: Optional[Callable] = None,
                 on_file_deleted: Optional[Callable] = None,
                 file_extensions: Optional[List[str]] = None):
        """
        Args:
            on_file_created: Dosya oluşturulduğunda çağrılacak fonksiyon
            on_file_modified: Dosya değiştirildiğinde çağrılacak fonksiyon
            on_file_deleted: Dosya silindiğinde çağrılacak fonksiyon
            file_extensions: İzlenecek dosya uzantıları (None ise hepsi)
        """
        super().__init__()
        self.on_file_created = on_file_created
        self.on_file_modified = on_file_modified
        self.on_file_deleted = on_file_deleted
        self.file_extensions = file_extensions or []
        self.last_event_time = {}
        self.debounce_seconds = 2  # Aynı dosya için 2 saniye içindeki olayları yoksay
        
    def _should_process(self, file_path: str) -> bool:
        """Dosyanın işlenmesi gerekip gerekmediğini kontrol eder"""
        # Gizli dosyaları ve sistem dosyalarını atla
        if os.path.basename(file_path).startswith('.'):
            return False
            
        # Uzantı filtresi varsa kontrol et
        if self.file_extensions:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in self.file_extensions:
                return False
                
        # Debounce kontrolü
        current_time = time.time()
        last_time = self.last_event_time.get(file_path, 0)
        
        if current_time - last_time < self.debounce_seconds:
            return False
            
        self.last_event_time[file_path] = current_time
        return True
    
    def on_created(self, event: FileSystemEvent):
        """Dosya oluşturulduğunda"""
        if event.is_directory:
            return
            
        if self._should_process(event.src_path):
            logger.info(f"Yeni dosya tespit edildi: {event.src_path}")
            if self.on_file_created:
                self.on_file_created(event.src_path)
    
    def on_modified(self, event: FileSystemEvent):
        """Dosya değiştirildiğinde"""
        if event.is_directory:
            return
            
        if self._should_process(event.src_path):
            logger.info(f"Dosya değiştirildi: {event.src_path}")
            if self.on_file_modified:
                self.on_file_modified(event.src_path)
    
    def on_deleted(self, event: FileSystemEvent):
        """Dosya silindiğinde"""
        if event.is_directory:
            return
            
        logger.info(f"Dosya silindi: {event.src_path}")
        if self.on_file_deleted:
            self.on_file_deleted(event.src_path)


class FileSystemWatcher:
    """Dosya sistemi izleyici ana sınıfı"""
    
    def __init__(self, directories: List[str]):
        """
        Args:
            directories: İzlenecek dizinler listesi
        """
        self.directories = directories
        self.observer = Observer()
        self.handlers = {}
        self.is_running = False
        
    def start(self, 
              on_file_created: Optional[Callable] = None,
              on_file_modified: Optional[Callable] = None,
              on_file_deleted: Optional[Callable] = None,
              file_extensions: Optional[List[str]] = None):
        """
        İzlemeyi başlatır
        
        Args:
            on_file_created: Dosya oluşturma callback'i
            on_file_modified: Dosya değiştirme callback'i
            on_file_deleted: Dosya silme callback'i
            file_extensions: İzlenecek uzantılar
        """
        if self.is_running:
            logger.warning("Watchdog zaten çalışıyor")
            return
            
        handler = DuplicateWatchdogHandler(
            on_file_created=on_file_created,
            on_file_modified=on_file_modified,
            on_file_deleted=on_file_deleted,
            file_extensions=file_extensions
        )
        
        for directory in self.directories:
            if os.path.exists(directory):
                self.observer.schedule(handler, directory, recursive=True)
                self.handlers[directory] = handler
                logger.info(f"Dizin izleniyor: {directory}")
            else:
                logger.warning(f"Dizin bulunamadı: {directory}")
        
        self.observer.start()
        self.is_running = True
        logger.info("Dosya sistemi izleyici başlatıldı")
        
    def stop(self):
        """İzlemeyi durdurur"""
        if not self.is_running:
            return
            
        self.observer.stop()
        self.observer.join()
        self.is_running = False
        logger.info("Dosya sistemi izleyici durduruldu")
        
    def is_watching(self) -> bool:
        """İzleme durumunu döndürür"""
        return self.is_running


# Kullanım örneği
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def on_new_file(filepath):
        print(f"📄 Yeni dosya: {filepath}")
        # Burada duplicate kontrolü yapılabilir
        
    def on_file_changed(filepath):
        print(f"✏️ Değişen dosya: {filepath}")
        
    def on_file_removed(filepath):
        print(f"🗑️ Silinen dosya: {filepath}")
    
    watcher = FileSystemWatcher(["/home/user/Downloads"])
    watcher.start(
        on_file_created=on_new_file,
        on_file_modified=on_file_changed,
        on_file_deleted=on_file_removed,
        file_extensions=['.jpg', '.png', '.pdf']
    )
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
