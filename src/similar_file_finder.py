#!/usr/bin/env python3
"""
Benzer Dosya Bulucu (Similar File Finder)
İçerik benzerliği analizi
"""

import os
import logging
from typing import List, Dict, Tuple, Optional
from PIL import Image
import imagehash
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class SimilarImageFinder:
    """Benzer resim bulucu - Perceptual Hash kullanır"""
    
    def __init__(self, similarity_threshold: int = 5):
        """
        Args:
            similarity_threshold: Benzerlik eşiği (0-64 arası, düşük = daha benzer)
        """
        self.similarity_threshold = similarity_threshold
        self.hash_cache = {}
        
    def calculate_phash(self, image_path: str) -> Optional[imagehash.ImageHash]:
        """
        Resmin perceptual hash'ini hesaplar
        
        Args:
            image_path: Resim dosyası yolu
            
        Returns:
            Perceptual hash veya hata durumunda None
        """
        try:
            with Image.open(image_path) as img:
                # RGB'ye çevir (RGBA, P vb. formatlar için)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                return imagehash.phash(img)
        except Exception as e:
            logger.error(f"pHash hesaplama hatası ({image_path}): {e}")
            return None
    
    def calculate_average_hash(self, image_path: str) -> Optional[imagehash.ImageHash]:
        """Average hash hesaplar (daha hızlı, az hassas)"""
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                return imagehash.average_hash(img)
        except Exception as e:
            logger.error(f"aHash hesaplama hatası ({image_path}): {e}")
            return None
    
    def find_similar_images(self, 
                           image_paths: List[str], 
                           use_average_hash: bool = False) -> List[List[str]]:
        """
        Benzer resimleri bulur
        
        Args:
            image_paths: Resim dosya yolları listesi
            use_average_hash: True ise average hash kullanır (hızlı)
            
        Returns:
            Benzer resim grupları [[img1, img2], [img3, img4, img5], ...]
        """
        # Hash'leri hesapla
        image_hashes = {}
        hash_func = self.calculate_average_hash if use_average_hash else self.calculate_phash
        
        logger.info(f"{len(image_paths)} resim için hash hesaplanıyor...")
        for img_path in image_paths:
            img_hash = hash_func(img_path)
            if img_hash:
                image_hashes[img_path] = img_hash
        
        # Benzer olanları grupla
        similar_groups = []
        processed = set()
        
        logger.info("Benzerlikler analiz ediliyor...")
        for img1_path, hash1 in image_hashes.items():
            if img1_path in processed:
                continue
                
            current_group = [img1_path]
            processed.add(img1_path)
            
            for img2_path, hash2 in image_hashes.items():
                if img2_path in processed:
                    continue
                    
                # Hamming distance hesapla
                distance = hash1 - hash2
                
                if distance <= self.similarity_threshold:
                    current_group.append(img2_path)
                    processed.add(img2_path)
            
            # Birden fazla resim varsa grup olarak ekle
            if len(current_group) > 1:
                similar_groups.append(current_group)
        
        logger.info(f"{len(similar_groups)} benzer resim grubu bulundu")
        return similar_groups
    
    def get_similarity_percentage(self, img1_path: str, img2_path: str) -> float:
        """
        İki resim arasındaki benzerlik yüzdesini döndürür
        
        Returns:
            Benzerlik yüzdesi (0-100)
        """
        hash1 = self.calculate_phash(img1_path)
        hash2 = self.calculate_phash(img2_path)
        
        if not hash1 or not hash2:
            return 0.0
        
        distance = hash1 - hash2
        max_distance = 64  # Hash boyutu
        similarity = (1 - (distance / max_distance)) * 100
        
        return similarity


class SimilarTextFinder:
    """Benzer metin dosyası bulucu"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        """
        Args:
            similarity_threshold: Benzerlik eşiği (0.0-1.0 arası)
        """
        self.similarity_threshold = similarity_threshold
        
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        İki metin arasındaki benzerliği hesaplar
        
        Returns:
            Benzerlik oranı (0.0-1.0)
        """
        return SequenceMatcher(None, text1, text2).ratio()
    
    def read_file_content(self, file_path: str, max_chars: int = 100000) -> Optional[str]:
        """
        Dosya içeriğini okur
        
        Args:
            file_path: Dosya yolu
            max_chars: Maksimum karakter sayısı
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(max_chars)
        except Exception as e:
            logger.error(f"Dosya okuma hatası ({file_path}): {e}")
            return None
    
    def find_similar_texts(self, file_paths: List[str]) -> List[List[str]]:
        """
        Benzer metin dosyalarını bulur
        
        Args:
            file_paths: Metin dosya yolları
            
        Returns:
            Benzer dosya grupları
        """
        # Dosya içeriklerini oku
        file_contents = {}
        
        logger.info(f"{len(file_paths)} metin dosyası okunuyor...")
        for file_path in file_paths:
            content = self.read_file_content(file_path)
            if content:
                file_contents[file_path] = content
        
        # Benzer olanları bul
        similar_groups = []
        processed = set()
        
        logger.info("Benzerlikler analiz ediliyor...")
        for file1_path, content1 in file_contents.items():
            if file1_path in processed:
                continue
                
            current_group = [file1_path]
            processed.add(file1_path)
            
            for file2_path, content2 in file_contents.items():
                if file2_path in processed:
                    continue
                
                similarity = self.calculate_text_similarity(content1, content2)
                
                if similarity >= self.similarity_threshold:
                    current_group.append(file2_path)
                    processed.add(file2_path)
            
            if len(current_group) > 1:
                similar_groups.append(current_group)
        
        logger.info(f"{len(similar_groups)} benzer metin grubu bulundu")
        return similar_groups


class SimilarFileFinder:
    """Tüm dosya tipleri için benzer dosya bulucu"""
    
    # Desteklenen resim formatları
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    # Desteklenen metin formatları
    TEXT_EXTENSIONS = {'.txt', '.log', '.md', '.py', '.js', '.html', '.css', '.json', '.xml'}
    
    def __init__(self, 
                 image_threshold: int = 5,
                 text_threshold: float = 0.8):
        """
        Args:
            image_threshold: Resim benzerlik eşiği
            text_threshold: Metin benzerlik eşiği
        """
        self.image_finder = SimilarImageFinder(image_threshold)
        self.text_finder = SimilarTextFinder(text_threshold)
        
    def find_similar_files(self, file_paths: List[str]) -> Dict[str, List[List[str]]]:
        """
        Tüm dosya tiplerinde benzer dosyaları bulur
        
        Args:
            file_paths: Dosya yolları listesi
            
        Returns:
            Tip bazında benzer gruplar {'images': [...], 'texts': [...]}
        """
        results = {
            'images': [],
            'texts': [],
            'other': []
        }
        
        # Dosyaları tipe göre ayır
        image_files = []
        text_files = []
        
        for file_path in file_paths:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in self.IMAGE_EXTENSIONS:
                image_files.append(file_path)
            elif ext in self.TEXT_EXTENSIONS:
                text_files.append(file_path)
        
        # Benzer resimleri bul
        if image_files:
            logger.info(f"{len(image_files)} resim dosyası analiz ediliyor...")
            results['images'] = self.image_finder.find_similar_images(image_files)
        
        # Benzer metinleri bul
        if text_files:
            logger.info(f"{len(text_files)} metin dosyası analiz ediliyor...")
            results['texts'] = self.text_finder.find_similar_texts(text_files)
        
        return results


# Kullanım örneği
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Benzer resim arama
    finder = SimilarFileFinder(image_threshold=10, text_threshold=0.75)
    
    test_files = [
        '/path/to/photo1.jpg',
        '/path/to/photo1_edited.jpg',
        '/path/to/photo2.jpg',
        '/path/to/document1.txt',
        '/path/to/document1_copy.txt',
    ]
    
    results = finder.find_similar_files(test_files)
    
    print("\n📸 Benzer Resimler:")
    for group in results['images']:
        print(f"  Grup: {len(group)} resim")
        for img in group:
            print(f"    - {img}")
    
    print("\n📄 Benzer Metinler:")
    for group in results['texts']:
        print(f"  Grup: {len(group)} dosya")
        for txt in group:
            print(f"    - {txt}")
