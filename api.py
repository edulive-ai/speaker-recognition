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
CORS(app)  # Cho phép Cross-Origin Resource Sharing

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

@app.route('/api/health', methods=['GET'])
def health_check():
    """API kiểm tra trạng thái hoạt động"""
    return jsonify({'status': 'ok', 'message': 'API đang hoạt động'})

@app.route('/api/speakers', methods=['GET'])
def list_speakers():
    """API lấy danh sách người nói"""
    speakers = speaker_app.list_speakers()
    return jsonify({'speakers': speakers})

@app.route('/api/speakers/<speaker_name>', methods=['DELETE'])
def remove_speaker(speaker_name):
    """API xóa người nói khỏi cơ sở dữ liệu"""
    success = speaker_app.remove_speaker(speaker_name)
    if success:
        return jsonify({'success': True, 'message': f'Đã xóa người nói {speaker_name}'})
    return jsonify({'success': False, 'message': f'Không thể xóa người nói {speaker_name}'})

@app.route('/api/speakers', methods=['POST'])
def add_speaker():
    """API thêm người nói mới"""
    # Kiểm tra có file nào được gửi lên không
    if 'files[]' not in request.files:
        return jsonify({'success': False, 'message': 'Không có file nào được gửi lên'})
    
    # Lấy tên người nói từ form data
    speaker_name = request.form.get('speaker_name')
    if not speaker_name:
        return jsonify({'success': False, 'message': 'Tên người nói không được cung cấp'})
    
    # Lấy danh sách các file từ request
    files = request.files.getlist('files[]')
    if not files or len(files) == 0:
        return jsonify({'success': False, 'message': 'Không có file nào được gửi lên'})
    
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
        return jsonify({'success': False, 'message': 'Không có file hợp lệ nào được gửi lên'})
    
    # Thêm người nói vào cơ sở dữ liệu
    success = speaker_app.add_speaker(saved_files, speaker_name)
    
    # Trả về kết quả
    if success:
        return jsonify({
            'success': True, 
            'message': f'Đã thêm người nói {speaker_name} với {len(saved_files)} file âm thanh',
            'speaker_name': speaker_name,
            'file_count': len(saved_files)
        })
    else:
        return jsonify({'success': False, 'message': 'Không thể thêm người nói vào cơ sở dữ liệu'})

@app.route('/api/identify', methods=['POST'])
def identify_speaker():
    """API nhận dạng người nói từ file âm thanh"""
    # Kiểm tra có file nào được gửi lên không
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Không có file nào được gửi lên'})
    
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'File không hợp lệ'})
    
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
    
    # Trả về kết quả
    if name is None:
        return jsonify({
            'success': False,
            'message': 'Không thể nhận dạng người nói'
        })
    elif is_known:
        return jsonify({
            'success': True,
            'is_known': True,
            'speaker_name': name,
            'similarity': float(similarity),
            'message': f'Người nói được nhận dạng: {name} (độ tương đồng: {similarity:.4f})'
        })
    else:
        return jsonify({
            'success': True,
            'is_known': False,
            'closest_match': name,
            'similarity': float(similarity),
            'threshold': threshold,
            'message': f'Người nói không xác định. Gần nhất: {name} (độ tương đồng: {similarity:.4f}, thấp hơn ngưỡng {threshold})'
        })

@app.route('/api/check-similarity', methods=['POST'])
def check_similarity():
    """API kiểm tra độ tương đồng giữa hai file âm thanh"""
    # Kiểm tra có đủ 2 file không
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({'success': False, 'message': 'Cần gửi lên cả 2 file âm thanh'})
    
    file1 = request.files['file1']
    file2 = request.files['file2']
    
    if not file1 or not file2 or not allowed_file(file1.filename) or not allowed_file(file2.filename):
        return jsonify({'success': False, 'message': 'File không hợp lệ'})
    
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
    
    if embedding1 is None or embedding2 is None:
        return jsonify({
            'success': False,
            'message': 'Không thể trích xuất embedding từ một hoặc cả hai file'
        })
    
    # Tính độ tương đồng
    similarity = speaker_app.database.calculate_cosine_similarity(embedding1, embedding2)
    
    return jsonify({
        'success': True,
        'similarity': float(similarity),
        'message': f'Độ tương đồng giữa hai file: {similarity:.4f}'
    })

@app.route('/api/speech-to-text/file', methods=['POST'])
def speech_to_text_file():
    """API nhận dạng văn bản từ file âm thanh"""
    # Kiểm tra có file nào được gửi lên không
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Không có file nào được gửi lên'})
    
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'File không hợp lệ'})
    
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
    
    # Trả về kết quả
    if success:
        return jsonify({
            'success': True,
            'text': text,
            'language': language,
            'message': 'Đã nhận dạng văn bản thành công'
        })
    else:
        return jsonify({
            'success': False,
            'message': text  # Lỗi được trả về trong text
        })

@app.route('/api/speech-to-text/record', methods=['POST'])
def speech_to_text_record():
    """API ghi âm trực tiếp và nhận dạng văn bản"""
    try:
        # Lấy thông số
        data = request.get_json()
        duration = data.get('duration', 5)
        language = data.get('language', 'vi-VN')
        
        # Kiểm tra duration nằm trong khoảng hợp lệ (1-60 giây)
        if not 1 <= duration <= 60:
            return jsonify({'success': False, 'message': 'Thời lượng ghi âm phải từ 1 đến 60 giây'})
        
        # Khởi tạo speech-to-text
        stt = SpeechToText(language=language)
        
        # Ghi âm và nhận dạng
        text, success, temp_file = stt.record_and_recognize(record_seconds=duration)
        
        # Trích xuất embedding từ file âm thanh (nếu cần)
        embedding = None
        if success and 'extract_embedding' in data and data['extract_embedding']:
            if speaker_app.embedder is None:
                speaker_app.initialize()
            embedding = speaker_app.embedder.process_audio(temp_file)
            
            # Nếu cần lưu embedding vào DB
            if 'speaker_name' in data and data['speaker_name'] and embedding is not None:
                speaker_name = data['speaker_name']
                speaker_app.database.add_embedding(speaker_name, embedding)
                speaker_app.database.build_index()
                speaker_app.database.save(speaker_app.database_dir)
        
        # Xóa file tạm
        try:
            os.remove(temp_file)
        except:
            pass
        
        # Trả về kết quả
        if success:
            response = {
                'success': True,
                'text': text,
                'language': language,
                'message': 'Đã nhận dạng văn bản thành công'
            }
            
            # Nếu đã trích xuất embedding
            if embedding is not None:
                # Nếu có speaker_name, trả về thông tin đã lưu
                if 'speaker_name' in data and data['speaker_name']:
                    response['embedding_saved'] = True
                    response['speaker_name'] = data['speaker_name']
                
                # Nếu cần nhận dạng người nói
                if 'identify_speaker' in data and data['identify_speaker']:
                    threshold = data.get('threshold', 0.6)
                    name, similarity, is_known = speaker_app.database.identify_speaker(embedding, threshold)
                    response['speaker_identification'] = {
                        'is_known': is_known,
                        'speaker_name': name,
                        'similarity': float(similarity) if similarity is not None else None,
                        'threshold': threshold
                    }
            
            return jsonify(response)
        else:
            return jsonify({
                'success': False,
                'message': text  # Lỗi được trả về trong text
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 