// emotions.js - Quản lý Video Cảm xúc

import { API_URL, $, openModal, closeModal, showNotification } from './admin.js';

const EMOTION_VIDEOS = [
    { id: 'vui', name: 'Vui vẻ', emoji: '😊', path: '../../assets/videos/happy.mp4' },
    { id: 'buon', name: 'Buồn bã', emoji: '😢', path: '../../assets/videos/sad.mp4' },
    { id: 'tuc', name: 'Tức giận', emoji: '😠', path: '../../assets/videos/angry.mp4' },
    { id: 'so', name: 'Sợ hãi', emoji: '😨', path: '../../assets/videos/fear.mp4' },
    { id: 'ngac', name: 'Ngạc nhiên', emoji: '😲', path: '../../assets/videos/surprise.mp4' },
    { id: 'ghe', name: 'Ghê tởm', emoji: '🤢', path: '../../assets/videos/disgust.mp4' }
];

let currentVideoFile = null;
let editingVideoId = null;

function loadEmotionVideos() {
    renderVideoGrid();
}

function renderVideoGrid() {
    const grid = $('emotions-grid');
    
    grid.innerHTML = EMOTION_VIDEOS.map(video => `
        <div class="video-card" data-video-id="${video.id}">
            <div class="video-preview">
                <video src="${video.path}" controls style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;">
                    Video không tải được
                </video>
            </div>
            <div class="video-info">
                <h3>${video.emoji} ${video.name}</h3>
                <p style="font-size: 12px; color: #7f8c8d; margin: 5px 0;">
                    📹 ${video.path}
                </p>
            </div>
            <div class="actions" style="margin-top: 10px;">
                <button class="btn btn-warning" onclick="window.replaceVideo('${video.id}')">
                    🔄 Thay thế video
                </button>
                <button class="btn btn-danger" onclick="window.deleteVideo('${video.id}')">
                    🗑️ Xóa video
                </button>
            </div>
        </div>
    `).join('');
}

function setupEmotionEvents() {
    $('video-file-input')?.addEventListener('change', (e) => {
        const file = e.target.files[0];
        
        if (!file) {
            currentVideoFile = null;
            $('video-preview-container').style.display = 'none';
            return;
        }

        if (!file.type.startsWith('video/')) {
            alert('❌ Vui lòng chọn file video!');
            e.target.value = '';
            return;
        }

        if (file.size > 50 * 1024 * 1024) {
            alert('❌ Video quá lớn! Tối đa 50MB.');
            e.target.value = '';
            return;
        }
        
        currentVideoFile = file;

        const reader = new FileReader();
        reader.onload = (e) => {
            $('video-preview-player').src = e.target.result;
            $('video-preview-container').style.display = 'block';
            $('video-file-name').textContent = file.name;
            $('video-file-size').textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
        };
        reader.readAsDataURL(file);
    });

    $('video-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!currentVideoFile) {
            alert('❌ Vui lòng chọn video!');
            return;
        }
        
        const video = EMOTION_VIDEOS.find(v => v.id === editingVideoId);
        if (!video) return;
        
        const formData = new FormData();
        formData.append('video_file', currentVideoFile);
        formData.append('emotion_id', video.id);
        formData.append('emotion_name', video.name);
        formData.append('old_path', video.path);
        
        const uploadBtn = e.target.querySelector('button[type="submit"]');
        uploadBtn.disabled = true;
        uploadBtn.textContent = '⏳ Đang tải lên...';
        
        try {
            const res = await fetch(`${API_URL}/emotions/upload-video`, {
                method: 'POST',
                body: formData
            });
            
            const data = await res.json();
            
            if (!res.ok || data.status !== 'success') {
                throw new Error(data.message || 'Lỗi upload video');
            }
            
            showNotification(`✅ Đã thay thế video "${video.name}"!`, 'success');
            closeModal('video-modal');
            loadEmotionVideos();
            
        } catch (err) {
            showNotification(`❌ ${err.message}`, 'error');
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.textContent = '💾 Lưu video';
        }
    });

    $('cancel-video-btn')?.addEventListener('click', () => closeModal('video-modal'));
}

window.replaceVideo = function(videoId) {
    editingVideoId = videoId;
    const video = EMOTION_VIDEOS.find(v => v.id === videoId);
    
    if (video) {
        $('video-modal-title').textContent = `🔄 Thay thế Video: ${video.emoji} ${video.name}`;
        $('video-emotion-name').textContent = video.name;
        $('video-current-path').textContent = video.path;
        $('video-file-input').value = '';
        currentVideoFile = null;
        
        openModal('video-modal');
    }
};

window.deleteVideo = function(videoId) {
    const video = EMOTION_VIDEOS.find(v => v.id === videoId);
    
    if (!video) return;
    
    if (!confirm(`⚠️ Bạn có chắc chắn muốn xóa video "${video.name}"?\n\nLưu ý: Video sẽ bị xóa khỏi thư mục assets!`)) return;
    
    fetch(`${API_URL}/emotions/delete-video`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_path: video.path })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification(`✅ Đã xóa video "${video.name}"!`, 'success');
            loadEmotionVideos();
        } else {
            throw new Error(data.message || 'Lỗi xóa video');
        }
    })
    .catch(err => {
        showNotification(`❌ ${err.message}`, 'error');
    });
};

export { loadEmotionVideos, setupEmotionEvents };