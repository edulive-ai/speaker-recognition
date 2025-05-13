#!/usr/bin/env python3

import os
import subprocess
import glob
from pathlib import Path

def convert_audio_to_wav(audio_dir="audio", output_dir=None, sample_rate=16000, formats=None):
    """
    Chuyển đổi các file âm thanh trong thư mục audio_dir thành file wav.
    
    Args:
        audio_dir (str): Thư mục chứa file âm thanh
        output_dir (str): Thư mục đầu ra cho file wav. Nếu None, sẽ lưu vào cùng thư mục với file âm thanh
        sample_rate (int): Tần số lấy mẫu cho file wav đầu ra
        formats (list): Danh sách các định dạng cần chuyển đổi. Nếu None, mặc định sẽ chuyển đổi các định dạng phổ biến
    """
    # Tạo thư mục đầu ra nếu không tồn tại và được chỉ định
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = audio_dir
    
    # Các định dạng âm thanh phổ biến nếu không có định dạng được chỉ định
    if formats is None:
        formats = ['.mp3', '.m4a', '.aac', '.ogg', '.flac', '.wma', '.aiff', '.webm']
    
    # Đảm bảo các định dạng bắt đầu bằng dấu chấm
    formats = [fmt if fmt.startswith('.') else '.' + fmt for fmt in formats]
    
    # Tìm tất cả file âm thanh trong thư mục
    audio_files = []
    for fmt in formats:
        audio_files.extend(glob.glob(os.path.join(audio_dir, f"*{fmt}")))
        # Cũng tìm kiếm định dạng viết hoa
        audio_files.extend(glob.glob(os.path.join(audio_dir, f"*{fmt.upper()}")))
    
    if not audio_files:
        print(f"Không tìm thấy file âm thanh nào trong các định dạng {formats} trong thư mục {audio_dir}")
        return
    
    print(f"Tìm thấy {len(audio_files)} file âm thanh để chuyển đổi")
    
    # Chuyển đổi từng file âm thanh thành wav
    for audio_file in audio_files:
        file_name = os.path.basename(audio_file)
        file_base, file_ext = os.path.splitext(file_name)
        wav_name = file_base + ".wav"
        wav_path = os.path.join(output_dir, wav_name)
        
        # Bỏ qua nếu đây là file wav và đường dẫn đầu ra giống với đường dẫn đầu vào
        if file_ext.lower() == '.wav' and os.path.abspath(audio_file) == os.path.abspath(wav_path):
            print(f"Bỏ qua file {file_name} vì đã là file WAV")
            continue
        
        print(f"Đang chuyển đổi {file_name} thành {wav_name}...")
        
        # Sử dụng ffmpeg để chuyển đổi
        cmd = [
            "ffmpeg",
            "-i", audio_file,
            "-acodec", "pcm_s16le",  # Định dạng PCM 16-bit
            "-ar", str(sample_rate),  # Sample rate
            "-ac", "1",  # Mono
            "-y",  # Ghi đè nếu file đã tồn tại
            wav_path
        ]
        
        try:
            # Chạy lệnh ffmpeg
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Đã chuyển đổi thành công: {wav_path}")
        except subprocess.CalledProcessError as e:
            print(f"Lỗi khi chuyển đổi {audio_file}: {e}")
            stderr_output = e.stderr.decode('utf-8') if e.stderr else "Không có thông tin lỗi"
            print(f"Stderr: {stderr_output}")

def check_ffmpeg():
    """Kiểm tra xem ffmpeg đã được cài đặt chưa"""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def list_audio_files(directory, formats=None):
    """Liệt kê các file âm thanh trong thư mục với các định dạng được chỉ định"""
    if formats is None:
        formats = ['.mp3', '.m4a', '.aac', '.ogg', '.flac', '.wma', '.aiff', '.webm', '.wav']
    
    # Đảm bảo các định dạng bắt đầu bằng dấu chấm
    formats = [fmt if fmt.startswith('.') else '.' + fmt for fmt in formats]
    
    audio_files = []
    for fmt in formats:
        audio_files.extend(glob.glob(os.path.join(directory, f"*{fmt}")))
        audio_files.extend(glob.glob(os.path.join(directory, f"*{fmt.upper()}")))
    
    return sorted(audio_files)

if __name__ == "__main__":
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Chuyển đổi file âm thanh sang định dạng WAV")
    parser.add_argument("--dir", default="audio", help="Thư mục chứa file âm thanh đầu vào")
    parser.add_argument("--output", help="Thư mục đầu ra cho file WAV")
    parser.add_argument("--rate", type=int, default=16000, help="Tần số lấy mẫu cho file WAV đầu ra (Hz)")
    parser.add_argument("--formats", nargs="+", help="Các định dạng cần chuyển đổi (ví dụ: mp3 m4a ogg)")
    parser.add_argument("--list", action="store_true", help="Chỉ liệt kê các file âm thanh mà không chuyển đổi")
    
    args = parser.parse_args()
    
    if not check_ffmpeg():
        print("ERROR: FFmpeg chưa được cài đặt.")
        print("Hãy cài đặt FFmpeg trước khi chạy script này:")
        print("Trên Ubuntu/Debian: sudo apt-get update && sudo apt-get install ffmpeg")
        print("Trên macOS với Homebrew: brew install ffmpeg")
        print("Trên Windows: Tải từ https://ffmpeg.org/download.html")
        exit(1)
    
    # Liệt kê các file nếu được yêu cầu
    if args.list:
        files = list_audio_files(args.dir)
        print(f"Các file âm thanh trong thư mục {args.dir}:")
        for i, file in enumerate(files, 1):
            print(f"{i}. {os.path.basename(file)}")
        exit(0)
    
    # Chuyển đổi các file âm thanh sang WAV
    convert_audio_to_wav(
        audio_dir=args.dir,
        output_dir=args.output,
        sample_rate=args.rate,
        formats=args.formats
    )
    
    print("Hoàn tất chuyển đổi!") 