#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import faiss
import json
from pathlib import Path
from scipy.spatial.distance import cosine

class SpeakerDatabase:
    """
    Cơ sở dữ liệu lưu trữ và tìm kiếm các embedding của người nói
    sử dụng thư viện Faiss để tìm kiếm hiệu quả
    """
    
    def __init__(self):
        """Khởi tạo cơ sở dữ liệu trống"""
        self.embeddings = {}  # Dictionary lưu trữ embeddings theo tên
        self.names = []       # Danh sách tên người nói theo thứ tự trong index
        self.dimension = 0    # Chiều của embedding vectors
        self.index = None     # Faiss index
        
    def add_embedding(self, name, embedding):
        """
        Thêm một embedding mới vào cơ sở dữ liệu
        
        Args:
            name: Tên người nói
            embedding: Vector embedding (numpy array)
        """
        # Chuẩn hóa embedding để sử dụng với Inner Product (cosine similarity)
        normalized_embedding = embedding / np.linalg.norm(embedding)
        
        # Lưu embedding vào dictionary
        self.embeddings[name] = normalized_embedding
        
        # Cập nhật danh sách tên
        self.names.append(name)
        
        # Cập nhật chiều nếu chưa có
        if self.dimension == 0:
            self.dimension = embedding.shape[0]
            
        # Verify dimension
        assert embedding.shape[0] == self.dimension, f"Chiều của embedding ({embedding.shape[0]}) không khớp với chiều hiện tại ({self.dimension})"
            
    def add_embeddings(self, embeddings_dict):
        """
        Thêm nhiều embeddings vào cơ sở dữ liệu
        
        Args:
            embeddings_dict: Dictionary ánh xạ từ tên đến embedding
        """
        for name, embedding in embeddings_dict.items():
            self.add_embedding(name, embedding)
            
    def build_index(self):
        """Xây dựng Faiss index từ các embeddings đã thêm vào"""
        if not self.embeddings:
            print("Không có embeddings nào để xây dựng index")
            return False
            
        # Chuyển embeddings thành ma trận numpy
        embeddings_matrix = np.vstack(list(self.embeddings.values()))
        
        # Tạo Faiss index (Inner Product cho cosine similarity)
        # Sử dụng IndexFlatIP thay vì IndexFlatL2 để sử dụng cosine similarity
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # Thêm vectors vào index
        self.index.add(embeddings_matrix.astype(np.float32))
        
        print(f"Đã xây dựng Faiss index với {len(self.embeddings)} vectors")
        return True
        
    def search(self, query_embedding, top_k=1):
        """
        Tìm kiếm người nói gần nhất dựa trên embedding
        
        Args:
            query_embedding: Vector embedding truy vấn
            top_k: Số kết quả trả về
            
        Returns:
            Tuple của (danh sách tên, danh sách độ tương đồng)
        """
        if self.index is None:
            print("Chưa xây dựng index, đang xây dựng...")
            if not self.build_index():
                return [], []
                
        # Đảm bảo query_embedding là numpy array với shape phù hợp
        if isinstance(query_embedding, np.ndarray) and query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
            
        # Chuẩn hóa query embedding
        query_embedding_norm = query_embedding / np.linalg.norm(query_embedding)
            
        # Tìm kiếm kNN trên Faiss index
        # Inner Product của 2 vector chuẩn hóa = cosine similarity
        similarities, indices = self.index.search(query_embedding_norm.astype(np.float32), k=min(top_k, len(self.names)))
        
        # Ánh xạ indices sang tên người nói
        result_names = [self.names[i] for i in indices[0]]
        
        return result_names, similarities[0]
        
    def calculate_cosine_similarity(self, embedding1, embedding2):
        """
        Tính độ tương đồng cosine giữa hai embeddings
        
        Args:
            embedding1, embedding2: Hai vector embeddings
            
        Returns:
            Độ tương đồng cosine (1 = giống nhau, 0 = không liên quan)
        """
        return 1 - cosine(embedding1, embedding2)
        
    def identify_speaker(self, query_embedding, threshold=0.6):
        """
        Nhận dạng người nói dựa trên embedding
        
        Args:
            query_embedding: Vector embedding truy vấn
            threshold: Ngưỡng độ tương đồng tối thiểu để xác định là cùng người nói
                       (cosine similarity, 0.6 là ngưỡng hợp lý để bắt đầu)
                       
        Returns:
            Tuple (tên người nói gần nhất, độ tương đồng, is_known_speaker)
        """
        names, similarities = self.search(query_embedding, top_k=1)
        
        if not names:
            return None, 0.0, False
            
        name = names[0]
        # Do similarities từ IndexFlatIP đã là inner product của các vector đơn vị,
        # nên nó tương đương với cosine similarity
        cosine_sim = similarities[0]
        
        # Kiểm tra ngưỡng nếu có
        is_known_speaker = cosine_sim >= threshold
            
        return name, cosine_sim, is_known_speaker
        
    def save(self, directory):
        """
        Lưu cơ sở dữ liệu vào thư mục
        
        Args:
            directory: Thư mục đích
        """
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(directory, exist_ok=True)
        
        # Lưu embeddings thành file numpy
        embeddings_path = os.path.join(directory, "embeddings.npz")
        np.savez(embeddings_path, **self.embeddings)
        
        # Lưu metadata (danh sách tên, chiều)
        metadata = {
            "names": self.names,
            "dimension": self.dimension
        }
        metadata_path = os.path.join(directory, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
        # Lưu Faiss index nếu đã xây dựng
        if self.index is not None:
            index_path = os.path.join(directory, "faiss_index.bin")
            faiss.write_index(self.index, index_path)
            
        print(f"Đã lưu cơ sở dữ liệu vào {directory}")
        
    @classmethod
    def load(cls, directory):
        """
        Tải cơ sở dữ liệu từ thư mục
        
        Args:
            directory: Thư mục chứa dữ liệu
            
        Returns:
            Đối tượng SpeakerDatabase đã tải
        """
        # Khởi tạo đối tượng mới
        db = cls()
        
        # Đường dẫn đến các file
        embeddings_path = os.path.join(directory, "embeddings.npz")
        metadata_path = os.path.join(directory, "metadata.json")
        index_path = os.path.join(directory, "faiss_index.bin")
        
        # Kiểm tra xem các file cần thiết có tồn tại không
        if not os.path.exists(embeddings_path) or not os.path.exists(metadata_path):
            print(f"Không tìm thấy file dữ liệu cần thiết trong {directory}")
            return None
            
        # Tải embeddings
        embeddings_data = np.load(embeddings_path)
        db.embeddings = {name: embeddings_data[name] for name in embeddings_data.files}
        
        # Tải metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            db.names = metadata["names"]
            db.dimension = metadata["dimension"]
            
        # Tải Faiss index nếu có
        if os.path.exists(index_path):
            db.index = faiss.read_index(index_path)
        else:
            # Xây dựng lại index nếu không tìm thấy file
            db.build_index()
            
        print(f"Đã tải cơ sở dữ liệu từ {directory} với {len(db.embeddings)} embeddings")
        return db
        
# Test function
if __name__ == "__main__":
    from speaker_embedder import load_embeddings
    
    # Tải embeddings từ file
    try:
        embeddings = load_embeddings("speaker_embeddings.npz")
        
        # Tạo cơ sở dữ liệu
        db = SpeakerDatabase()
        db.add_embeddings(embeddings)
        
        # Xây dựng index
        db.build_index()
        
        # Lưu cơ sở dữ liệu
        db.save("speaker_db")
        
        print(f"Đã tạo cơ sở dữ liệu với {len(embeddings)} người nói")
        
    except Exception as e:
        print(f"Lỗi: {e}")
        print("Hãy chạy speaker_embedder.py trước để tạo file embeddings") 