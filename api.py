#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import uuid
import json
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from speaker_recognition_app import SpeakerRecognitionApp
from speech_to_text import SpeechToText

# Khởi tạo Flask app
app = Flask(__name__, static_folder='static')

# Cấu hình CORS chi tiết hơn với các domain cụ thể
CORS(app, resources={r"/*": {
    "origins": ["http://localhost:5000", "https://ba12-14-232-211-211.ngrok-free.app", "https://*.ngrok-free.app", "https://*.ngrok.io", "*"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Access-Control-Allow-Origin", "*"],
    "expose_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
    "supports_credentials": True
}})

# Middleware để đảm bảo CORS headers được áp dụng cho mỗi response
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin', '*')
    if request.method == 'OPTIONS':
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    else:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Origin', origin)
    return response

# Cấu hình
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac', 'm4a'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Đảm bảo thư mục upload tồn tại
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Khởi tạo ứng dụng nhận dạng người nói
speaker_app = SpeakerRecognitionApp()
speaker_app.initialize()

# Hàm kiểm tra định dạng file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route phục vụ file index.html
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# Route phục vụ các file tĩnh
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

# ====================== HEALTH CHECK ======================
@app.route('/health', methods=['GET'])
def health_check():
    """API kiểm tra trạng thái hoạt động của hệ thống"""
    return jsonify({
        'status': 'healthy',
        'message': 'API đang hoạt động',
        'version': '1.0.0'
    }), 200

# ====================== SPEAKER MANAGEMENT ======================
@app.route('/speakers', methods=['GET'])
def get_speakers():
    """Lấy danh sách tất cả người nói"""
    try:
        speakers = speaker_app.list_speakers()
        return jsonify({
            'status': 'success',
            'data': {
                'speakers': speakers,
                'count': len(speakers)
            },
            'message': 'Lấy danh sách người nói thành công'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Lỗi khi lấy danh sách người nói: {str(e)}'
        }), 500

@app.route('/speakers', methods=['POST'])
def create_speaker():
    """Tạo người nói mới"""
    try:
        # Kiểm tra có file nào được gửi lên không
        if 'files[]' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Không có file nào được gửi lên'
            }), 400
        
        # Lấy tên người nói từ form data
        speaker_name = request.form.get('speaker_name')
        if not speaker_name:
            return jsonify({
                'status': 'error',
                'message': 'Tên người nói không được cung cấp'
            }), 400
        
        # Lấy danh sách các file từ request
        files = request.files.getlist('files[]')
        if not files or len(files) == 0:
            return jsonify({
                'status': 'error',
                'message': 'Không có file nào được gửi lên'
            }), 400
        
        # Lưu các file vào thư mục upload
        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                # Tạo tên file ngẫu nhiên để tránh trùng lặp
                original_filename = secure_filename(file.filename)
                extension = original_filename.rsplit('.', 1)[1].lower()
                random_filename = f"{uuid.uuid4().hex}.{extension}"
                
                # Lưu file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], random_filename)
                file.save(file_path)
                saved_files.append(file_path)
        
        if not saved_files:
            return jsonify({
                'status': 'error',
                'message': 'Không có file hợp lệ nào được gửi lên'
            }), 400
        
        # Thêm người nói vào cơ sở dữ liệu
        success = speaker_app.add_speaker(saved_files, speaker_name)
        
        # Trả về kết quả
        if success:
            return jsonify({
                'status': 'success',
                'data': {
                    'speaker_name': speaker_name,
                    'file_count': len(saved_files)
                },
                'message': f'Đã tạo người nói {speaker_name} với {len(saved_files)} file âm thanh'
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': 'Không thể tạo người nói trong cơ sở dữ liệu'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Lỗi khi tạo người nói: {str(e)}'
        }), 500

@app.route('/speakers/<speaker_name>', methods=['DELETE'])
def delete_speaker(speaker_name):
    """Xóa người nói khỏi cơ sở dữ liệu"""
    try:
        success = speaker_app.remove_speaker(speaker_name)
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Đã xóa người nói {speaker_name}'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'Không thể xóa người nói {speaker_name}'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Lỗi khi xóa người nói: {str(e)}'
        }), 500

# ====================== SPEAKER IDENTIFICATION ======================
@app.route('/speakers/identify', methods=['POST'])
def identify_speaker():
    """Nhận dạng người nói từ file âm thanh"""
    try:
        # Kiểm tra có file nào được gửi lên không
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Không có file nào được gửi lên'
            }), 400
        
        file = request.files['file']
        if not file or not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': 'File không hợp lệ'
            }), 400
        
        # Lấy ngưỡng từ request (nếu có)
        threshold = request.form.get('threshold', 0.6)
        try:
            threshold = float(threshold)
        except:
            threshold = 0.6
        
        # Lưu file tạm thời
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        random_filename = f"{uuid.uuid4().hex}.{extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], random_filename)
        file.save(file_path)
        
        # Nhận dạng người nói
        speaker_app.threshold = threshold
        name, similarity, is_known = speaker_app.identify_file(file_path)
        
        # Xóa file tạm
        try:
            os.remove(file_path)
        except:
            pass
        
        # Trả về kết quả
        if name is None:
            return jsonify({
                'status': 'error',
                'message': 'Không thể nhận dạng người nói'
            }), 422
        elif is_known:
            return jsonify({
                'status': 'success',
                'data': {
                    'is_known': True,
                    'speaker_name': name,
                    'similarity': float(similarity),
                    'threshold': threshold
                },
                'message': f'Người nói được nhận dạng: {name} (độ tương đồng: {similarity:.4f})'
            }), 200
        else:
            return jsonify({
                'status': 'success',
                'data': {
                    'is_known': False,
                    'closest_match': name,
                    'similarity': float(similarity),
                    'threshold': threshold
                },
                'message': f'Người nói không xác định. Gần nhất: {name} (độ tương đồng: {similarity:.4f}, thấp hơn ngưỡng {threshold})'
            }), 200
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Lỗi khi nhận dạng người nói: {str(e)}'
        }), 500

# ====================== SIMILARITY CHECK ======================
@app.route('/similarity', methods=['POST'])
def check_similarity():
    """Kiểm tra độ tương đồng giữa hai file âm thanh"""
    try:
        # Kiểm tra có đủ 2 file không
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Cần gửi lên cả 2 file âm thanh'
            }), 400
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if not file1 or not file2 or not allowed_file(file1.filename) or not allowed_file(file2.filename):
            return jsonify({
                'status': 'error',
                'message': 'File không hợp lệ'
            }), 400
        
        # Lưu các file tạm thời
        file1_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.wav")
        file2_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}.wav")
        file1.save(file1_path)
        file2.save(file2_path)
        
        # Khởi tạo ứng dụng nếu cần
        if speaker_app.embedder is None:
            speaker_app.initialize()
        
        # Trích xuất embeddings
        embedding1 = speaker_app.embedder.process_audio(file1_path)
        embedding2 = speaker_app.embedder.process_audio(file2_path)
        
        # Xóa file tạm
        try:
            os.remove(file1_path)
            os.remove(file2_path)
        except:
            pass
        
        if embedding1 is None or embedding2 is None:
            return jsonify({
                'status': 'error',
                'message': 'Không thể trích xuất embedding từ một hoặc cả hai file'
            }), 422
        
        # Tính độ tương đồng
        similarity = speaker_app.database.calculate_cosine_similarity(embedding1, embedding2)
        
        return jsonify({
            'status': 'success',
            'data': {
                'similarity': float(similarity)
            },
            'message': f'Độ tương đồng giữa hai file: {similarity:.4f}'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Lỗi khi kiểm tra độ tương đồng: {str(e)}'
        }), 500

# ====================== SPEECH TO TEXT ======================
@app.route('/speech-to-text/files', methods=['POST'])
def convert_file_to_text():
    """Nhận dạng văn bản từ file âm thanh"""
    try:
        # Kiểm tra có file nào được gửi lên không
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Không có file nào được gửi lên'
            }), 400
        
        file = request.files['file']
        if not file or not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': 'File không hợp lệ'
            }), 400
        
        # Lấy ngôn ngữ (nếu có)
        language = request.form.get('language', 'vi-VN')
        
        # Lưu file tạm thời
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        random_filename = f"{uuid.uuid4().hex}.{extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], random_filename)
        file.save(file_path)
        
        # Khởi tạo speech-to-text
        stt = SpeechToText(language=language)
        
        # Nhận dạng văn bản
        text, success = stt.recognize_from_file(file_path)
        
        # Xóa file tạm
        try:
            os.remove(file_path)
        except:
            pass
        
        # Trả về kết quả
        if success:
            return jsonify({
                'status': 'success',
                'data': {
                    'text': text,
                    'language': language
                },
                'message': 'Đã nhận dạng văn bản thành công'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': text  # Lỗi được trả về trong text
            }), 422
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Lỗi khi nhận dạng văn bản: {str(e)}'
        }), 500

@app.route('/speech-to-text/recordings', methods=['POST'])
def create_recording_and_convert():
    """Ghi âm trực tiếp và nhận dạng văn bản"""
    try:
        # Lấy thông số
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Dữ liệu JSON không hợp lệ'
            }), 400
            
        duration = data.get('duration', 5)
        language = data.get('language', 'vi-VN')
        
        # Kiểm tra duration nằm trong khoảng hợp lệ (1-60 giây)
        if not 1 <= duration <= 60:
            return jsonify({
                'status': 'error',
                'message': 'Thời lượng ghi âm phải từ 1 đến 60 giây'
            }), 400
        
        # Khởi tạo speech-to-text
        stt = SpeechToText(language=language)
        
        # Ghi âm và nhận dạng
        text, success, temp_file = stt.record_and_recognize(record_seconds=duration)
        
        response_data = {
            'text': text,
            'language': language,
            'duration': duration
        }
        
        # Trích xuất embedding từ file âm thanh (nếu cần)
        embedding = None
        if success and data.get('extract_embedding', False):
            if speaker_app.embedder is None:
                speaker_app.initialize()
            embedding = speaker_app.embedder.process_audio(temp_file)
            
            # Nếu cần lưu embedding vào DB
            if data.get('speaker_name') and embedding is not None:
                speaker_name = data['speaker_name']
                speaker_app.database.add_embedding(speaker_name, embedding)
                speaker_app.database.build_index()
                speaker_app.database.save(speaker_app.database_dir)
                response_data['embedding_saved'] = True
                response_data['speaker_name'] = speaker_name
        
        # Nếu có embedding và cần nhận dạng người nói
        if embedding is not None and data.get('identify_speaker', False):
            threshold = data.get('threshold', 0.6)
            name, similarity, is_known = speaker_app.database.identify_speaker(embedding, threshold)
            response_data['speaker_identification'] = {
                'is_known': is_known,
                'speaker_name': name,
                'similarity': float(similarity) if similarity is not None else None,
                'threshold': threshold
            }
        
        # Xóa file tạm
        try:
            os.remove(temp_file)
        except:
            pass
        
        # Trả về kết quả
        if success:
            return jsonify({
                'status': 'success',
                'data': response_data,
                'message': 'Đã nhận dạng văn bản thành công'
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': text  # Lỗi được trả về trong text
            }), 422
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Lỗi khi ghi âm và nhận dạng: {str(e)}'
        }), 500

# ====================== ERROR HANDLERS ======================
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint không tồn tại'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'status': 'error',
        'message': 'Phương thức HTTP không được hỗ trợ'
    }), 405

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'status': 'error',
        'message': 'File quá lớn (tối đa 16MB)'
    }), 413

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Lỗi server nội bộ'
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)