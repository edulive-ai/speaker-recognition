#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import re
from pydub import AudioSegment
from pathlib import Path

def natural_sort_key(s):
    """Hàm sắp xếp theo thứ tự tự nhiên (1, 2, 10 thay vì 1, 10, 2)"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def merge_audio_files(input_dir, output_file, format_filter=None, sort_by='name', reverse=False, 
                      add_silence=0, normalize=False, sample_rate=None, channels=None, force_wav=False):
    """
    Gộp các file âm thanh trong thư mục thành một file duy nhất
    
    Args:
        input_dir: Thư mục chứa các file âm thanh
        output_file: Đường dẫn đến file đầu ra
        format_filter: Lọc theo định dạng file (vd: wav, mp3, ...)
        sort_by: Sắp xếp theo 'name' hoặc 'time' (thời gian tạo file)
        reverse: Đảo ngược thứ tự sắp xếp
        add_silence: Thêm khoảng lặng giữa các file (mili giây)
        normalize: Chuẩn hóa âm thanh
        sample_rate: Tần số lấy mẫu cho file đầu ra (Hz)
        channels: Số kênh cho file đầu ra (1=mono, 2=stereo)
        force_wav: Luôn xuất ra định dạng WAV bất kể đuôi file
    """
    input_dir = Path(input_dir)
    
    # Kiểm tra thư mục đầu vào
    if not input_dir.exists() or not input_dir.is_dir():
        raise ValueError(f"Thư mục '{input_dir}' không tồn tại!")
    
    # Lấy danh sách các file âm thanh
    files = []
    for file in input_dir.iterdir():
        if file.is_file():
            # Lọc theo định dạng nếu cần
            if format_filter and file.suffix.lower()[1:] not in format_filter:
                continue
            files.append(file)
    
    if not files:
        raise ValueError(f"Không tìm thấy file âm thanh nào trong thư mục '{input_dir}'!")
    
    # Sắp xếp files
    if sort_by == 'name':
        files.sort(key=lambda x: natural_sort_key(x.name), reverse=reverse)
    elif sort_by == 'time':
        files.sort(key=lambda x: os.path.getmtime(x), reverse=reverse)
    
    print(f"Tìm thấy {len(files)} file âm thanh.")
    
    # Tạo đối tượng silence nếu cần
    silence = None
    if add_silence > 0:
        silence = AudioSegment.silent(duration=add_silence)
    
    # Gộp các file
    print("Đang gộp các file...")
    combined = AudioSegment.empty()
    
    for i, file in enumerate(files):
        print(f"[{i+1}/{len(files)}] Đang xử lý: {file.name}")
        try:
            audio = AudioSegment.from_file(file)
            
            # Áp dụng các tham số nếu cần
            if sample_rate:
                audio = audio.set_frame_rate(sample_rate)
            if channels:
                if channels == 1:
                    audio = audio.set_channels(1)
                elif channels == 2:
                    audio = audio.set_channels(2)
            
            # Thêm đoạn âm thanh vào kết quả
            combined += audio
            
            # Thêm khoảng lặng nếu không phải file cuối cùng
            if silence and i < len(files) - 1:
                combined += silence
                
        except Exception as e:
            print(f"Lỗi khi xử lý file '{file.name}': {str(e)}")
            continue
    
    # Chuẩn hóa âm thanh nếu cần
    if normalize and len(combined) > 0:
        print("Đang chuẩn hóa âm thanh...")
        combined = combined.normalize()
    
    # Lưu file
    output_path = Path(output_file)
    output_format = output_path.suffix[1:].lower()
    
    # Nếu không có định dạng hoặc yêu cầu xuất WAV
    if not output_format or force_wav:
        output_format = 'wav'
        if force_wav and output_path.suffix.lower() != '.wav':
            output_path = Path(str(output_path).rsplit('.', 1)[0] + '.wav')
        elif not output_format:
            output_path = Path(str(output_path) + '.wav')
    
    print(f"Đang lưu file '{output_path}'...")
    combined.export(output_path, format=output_format)
    
    print(f"Đã gộp {len(files)} file thành công và lưu vào '{output_path}'")
    print(f"Độ dài: {len(combined)/1000:.2f} giây")
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Gộp các file âm thanh trong thư mục thành một file duy nhất')
    parser.add_argument('input_dir', help='Thư mục chứa các file âm thanh')
    parser.add_argument('output_file', help='Đường dẫn đến file đầu ra')
    parser.add_argument('--formats', nargs='+', help='Lọc theo định dạng file (ví dụ: wav mp3)')
    parser.add_argument('--sort', choices=['name', 'time'], default='name',
                       help='Sắp xếp theo tên file hoặc thời gian tạo file (mặc định: name)')
    parser.add_argument('--reverse', action='store_true',
                       help='Đảo ngược thứ tự sắp xếp')
    parser.add_argument('--silence', type=int, default=0,
                       help='Thêm khoảng lặng giữa các file (mili giây)')
    parser.add_argument('--normalize', action='store_true',
                       help='Chuẩn hóa âm thanh')
    parser.add_argument('--sample-rate', type=int,
                       help='Tần số lấy mẫu cho file đầu ra (Hz)')
    parser.add_argument('--channels', type=int, choices=[1, 2],
                       help='Số kênh cho file đầu ra (1=mono, 2=stereo)')
    parser.add_argument('--wav', action='store_true',
                       help='Luôn xuất ra định dạng WAV bất kể đuôi file')
    
    args = parser.parse_args()
    
    try:
        merge_audio_files(
            args.input_dir,
            args.output_file,
            format_filter=args.formats,
            sort_by=args.sort,
            reverse=args.reverse,
            add_silence=args.silence,
            normalize=args.normalize,
            sample_rate=args.sample_rate,
            channels=args.channels,
            force_wav=args.wav
        )
        return 0
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 