#!/usr/bin/env python3
"""
Compression Suggester (Sıkıştırma Önerici)
Duplicate dosyalar yerine sıkıştırılmış arşiv önerir
"""

import os
import zipfile
import tarfile
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CompressionAnalyzer:
    """Sıkıştırma analizi yapan sınıf"""
    
    COMPRESSIBLE_TYPES = {
        '.txt', '.log', '.md', '.csv', '.json', '.xml', '.html', '.css', '.js',
        '.bmp', '.tiff', '.svg', '.doc', '.docx', '.py', '.java', '.cpp'
    }
    
    ALREADY_COMPRESSED = {
        '.zip', '.rar', '.7z', '.gz', '.bz2', '.jpg', '.jpeg', '.png', '.mp3', '.mp4'
    }
    
    def is_compressible(self, file_path: str) -> bool:
        """Dosyanın sıkıştırmaya uygun olup olmadığını kontrol eder"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.COMPRESSIBLE_TYPES and ext not in self.ALREADY_COMPRESSED
    
    def estimate_compression_ratio(self, file_path: str) -> float:
        """Tahmini sıkıştırma oranı (0.3 = %70 küçülme)"""
        ext = os.path.splitext(file_path)[1].lower()
        ratios = {'.txt': 0.25, '.log': 0.20, '.json': 0.30, '.xml': 0.25, '.html': 0.30}
        return ratios.get(ext, 0.50)


class CompressionSuggester:
    """Sıkıştırma önerisi yapan ana sınıf"""
    
    def __init__(self, min_group_size: int = 3, min_savings_mb: float = 1.0):
        self.analyzer = CompressionAnalyzer()
        self.min_group_size = min_group_size
        self.min_savings_mb = min_savings_mb
        
    def analyze_duplicate_groups(self, duplicate_groups: List[Dict]) -> List[Dict]:
        """Duplicate gruplarını analiz eder ve sıkıştırma önerileri sunar"""
        suggestions = []
        
        for group in duplicate_groups:
            files = group.get('files', [])
            size_bytes = group.get('size_bytes', 0)
            
            if len(files) < self.min_group_size:
                continue
            
            sample_file = files[0]
            if not self.analyzer.is_compressible(sample_file):
                continue
            
            compression_ratio = self.analyzer.estimate_compression_ratio(sample_file)
            total_size = size_bytes * len(files)
            compressed_size = size_bytes * compression_ratio
            savings = total_size - compressed_size
            savings_mb = savings / (1024 * 1024)
            
            if savings_mb < self.min_savings_mb:
                continue
            
            suggestion = {
                'files': files,
                'original_total_size': total_size,
                'compressed_size': compressed_size,
                'savings_bytes': savings,
                'savings_readable': self._format_size(savings),
                'compression_ratio': compression_ratio,
                'archive_name': self._generate_archive_name(sample_file, len(files))
            }
            suggestions.append(suggestion)
        
        suggestions.sort(key=lambda x: x['savings_bytes'], reverse=True)
        return suggestions
    
    def create_archive(self, files: List[str], archive_path: str, delete_originals: bool = False) -> bool:
        """Dosyalardan ZIP arşivi oluşturur"""
        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files:
                    if os.path.exists(file_path):
                        zipf.write(file_path, os.path.basename(file_path))
            
            if delete_originals:
                for file_path in files:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.warning(f"Dosya silinemedi: {e}")
            
            logger.info(f"Arşiv oluşturuldu: {archive_path}")
            return True
        except Exception as e:
            logger.error(f"Arşiv hatası: {e}")
            return False
    
    def _generate_archive_name(self, sample_file: str, count: int) -> str:
        basename = os.path.splitext(os.path.basename(sample_file))[0]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{basename}_duplicates_{count}files_{timestamp}.zip"
    
    def _format_size(self, size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
