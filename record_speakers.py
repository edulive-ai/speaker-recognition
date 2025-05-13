import os
import argparse
from record_audio import record_audio

def record_speaker_samples(speaker_name, num_samples=3, duration=5, output_dir="test"):
    """
    Ghi âm nhiều mẫu giọng nói cho một speaker.
    
    Parameters:
    - speaker_name: Tên của speaker
    - num_samples: Số lượng mẫu cần ghi
    - duration: Thời lượng mỗi mẫu (giây)
    - output_dir: Thư mục đầu ra
    
    Returns:
    - Danh sách các file đã ghi âm
    """
    # Tạo thư mục cho speaker
    speaker_dir = os.path.join(output_dir, speaker_name)
    if not os.path.exists(speaker_dir):
        os.makedirs(speaker_dir)
        print(f"Đã tạo thư mục cho speaker: {speaker_dir}")
    
    recorded_files = []
    
    # Ghi âm các mẫu
    for i in range(1, num_samples + 1):
        print(f"\n--- Ghi âm mẫu {i}/{num_samples} cho {speaker_name} ---")
        
        # Tạo tên file với định dạng: TênSpeaker + Số thứ tự
        filename = os.path.join(speaker_dir, f"{speaker_name}{i}.wav")
        
        # Ghi âm
        recorded_file = record_audio(
            output_filename=filename,
            record_seconds=duration
        )
        
        recorded_files.append(recorded_file)
        
        # Chờ người dùng sẵn sàng cho mẫu tiếp theo
        if i < num_samples:
            input("\nNhấn Enter để tiếp tục ghi mẫu tiếp theo...")
    
    print(f"\nĐã hoàn thành ghi âm {num_samples} mẫu cho {speaker_name}.")
    print(f"Các file đã ghi: {recorded_files}")
    
    return recorded_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ghi âm nhiều mẫu cho một speaker")
    parser.add_argument("speaker_name", help="Tên của speaker (ví dụ: Tien, Linh, etc.)")
    parser.add_argument("--samples", "-s", type=int, default=3, help="Số lượng mẫu cần ghi (mặc định: 3)")
    parser.add_argument("--duration", "-d", type=int, default=5, help="Thời lượng mỗi mẫu - giây (mặc định: 5)")
    parser.add_argument("--output-dir", "-o", default="test", help="Thư mục gốc để lưu dữ liệu (mặc định: audio/speaker)")
    
    args = parser.parse_args()
    
    record_speaker_samples(
        speaker_name=args.speaker_name,
        num_samples=args.samples,
        duration=args.duration,
        output_dir=args.output_dir
    ) 