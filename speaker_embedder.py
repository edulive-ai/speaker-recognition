#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
from pathlib import Path
import torch
import torchaudio
from speechbrain.inference import EncoderClassifier

class SpeakerEmbedder:
    """
    Lớp xử lý việc tạo embeddings từ các file âm thanh
    sử dụng SpeechBrain để trích xuất đặc trưng giọng nói
    """
    
    def __init__(self, model_name="speechbrain/spkrec-ecapa-voxceleb"):
        """
        Khởi tạo embedder với model SpeechBrain
        
        Args:
            model_name: Tên model SpeechBrain để sử dụng
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = EncoderClassifier.from_hparams(
            source=model_name,
            savedir="pretrained_models/spkrec-ecapa-voxceleb",
            run_opts={"device": self.device}
        )
        
    def process_audio(self, audio_path):
        """
        Xử lý file âm thanh và trích xuất embedding
        
        Args:
            audio_path: Đường dẫn đến file âm thanh
            
        Returns:
            Vector embedding của giọng nói
        """
        # Load và xử lý âm thanh
        signal, fs = torchaudio.load(audio_path)
        
        # Đảm bảo âm thanh là mono
        if signal.shape[0] > 1:
            signal = torch.mean(signal, dim=0, keepdim=True)
            
        # Tạo embedding
        embedding = self.model.encode_batch(signal)
        return embedding.squeeze().cpu().numpy()
        
    def process_speaker_directory(self, speaker_dir):
        """
        Xử lý tất cả các file âm thanh trong thư mục của một người nói
        
        Args:
            speaker_dir: Đường dẫn đến thư mục chứa các mẫu giọng nói
            
        Returns:
            List các embeddings của người nói
        """
        embeddings = []
        audio_files = list(Path(speaker_dir).glob("*.wav"))
        
        if not audio_files:
            print(f"Không tìm thấy file âm thanh trong {speaker_dir}")
            return embeddings
            
        print(f"Đang xử lý {len(audio_files)} file âm thanh cho {Path(speaker_dir).name}")
        
        for audio_file in audio_files:
            try:
                embedding = self.process_audio(str(audio_file))
                embeddings.append(embedding)
                print(f"Đã xử lý {audio_file.name}")
            except Exception as e:
                print(f"Lỗi khi xử lý {audio_file.name}: {e}")
                
        return embeddings
        
    def process_all_speakers(self, speakers_dir):
        """
        Xử lý tất cả các thư mục người nói
        
        Args:
            speakers_dir: Đường dẫn đến thư mục chứa các thư mục người nói
            
        Returns:
            Dictionary ánh xạ từ tên người nói đến list embeddings
        """
        # Tạo thư mục nếu chưa tồn tại
        speakers_path = Path(speakers_dir)
        speakers_path.mkdir(parents=True, exist_ok=True)
        
        speakers_embeddings = {}
        speaker_dirs = [d for d in speakers_path.iterdir() if d.is_dir()]
        
        if not speaker_dirs:
            print(f"Không tìm thấy thư mục người nói trong {speakers_dir}")
            print("Hãy tạo các thư mục con cho mỗi người nói và đặt các file .wav vào đó")
            print("Ví dụ:")
            print("  audio/speakers/speaker_1/sample1.wav")
            print("  audio/speakers/speaker_1/sample2.wav")
            print("  audio/speakers/speaker_2/sample1.wav")
            return speakers_embeddings
            
        print(f"Tìm thấy {len(speaker_dirs)} người nói")
        
        for speaker_dir in speaker_dirs:
            speaker_name = speaker_dir.name
            embeddings = self.process_speaker_directory(speaker_dir)
            
            if embeddings:
                speakers_embeddings[speaker_name] = embeddings
                print(f"Đã tạo {len(embeddings)} embeddings cho {speaker_name}")
                
        return speakers_embeddings

# Hàm độc lập để lưu và tải embeddings
def save_embeddings(embeddings_dict, output_path):
    """
    Lưu embeddings vào file numpy
    
    Args:
        embeddings_dict: Dictionary ánh xạ từ tên người nói đến list embeddings
        output_path: Đường dẫn đến file output
    """
    # Tạo thư mục nếu chưa tồn tại
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Chuyển đổi list embeddings thành numpy array cho mỗi người nói
    np_embeddings = {
        name: np.array(embeddings) 
        for name, embeddings in embeddings_dict.items()
    }
    
    # Lưu vào file
    np.savez(output_path, **np_embeddings)
    print(f"Đã lưu embeddings vào {output_path}")

def load_embeddings(file_path):
    """
    Tải embeddings từ file numpy
    
    Args:
        file_path: Đường dẫn đến file embeddings
        
    Returns:
        Dictionary ánh xạ từ tên người nói đến list embeddings
    """
    data = np.load(file_path)
    return {name: list(data[name]) for name in data.files}

if __name__ == "__main__":
    # Khởi tạo embedder
    embedder = SpeakerEmbedder()
    
    # Xử lý tất cả các người nói
    speakers_dir = "audio/speakers"
    embeddings = embedder.process_all_speakers(speakers_dir)
    
    if embeddings:
        # Lưu embeddings
        save_embeddings(embeddings, "speaker_embeddings.npz")
        
        # In thống kê
        total_embeddings = sum(len(emb_list) for emb_list in embeddings.values())
        print(f"\nTổng kết:")
        print(f"- Số người nói: {len(embeddings)}")
        print(f"- Tổng số embeddings: {total_embeddings}")
        print(f"- Trung bình embeddings/người: {total_embeddings/len(embeddings):.1f}")
    else:
        print("Không tạo được embeddings nào") 