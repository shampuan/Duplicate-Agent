#!/usr/bin/env python3
"""
Duplicate Folder Finder (Kopya Klasör Bulucu)
Özdeş klasör ağaçlarını bulur
"""

import os
import hashlib
import logging
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class FolderFingerprint:
    """Klasör parmak izi - klasörün yapısını ve içeriğini temsil eder"""
    
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.file_hashes = {}  # {relative_path: md5_hash}
        self.folder_structure = []  # Alt klasör yapısı
        self.total_size = 0
        self.file_count = 0
        
    def calculate(self, ignore_hidden: bool = True) -> str:
        """
        Klasör parmak izini hesaplar
        
        Returns:
            Klasörün benzersiz fingerprint'i
        """
        if not os.path.exists(self.folder_path):
            return ""
        
        # Tüm dosyaları ve klasörleri tara
        for root, dirs, files in os.walk(self.folder_path):
            # Gizli klasörleri atla
            if ignore_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]
            
            # Klasör yapısını kaydet
            rel_root = os.path.relpath(root, self.folder_path)
            if rel_root != '.':
                self.folder_structure.append(rel_root)
            
            # Dosya hash'lerini hesapla
            for filename in sorted(files):
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, self.folder_path)
                
                try:
                    file_size = os.path.getsize(file_path)
                    self.total_size += file_size
                    self.file_count += 1
                    
                    # Küçük dosyalar için tam hash, büyükler için sample hash
                    if file_size < 10 * 1024 * 1024:  # 10MB altı
                        file_hash = self._calculate_file_hash(file_path)
                    else:
                        file_hash = self._calculate_sample_hash(file_path)
                    
                    self.file_hashes[rel_path] = file_hash
                    
                except Exception as e:
                    logger.warning(f"Dosya hash hesaplanamadı ({file_path}): {e}")
        
        # Klasör fingerprint'ini oluştur
        return self._generate_fingerprint()
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Dosyanın MD5 hash'ini hesaplar"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""
    
    def _calculate_sample_hash(self, file_path: str) -> str:
        """Büyük dosyalar için örnek hash (başlangıç + son)"""
        hasher = hashlib.md5()
        sample_size = 1024 * 1024  # 1MB
        
        try:
            file_size = os.path.getsize(file_path)
            with open(file_path, 'rb') as f:
                # Baştan 1MB
                hasher.update(f.read(sample_size))
                
                # Ortadan 1MB
                if file_size > 3 * sample_size:
                    f.seek(file_size // 2)
                    hasher.update(f.read(sample_size))
                
                # Sondan 1MB
                if file_size > sample_size:
                    f.seek(-sample_size, 2)
                    hasher.update(f.read(sample_size))
                    
            return hasher.hexdigest()
        except Exception:
            return ""
    
    def _generate_fingerprint(self) -> str:
        """Klasör fingerprint'ini oluşturur"""
        fingerprint_data = {
            'structure': sorted(self.folder_structure),
            'files': sorted(self.file_hashes.items()),
            'file_count': self.file_count,
            'total_size': self.total_size
        }
        
        # JSON string'e çevir ve hash al
        json_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()


class DuplicateFolderFinder:
    """Duplicate klasör bulucu ana sınıfı"""
    
    def __init__(self, 
                 min_file_count: int = 3,
                 ignore_hidden: bool = True,
                 match_exact: bool = True):
        """
        Args:
            min_file_count: Minimum dosya sayısı (daha az dosyalı klasörler atlanır)
            ignore_hidden: Gizli dosya/klasörleri yoksay
            match_exact: True ise tam eşleşme, False ise benzerlik
        """
        self.min_file_count = min_file_count
        self.ignore_hidden = ignore_hidden
        self.match_exact = match_exact
        self.fingerprints = {}  # {folder_path: fingerprint}
        
    def scan_directories(self, 
                        root_directories: List[str],
                        max_depth: Optional[int] = None) -> Dict[str, List[str]]:
        """
        Dizinleri tarar ve duplicate klasörleri bulur
        
        Args:
            root_directories: Taranacak kök dizinler
            max_depth: Maksimum tarama derinliği (None = sınırsız)
            
        Returns:
            Duplicate gruplar {fingerprint: [folder1, folder2, ...]}
        """
        logger.info(f"{len(root_directories)} dizin taranıyor...")
        
        # Tüm alt klasörleri bul
        all_folders = []
        for root_dir in root_directories:
            folders = self._get_all_folders(root_dir, max_depth)
            all_folders.extend(folders)
        
        logger.info(f"{len(all_folders)} klasör bulundu, fingerprint'ler hesaplanıyor...")
        
        # Her klasör için fingerprint hesapla
        fingerprint_groups = defaultdict(list)
        
        for i, folder_path in enumerate(all_folders):
            if i % 100 == 0 and i > 0:
                logger.info(f"  İşleniyor: {i}/{len(all_folders)}")
            
            fp = FolderFingerprint(folder_path)
            fingerprint = fp.calculate(self.ignore_hidden)
            
            # Minimum dosya sayısı kontrolü
            if fp.file_count >= self.min_file_count:
                self.fingerprints[folder_path] = fp
                fingerprint_groups[fingerprint].append(folder_path)
        
        # Sadece duplicate olanları filtrele
        duplicates = {fp: folders for fp, folders in fingerprint_groups.items() 
                     if len(folders) > 1}
        
        logger.info(f"{len(duplicates)} duplicate klasör grubu bulundu")
        return duplicates
    
    def _get_all_folders(self, 
                        root_dir: str, 
                        max_depth: Optional[int] = None) -> List[str]:
        """
        Tüm alt klasörleri listeler
        
        Args:
            root_dir: Kök dizin
            max_depth: Maksimum derinlik
            
        Returns:
            Klasör yolları listesi
        """
        folders = []
        
        try:
            for root, dirs, files in os.walk(root_dir):
                # Derinlik kontrolü
                if max_depth is not None:
                    depth = root[len(root_dir):].count(os.sep)
                    if depth >= max_depth:
                        dirs.clear()
                        continue
                
                # Gizli klasörleri atla
                if self.ignore_hidden:
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # Alt klasörleri ekle
                for dir_name in dirs:
                    folder_path = os.path.join(root, dir_name)
                    folders.append(folder_path)
                    
        except PermissionError as e:
            logger.warning(f"İzin hatası: {root_dir}")
        
        return folders
    
    def get_duplicate_stats(self, duplicates: Dict[str, List[str]]) -> Dict:
        """
        Duplicate istatistiklerini hesaplar
        
        Returns:
            İstatistik sözlüğü
        """
        total_groups = len(duplicates)
        total_folders = sum(len(folders) for folders in duplicates.values())
        
        # Tasarruf edilebilir alan
        total_wasted_space = 0
        for fingerprint, folders in duplicates.items():
            if folders:
                # İlk klasörü orijinal kabul et, geri kalanlar silinebilir
                first_folder = folders[0]
                if first_folder in self.fingerprints:
                    folder_size = self.fingerprints[first_folder].total_size
                    wasted_space = folder_size * (len(folders) - 1)
                    total_wasted_space += wasted_space
        
        return {
            'total_groups': total_groups,
            'total_duplicate_folders': total_folders,
            'original_folders': total_groups,
            'removable_folders': total_folders - total_groups,
            'wasted_space_bytes': total_wasted_space,
            'wasted_space_readable': self._format_size(total_wasted_space)
        }
    
    def _format_size(self, size_bytes: int) -> str:
        """Bayt cinsinden boyutu okunabilir formata çevirir"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def compare_folders(self, folder1: str, folder2: str) -> Dict:
        """
        İki klasörü karşılaştırır ve farkları gösterir
        
        Returns:
            Karşılaştırma sonucu
        """
        fp1 = FolderFingerprint(folder1)
        fp2 = FolderFingerprint(folder2)
        
        fingerprint1 = fp1.calculate(self.ignore_hidden)
        fingerprint2 = fp2.calculate(self.ignore_hidden)
        
        is_identical = fingerprint1 == fingerprint2
        
        # Farkları bul
        files1 = set(fp1.file_hashes.keys())
        files2 = set(fp2.file_hashes.keys())
        
        only_in_folder1 = files1 - files2
        only_in_folder2 = files2 - files1
        common_files = files1 & files2
        
        # Ortak dosyalarda hash farklılıkları
        different_content = []
        for file_path in common_files:
            if fp1.file_hashes[file_path] != fp2.file_hashes[file_path]:
                different_content.append(file_path)
        
        return {
            'is_identical': is_identical,
            'folder1': {
                'path': folder1,
                'file_count': fp1.file_count,
                'total_size': self._format_size(fp1.total_size)
            },
            'folder2': {
                'path': folder2,
                'file_count': fp2.file_count,
                'total_size': self._format_size(fp2.total_size)
            },
            'only_in_folder1': list(only_in_folder1),
            'only_in_folder2': list(only_in_folder2),
            'different_content': different_content,
            'similarity_percentage': self._calculate_similarity(fp1, fp2)
        }
    
    def _calculate_similarity(self, fp1: FolderFingerprint, fp2: FolderFingerprint) -> float:
        """İki klasör arasındaki benzerlik yüzdesini hesaplar"""
        files1 = set(fp1.file_hashes.keys())
        files2 = set(fp2.file_hashes.keys())
        
        if not files1 and not files2:
            return 100.0
        
        common = files1 & files2
        total = files1 | files2
        
        if not total:
            return 0.0
        
        # Dosya adı benzerliği
        name_similarity = (len(common) / len(total)) * 100
        
        # İçerik benzerliği (ortak dosyalar için)
        content_matches = sum(1 for f in common 
                            if fp1.file_hashes[f] == fp2.file_hashes[f])
        content_similarity = (content_matches / len(total)) * 100 if total else 0
        
        # Ortalama benzerlik
        return (name_similarity + content_similarity) / 2


# Kullanım örneği
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    finder = DuplicateFolderFinder(
        min_file_count=3,
        ignore_hidden=True,
        match_exact=True
    )
    
    # Duplicate klasörleri bul
    duplicates = finder.scan_directories(
        root_directories=['/home/user/Documents', '/media/backup'],
        max_depth=5
    )
    
    # Sonuçları göster
    print("\n📁 Duplicate Klasörler:")
    for i, (fingerprint, folders) in enumerate(duplicates.items(), 1):
        print(f"\nGrup {i}: {len(folders)} özdeş klasör")
        for folder in folders:
            fp = finder.fingerprints.get(folder)
            if fp:
                print(f"  📂 {folder}")
                print(f"     Dosya: {fp.file_count}, Boyut: {finder._format_size(fp.total_size)}")
    
    # İstatistikler
    stats = finder.get_duplicate_stats(duplicates)
    print(f"\n📊 İstatistikler:")
    print(f"  Toplam grup: {stats['total_groups']}")
    print(f"  Silinebilir klasör: {stats['removable_folders']}")
    print(f"  Tasarruf edilebilir alan: {stats['wasted_space_readable']}")
