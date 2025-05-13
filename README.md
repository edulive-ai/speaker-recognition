# Hệ thống nhận dạng người nói (Speaker Recognition)

Dự án này xây dựng một hệ thống nhận dạng người nói hoàn chỉnh, sử dụng mô hình ECAPA-TDNN từ SpeechBrain để trích xuất đặc trưng giọng nói và thư viện Faiss để lưu trữ và tìm kiếm hiệu quả.

## Tính năng

- Trích xuất đặc trưng (embedding) từ file âm thanh
- Xây dựng và quản lý cơ sở dữ liệu người nói với Faiss
- Nhận dạng người nói từ file âm thanh mới
- Thêm người nói mới vào cơ sở dữ liệu
- Chuyển đổi nhiều định dạng âm thanh sang định dạng wav
- So sánh trực tiếp độ tương đồng giữa hai file âm thanh

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/edulive-ai/speaker-recognition.git
cd speaker-recognition
```

2. Tạo môi trường ảo và cài đặt các thư viện:
```bash
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Cài đặt FFmpeg (cần thiết để xử lý file âm thanh):
```bash
# Trên Ubuntu/Debian
sudo apt-get update && sudo apt-get install ffmpeg

# Trên macOS với Homebrew
brew install ffmpeg

# Trên Windows: Tải từ https://ffmpeg.org/download.html
```

## Cách sử dụng

### Chuẩn bị dữ liệu

1. Đặt các file âm thanh của người nói (nhiều định dạng khác nhau như wav, mp3, m4a, flac,...) vào thư mục `audio/`.

2. Nếu file của bạn không phải định dạng wav, bạn có thể chuyển đổi tất cả sang định dạng wav:
```bash
python convert_audio_to_wav.py
```

Công cụ chuyển đổi âm thanh hỗ trợ nhiều tùy chọn:
```bash
# Chỉ định thư mục đầu vào
python convert_audio_to_wav.py --dir đường/dẫn/đến/thư/mục

# Chỉ định thư mục đầu ra
python convert_audio_to_wav.py --output thư/mục/đầu/ra

# Chỉ định tần số lấy mẫu
python convert_audio_to_wav.py --rate 44100

# Chỉ định các định dạng cần chuyển đổi
python convert_audio_to_wav.py --formats mp3 m4a ogg

# Chỉ liệt kê các file âm thanh mà không chuyển đổi
python convert_audio_to_wav.py --list
```

### Xây dựng cơ sở dữ liệu

```bash
python speaker_recognition_app.py prepare
```

Lệnh này sẽ:
- Trích xuất đặc trưng từ các file âm thanh trong thư mục `audio/`
- Xây dựng cơ sở dữ liệu và lưu vào thư mục `speaker_db/`

### Nhận dạng người nói

```bash
python speaker_recognition_app.py identify đường/dẫn/đến/file.wav
```

Bạn có thể điều chỉnh ngưỡng độ tương đồng để được coi là cùng một người nói:
```bash
python speaker_recognition_app.py identify đường/dẫn/đến/file.wav --threshold 0.7
```

### Thêm người nói mới

```bash
python speaker_recognition_app.py add "Tên người nói" đường/dẫn/đến/file1.wav đường/dẫn/đến/file2.wav
```

### Liệt kê danh sách người nói

```bash
python speaker_recognition_app.py list
```

### So sánh hai file âm thanh

```bash
python speaker_recognition_app.py check file1.wav file2.wav
```

## Cấu trúc dự án

- `speaker_embedder.py`: Module trích xuất đặc trưng từ file âm thanh
- `speaker_database.py`: Module quản lý cơ sở dữ liệu người nói với Faiss
- `speaker_recognition_app.py`: Ứng dụng chính để nhận dạng người nói
- `convert_audio_to_wav.py`: Công cụ chuyển đổi nhiều định dạng âm thanh sang wav
- `audio/`: Thư mục chứa file âm thanh đầu vào
- `speaker_db/`: Thư mục chứa cơ sở dữ liệu người nói
- `pretrained_models/`: Thư mục chứa mô hình ECAPA-TDNN đã tải

## Cách hoạt động

1. **Trích xuất đặc trưng**: Hệ thống sử dụng mô hình ECAPA-TDNN (từ SpeechBrain) để trích xuất vector đặc trưng 192 chiều từ file âm thanh.

2. **Lưu trữ và tìm kiếm**: Các vector đặc trưng được chuẩn hóa và lưu trữ trong Faiss index, cho phép tìm kiếm nhanh chóng và hiệu quả.

3. **Nhận dạng**: Khi cần nhận dạng một file âm thanh mới, hệ thống trích xuất vector đặc trưng và tìm kiếm vector gần nhất trong cơ sở dữ liệu.

4. **So sánh cosine**: Độ tương đồng cosine giữa các vector được sử dụng để xác định mức độ tương đồng. Độ tương đồng lớn hơn ngưỡng được coi là cùng một người nói.

## Lưu ý

- Đảm bảo các file âm thanh của bạn có chất lượng tốt và độ dài đủ (ít nhất 3-5 giây).
- Ngưỡng độ tương đồng mặc định là 0.6, có thể điều chỉnh tùy theo nhu cầu và dữ liệu cụ thể. Giá trị cao hơn (gần 1.0) yêu cầu độ tương đồng cao hơn.
- Tránh nhiễu và tiếng ồn nền trong file âm thanh để có kết quả chính xác nhất.
- Model cần tải dữ liệu từ Hugging Face Hub, nên lần đầu tiên sử dụng sẽ yêu cầu kết nối internet. 