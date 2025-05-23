# Hệ thống nhận dạng người nói (Speaker Recognition)

Dự án này xây dựng một hệ thống nhận dạng người nói hoàn chỉnh, sử dụng mô hình ECAPA-TDNN từ SpeechBrain để trích xuất đặc trưng giọng nói và thư viện Faiss để lưu trữ và tìm kiếm hiệu quả.

## Tính năng

- Trích xuất đặc trưng (embedding) từ file âm thanh
- Xây dựng và quản lý cơ sở dữ liệu người nói với Faiss
- Nhận dạng người nói từ file âm thanh mới
- Thêm người nói mới vào cơ sở dữ liệu (từ nhiều file hoặc từ thư mục)
- Xóa người nói khỏi cơ sở dữ liệu
- Chuyển đổi nhiều định dạng âm thanh sang định dạng wav
- So sánh trực tiếp độ tương đồng giữa hai file âm thanh
- Ghi âm trực tiếp từ microphone và lưu thành file WAV
- Phân tích cuộc họp để xác định ai nói gì và khi nào (tự động phát hiện đoạn giọng nói)

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
python convert_audio_to_wav.py --rate 16000

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

Bạn có thể thêm người nói bằng một trong hai cách:

1. Từ nhiều file âm thanh riêng lẻ:
```bash
python speaker_recognition_app.py add "Tên người nói" đường/dẫn/file1.wav đường/dẫn/file2.wav
```

2. Từ một thư mục chứa nhiều file WAV:
```bash
python speaker_recognition_app.py add_folder "Tên người nói" đường/dẫn/đến/thư/mục
```

### Xóa người nói

```bash
python speaker_recognition_app.py remove "Tên người nói"
```

### Liệt kê danh sách người nói

```bash
python speaker_recognition_app.py list
```

### So sánh hai file âm thanh

```bash
python speaker_recognition_app.py check file1.wav file2.wav
```

### Ghi âm từ microphone

Dự án cũng bao gồm công cụ ghi âm từ microphone:

```bash
# Ghi nhiều mẫu cho một người nói
python record_speaker.py "Tên người nói" --samples 3 --duration 5
```

Các file ghi âm sẽ được lưu ở định dạng WAV và có thể được sử dụng trực tiếp với ứng dụng nhận dạng người nói.

## Cấu trúc dự án

- `speaker_embedder.py`: Module trích xuất đặc trưng từ file âm thanh
- `speaker_database.py`: Module quản lý cơ sở dữ liệu người nói với Faiss
- `speaker_recognition_app.py`: Ứng dụng chính để nhận dạng người nói
- `convert_audio_to_wav.py`: Công cụ chuyển đổi nhiều định dạng âm thanh sang wav
- `record_audio.py`: Công cụ ghi âm từ microphone
- `record_speaker.py`: Công cụ ghi nhiều mẫu âm thanh cho một người nói
- `play_audio.py`: Công cụ phát lại file âm thanh
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

## Công cụ gộp file âm thanh (merge_audio_files.py)

Đây là công cụ giúp gộp nhiều file âm thanh trong một thư mục thành một file duy nhất.

### Cài đặt

Đảm bảo bạn đã cài đặt thư viện pydub:

```bash
pip install pydub
```

Thư viện này cũng yêu cầu ffmpeg để xử lý các định dạng âm thanh. Nếu chưa cài đặt, bạn có thể cài đặt như sau:

```bash
# Trên Ubuntu/Debian
sudo apt-get install ffmpeg

# Trên macOS với Homebrew
brew install ffmpeg
```

### Cách sử dụng cơ bản

```bash
python merge_audio_files.py đường_dẫn_thư_mục_chứa_file_âm_thanh đường_dẫn_file_đầu_ra
```

Ví dụ:
```bash
python merge_audio_files.py ./audio_files ./output.wav
```

### Các tùy chọn

| Tùy chọn | Mô tả |
|----------|-------|
| `--formats` | Lọc theo định dạng file (ví dụ: wav, mp3) |
| `--sort` | Sắp xếp theo `name` (tên file) hoặc `time` (thời gian tạo file) |
| `--reverse` | Đảo ngược thứ tự sắp xếp |
| `--silence` | Thêm khoảng lặng giữa các file (mili giây) |
| `--normalize` | Chuẩn hóa âm thanh |
| `--sample-rate` | Tần số lấy mẫu cho file đầu ra (Hz) |
| `--channels` | Số kênh cho file đầu ra (1=mono, 2=stereo) |
| `--wav` | Luôn xuất ra định dạng WAV bất kể đuôi file đầu ra |

### Ví dụ nâng cao

1. Gộp tất cả file WAV, thêm khoảng lặng 500ms giữa các file:
```bash
python merge_audio_files.py ./audio_files ./output.mp3 --formats wav --silence 500
```

2. Gộp file theo thời gian tạo, đảo ngược thứ tự và chuẩn hóa âm thanh:
```bash
python merge_audio_files.py ./audio_files ./output.wav --sort time --reverse --normalize
```

3. Gộp file và chuyển đổi sang âm thanh mono với tần số 44100Hz:
```bash
python merge_audio_files.py ./audio_files ./output.wav --channels 1 --sample-rate 44100
```

### Sử dụng trong mã Python

Bạn có thể import và sử dụng hàm `merge_audio_files` trong mã Python:

```python
from merge_audio_files import merge_audio_files

output_path = merge_audio_files(
    input_dir="./audio_files",
    output_file="./output.wav",
    format_filter=["wav", "mp3"],
    add_silence=500,
    normalize=True,
    channels=1
)

print(f"File đã được lưu tại: {output_path}")
```

## Phân đoạn người nói (diarization_speaker.py)

Đây là công cụ giúp phân tích và nhận diện các đoạn người nói khác nhau trong một file âm thanh có nhiều người tham gia (như cuộc họp, phỏng vấn).

### Cài đặt thêm

Đảm bảo bạn đã cài đặt các thư viện cần thiết:

```bash
pip install pyannote.audio matplotlib pydub tqdm
```

Bạn cần có token Hugging Face và đã chấp nhận điều khoản sử dụng mô hình tại: https://huggingface.co/pyannote/speaker-diarization-3.1

### Cách sử dụng cơ bản

```bash
python diarization_speaker.py đường_dẫn_đến_file_âm_thanh
```

Ví dụ:
```bash
python diarization_speaker.py meeting_voice/voice_meeting.wav
```

### Các tùy chọn

| Tùy chọn | Mô tả |
|----------|-------|
| `--num_speakers` | Chỉ định số lượng người nói cố định (nếu biết trước) |
| `--min_speakers` | Chỉ định số người nói tối thiểu |
| `--max_speakers` | Chỉ định số người nói tối đa |
| `--visualize` | Tạo biểu đồ trực quan kết quả phân đoạn |
| `--extract` | Tạo các file âm thanh riêng biệt cho từng người nói |
| `--output_dir` | Chỉ định thư mục đầu ra cho kết quả |
| `--format` | Chọn định dạng file kết quả (json, rttm, txt, all) |

### Ví dụ nâng cao

1. Chỉ định số lượng người nói:
```bash
python diarization_speaker.py meeting_voice/voice_meeting.wav --num_speakers 3
```

2. Tạo biểu đồ trực quan và tách riêng âm thanh từng người:
```bash
python diarization_speaker.py meeting_voice/voice_meeting.wav --visualize --extract
```

3. Chỉ định khoảng người nói và định dạng đầu ra:
```bash
python diarization_speaker.py meeting_voice/voice_meeting.wav --min_speakers 2 --max_speakers 5 --format json
```

### Hiểu kết quả

Kết quả phân đoạn sẽ hiển thị:
- Thời gian bắt đầu và kết thúc của từng đoạn nói
- Nhãn người nói (SPEAKER_00, SPEAKER_01, ...)
- Thống kê tổng thời lượng nói của từng người
- Các file output định dạng JSON, RTTM và TXT

### Tích hợp với dự án

Công cụ này có thể được sử dụng với hệ thống nhận dạng người nói để:
1. Phân tách các đoạn nói trong cuộc họp
2. Tạo dữ liệu cho từng người nói riêng biệt
3. Kết hợp với nhận dạng người nói để gán tên thật thay cho SPEAKER_XX

# Speaker Recognition API Documentation

This document provides detailed information about the available API endpoints and how to use them with curl commands.

## Base URL

All API endpoints are relative to the base URL: `http://localhost:5000`

## API Endpoints

### Health Check

Check if the API is running properly.

```bash
curl -X GET http://localhost:5000/health
```

### Speaker Management

#### Get All Speakers

Retrieve a list of all registered speakers.

```bash
curl -X GET http://localhost:5000/speakers
```

#### Create New Speaker

Add a new speaker with audio files.

```bash
curl -X POST http://localhost:5000/speakers \
  -F "speaker_name=John Doe" \
  -F "files[]=@/path/to/audio1.wav" \
  -F "files[]=@/path/to/audio2.wav"
```

#### Delete Speaker

Remove a speaker from the database.

```bash
curl -X DELETE http://localhost:5000/speakers/John%20Doe
```

### Speaker Identification

#### Identify Speaker from Audio File

Identify a speaker from an audio file.

```bash
curl -X POST http://localhost:5000/speakers/identify \
  -F "file=@/path/to/audio.wav" \
  -F "threshold=0.6"
```

### Similarity Check

#### Check Similarity Between Two Audio Files

Compare two audio files and get their similarity score.

```bash
curl -X POST http://localhost:5000/similarity \
  -F "file1=@/path/to/audio1.wav" \
  -F "file2=@/path/to/audio2.wav"
```

### Speech to Text

#### Convert Audio File to Text

Convert speech in an audio file to text.

```bash
curl -X POST http://localhost:5000/speech-to-text/files \
  -F "file=@/path/to/audio.wav" \
  -F "language=vi-VN"
```

#### Record and Convert to Text

Record audio and convert it to text in real-time.

```bash
curl -X POST http://localhost:5000/speech-to-text/recordings \
  -H "Content-Type: application/json" \
  -d '{
    "duration": 5,
    "language": "vi-VN",
    "extract_embedding": true,
    "speaker_name": "John Doe",
    "identify_speaker": true,
    "threshold": 0.6
  }'
```

## Response Format

All API responses follow this format:

```json
{
  "status": "success|error",
  "data": {
    // Response data (if any)
  },
  "message": "Human readable message"
}
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 405: Method Not Allowed
- 413: Request Entity Too Large
- 422: Unprocessable Entity
- 500: Internal Server Error

## File Requirements

- Supported audio formats: WAV, MP3, OGG, FLAC, M4A
- Maximum file size: 16MB

## CORS Support

The API supports CORS and is configured to work with:
- http://localhost:5000
- https://*.ngrok-free.app
- https://*.ngrok.io