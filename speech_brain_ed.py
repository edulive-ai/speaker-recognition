from speechbrain.pretrained import EncoderClassifier
import torchaudio
import torch
import numpy as np
from scipy.spatial.distance import cosine
import os

def tinh_cosine_similarity(a, b):
    # Tính độ tương đồng cosine (1 là giống nhau hoàn toàn, 0 là không liên quan)
    return 1 - cosine(a, b)

def kiem_tra_cung_nguoi_noi(similarity, threshold=0.75):
    # Kiểm tra xem có phải cùng một người nói không dựa trên ngưỡng
    return similarity > threshold, similarity

# Đường dẫn đến file WAV của bạn
file_wav_1 = "audio/Alice1.wav"  # Cập nhật đường dẫn
file_wav_2 = "audio/Alice2.wav"  # Cập nhật đường dẫn

def main():
    try:
        # Kiểm tra xem file có tồn tại không
        if not os.path.exists(file_wav_1):
            print(f"Lỗi: File {file_wav_1} không tồn tại")
            return
        if not os.path.exists(file_wav_2):
            print(f"Lỗi: File {file_wav_2} không tồn tại")
            return
            
        print("Đang tải mô hình speaker recognition...")
        # Tải một mô hình speaker recognition đã được huấn luyện trước
        # Ví dụ: 'speechbrain/spkrec-ecapa-voxceleb' (ECAPA-TDNN, rất phổ biến)
        # Hoặc 'speechbrain/spkrec-xvect-voxceleb' (XVector)
        classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/spkrec-ecapa-voxceleb", # Thư mục để lưu model
            run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"}
        )
        
        print(f"Đang xử lý file {file_wav_1}...")
        # Đọc file audio và tạo embedding cho file 1
        signal_1, fs_1 = torchaudio.load(file_wav_1)
        # SpeechBrain thường mong đợi input là 16kHz, mono, và được chuẩn hóa
        # Interface của SpeechBrain có thể tự xử lý resampling nếu cần
        embedding_1_sb = classifier.encode_batch(signal_1)
        # Output của encode_batch là (1, 1, D), cần squeeze
        embedding_1_sb = embedding_1_sb.squeeze()

        print(f"Đang xử lý file {file_wav_2}...")
        # Đọc file audio và tạo embedding cho file 2
        signal_2, fs_2 = torchaudio.load(file_wav_2)
        embedding_2_sb = classifier.encode_batch(signal_2)
        embedding_2_sb = embedding_2_sb.squeeze()

        print(f"SpeechBrain - Embedding 1: {embedding_1_sb.cpu().detach().numpy()}...")
        print(f"SpeechBrain - Embedding 2: {embedding_2_sb.cpu().detach().numpy()}...")

        # So sánh embeddings
        similarity_sb = tinh_cosine_similarity(embedding_1_sb.cpu().detach().numpy(),
                                            embedding_2_sb.cpu().detach().numpy())
        print(f"SpeechBrain - Độ tương đồng Cosine: {similarity_sb:.4f}")
        
        # Kiểm tra xem có phải cùng một người nói không
        is_same_speaker, score = kiem_tra_cung_nguoi_noi(similarity_sb)
        print(f"Cùng người nói: {is_same_speaker} (điểm số: {score:.4f})")

    except Exception as e:
        print(f"Lỗi với SpeechBrain: {e}")

if __name__ == "__main__":
    main()