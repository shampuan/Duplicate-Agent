#!/usr/bin/env python3
"""
Zamanlanmış Tarama Sistemi (Scheduler)
Cron job benzeri otomatik tarama
"""

import schedule
import time
import logging
from typing import Callable, List, Optional
from datetime import datetime
import threading
import json
import os

logger = logging.getLogger(__name__)


class ScanSchedule:
    """Tarama zamanlama sınıfı"""
    
    def __init__(self, 
                 schedule_type: str,
                 time_value: str,
                 directories: List[str],
                 options: dict):
        """
        Args:
            schedule_type: 'daily', 'weekly', 'hourly', 'interval'
            time_value: Zaman değeri (örn: "14:30", "monday", "2" saat)
            directories: Taranacak dizinler
            options: Tarama seçenekleri
        """
        self.schedule_type = schedule_type
        self.time_value = time_value
        self.directories = directories
        self.options = options
        self.enabled = True
        self.last_run = None
        self.next_run = None
        
    def to_dict(self) -> dict:
        """Schedule'u dictionary'ye çevirir"""
        return {
            'schedule_type': self.schedule_type,
            'time_value': self.time_value,
            'directories': self.directories,
            'options': self.options,
            'enabled': self.enabled,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ScanSchedule':
        """Dictionary'den schedule oluşturur"""
        schedule_obj = cls(
            schedule_type=data['schedule_type'],
            time_value=data['time_value'],
            directories=data['directories'],
            options=data['options']
        )
        schedule_obj.enabled = data.get('enabled', True)
        return schedule_obj


class ScheduledScanner:
    """Zamanlanmış tarayıcı ana sınıfı"""
    
    def __init__(self, config_path: str = None):
        """
        Args:
            config_path: Ayar dosyası yolu
        """
        self.config_path = config_path or os.path.expanduser('~/.duplicateagent/schedules.json')
        self.schedules: List[ScanSchedule] = []
        self.scan_callback: Optional[Callable] = None
        self.is_running = False
        self.scheduler_thread = None
        self.load_schedules()
        
    def load_schedules(self):
        """Kaydedilmiş zamanlamaları yükler"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.schedules = [ScanSchedule.from_dict(s) for s in data]
                logger.info(f"{len(self.schedules)} zamanlama yüklendi")
            except Exception as e:
                logger.error(f"Zamanlamalar yüklenemedi: {e}")
        
    def save_schedules(self):
        """Zamanlamaları kaydeder"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                data = [s.to_dict() for s in self.schedules]
                json.dump(data, f, indent=2)
            logger.info("Zamanlamalar kaydedildi")
        except Exception as e:
            logger.error(f"Zamanlamalar kaydedilemedi: {e}")
    
    def add_schedule(self, scan_schedule: ScanSchedule):
        """Yeni zamanlama ekler"""
        self.schedules.append(scan_schedule)
        self.save_schedules()
        self._register_schedule(scan_schedule)
        logger.info(f"Yeni zamanlama eklendi: {scan_schedule.schedule_type}")
        
    def remove_schedule(self, index: int):
        """Zamanlama siler"""
        if 0 <= index < len(self.schedules):
            removed = self.schedules.pop(index)
            self.save_schedules()
            logger.info(f"Zamanlama silindi: {removed.schedule_type}")
            
    def _register_schedule(self, scan_schedule: ScanSchedule):
        """Schedule'u schedule kütüphanesine kaydeder"""
        if not scan_schedule.enabled:
            return
            
        def job():
            """Tarama işini çalıştır"""
            scan_schedule.last_run = datetime.now()
            logger.info(f"Zamanlanmış tarama başlatılıyor: {scan_schedule.directories}")
            
            if self.scan_callback:
                self.scan_callback(scan_schedule.directories, scan_schedule.options)
            
            self.save_schedules()
        
        # Schedule tipine göre kaydet
        if scan_schedule.schedule_type == 'daily':
            schedule.every().day.at(scan_schedule.time_value).do(job)
            
        elif scan_schedule.schedule_type == 'weekly':
            # time_value: "monday", "tuesday", vb.
            day_func = getattr(schedule.every(), scan_schedule.time_value.lower())
            day_func.do(job)
            
        elif scan_schedule.schedule_type == 'hourly':
            schedule.every().hour.do(job)
            
        elif scan_schedule.schedule_type == 'interval':
            # time_value: saat cinsinden interval
            hours = int(scan_schedule.time_value)
            schedule.every(hours).hours.do(job)
        
        # Bir sonraki çalışma zamanını kaydet
        scan_schedule.next_run = datetime.now()  # schedule kütüphanesi günceller
        
    def start(self, scan_callback: Callable):
        """
        Scheduler'ı başlatır
        
        Args:
            scan_callback: Tarama fonksiyonu callback'i
                          signature: callback(directories: List[str], options: dict)
        """
        if self.is_running:
            logger.warning("Scheduler zaten çalışıyor")
            return
            
        self.scan_callback = scan_callback
        
        # Tüm schedule'ları kaydet
        schedule.clear()
        for scan_schedule in self.schedules:
            self._register_schedule(scan_schedule)
        
        # Arka plan thread'i başlat
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Zamanlanmış tarayıcı başlatıldı")
        
    def _run_scheduler(self):
        """Scheduler döngüsü (thread'de çalışır)"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol et
            
    def stop(self):
        """Scheduler'ı durdurur"""
        if not self.is_running:
            return
            
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        logger.info("Zamanlanmış tarayıcı durduruldu")
        
    def get_next_run_time(self) -> Optional[datetime]:
        """Bir sonraki çalışma zamanını döndürür"""
        jobs = schedule.get_jobs()
        if jobs:
            next_job = min(jobs, key=lambda j: j.next_run)
            return next_job.next_run
        return None
    
    def get_schedules_info(self) -> List[dict]:
        """Tüm zamanlamaların bilgilerini döndürür"""
        return [s.to_dict() for s in self.schedules]


# Kullanım örneği
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def scan_callback(directories, options):
        print(f"🔍 Tarama başlatıldı: {directories}")
        print(f"   Seçenekler: {options}")
        # Gerçek tarama burada yapılır
        time.sleep(2)
        print("✅ Tarama tamamlandı")
    
    scheduler = ScheduledScanner()
    
    # Günlük tarama ekle
    daily_scan = ScanSchedule(
        schedule_type='daily',
        time_value='14:30',
        directories=['/home/user/Downloads', '/home/user/Documents'],
        options={'match_content': True, 'ignore_zero_byte': True}
    )
    scheduler.add_schedule(daily_scan)
    
    # Saatlik tarama ekle
    hourly_scan = ScanSchedule(
        schedule_type='interval',
        time_value='2',  # Her 2 saatte bir
        directories=['/home/user/Downloads'],
        options={'match_content': True}
    )
    scheduler.add_schedule(hourly_scan)
    
    scheduler.start(scan_callback)
    
    print(f"📅 Sonraki çalışma: {scheduler.get_next_run_time()}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
