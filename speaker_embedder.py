#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import torch
import torchaudio
import numpy as np
from pathlib import Path
from speechbrain.pretrained import EncoderClassifier
from tqdm import tqdm

class SpeakerEmbedder:
    """
    Lớp trích xuất đặc trưng từ file âm thanh giọng nói
    sử dụng mô hình ECAPA-TDNN từ SpeechBrain
    """
    
    def __init__(self, device=None):
        """
        Khởi tạo embedder
        
        Args:
            device: Thiết bị sử dụng cho mô hình (None để tự động chọn)
        """
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"Đang tải mô hình speaker embedding trên thiết bị: {self.device}")
        self.model = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/spkrec-ecapa-voxceleb",
            run_opts={"device": self.device}
        )
        print("Đã tải xong mô hình")
        
    def embed_file(self, audio_file):
        """
        Trích xuất đặc trưng từ một file âm thanh
        
        Args:
            audio_file: Đường dẫn đến file âm thanh
            
        Returns:
            Embedding vector (numpy array)
        """
        try:
            # Đọc file âm thanh
            signal, fs = torchaudio.load(audio_file)
            
            # Trích xuất embedding từ tín hiệu âm thanh
            with torch.no_grad():
                embedding = self.model.encode_batch(signal)
                
            # Chuyển về numpy array và squeeze để loại bỏ chiều dư thừa
            return embedding.squeeze().cpu().numpy()
            
        except Exception as e:
            print(f"Lỗi khi trích xuất embedding từ {audio_file}: {e}")
            return None
            
    def embed_files(self, audio_files, show_progress=True):
        """
        Trích xuất đặc trưng từ nhiều file âm thanh
        
        Args:
            audio_files: Danh sách đường dẫn đến các file âm thanh
            show_progress: Hiển thị thanh tiến trình
            
        Returns:
            Dictionary map từ tên file đến embedding vector
        """
        embeddings = {}
        
        # Tạo iterator với hoặc không có thanh tiến trình
        files_iter = tqdm(audio_files) if show_progress else audio_files
        
        for audio_file in files_iter:
            try:
                # Lấy tên file không có phần mở rộng
                file_name = os.path.splitext(os.path.basename(audio_file))[0]
                
                # Trích xuất embedding
                embedding = self.embed_file(audio_file)
                
                if embedding is not None:
                    embeddings[file_name] = embedding
                    
            except Exception as e:
                print(f"Lỗi với file {audio_file}: {e}")
                continue
                
        return embeddings
        
    def embed_directory(self, audio_dir, extensions=(".wav", ".mp3"), show_progress=True):
        """
        Trích xuất đặc trưng từ tất cả file âm thanh trong một thư mục
        
        Args:
            audio_dir: Thư mục chứa file âm thanh
            extensions: Các phần mở rộng hợp lệ cho file âm thanh
            show_progress: Hiển thị thanh tiến trình
            
        Returns:
            Dictionary map từ tên file đến embedding vector
        """
        audio_files = []
        
        # Thu thập tất cả file âm thanh trong thư mục
        for ext in extensions:
            audio_files.extend(list(Path(audio_dir).glob(f"*{ext}")))
            
        if not audio_files:
            print(f"Không tìm thấy file âm thanh nào trong thư mục {audio_dir}")
            return {}
            
        return self.embed_files(audio_files, show_progress=show_progress)
        
# Hàm trợ giúp để lưu và tải embeddings
def save_embeddings(embeddings, output_file):
    """Lưu embeddings dưới dạng file numpy"""
    np.savez(output_file, **embeddings)
    print(f"Đã lưu {len(embeddings)} embeddings vào {output_file}")
    
def load_embeddings(input_file):
    """Tải embeddings từ file numpy"""
    data = np.load(input_file)
    embeddings = {name: data[name] for name in data.files}
    return embeddings
    
# Test function
if __name__ == "__main__":
    # Khởi tạo speaker embedder
    embedder = SpeakerEmbedder()
    
    # Nhúng tất cả file âm thanh trong thư mục audio
    embeddings = embedder.embed_directory("audio")
    
    if embeddings:
        print(f"Đã trích xuất {len(embeddings)} embeddings")
        
        # Lưu embeddings
        save_embeddings(embeddings, "speaker_embeddings.npz")
    else:
        print("Không tìm thấy file âm thanh nào để trích xuất embedding") 