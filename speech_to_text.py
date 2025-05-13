#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile
import speech_recognition as sr
import pyaudio
import wave
import numpy as np
from datetime import datetime

class SpeechToText:
    """
    Lớp xử lý chuyển đổi âm thanh thành văn bản
    """
    
    def __init__(self, language="vi-VN"):
        """
        Khởi tạo với ngôn ngữ cụ thể
        
        Args:
            language: Mã ngôn ngữ (mặc định: tiếng Việt)
        """
        self.language = language
        self.recognizer = sr.Recognizer()
        
    def recognize_from_file(self, audio_file):
        """
        Nhận dạng văn bản từ file âm thanh
        
        Args:
            audio_file: Đường dẫn tới file âm thanh
            
        Returns:
            Tuple (văn bản nhận dạng, trạng thái thành công)
        """
        try:
            with sr.AudioFile(audio_file) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language=self.language)
                return text, True
        except sr.UnknownValueError:
            return "Không thể nhận dạng văn bản từ âm thanh", False
        except sr.RequestError as e:
            return f"Lỗi kết nối đến Google API: {e}", False
        except Exception as e:
            return f"Lỗi: {e}", False
            
    def record_and_recognize(self, record_seconds=5, sample_rate=16000):
        """
        Ghi âm và nhận dạng văn bản
        
        Args:
            record_seconds: Thời gian ghi âm (giây)
            sample_rate: Tần số lấy mẫu
            
        Returns:
            Tuple (văn bản nhận dạng, trạng thái thành công, đường dẫn file tạm)
        """
        # Tạo file tạm
        temp_file = tempfile.mktemp(suffix=".wav")
        
        # Ghi âm
        self._record_audio(temp_file, record_seconds, sample_rate)
        
        # Nhận dạng văn bản
        text, success = self.recognize_from_file(temp_file)
        
        return text, success, temp_file
    
    def _record_audio(self, output_file, record_seconds=5, sample_rate=16000, chunk=1024, channels=1):
        """
        Ghi âm từ microphone và lưu vào file
        
        Args:
            output_file: Đường dẫn file đầu ra
            record_seconds: Thời gian ghi âm (giây)
            sample_rate: Tần số lấy mẫu
            chunk: Kích thước buffer
            channels: Số kênh (1=mono, 2=stereo)
        """
        # Khởi tạo PyAudio
        p = pyaudio.PyAudio()
        
        # Mở stream
        stream = p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk
        )
        
        print(f"Bắt đầu ghi âm trong {record_seconds} giây...")
        
        # Ghi âm thành các frame
        frames = []
        for i in range(0, int(sample_rate / chunk * record_seconds)):
            data = stream.read(chunk)
            frames.append(data)
            
        print("Đã hoàn thành ghi âm")
        
        # Dừng và đóng stream
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Lưu file WAV
        wf = wave.open(output_file, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        print(f"Đã lưu file âm thanh tại: {output_file}")
    
    @staticmethod
    def detect_language(text):
        """
        Phát hiện ngôn ngữ của văn bản (đơn giản)
        
        Args:
            text: Văn bản cần phát hiện
            
        Returns:
            Mã ngôn ngữ (vi-VN hoặc en-US)
        """
        # Danh sách các từ thông dụng trong tiếng Việt
        vietnamese_words = ['của', 'và', 'là', 'trong', 'có', 'được', 'không', 'những', 'người', 'một']
        
        # Đếm số từ tiếng Việt
        count = sum(1 for word in vietnamese_words if word in text.lower())
        
        # Nếu có ít nhất 1 từ tiếng Việt, coi là tiếng Việt
        if count > 0:
            return "vi-VN"
        return "en-US"

# Test function
if __name__ == "__main__":
    # Khởi tạo
    stt = SpeechToText(language="vi-VN")
    
    # Ghi âm và nhận dạng
    text, success, temp_file = stt.record_and_recognize(record_seconds=5)
    
    if success:
        print(f"Kết quả nhận dạng: {text}")
    else:
        print(f"Lỗi: {text}")
        
    # Xóa file tạm
    try:
        os.remove(temp_file)
    except:
        pass 