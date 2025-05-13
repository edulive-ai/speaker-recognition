// Cấu hình API
const API_BASE_URL = 'http://localhost:5000/api';

// Các elements DOM
const navLinks = document.querySelectorAll('nav a');
const pages = document.querySelectorAll('.page');
const identifyUploadArea = document.getElementById('identify-upload-area');
const identifyFileInput = document.getElementById('identify-file');
const identifyBtn = document.getElementById('identify-btn');
const resultArea = document.getElementById('identify-result');
const resultContent = document.getElementById('result-content');
const thresholdInput = document.getElementById('threshold');
const thresholdValue = document.getElementById('threshold-value');
const speakerList = document.getElementById('speaker-list');
const speakerNameInput = document.getElementById('speaker-name');
const addUploadArea = document.getElementById('add-upload-area');
const addFilesInput = document.getElementById('add-files');
const fileList = document.getElementById('file-list');
const selectedFilesList = document.getElementById('selected-files');
const addSpeakerBtn = document.getElementById('add-speaker-btn');
const addResult = document.getElementById('add-result');
const addResultContent = document.getElementById('add-result-content');
const compareUploadArea1 = document.getElementById('compare-upload-area-1');
const compareUploadArea2 = document.getElementById('compare-upload-area-2');
const compareFileInput1 = document.getElementById('compare-file-1');
const compareFileInput2 = document.getElementById('compare-file-2');
const file1Name = document.getElementById('file1-name');
const file2Name = document.getElementById('file2-name');
const compareBtn = document.getElementById('compare-btn');
const compareResult = document.getElementById('compare-result');
const compareResultContent = document.getElementById('compare-result-content');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingMessage = document.getElementById('loading-message');

// Elements cho speech-to-text
const sttUploadArea = document.getElementById('stt-upload-area');
const sttFileInput = document.getElementById('stt-file');
const sttLanguage = document.getElementById('language');
const sttFromFileBtn = document.getElementById('stt-from-file-btn');
const sttFileResult = document.getElementById('stt-file-result');
const sttFileContent = document.getElementById('stt-file-content');
const recordDuration = document.getElementById('record-duration');
const recordLanguage = document.getElementById('record-language');
const extractEmbedding = document.getElementById('extract-embedding');
const speakerOptions = document.getElementById('speaker-options');
const identifySpeakerOption = document.getElementById('identify-speaker-option');
const saveEmbeddingOption = document.getElementById('save-embedding-option');
const saveSpeakerNameGroup = document.getElementById('save-speaker-name-group');
const saveSpeakerName = document.getElementById('save-speaker-name');
const recordBtn = document.getElementById('record-btn');
const sttRecordResult = document.getElementById('stt-record-result');
const sttRecordContent = document.getElementById('stt-record-content');

// Biến lưu trữ dữ liệu
let identifyFile = null;
let addFiles = [];
let compareFile1 = null;
let compareFile2 = null;
let sttFile = null;
let isRecording = false;

// Xử lý điều hướng
navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Xóa active class từ tất cả nav links
        navLinks.forEach(item => item.classList.remove('active'));
        
        // Thêm active class vào link được click
        this.classList.add('active');
        
        // Hiển thị trang tương ứng
        const pageId = this.getAttribute('data-page');
        pages.forEach(page => {
            page.classList.remove('active');
            if (page.id === pageId) {
                page.classList.add('active');
                
                // Nếu đang hiển thị trang quản lý, tải danh sách người nói
                if (pageId === 'manage') {
                    loadSpeakerList();
                }
            }
        });
    });
});

// Xử lý thay đổi ngưỡng nhận dạng
thresholdInput.addEventListener('input', function() {
    thresholdValue.textContent = this.value;
});

// Xử lý upload file nhận dạng
identifyUploadArea.addEventListener('click', function() {
    identifyFileInput.click();
});

identifyUploadArea.addEventListener('dragover', function(e) {
    e.preventDefault();
    this.classList.add('active');
});

identifyUploadArea.addEventListener('dragleave', function() {
    this.classList.remove('active');
});

identifyUploadArea.addEventListener('drop', function(e) {
    e.preventDefault();
    this.classList.remove('active');
    
    if (e.dataTransfer.files.length > 0) {
        handleIdentifyFile(e.dataTransfer.files[0]);
    }
});

identifyFileInput.addEventListener('change', function() {
    if (this.files.length > 0) {
        handleIdentifyFile(this.files[0]);
    }
});

function handleIdentifyFile(file) {
    const allowedTypes = ['audio/wav', 'audio/mpeg', 'audio/ogg', 'audio/flac', 'audio/mp4'];
    const fileType = file.type;
    
    if (!allowedTypes.includes(fileType) && !file.name.match(/\.(wav|mp3|ogg|flac|m4a)$/i)) {
        alert('Vui lòng chọn file âm thanh hợp lệ (WAV, MP3, OGG, FLAC, M4A)');
        return;
    }
    
    identifyFile = file;
    identifyUploadArea.innerHTML = `
        <i class="fas fa-file-audio"></i>
        <p>${file.name}</p>
        <p class="small">${formatFileSize(file.size)}</p>
    `;
    identifyBtn.disabled = false;
}

// Xử lý nhận dạng người nói
identifyBtn.addEventListener('click', function() {
    if (!identifyFile) return;
    
    const threshold = thresholdInput.value;
    
    // Hiển thị loading
    showLoading('Đang nhận dạng người nói...');
    
    // Tạo form data
    const formData = new FormData();
    formData.append('file', identifyFile);
    formData.append('threshold', threshold);
    
    // Gửi request đến API
    fetch(`${API_BASE_URL}/identify`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        // Hiển thị kết quả
        resultArea.classList.remove('hidden');
        
        if (!data.success) {
            resultContent.innerHTML = `<p class="error-message">${data.message}</p>`;
            return;
        }
        
        if (data.is_known) {
            resultContent.innerHTML = `
                <p class="success-message">${data.message}</p>
                <div class="similarity-meter">
                    <div class="similarity-value" style="width: ${data.similarity * 100}%"></div>
                </div>
                <p class="similarity-label">Độ tương đồng: ${(data.similarity * 100).toFixed(2)}%</p>
            `;
        } else {
            resultContent.innerHTML = `
                <p class="warning-message">${data.message}</p>
                <div class="similarity-meter">
                    <div class="similarity-value" style="width: ${data.similarity * 100}%"></div>
                </div>
                <p class="similarity-label">Độ tương đồng: ${(data.similarity * 100).toFixed(2)}%</p>
                <p>Ngưỡng nhận dạng hiện tại: ${data.threshold}</p>
            `;
        }
    })
    .catch(error => {
        hideLoading();
        resultArea.classList.remove('hidden');
        resultContent.innerHTML = `<p class="error-message">Đã xảy ra lỗi: ${error.message}</p>`;
    });
});

// Xử lý upload files thêm người nói
addUploadArea.addEventListener('click', function() {
    addFilesInput.click();
});

addUploadArea.addEventListener('dragover', function(e) {
    e.preventDefault();
    this.classList.add('active');
});

addUploadArea.addEventListener('dragleave', function() {
    this.classList.remove('active');
});

addUploadArea.addEventListener('drop', function(e) {
    e.preventDefault();
    this.classList.remove('active');
    
    if (e.dataTransfer.files.length > 0) {
        handleAddFiles(e.dataTransfer.files);
    }
});

addFilesInput.addEventListener('change', function() {
    if (this.files.length > 0) {
        handleAddFiles(this.files);
    }
});

function handleAddFiles(files) {
    const allowedTypes = ['audio/wav', 'audio/mpeg', 'audio/ogg', 'audio/flac', 'audio/mp4'];
    
    Array.from(files).forEach(file => {
        const fileType = file.type;
        
        if (allowedTypes.includes(fileType) || file.name.match(/\.(wav|mp3|ogg|flac|m4a)$/i)) {
            addFiles.push(file);
        }
    });
    
    updateFileList();
    updateAddButtonState();
}

function updateFileList() {
    if (addFiles.length === 0) {
        fileList.classList.add('hidden');
        return;
    }
    
    fileList.classList.remove('hidden');
    selectedFilesList.innerHTML = '';
    
    addFiles.forEach((file, index) => {
        const li = document.createElement('li');
        li.innerHTML = `
            <span>${file.name} (${formatFileSize(file.size)})</span>
            <button class="delete-btn" data-index="${index}">
                <i class="fas fa-times"></i>
            </button>
        `;
        selectedFilesList.appendChild(li);
    });
    
    // Thêm event listeners cho các nút xóa
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const index = parseInt(this.getAttribute('data-index'));
            addFiles.splice(index, 1);
            updateFileList();
            updateAddButtonState();
        });
    });
}

function updateAddButtonState() {
    addSpeakerBtn.disabled = !(speakerNameInput.value.trim() && addFiles.length > 0);
}

// Kiểm tra tên người nói
speakerNameInput.addEventListener('input', updateAddButtonState);

// Xử lý thêm người nói mới
addSpeakerBtn.addEventListener('click', function() {
    const speakerName = speakerNameInput.value.trim();
    
    if (!speakerName || addFiles.length === 0) return;
    
    // Hiển thị loading
    showLoading('Đang thêm người nói mới...');
    
    // Tạo form data
    const formData = new FormData();
    formData.append('speaker_name', speakerName);
    
    addFiles.forEach(file => {
        formData.append('files[]', file);
    });
    
    // Gửi request đến API
    fetch(`${API_BASE_URL}/speakers`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        // Hiển thị kết quả
        addResult.classList.remove('hidden');
        
        if (data.success) {
            addResultContent.innerHTML = `<p class="success-message">${data.message}</p>`;
            
            // Xóa dữ liệu đã nhập
            speakerNameInput.value = '';
            addFiles = [];
            updateFileList();
            updateAddButtonState();
            
            // Tải lại danh sách người nói
            loadSpeakerList();
        } else {
            addResultContent.innerHTML = `<p class="error-message">${data.message}</p>`;
        }
    })
    .catch(error => {
        hideLoading();
        addResult.classList.remove('hidden');
        addResultContent.innerHTML = `<p class="error-message">Đã xảy ra lỗi: ${error.message}</p>`;
    });
});

// Xử lý tải danh sách người nói
function loadSpeakerList() {
    // Hiển thị loading
    speakerList.innerHTML = '<p>Đang tải danh sách người nói...</p>';
    
    // Gửi request đến API
    fetch(`${API_BASE_URL}/speakers`)
    .then(response => response.json())
    .then(data => {
        if (!data.speakers || data.speakers.length === 0) {
            speakerList.innerHTML = '<p>Chưa có người nói nào trong cơ sở dữ liệu.</p>';
            return;
        }
        
        speakerList.innerHTML = '';
        data.speakers.forEach(speaker => {
            const div = document.createElement('div');
            div.className = 'speaker-item';
            div.innerHTML = `
                <span>${speaker}</span>
                <button class="delete-btn" data-speaker="${speaker}">
                    <i class="fas fa-trash"></i>
                </button>
            `;
            speakerList.appendChild(div);
        });
        
        // Thêm event listeners cho các nút xóa
        document.querySelectorAll('.speaker-item .delete-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const speaker = this.getAttribute('data-speaker');
                if (confirm(`Bạn có chắc chắn muốn xóa người nói "${speaker}"?`)) {
                    deleteSpeaker(speaker);
                }
            });
        });
    })
    .catch(error => {
        speakerList.innerHTML = `<p class="error-message">Đã xảy ra lỗi khi tải danh sách: ${error.message}</p>`;
    });
}

// Xử lý xóa người nói
function deleteSpeaker(speakerName) {
    // Hiển thị loading
    showLoading(`Đang xóa "${speakerName}"...`);
    
    // Gửi request đến API
    fetch(`${API_BASE_URL}/speakers/${encodeURIComponent(speakerName)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            // Tải lại danh sách người nói
            loadSpeakerList();
            
            // Hiển thị thông báo
            alert(`Đã xóa người nói "${speakerName}"`);
        } else {
            alert(`Lỗi: ${data.message}`);
        }
    })
    .catch(error => {
        hideLoading();
        alert(`Đã xảy ra lỗi: ${error.message}`);
    });
}

// Xử lý upload file so sánh
compareUploadArea1.addEventListener('click', function() {
    compareFileInput1.click();
});

compareUploadArea1.addEventListener('dragover', function(e) {
    e.preventDefault();
    this.classList.add('active');
});

compareUploadArea1.addEventListener('dragleave', function() {
    this.classList.remove('active');
});

compareUploadArea1.addEventListener('drop', function(e) {
    e.preventDefault();
    this.classList.remove('active');
    
    if (e.dataTransfer.files.length > 0) {
        handleCompareFile1(e.dataTransfer.files[0]);
    }
});

compareFileInput1.addEventListener('change', function() {
    if (this.files.length > 0) {
        handleCompareFile1(this.files[0]);
    }
});

function handleCompareFile1(file) {
    const allowedTypes = ['audio/wav', 'audio/mpeg', 'audio/ogg', 'audio/flac', 'audio/mp4'];
    const fileType = file.type;
    
    if (!allowedTypes.includes(fileType) && !file.name.match(/\.(wav|mp3|ogg|flac|m4a)$/i)) {
        alert('Vui lòng chọn file âm thanh hợp lệ (WAV, MP3, OGG, FLAC, M4A)');
        return;
    }
    
    compareFile1 = file;
    compareUploadArea1.innerHTML = `
        <i class="fas fa-file-audio"></i>
        <p>Đã chọn file</p>
    `;
    file1Name.textContent = file.name;
    
    updateCompareButtonState();
}

compareUploadArea2.addEventListener('click', function() {
    compareFileInput2.click();
});

compareUploadArea2.addEventListener('dragover', function(e) {
    e.preventDefault();
    this.classList.add('active');
});

compareUploadArea2.addEventListener('dragleave', function() {
    this.classList.remove('active');
});

compareUploadArea2.addEventListener('drop', function(e) {
    e.preventDefault();
    this.classList.remove('active');
    
    if (e.dataTransfer.files.length > 0) {
        handleCompareFile2(e.dataTransfer.files[0]);
    }
});

compareFileInput2.addEventListener('change', function() {
    if (this.files.length > 0) {
        handleCompareFile2(this.files[0]);
    }
});

function handleCompareFile2(file) {
    const allowedTypes = ['audio/wav', 'audio/mpeg', 'audio/ogg', 'audio/flac', 'audio/mp4'];
    const fileType = file.type;
    
    if (!allowedTypes.includes(fileType) && !file.name.match(/\.(wav|mp3|ogg|flac|m4a)$/i)) {
        alert('Vui lòng chọn file âm thanh hợp lệ (WAV, MP3, OGG, FLAC, M4A)');
        return;
    }
    
    compareFile2 = file;
    compareUploadArea2.innerHTML = `
        <i class="fas fa-file-audio"></i>
        <p>Đã chọn file</p>
    `;
    file2Name.textContent = file.name;
    
    updateCompareButtonState();
}

function updateCompareButtonState() {
    compareBtn.disabled = !(compareFile1 && compareFile2);
}

// Xử lý so sánh file
compareBtn.addEventListener('click', function() {
    if (!compareFile1 || !compareFile2) return;
    
    // Hiển thị loading
    showLoading('Đang so sánh độ tương đồng...');
    
    // Tạo form data
    const formData = new FormData();
    formData.append('file1', compareFile1);
    formData.append('file2', compareFile2);
    
    // Gửi request đến API
    fetch(`${API_BASE_URL}/check-similarity`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        // Hiển thị kết quả
        compareResult.classList.remove('hidden');
        
        if (!data.success) {
            compareResultContent.innerHTML = `<p class="error-message">${data.message}</p>`;
            return;
        }
        
        // Xác định mức độ tương đồng
        let similarityClass = '';
        let message = '';
        
        if (data.similarity >= 0.8) {
            similarityClass = 'success-message';
            message = 'Rất có thể là cùng một người nói';
        } else if (data.similarity >= 0.6) {
            similarityClass = 'warning-message';
            message = 'Có thể là cùng một người nói';
        } else {
            similarityClass = 'error-message';
            message = 'Có thể là hai người nói khác nhau';
        }
        
        compareResultContent.innerHTML = `
            <p class="${similarityClass}">Độ tương đồng: ${(data.similarity * 100).toFixed(2)}% - ${message}</p>
            <div class="similarity-meter">
                <div class="similarity-value" style="width: ${data.similarity * 100}%"></div>
            </div>
            <p>File 1: ${compareFile1.name}</p>
            <p>File 2: ${compareFile2.name}</p>
        `;
    })
    .catch(error => {
        hideLoading();
        compareResult.classList.remove('hidden');
        compareResultContent.innerHTML = `<p class="error-message">Đã xảy ra lỗi: ${error.message}</p>`;
    });
});

// Xử lý upload file cho speech-to-text
sttUploadArea.addEventListener('click', function() {
    sttFileInput.click();
});

sttUploadArea.addEventListener('dragover', function(e) {
    e.preventDefault();
    this.classList.add('active');
});

sttUploadArea.addEventListener('dragleave', function() {
    this.classList.remove('active');
});

sttUploadArea.addEventListener('drop', function(e) {
    e.preventDefault();
    this.classList.remove('active');
    
    if (e.dataTransfer.files.length > 0) {
        handleSTTFile(e.dataTransfer.files[0]);
    }
});

sttFileInput.addEventListener('change', function() {
    if (this.files.length > 0) {
        handleSTTFile(this.files[0]);
    }
});

function handleSTTFile(file) {
    const allowedTypes = ['audio/wav', 'audio/mpeg', 'audio/ogg', 'audio/flac', 'audio/mp4'];
    const fileType = file.type;
    
    if (!allowedTypes.includes(fileType) && !file.name.match(/\.(wav|mp3|ogg|flac|m4a)$/i)) {
        alert('Vui lòng chọn file âm thanh hợp lệ (WAV, MP3, OGG, FLAC, M4A)');
        return;
    }
    
    sttFile = file;
    sttUploadArea.innerHTML = `
        <i class="fas fa-file-audio"></i>
        <p>${file.name}</p>
        <p class="small">${formatFileSize(file.size)}</p>
    `;
    sttFromFileBtn.disabled = false;
}

// Xử lý chuyển đổi âm thanh thành văn bản từ file
sttFromFileBtn.addEventListener('click', function() {
    if (!sttFile) return;
    
    const language = sttLanguage.value;
    
    // Hiển thị loading
    showLoading('Đang chuyển đổi âm thanh thành văn bản...');
    
    // Tạo form data
    const formData = new FormData();
    formData.append('file', sttFile);
    formData.append('language', language);
    
    // Gửi request đến API
    fetch(`${API_BASE_URL}/speech-to-text/file`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        // Hiển thị kết quả
        sttFileResult.classList.remove('hidden');
        
        if (!data.success) {
            sttFileContent.innerHTML = `<p class="error-message">${data.message}</p>`;
            return;
        }
        
        sttFileContent.innerHTML = `
            <p class="success-message">Đã nhận dạng thành công!</p>
            <div class="text-result">
                <p><strong>Văn bản:</strong></p>
                <p>${data.text}</p>
            </div>
            <p><small>Ngôn ngữ: ${data.language}</small></p>
        `;
    })
    .catch(error => {
        hideLoading();
        sttFileResult.classList.remove('hidden');
        sttFileContent.innerHTML = `<p class="error-message">Đã xảy ra lỗi: ${error.message}</p>`;
    });
});

// Xử lý checkbox cho trích xuất đặc trưng
extractEmbedding.addEventListener('change', function() {
    if (this.checked) {
        speakerOptions.classList.remove('hidden');
    } else {
        speakerOptions.classList.add('hidden');
        saveSpeakerNameGroup.classList.add('hidden');
        saveEmbeddingOption.checked = false;
        identifySpeakerOption.checked = false;
    }
});

// Xử lý checkbox cho lưu đặc trưng
saveEmbeddingOption.addEventListener('change', function() {
    if (this.checked) {
        saveSpeakerNameGroup.classList.remove('hidden');
    } else {
        saveSpeakerNameGroup.classList.add('hidden');
    }
});

// Xử lý nút ghi âm
recordBtn.addEventListener('click', function() {
    if (isRecording) return;
    
    const duration = parseInt(recordDuration.value) || 5;
    const language = recordLanguage.value;
    const shouldExtractEmbedding = extractEmbedding.checked;
    const shouldIdentifySpeaker = shouldExtractEmbedding && identifySpeakerOption.checked;
    const shouldSaveEmbedding = shouldExtractEmbedding && saveEmbeddingOption.checked;
    const speakerName = shouldSaveEmbedding ? saveSpeakerName.value : '';
    
    // Validate
    if (shouldSaveEmbedding && !speakerName.trim()) {
        alert('Vui lòng nhập tên người nói nếu bạn muốn lưu đặc trưng.');
        return;
    }
    
    // Hiển thị trạng thái ghi âm
    isRecording = true;
    recordBtn.disabled = true;
    recordBtn.classList.add('recording');
    recordBtn.textContent = 'Đang ghi âm...';
    showLoading(`Đang ghi âm... (${duration} giây)`);
    
    // Đếm ngược
    let remainingTime = duration;
    const countdownInterval = setInterval(() => {
        remainingTime--;
        if (remainingTime > 0) {
            loadingMessage.textContent = `Đang ghi âm... (${remainingTime} giây)`;
        } else {
            clearInterval(countdownInterval);
            loadingMessage.textContent = 'Đang xử lý...';
        }
    }, 1000);
    
    // Chuẩn bị dữ liệu request
    const requestData = {
        duration: duration,
        language: language,
        extract_embedding: shouldExtractEmbedding,
        identify_speaker: shouldIdentifySpeaker,
        threshold: 0.6
    };
    
    if (shouldSaveEmbedding) {
        requestData.speaker_name = speakerName;
    }
    
    // Gửi request đến API sau khi đếm ngược hoàn tất
    setTimeout(() => {
        // Gửi request đến API
        fetch(`${API_BASE_URL}/speech-to-text/record`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            // Ẩn loading và reset UI
            hideLoading();
            isRecording = false;
            recordBtn.disabled = false;
            recordBtn.classList.remove('recording');
            recordBtn.textContent = 'Bắt đầu ghi âm';
            clearInterval(countdownInterval);
            
            // Hiển thị kết quả
            sttRecordResult.classList.remove('hidden');
            
            if (!data.success) {
                sttRecordContent.innerHTML = `<p class="error-message">${data.message}</p>`;
                return;
            }
            
            let resultHTML = `
                <p class="success-message">Đã nhận dạng thành công!</p>
                <div class="text-result">
                    <p><strong>Văn bản:</strong></p>
                    <p>${data.text}</p>
                </div>
                <p><small>Ngôn ngữ: ${data.language}</small></p>
            `;
            
            // Nếu có thông tin nhận dạng người nói
            if (data.speaker_identification) {
                const speakerInfo = data.speaker_identification;
                if (speakerInfo.is_known) {
                    resultHTML += `
                        <div class="speaker-info">
                            <p><strong>Nhận dạng người nói:</strong> ${speakerInfo.speaker_name}</p>
                            <div class="similarity-meter">
                                <div class="similarity-value" style="width: ${speakerInfo.similarity * 100}%"></div>
                            </div>
                            <p class="similarity-label">Độ tương đồng: ${(speakerInfo.similarity * 100).toFixed(2)}%</p>
                        </div>
                    `;
                } else {
                    resultHTML += `
                        <div class="speaker-info">
                            <p><strong>Nhận dạng người nói:</strong> Không xác định</p>
                            <p>Người nói gần nhất: ${speakerInfo.speaker_name}</p>
                            <div class="similarity-meter">
                                <div class="similarity-value" style="width: ${speakerInfo.similarity * 100}%"></div>
                            </div>
                            <p class="similarity-label">Độ tương đồng: ${(speakerInfo.similarity * 100).toFixed(2)}% (thấp hơn ngưỡng ${speakerInfo.threshold})</p>
                        </div>
                    `;
                }
            }
            
            // Nếu có thông tin lưu embedding
            if (data.embedding_saved) {
                resultHTML += `<p class="success-message">Đã lưu đặc trưng giọng nói cho ${data.speaker_name}</p>`;
            }
            
            sttRecordContent.innerHTML = resultHTML;
        })
        .catch(error => {
            hideLoading();
            isRecording = false;
            recordBtn.disabled = false;
            recordBtn.classList.remove('recording');
            recordBtn.textContent = 'Bắt đầu ghi âm';
            clearInterval(countdownInterval);
            
            sttRecordResult.classList.remove('hidden');
            sttRecordContent.innerHTML = `<p class="error-message">Đã xảy ra lỗi: ${error.message}</p>`;
        });
    }, duration * 1000); // Đặt timeout bằng thời gian ghi âm
});

// Helper functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showLoading(message) {
    loadingMessage.textContent = message || 'Đang xử lý...';
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

// Kiểm tra trạng thái API khi tải trang
fetch(`${API_BASE_URL}/health`)
    .then(response => response.json())
    .then(data => {
        console.log('API status:', data.status);
    })
    .catch(error => {
        console.error('API connection error:', error);
        alert('Không thể kết nối đến API. Vui lòng đảm bảo server đang chạy.');
    });

// Tạo thư mục cần thiết
function createDirectories() {
    const dirs = ['static/css', 'static/js', 'uploads'];
    dirs.forEach(dir => {
        try {
            // Do nothing, directories will be created when files are saved
        } catch (error) {
            console.error(`Error creating directory ${dir}:`, error);
        }
    });
} 