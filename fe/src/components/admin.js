const API_BASE = "http://localhost:8000";
const API_URL = `${API_BASE}/admin`;

function $(id) {
    return document.getElementById(id);
}

async function fetchAPI(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    return fetch(url, {
        ...options,
        headers
    });
}

// ==========================================
// AUTHENTICATION & ROLE CHECK
// ==========================================
function checkAdminRole() {
    const currentUserStr = sessionStorage.getItem('currentUser') || localStorage.getItem('currentUser');

    if (!currentUserStr) {
        alert('⛔ Bạn chưa đăng nhập!');
        window.location.href = '../pages/login.html';
        return false;
    }

    const userData = JSON.parse(currentUserStr);
    const role = (userData.role || userData.accountType || '').toLowerCase().trim();

    if (role !== 'admin') {
        alert(`⛔ Bạn không có quyền truy cập! Role của bạn: ${role}`);
        window.location.href = '../pages/login.html';
        return false;
    }

    const adminName = userData.name || userData.fullName || userData.username || 'Admin';
    const adminNameEl = $('admin-name');
    if (adminNameEl) adminNameEl.textContent = adminName;

    return true;
}

// ==========================================
// NAVIGATION
// ==========================================
const navItems = document.querySelectorAll('.nav-item');
const sections = document.querySelectorAll('.content-section');

navItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const targetSection = item.dataset.section;

        navItems.forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');

        sections.forEach(section => section.classList.remove('active'));
        $(`${targetSection}-section`).classList.add('active');

        loadSectionData(targetSection);
    });
});

// ==========================================
// USERS MANAGEMENT
// ==========================================
let currentUsers = [];
let editingUserId = null;

async function loadUsers() {
    try {
        const res = await fetchAPI(`${API_URL}/users?skip=0&limit=100`);

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();
        currentUsers = data.data.users || [];
        renderUsersTable(currentUsers);
        
        // Update dashboard stats
        if ($('total-users')) {
            $('total-users').textContent = currentUsers.length;
        }
        
    } catch (err) {
        console.error("❌ Load users error:", err);
        showNotification(`Lỗi tải users: ${err.message}`, 'error');
    }
}

function renderUsersTable(users) {
    const tbody = $('users-tbody');

    if (!tbody) {
        console.error("Không tìm thấy #users-tbody trong DOM!");
        return;
    }

    if (!users.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align:center">Không có dữ liệu</td>
            </tr>`;
        return;
    }

    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.user_id.substring(0, 8)}...</td>
            <td><strong>${user.username}</strong></td>
            <td>${user.email}</td>
            <td><span class="badge badge-${user.role}">${user.role.toUpperCase()}</span></td>
            <td>${user.age || 'N/A'}</td>
            <td>${user.created_at ? new Date(user.created_at).toLocaleDateString('vi-VN') : 'N/A'}</td>
            <td>
                <span class="badge badge-active">Hoạt động</span>
            </td>
            <td class="actions">
                <button class="btn btn-warning" onclick="editUser('${user.user_id}')">✏️</button>
                <button class="btn btn-danger" onclick="deleteUser('${user.user_id}')">🗑️</button>
            </td>
        </tr>
    `).join('');
}

$('add-user-btn')?.addEventListener('click', () => {
    editingUserId = null;
    $('user-modal-title').textContent = '➕ Thêm User Mới';
    $('user-form').reset();
    $('user-password').required = true;
    $('user-password').placeholder = 'Nhập mật khẩu';
    openModal('user-modal');
});

window.editUser = (id) => {
    editingUserId = id;
    const user = currentUsers.find(u => u.user_id === id);
    if (!user) return;

    $('user-modal-title').textContent = '✏️ Chỉnh sửa User';

    $('user-username').value = user.username;
    $('user-email').value = user.email;
    $('user-name').value = user.name;
    $('user-role').value = user.role;
    $('user-age').value = user.age ?? '';
    $('user-gender').value = user.gender ?? 'male';

    $('user-password').required = false;
    $('user-password').placeholder = 'Để trống nếu không đổi';

    openModal('user-modal');
};

window.deleteUser = async (id) => {
    if (!confirm("⚠️ Bạn có chắc chắn muốn xóa user này?")) return;

    try {
        const res = await fetchAPI(`${API_URL}/users/${id}`, {
            method: "DELETE"
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Lỗi xóa user");
        }

        showNotification("✅ Đã xóa user!", "success");
        loadUsers();

    } catch (err) {
        console.error(err);
        showNotification(`❌ ${err.message}`, 'error');
    }
};

$('user-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
        username: $('user-username').value,
        name: $('user-name').value,
        email: $('user-email').value,
        role: $('user-role').value,
        age: $('user-age').value ? parseInt($('user-age').value) : null,
        gender: $('user-gender').value || null
    };

    const passwordValue = $('user-password').value;
    if (passwordValue) data.password = passwordValue;

    try {
        let res;

        const options = {
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        };

        if (editingUserId) {
            res = await fetchAPI(`${API_URL}/users/${editingUserId}`, {
                method: "PUT",
                ...options
            });
        } else {
            res = await fetchAPI(`${API_URL}/users`, {
                method: "POST",
                ...options
            });
        }

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Lỗi API");
        }

        showNotification("✔ Thành công!", "success");
        closeModal("user-modal");
        loadUsers();

    } catch (err) {
        showNotification("❌ " + err.message, "error");
    }
});

// ==========================================
// ⭐ EMOTION VIDEOS MANAGEMENT
// ==========================================
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
                <button class="btn btn-warning" onclick="replaceVideo('${video.id}')">
                    🔄 Thay thế video
                </button>
                <button class="btn btn-danger" onclick="deleteVideo('${video.id}')">
                    🗑️ Xóa video
                </button>
            </div>
        </div>
    `).join('');
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

// ==========================================
// ⭐ GAME CONTENTS MANAGEMENT
// ==========================================
// ==========================================
// ⭐ GAME CONTENTS MANAGEMENT (FIXED)
// ==========================================
let currentGameContents = [];
let editingGameContentId = null;  // ✅ Đây là content_id (primary key)
let currentMediaFile = null;

async function loadGameContents(filters = {}) {
    try {
        let url = `${API_URL}/game-contents?skip=0&limit=100`;
        
        if (filters.game_id) url += `&game_id=${filters.game_id}`;
        if (filters.level) url += `&level=${filters.level}`;
        if (filters.emotion) url += `&emotion=${filters.emotion}`;
        
        console.log('📡 Loading game contents from:', url);
        
        const res = await fetchAPI(url);

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();
        console.log('📦 Received data:', data);
        
        currentGameContents = data.data?.game_contents || [];
        
        console.log(`✅ Loaded ${currentGameContents.length} game contents`);
        
        renderGameContentsTable(currentGameContents);
        
        // Update dashboard stats
        if ($('total-game-contents')) {
            $('total-game-contents').textContent = data.data?.total || currentGameContents.length;
        }
        
    } catch (err) {
        console.error("❌ Load game contents error:", err);
        showNotification(`Lỗi tải nội dung game: ${err.message}`, 'error');
    }
}

function renderGameContentsTable(contents) {
    const tbody = $('game-contents-tbody');

    if (!tbody) {
        console.error("Không tìm thấy #game-contents-tbody trong DOM!");
        return;
    }

    if (!contents || contents.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align:center; padding: 30px;">
                    <div style="color: #999;">
                        <i class="fas fa-inbox" style="font-size: 48px; margin-bottom: 10px;"></i>
                        <p>Chưa có nội dung game nào</p>
                    </div>
                </td>
            </tr>`;
        return;
    }

    tbody.innerHTML = contents.map(content => `
        <tr>
            <td title="${content.content_id}">${content.content_id.substring(0, 8)}...</td>
            <td title="${content.game_id}">${content.game_id.substring(0, 8)}...</td>
            <td><span class="badge badge-info">Level ${content.level}</span></td>
            <td><span class="badge badge-secondary">${content.content_type}</span></td>
            <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis;" title="${content.question_text}">
                ${content.question_text.substring(0, 50)}${content.question_text.length > 50 ? '...' : ''}
            </td>
            <td>${content.emotion ? getEmotionEmoji(content.emotion) + ' ' + content.emotion : '<span style="color:#999">N/A</span>'}</td>
            <td>${content.media_path ? '✅' : '❌'}</td>
            <td class="actions">
                <button class="btn btn-warning" onclick="editGameContent('${content.content_id}')" title="Chỉnh sửa">✏️</button>
                <button class="btn btn-danger" onclick="deleteGameContent('${content.content_id}')" title="Xóa">🗑️</button>
            </td>
        </tr>
    `).join('');
}

function getEmotionEmoji(emotion) {
    const emojis = {
        'vui': '😊',
        'vui vẻ': '😊',
        'happy': '😊',
        'buồn': '😢',
        'buồn bã': '😢',
        'sad': '😢',
        'tức giận': '😠',
        'angry': '😠',
        'sợ hãi': '😨',
        'fear': '😨',
        'ngạc nhiên': '😲',
        'surprise': '😲',
        'ghê tởm': '🤢',
        'disgust': '🤢'
    };
    return emojis[emotion?.toLowerCase()] || '❓';
}

$('add-game-content-btn')?.addEventListener('click', () => {
    editingGameContentId = null;
    $('game-content-modal-title').textContent = '➕ Thêm Nội dung Game';
    $('game-content-form').reset();
    currentMediaFile = null;
    $('gc-media-preview').style.display = 'none';
    
    // ✅ Khi tạo mới, game_id field phải enabled và rỗng
    $('gc-game-id').disabled = false;
    $('gc-game-id').value = '';
    
    openModal('game-content-modal');
});

$('apply-filters-btn')?.addEventListener('click', () => {
    const filters = {
        game_id: $('filter-game-id').value,
        level: $('filter-level').value,
        emotion: $('filter-emotion').value
    };
    
    console.log('🔍 Applying filters:', filters);
    loadGameContents(filters);
});

window.editGameContent = async (content_id) => {
    // ✅ Lưu content_id (primary key) để update
    editingGameContentId = content_id;
    
    try {
        const res = await fetchAPI(`${API_URL}/game-contents/${content_id}`);
        
        if (!res.ok) {
            throw new Error('Không tìm thấy nội dung');
        }
        
        const data = await res.json();
        const content = data.data;
        
        console.log('📝 Editing content:', content);
        
        $('game-content-modal-title').textContent = '✏️ Chỉnh sửa Nội dung Game';
        
        // ✅ Hiển thị CẢ content_id VÀ game_id
        $('gc-game-id').value = content.game_id;
        $('gc-game-id').disabled = false;  // Cho phép sửa game_id
        
        $('gc-level').value = content.level;
        $('gc-content-type').value = content.content_type;
        $('gc-emotion').value = content.emotion || '';
        $('gc-question-text').value = content.question_text;
        $('gc-correct-answer').value = content.correct_answer || '';
        $('gc-explanation').value = content.explanation || '';
        
        openModal('game-content-modal');
        
    } catch (err) {
        console.error('❌ Edit error:', err);
        showNotification(`❌ ${err.message}`, 'error');
    }
};

window.deleteGameContent = async (content_id) => {
    if (!confirm("⚠️ Bạn có chắc chắn muốn xóa nội dung này?")) return;

    try {
        // ✅ Xóa theo content_id
        const res = await fetchAPI(`${API_URL}/game-contents/${content_id}`, {
            method: "DELETE"
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Lỗi xóa nội dung");
        }

        showNotification("✅ Đã xóa nội dung!", "success");
        loadGameContents();

    } catch (err) {
        console.error('❌ Delete error:', err);
        showNotification(`❌ ${err.message}`, 'error');
    }
};

$('gc-media-file')?.addEventListener('change', (e) => {
    const file = e.target.files[0];
    
    if (!file) {
        currentMediaFile = null;
        $('gc-media-preview').style.display = 'none';
        return;
    }
    
    currentMediaFile = file;
    const previewContent = $('gc-media-preview-content');
    
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewContent.innerHTML = `<img src="${e.target.result}" style="max-width: 300px; border-radius: 8px;">`;
            $('gc-media-preview').style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else if (file.type.startsWith('video/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewContent.innerHTML = `<video src="${e.target.result}" controls style="max-width: 300px; border-radius: 8px;"></video>`;
            $('gc-media-preview').style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else if (file.type.startsWith('audio/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewContent.innerHTML = `<audio src="${e.target.result}" controls style="width: 100%;"></audio>`;
            $('gc-media-preview').style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
});

$('game-content-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ Đang xử lý...';
    
    try {
        let mediaPath = null;
        
        // Upload media file first if exists
        if (currentMediaFile) {
            const formData = new FormData();
            formData.append('file', currentMediaFile);
            formData.append('content_type', $('gc-content-type').value);
            formData.append('game_name', 'emotion_game');
            formData.append('emotion', $('gc-emotion').value || '');
            
            console.log('📤 Uploading media...');
            
            const uploadRes = await fetch(`${API_URL}/game-contents/upload-media`, {
                method: 'POST',
                body: formData
            });
            
            const uploadData = await uploadRes.json();
            
            if (!uploadRes.ok || uploadData.status !== 'success') {
                throw new Error(uploadData.message || 'Lỗi upload media');
            }
            
            mediaPath = uploadData.data.media_path;
            console.log('✅ Media uploaded:', mediaPath);
        }
        
        // ✅ Prepare data với game_id
        const data = {
            game_id: $('gc-game-id').value.trim(),  // ✅ Đọc game_id từ form
            level: parseInt($('gc-level').value),
            content_type: $('gc-content-type').value,
            question_text: $('gc-question-text').value,
            correct_answer: $('gc-correct-answer').value || null,
            emotion: $('gc-emotion').value || null,
            explanation: $('gc-explanation').value || null,
            media_path: mediaPath
        };
        
        // ✅ Validate game_id format (UUID)
        const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
        if (!uuidRegex.test(data.game_id)) {
            throw new Error('Game ID phải là UUID hợp lệ (VD: 550e8400-e29b-41d4-a716-446655440000)');
        }
        
        console.log('💾 Saving game content:', data);
        
        let res;
        
        if (editingGameContentId) {
            // ✅ UPDATE: Dùng content_id trong URL
            res = await fetchAPI(`${API_URL}/game-contents/${editingGameContentId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
        } else {
            // ✅ CREATE: Backend sẽ tự tạo content_id mới
            res = await fetchAPI(`${API_URL}/game-contents`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
        }

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Lỗi API");
        }

        showNotification("✔ Thành công!", "success");
        closeModal("game-content-modal");
        loadGameContents();

    } catch (err) {
        console.error('❌ Save error:', err);
        showNotification("❌ " + err.message, "error");
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '💾 Lưu';
    }
});

// ==========================================
// MODAL + NOTIFICATION
// ==========================================
function openModal(id) {
    $(id).classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal(id) {
    $(id).classList.remove('active');
    document.body.style.overflow = 'auto';
}

function showNotification(message, type = 'success') {
    const noti = document.createElement('div');
    noti.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#2ecc71' : '#e74c3c'};
        color: white;
        border-radius: 10px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    `;
    noti.textContent = message;
    document.body.appendChild(noti);

    setTimeout(() => {
        noti.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => noti.remove(), 300);
    }, 3000);
}

document.querySelectorAll('.close').forEach(btn => {
    btn.addEventListener('click', () => {
        closeModal(btn.closest('.modal').id);
    });
});

$('cancel-user-btn')?.addEventListener('click', () => closeModal('user-modal'));
$('cancel-video-btn')?.addEventListener('click', () => closeModal('video-modal'));
$('cancel-game-content-btn')?.addEventListener('click', () => closeModal('game-content-modal'));

document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal(modal.id);
    });
});

// ==========================================
// LOGOUT
// ==========================================
$('logout-btn')?.addEventListener('click', () => {
    if (confirm("Bạn có chắc chắn muốn đăng xuất?")) {
        sessionStorage.removeItem("currentUser");
        localStorage.removeItem("currentUser");
        window.location.href = "../pages/login.html";
    }
});

// ==========================================
// DASHBOARD LOAD
// ==========================================
function loadDashboard() {
    loadUsers();
    loadEmotionVideos();
    loadGameContents();
}

function loadSectionData(section) {
    switch(section) {
        case 'users':
            loadUsers();
            break;
        case 'emotions':
            loadEmotionVideos();
            break;
        case 'game-contents':
            loadGameContents();
            break;
        case 'dashboard':
            loadDashboard();
            break;
    }
}

// ==========================================
// INITIALIZE
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
    if (checkAdminRole()) {
        loadDashboard();
    }
});

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
    
    .video-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .video-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .video-preview-container {
        margin: 15px 0;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 8px;
    }
`;
document.head.appendChild(style);