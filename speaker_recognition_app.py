#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import numpy as np
import glob
from pathlib import Path
from speaker_embedder import SpeakerEmbedder, save_embeddings, load_embeddings
from speaker_database import SpeakerDatabase

class SpeakerRecognitionApp:
    """Ứng dụng nhận dạng người nói"""
    
    def __init__(self, database_dir="speaker_db", threshold=0.6):
        """
        Khởi tạo ứng dụng
        
        Args:
            database_dir: Thư mục chứa cơ sở dữ liệu
            threshold: Ngưỡng độ tương đồng tối thiểu để xác định cùng người nói (0.6 là hợp lý để bắt đầu)
        """
        self.database_dir = database_dir
        self.threshold = threshold
        self.embedder = None
        self.database = None
        
    def initialize(self):
        """Khởi tạo embedder và database"""
        print("Đang khởi tạo speaker recognition...")
        
        # Khởi tạo embedder
        self.embedder = SpeakerEmbedder()
        
        # Tải hoặc tạo cơ sở dữ liệu
        if os.path.exists(self.database_dir):
            self.database = SpeakerDatabase.load(self.database_dir)
            if self.database is None:
                self.database = SpeakerDatabase()
        else:
            self.database = SpeakerDatabase()
            
        print("Đã khởi tạo xong speaker recognition")
        
    def prepare_database(self, audio_dir="audio"):
        """
        Chuẩn bị cơ sở dữ liệu từ thư mục chứa file âm thanh
        
        Args:
            audio_dir: Thư mục chứa file âm thanh
        """
        print(f"Đang chuẩn bị cơ sở dữ liệu từ thư mục {audio_dir}...")
        
        # Đảm bảo embedder đã được khởi tạo
        if self.embedder is None:
            self.initialize()
            
        # Trích xuất embeddings
        embeddings = self.embedder.process_all_speakers(audio_dir)
        
        if not embeddings:
            print(f"Không tìm thấy file âm thanh nào trong thư mục {audio_dir}")
            return False
            
        # Tạo cơ sở dữ liệu
        self.database = SpeakerDatabase()
        self.database.add_embeddings(embeddings)
        
        # Xây dựng index
        self.database.build_index()
        
        # Lưu cơ sở dữ liệu
        self.database.save(self.database_dir)
        
        print(f"Đã chuẩn bị xong cơ sở dữ liệu với {len(embeddings)} người nói")
        return True
        
    def identify_file(self, audio_file):
        """
        Nhận dạng người nói từ file âm thanh
        
        Args:
            audio_file: Đường dẫn đến file âm thanh
            
        Returns:
            Tuple (tên người nói, độ tương đồng, is_known)
        """
        # Đảm bảo embedder và database đã được khởi tạo
        if self.embedder is None or self.database is None:
            self.initialize()
            
        # Nếu database vẫn None, có thể cần chuẩn bị trước
        if self.database is None or not self.database.embeddings:
            print("Cơ sở dữ liệu trống, hãy chuẩn bị cơ sở dữ liệu trước")
            return None, 0.0, False
            
        # Kiểm tra file tồn tại
        if not os.path.exists(audio_file):
            print(f"File âm thanh {audio_file} không tồn tại")
            return None, 0.0, False
            
        print(f"Đang nhận dạng người nói từ file {audio_file}...")
        
        # Trích xuất embedding
        embedding = self.embedder.process_audio(audio_file)
        
        if embedding is None:
            print(f"Không thể trích xuất embedding từ file {audio_file}")
            return None, 0.0, False
            
        # Nhận dạng người nói
        name, similarity, is_known = self.database.identify_speaker(embedding, self.threshold)
        
        return name, similarity, is_known
        
    def add_speaker(self, audio_files, speaker_name):
        """
        Thêm người nói mới vào cơ sở dữ liệu
        
        Args:
            audio_files: Đường dẫn đến file hoặc danh sách các file âm thanh
            speaker_name: Tên người nói
            
        Returns:
            Thành công hay không
        """
        # Đảm bảo embedder và database đã được khởi tạo
        if self.embedder is None or self.database is None:
            self.initialize()
            
        # Chuyển thành danh sách nếu chỉ là một file
        if isinstance(audio_files, str):
            audio_files = [audio_files]
            
        # Kiểm tra tồn tại của các file
        for audio_file in audio_files:
            if not os.path.exists(audio_file):
                print(f"File âm thanh {audio_file} không tồn tại")
                return False
                
        print(f"Đang thêm người nói {speaker_name} với {len(audio_files)} file âm thanh...")
        
        # Trích xuất embeddings
        all_embeddings = []
        for audio_file in audio_files:
            embedding = self.embedder.process_audio(audio_file)
            if embedding is not None:
                all_embeddings.append(embedding)
                
        if not all_embeddings:
            print("Không thể trích xuất embedding từ bất kỳ file âm thanh nào")
            return False
            
        # Thêm tất cả embeddings vào cơ sở dữ liệu
        for embedding in all_embeddings:
            self.database.add_embedding(speaker_name, embedding)
        
        # Xây dựng lại index
        self.database.build_index()
        
        # Lưu cơ sở dữ liệu
        self.database.save(self.database_dir)
        
        print(f"Đã thêm người nói {speaker_name} vào cơ sở dữ liệu với {len(all_embeddings)} embeddings")
        return True
        
    def list_speakers(self):
        """Liệt kê danh sách người nói trong cơ sở dữ liệu"""
        # Đảm bảo database đã được khởi tạo
        if self.database is None:
            self.initialize()
            
        if not self.database or not self.database.names:
            print("Cơ sở dữ liệu trống")
            return []
            
        return self.database.names
        
    def add_speaker_from_folder(self, folder_path, speaker_name):
        """
        Thêm người nói mới vào cơ sở dữ liệu từ thư mục chứa các file âm thanh
        
        Args:
            folder_path: Đường dẫn đến thư mục chứa các file WAV
            speaker_name: Tên người nói
            
        Returns:
            Thành công hay không
        """
        # Đảm bảo embedder và database đã được khởi tạo
        if self.embedder is None or self.database is None:
            self.initialize()
            
        # Kiểm tra thư mục tồn tại
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            print(f"Thư mục {folder_path} không tồn tại hoặc không phải là thư mục")
            return False
            
        # Tìm tất cả các file WAV trong thư mục
        wav_files = glob.glob(os.path.join(folder_path, "*.wav"))
        
        if not wav_files:
            print(f"Không tìm thấy file WAV nào trong thư mục {folder_path}")
            return False
            
        print(f"Đang thêm người nói {speaker_name} với {len(wav_files)} file âm thanh từ thư mục {folder_path}...")
        
        # Thêm người nói sử dụng hàm add_speaker đã có
        return self.add_speaker(wav_files, speaker_name)
        
    def remove_speaker(self, speaker_name):
        """
        Xóa người nói khỏi cơ sở dữ liệu
        
        Args:
            speaker_name: Tên người nói cần xóa
            
        Returns:
            Thành công hay không
        """
        # Đảm bảo database đã được khởi tạo
        if self.database is None:
            self.initialize()
            
        # Kiểm tra database có dữ liệu không
        if not self.database or not self.database.names:
            print("Cơ sở dữ liệu trống")
            return False
            
        # Kiểm tra người nói có tồn tại không
        if speaker_name not in self.database.names:
            print(f"Không tìm thấy người nói '{speaker_name}' trong cơ sở dữ liệu")
            return False
            
        # Xóa người nói khỏi database
        print(f"Đang xóa người nói '{speaker_name}' khỏi cơ sở dữ liệu...")
        
        # Xóa embeddings của người nói này
        del self.database.embeddings[speaker_name]
        
        # Cập nhật danh sách tên
        self.database.names = [name for name in self.database.names if name != speaker_name]
        
        # Xây dựng lại mapping và index từ đầu
        self.database.embedding_to_name = []
        self.database.build_index()
        
        # Lưu cơ sở dữ liệu
        self.database.save(self.database_dir)
        
        print(f"Đã xóa người nói '{speaker_name}' khỏi cơ sở dữ liệu")
        return True
        
def main():
    """Hàm main xử lý lệnh từ command line"""
    parser = argparse.ArgumentParser(description="Ứng dụng nhận dạng người nói")
    
    # Các subcommands
    subparsers = parser.add_subparsers(dest="command", help="Lệnh")
    
    # Subcommand "prepare"
    prepare_parser = subparsers.add_parser("prepare", help="Chuẩn bị cơ sở dữ liệu")
    prepare_parser.add_argument("--dir", default="audio/speakers", help="Thư mục chứa file âm thanh")
    
    # Subcommand "identify"
    identify_parser = subparsers.add_parser("identify", help="Nhận dạng người nói")
    identify_parser.add_argument("file", help="Đường dẫn đến file âm thanh")
    identify_parser.add_argument("--threshold", type=float, default=0.6, 
                                help="Ngưỡng độ tương đồng tối thiểu (cosine) để xác định là cùng người nói")
    
    # Subcommand "add"
    add_parser = subparsers.add_parser("add", help="Thêm người nói mới")
    add_parser.add_argument("name", help="Tên người nói")
    add_parser.add_argument("files", nargs="+", help="Đường dẫn đến các file âm thanh")
    
    # Subcommand "add_folder"
    add_folder_parser = subparsers.add_parser("add_folder", help="Thêm người nói mới từ thư mục chứa các file WAV")
    add_folder_parser.add_argument("name", help="Tên người nói")
    add_folder_parser.add_argument("folder", help="Đường dẫn đến thư mục chứa các file WAV")
    
    # Subcommand "list"
    subparsers.add_parser("list", help="Liệt kê danh sách người nói")
    
    # Subcommand "remove"
    remove_parser = subparsers.add_parser("remove", help="Xóa người nói khỏi cơ sở dữ liệu")
    remove_parser.add_argument("name", help="Tên người nói cần xóa")
    
    # Subcommand "check"
    check_parser = subparsers.add_parser("check", help="Kiểm tra độ tương đồng giữa hai file âm thanh")
    check_parser.add_argument("file1", help="Đường dẫn đến file âm thanh thứ nhất")
    check_parser.add_argument("file2", help="Đường dẫn đến file âm thanh thứ hai")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Khởi tạo ứng dụng
    app = SpeakerRecognitionApp()
    
    # Xử lý các lệnh
    if args.command == "prepare":
        app.prepare_database(args.dir)
        
    elif args.command == "identify":
        app.threshold = args.threshold
        app.initialize()
        name, similarity, is_known = app.identify_file(args.file)
        
        if name is None:
            print("Không thể nhận dạng người nói")
        elif is_known:
            print(f"Người nói được nhận dạng: {name} (độ tương đồng: {similarity:.4f})")
        else:
            print(f"Người nói không xác định. Gần nhất: {name} (độ tương đồng: {similarity:.4f}, thấp hơn ngưỡng {args.threshold})")
            
    elif args.command == "add":
        app.add_speaker(args.files, args.name)
        
    elif args.command == "add_folder":
        app.add_speaker_from_folder(args.folder, args.name)
        
    elif args.command == "list":
        speakers = app.list_speakers()
        print("Danh sách người nói:")
        for i, speaker in enumerate(speakers, 1):
            print(f"{i}. {speaker}")
            
    elif args.command == "remove":
        app.remove_speaker(args.name)
        
    elif args.command == "check":
        app.initialize()
        
        # Kiểm tra file tồn tại
        if not os.path.exists(args.file1):
            print(f"File âm thanh {args.file1} không tồn tại")
            return
        if not os.path.exists(args.file2):
            print(f"File âm thanh {args.file2} không tồn tại")
            return
            
        # Trích xuất embeddings
        embedding1 = app.embedder.process_audio(args.file1)
        embedding2 = app.embedder.process_audio(args.file2)
        
        if embedding1 is None or embedding2 is None:
            print("Không thể trích xuất embedding từ một hoặc cả hai file")
            return
            
        # Tính độ tương đồng
        similarity = app.database.calculate_cosine_similarity(embedding1, embedding2)
        print(f"Độ tương đồng giữa hai file: {similarity:.4f}")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 