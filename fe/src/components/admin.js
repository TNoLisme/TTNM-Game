const API_BASE = "http://localhost:8000";
const API_URL = `${API_BASE}/admin`;

function parseErrorMessage(error) {
    if (typeof error === "string") return error;
    if (error?.detail) return error.detail;
    return "Unknown error";
}

function $(id) {
    return document.getElementById(id);
}

function getAuthToken() {
    const token = localStorage.getItem('token');
    if (!token) {
        console.error('❌ No access token found!');
        alert('⛔ Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!');
        window.location.href = '../pages/login.html';
        return null;
    }
    return token;
}

async function fetchWithAuth(url, options = {}) {
    const token = getAuthToken();
    if (!token) throw new Error('No authentication token');

    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
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
    const currentUserStr = localStorage.getItem('currentUser');
    const accessToken = localStorage.getItem('token');

    console.log('%c🔍 CHECKING ADMIN ROLE:', 'color: blue; font-weight: bold;');
    console.log('currentUser:', currentUserStr);
    console.log('token:', accessToken ? 'EXISTS ✅' : 'MISSING ❌');

    if (!currentUserStr || !accessToken) {
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

    console.log('%c✅ ADMIN VERIFIED', 'color: green; font-weight: bold;');
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
        console.log('📡 Loading users with token...');
        
        const res = await fetchWithAuth(`${API_URL}/users`);

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();
        console.log('✅ Users loaded:', data);
        
        currentUsers = data.data.users || [];
        renderUsersTable(currentUsers);
        
    } catch (err) {
        console.error("❌ Load users error:", err);
        showNotification(`Lỗi tải users: ${err.message}`, 'error');
        
        if (err.message.includes('401') || err.message.includes('403')) {
            setTimeout(() => {
                localStorage.clear();
                window.location.href = '../pages/login.html';
            }, 2000);
        }
    }
}

function renderUsersTable(users) {
    const tbody = document.getElementById('users-tbody');

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
            <td>${user.user_id}</td>
            <td><strong>${user.username}</strong></td>
            <td>${user.email}</td>
            <td><span class="badge badge-${user.role}">${user.role.toUpperCase()}</span></td>
            <td>${user.age || 'N/A'}</td>
            <td>${new Date(user.created_at).toLocaleDateString('vi-VN')}</td>
            <td>
                <span class="badge badge-${user.status}">
                    ${user.status === 'active' ? 'Hoạt động' : 'Không hoạt động'}
                </span>
            </td>
            <td class="actions">
                <button class="btn btn-warning" onclick="editUser('${user.user_id}')">✏️</button>
                <button class="btn btn-danger" onclick="deleteUser('${user.user_id}')">🗑️</button>
            </td>
        </tr>
    `).join('');
}

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
    $('user-status').value = user.status;
    $('user-dob').value = user.date_of_birth ?? '';
    $('user-phone').value = user.phone_number ?? '';

    $('user-password').required = false;
    $('user-password').placeholder = 'Để trống nếu không đổi';

    openModal('user-modal');
};

$('add-user-btn')?.addEventListener('click', () => {
    console.log("🔵 [DEBUG] Click: add-user-btn → mở modal tạo user mới");

    editingUserId = null;
    $('user-modal-title').textContent = '➕ Thêm User Mới';
    $('user-form').reset();

    $('user-password').required = true;
    $('user-password').placeholder = 'Nhập mật khẩu';

    openModal('user-modal');
});

window.deleteUser = async (id) => {
    console.log(`🟠 [DEBUG] deleteUser(${id})`);

    if (!confirm("⚠️ Bạn có chắc chắn muốn xóa user này?")) {
        console.log("🟡 [DEBUG] Hủy xóa user");
        return;
    }

    try {
        console.log(`🔵 [DEBUG] DELETE → ${API_URL}/users/${id}`);

        const res = await fetchWithAuth(`${API_URL}/users/${id}`, {
            method: "DELETE"
        });

        console.log("🟣 [DEBUG] DELETE Response status:", res.status);

        if (!res.ok) {
            const err = await res.json();
            console.error("🔴 [DEBUG] DELETE Error response:", err);
            throw new Error(err.detail || "Lỗi xóa user");
        }

        showNotification("✅ Đã xóa user!", "success");
        loadUsers();

    } catch (err) {
        console.error("❌ [DEBUG] deleteUser catch:", err);
        showNotification(`❌ ${err.message}`, 'error');
    }
};

$('user-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    console.log("🔵 [DEBUG] Submit user-form");

    const data = {
        username: $('user-username').value,
        email: $('user-email').value,
        name: $('user-name').value,
        role: $('user-role').value,
        gender: $('user-gender').value,
        date_of_birth: $('user-dob').value,  
        phone_number: $('user-phone').value,  
    };

    const age = $('user-age').value;
    if (age) data.age = parseInt(age);

    const status = $('user-status').value;
    if (status) data.status = status;

    const passwordValue = $('user-password').value;
    if (passwordValue) data.password = passwordValue;

    console.log("🟣 [DEBUG] Form data gửi lên API:", data);

    try {
        let res;
        let url;
        let method;

        if (editingUserId) {
            method = "PUT";
            url = `${API_URL}/users/${editingUserId}`;
        } else {
            method = "POST";
            url = `${API_URL}/users`;

            if (!passwordValue) {
                console.warn("🟡 [DEBUG] Không nhập password khi tạo user mới");
                showNotification("❌ Vui lòng nhập mật khẩu!", "error");
                return;
            }
        }

        console.log(`🔵 [DEBUG] API CALL → ${method} ${url}`);

        res = await fetchWithAuth(url, {
            method: method,
            body: JSON.stringify(data),
        });

        console.log("🔵 [DEBUG] API Response status:", res.status);

        if (!res.ok) {
            const err = await res.json();
            console.error("🔴 [DEBUG] API Error Response:", err);
            
            let errorMessage = "Lỗi API";
            if (err.message) {
                errorMessage = err.message;
            } else if (err.detail) {
                errorMessage = typeof err.detail === 'string' 
                    ? err.detail 
                    : JSON.stringify(err.detail);
            }
            
            throw new Error(errorMessage);
        }

        const result = await res.json();
        console.log("🟢 [DEBUG] API Success Response:", result);

        if (result.status === 'success') {
            showNotification("✅ " + result.message, "success");
        } else if (result.status === 'failed') {
            showNotification("❌ " + result.message, "error");
            return;
        } else {
            showNotification("✔ Thành công!", "success");
        }

        closeModal("user-modal");
        await loadUsers();
        await updateDashboardStats();

    } catch (err) {
        console.error('❌ [DEBUG] Submit error:', err);
        showNotification("❌ " + err.message, "error");
    }
});

// ==========================================
// EMOTIONS MANAGEMENT
// ==========================================
let currentEmotions = [];
let editingEmotionId = null;

function loadEmotions() {
    currentEmotions = getEmotions();
    renderEmotionsGrid(currentEmotions);
}

function getEmotions() {
    const stored = localStorage.getItem('adminEmotions');
    if (stored) return JSON.parse(stored);
    
    return [
        { id: 1, name: 'Vui vẻ', nameEn: 'Happy', icon: '😊', color: '#ffd700', category: 'happy', description: 'Cảm giác hạnh phúc và vui vẻ' },
        { id: 2, name: 'Buồn', nameEn: 'Sad', icon: '😢', color: '#4a90e2', category: 'sad', description: 'Cảm giác buồn bã' },
        { id: 3, name: 'Giận dữ', nameEn: 'Angry', icon: '😠', color: '#e74c3c', category: 'angry', description: 'Cảm giác tức giận' },
        { id: 4, name: 'Sợ hãi', nameEn: 'Scared', icon: '😨', color: '#9b59b6', category: 'scared', description: 'Cảm giác sợ sệt' },
        { id: 5, name: 'Ngạc nhiên', nameEn: 'Surprised', icon: '😲', color: '#f39c12', category: 'surprised', description: 'Cảm giác bất ngờ' }
    ];
}

function saveEmotions(emotions) {
    localStorage.setItem('adminEmotions', JSON.stringify(emotions));
}

function renderEmotionsGrid(emotions) {
    const grid = document.getElementById('emotions-grid');
    
    if (emotions.length === 0) {
        grid.innerHTML = '<p style="text-align: center; grid-column: 1/-1; padding: 30px;">Không có dữ liệu</p>';
        return;
    }
    
    grid.innerHTML = emotions.map(emotion => `
        <div class="emotion-card" style="border-top: 4px solid ${emotion.color}">
            <div class="emotion-icon-large">${emotion.icon}</div>
            <h3>${emotion.name}</h3>
            <p style="color: #7f8c8d; font-size: 12px; margin-bottom: 5px;">${emotion.nameEn}</p>
            <p>${emotion.description || ''}</p>
            <div class="actions">
                <button class="btn btn-warning" onclick="editEmotion(${emotion.id})">✏️ Sửa</button>
                <button class="btn btn-danger" onclick="deleteEmotion(${emotion.id})">🗑️ Xóa</button>
            </div>
        </div>
    `).join('');
}

document.getElementById('search-emotions')?.addEventListener('input', filterEmotions);
document.getElementById('filter-category')?.addEventListener('change', filterEmotions);

function filterEmotions() {
    const search = document.getElementById('search-emotions').value.toLowerCase();
    const category = document.getElementById('filter-category').value;
    
    let filtered = currentEmotions.filter(emotion => {
        const matchSearch = emotion.name.toLowerCase().includes(search) || 
                          emotion.nameEn.toLowerCase().includes(search);
        const matchCategory = !category || emotion.category === category;
        
        return matchSearch && matchCategory;
    });
    
    renderEmotionsGrid(filtered);
}

document.getElementById('add-emotion-btn')?.addEventListener('click', () => {
    editingEmotionId = null;
    document.getElementById('emotion-modal-title').textContent = '➕ Thêm Cảm xúc Mới';
    document.getElementById('emotion-form').reset();
    openModal('emotion-modal');
});

window.editEmotion = function(id) {
    editingEmotionId = id;
    const emotion = currentEmotions.find(e => e.id === id);
    
    if (emotion) {
        document.getElementById('emotion-modal-title').textContent = '✏️ Chỉnh sửa Cảm xúc';
        document.getElementById('emotion-name').value = emotion.name;
        document.getElementById('emotion-name-en').value = emotion.nameEn;
        document.getElementById('emotion-icon').value = emotion.icon;
        document.getElementById('emotion-color').value = emotion.color;
        document.getElementById('emotion-category').value = emotion.category;
        document.getElementById('emotion-description').value = emotion.description || '';
        
        openModal('emotion-modal');
    }
};

window.deleteEmotion = function(id) {
    if (confirm('⚠️ Bạn có chắc chắn muốn xóa cảm xúc này?')) {
        currentEmotions = currentEmotions.filter(e => e.id !== id);
        saveEmotions(currentEmotions);
        renderEmotionsGrid(currentEmotions);
        showNotification('✅ Đã xóa cảm xúc thành công!', 'success');
    }
};

document.getElementById('emotion-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const emotionData = {
        name: document.getElementById('emotion-name').value,
        nameEn: document.getElementById('emotion-name-en').value,
        icon: document.getElementById('emotion-icon').value,
        color: document.getElementById('emotion-color').value,
        category: document.getElementById('emotion-category').value,
        description: document.getElementById('emotion-description').value
    };
    
    if (editingEmotionId) {
        const index = currentEmotions.findIndex(e => e.id === editingEmotionId);
        currentEmotions[index] = { ...currentEmotions[index], ...emotionData };
        showNotification('✅ Đã cập nhật cảm xúc thành công!', 'success');
    } else {
        const newEmotion = { id: Date.now(), ...emotionData };
        currentEmotions.push(newEmotion);
        showNotification('✅ Đã thêm cảm xúc mới thành công!', 'success');
    }
    
    saveEmotions(currentEmotions);
    renderEmotionsGrid(currentEmotions);
    closeModal('emotion-modal');
});

// ==========================================
// QUESTIONS/GAME CONTENT MANAGEMENT
// ==========================================

const GAME_TYPES = {
    'face-recognition': { id: 1, name: 'Nhìn mặt đoán cảm xúc', table: 'game_content' },
    'text-scenario': { id: 2, name: 'Chọn đúng cảm xúc', table: 'game_content' },
    'mimic-expression': { id: 3, name: 'Bắt chước biểu cảm', table: 'game_content' },
    'camera-detection': { id: 4, name: 'Camera đoán cảm xúc', table: 'game_content' },
    'situation-image': { id: 5, name: 'Nhìn tình huống đoán cảm xúc', table: 'game_content' },
    'cv-advanced': { id: 6, name: 'Game CV - Nhận diện cảm xúc', table: 'game_content' }
};

const EMOTION_MAP = {
    'happy': 'Vui vẻ',
    'sad': 'Buồn bã',
    'angry': 'Tức giận',
    'scared': 'Sợ hãi',
    'surprised': 'Ngạc nhiên',
    'disgusted': 'Ghê tởm'
};

let uploadedImages = [];
let peopleList = [];
let currentQuestions = [];
let editingQuestionId = null;

// Dynamic form handling based on game type
document.getElementById('question-type')?.addEventListener('change', handleQuestionTypeChange);

function handleQuestionTypeChange() {
    const type = document.getElementById('question-type').value;
    const imageUploadSection = document.getElementById('image-upload-section');
    const promptSection = document.getElementById('prompt-section');
    const hintSection = document.getElementById('hint-section');
    const answersSection = document.getElementById('answers-section');
    const answersContainer = document.getElementById('answers-container');
    const answersLabel = document.getElementById('answers-label');
    const uploadHint = document.getElementById('upload-hint');
    const questionTextLabel = document.querySelector('label[for="question-text"]');
    
    // Reset all required attributes
    const allInputs = answersContainer.querySelectorAll('input, select, textarea');
    allInputs.forEach(input => input.removeAttribute('required'));
    
    // Reset sections
    imageUploadSection.style.display = 'none';
    promptSection.style.display = 'none';
    hintSection.style.display = 'none';
    answersSection.style.display = 'block';
    uploadedImages = [];
    document.getElementById('image-preview').innerHTML = '';
    
    const promptInput = document.getElementById('game-prompt');
    const hintInput = document.getElementById('question-hint');
    if (promptInput) promptInput.removeAttribute('required');
    if (hintInput) hintInput.removeAttribute('required');
    
    switch(type) {
        case 'face-recognition':
            questionTextLabel.textContent = 'Câu hỏi *';
            document.getElementById('question-text').placeholder = 'VD: Bạn nhỏ này đang vui phải không?';
            document.getElementById('question-text').setAttribute('required', 'required');
            
            imageUploadSection.style.display = 'block';
            uploadHint.textContent = 'Upload 1 ảnh khuôn mặt thể hiện cảm xúc';
            document.getElementById('question-images').multiple = false;
            
            answersLabel.textContent = 'Cảm xúc đúng *';
            answersContainer.innerHTML = `
                <select id="emotion-answer" required>
                    <option value="">Chọn cảm xúc</option>
                    <option value="happy">😊 Vui vẻ</option>
                    <option value="sad">😢 Buồn bã</option>
                    <option value="angry">😠 Tức giận</option>
                    <option value="scared">😨 Sợ hãi</option>
                    <option value="surprised">😲 Ngạc nhiên</option>
                    <option value="disgusted">🤢 Ghê tởm</option>
                </select>
            `;
            break;
            
        case 'text-scenario':
            questionTextLabel.textContent = 'Tình huống (text) *';
            document.getElementById('question-text').placeholder = 'VD: Khi được mẹ khen, bé thường cảm thấy?';
            document.getElementById('question-text').setAttribute('required', 'required');
            
            answersLabel.textContent = 'Cảm xúc đúng *';
            answersContainer.innerHTML = `
                <select id="emotion-answer" required>
                    <option value="">Chọn cảm xúc</option>
                    <option value="happy">😊 Vui vẻ</option>
                    <option value="sad">😢 Buồn bã</option>
                    <option value="angry">😠 Tức giận</option>
                    <option value="scared">😨 Sợ hãi</option>
                    <option value="surprised">😲 Ngạc nhiên</option>
                    <option value="disgusted">🤢 Ghê tởm</option>
                </select>
            `;
            break;
            
        case 'mimic-expression':
            questionTextLabel.textContent = 'Hướng dẫn *';
            document.getElementById('question-text').placeholder = 'VD: Làm giống video nhé!';
            document.getElementById('question-text').setAttribute('required', 'required');
            
            imageUploadSection.style.display = 'block';
            uploadHint.textContent = 'Upload video demo biểu cảm (mp4)';
            document.getElementById('question-images').multiple = false;
            document.getElementById('question-images').accept = 'video/*';
            
            answersLabel.textContent = 'Cảm xúc cần bắt chước *';
            answersContainer.innerHTML = `
                <select id="emotion-answer" required>
                    <option value="">Chọn cảm xúc</option>
                    <option value="happy">😊 Vui vẻ</option>
                    <option value="sad">😢 Buồn bã</option>
                    <option value="angry">😠 Tức giận</option>
                    <option value="scared">😨 Sợ hãi</option>
                    <option value="surprised">😲 Ngạc nhiên</option>
                    <option value="disgusted">🤢 Ghê tởm</option>
                </select>
            `;
            break;
            
        case 'camera-detection':
            questionTextLabel.textContent = 'Hướng dẫn *';
            document.getElementById('question-text').placeholder = 'VD: Nhìn camera và thể hiện cảm xúc!';
            document.getElementById('question-text').setAttribute('required', 'required');
            
            imageUploadSection.style.display = 'block';
            uploadHint.textContent = 'Upload ảnh hướng dẫn (tùy chọn)';
            document.getElementById('question-images').multiple = false;
            document.getElementById('question-images').accept = 'image/*';
            document.getElementById('question-images').removeAttribute('required');
            
            answersLabel.textContent = 'Cảm xúc cần thể hiện (tùy chọn)';
            answersContainer.innerHTML = `
                <select id="emotion-answer">
                    <option value="">Không chỉ định (tự do)</option>
                    <option value="happy">😊 Vui vẻ</option>
                    <option value="sad">😢 Buồn bã</option>
                    <option value="angry">😠 Tức giận</option>
                    <option value="scared">😨 Sợ hãi</option>
                    <option value="surprised">😲 Ngạc nhiên</option>
                    <option value="disgusted">🤢 Ghê tởm</option>
                </select>
                <small class="form-hint">Để trống nếu muốn AI tự nhận diện bất kỳ cảm xúc nào</small>
            `;
            break;
            
        case 'situation-image':
            questionTextLabel.textContent = 'Câu hỏi *';
            document.getElementById('question-text').placeholder = 'VD: Con cảm thấy thế nào?';
            document.getElementById('question-text').setAttribute('required', 'required');
            
            imageUploadSection.style.display = 'block';
            hintSection.style.display = 'block';
            uploadHint.textContent = 'Upload ảnh minh họa tình huống';
            document.getElementById('question-images').multiple = false;
            document.getElementById('question-images').accept = 'image/*';
            
            answersLabel.textContent = 'Cảm xúc đúng *';
            answersContainer.innerHTML = `
                <select id="emotion-answer" required>
                    <option value="">Chọn cảm xúc</option>
                    <option value="happy">😊 Vui vẻ</option>
                    <option value="sad">😢 Buồn bã</option>
                    <option value="angry">😠 Tức giận</option>
                    <option value="scared">😨 Sợ hãi</option>
                    <option value="surprised">😲 Ngạc nhiên</option>
                    <option value="disgusted">🤢 Ghê tởm</option>
                </select>
            `;
            break;
            
        case 'cv-advanced':
            questionTextLabel.textContent = 'Tên tình huống *';
            document.getElementById('question-text').placeholder = 'VD: Quà bất ngờ';
            document.getElementById('question-text').setAttribute('required', 'required');
            
            imageUploadSection.style.display = 'block';
            uploadHint.textContent = 'Upload ảnh minh họa tình huống';
            document.getElementById('question-images').multiple = false;
            document.getElementById('question-images').accept = 'image/*';
            
            document.querySelector('label[for="question-explanation"]').textContent = 'Mô tả chi tiết tình huống *';
            document.getElementById('question-explanation').placeholder = 'VD: Con mở hộp quà bất ngờ và thấy món con thích. Hãy tưởng tượng con vừa nhận được món quà yêu thích!';
            document.getElementById('question-explanation').setAttribute('required', 'required');
            
            answersLabel.textContent = 'Cảm xúc cần thể hiện *';
            answersContainer.innerHTML = `
                <select id="emotion-answer" required>
                    <option value="">Chọn cảm xúc</option>
                    <option value="happy">😊 Vui vẻ</option>
                    <option value="sad">😢 Buồn bã</option>
                    <option value="angry">😠 Tức giận</option>
                    <option value="scared">😨 Sợ hãi</option>
                    <option value="surprised">😲 Ngạc nhiên</option>
                    <option value="disgusted">🤢 Ghê tởm</option>
                </select>
            `;
            break;
    }
}

// Image upload handling
document.getElementById('question-images')?.addEventListener('change', function(e) {
    const files = Array.from(e.target.files);
    const previewContainer = document.getElementById('image-preview');
    
    files.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = function(event) {
            const mediaData = {
                name: file.name,
                type: file.type,
                data: event.target.result
            };
            uploadedImages.push(mediaData);
            
            const isVideo = file.type.startsWith('video/');
            const mediaTag = isVideo
                ? `<video src="${event.target.result}" controls></video>`
                : `<img src="${event.target.result}" alt="Preview">`;
            
            const itemDiv = document.createElement('div');
            itemDiv.className = 'image-preview-item';
            itemDiv.innerHTML = `
                ${mediaTag}
                <button type="button" class="remove-image" onclick="removeImage(${uploadedImages.length - 1})">×</button>
            `;
            previewContainer.appendChild(itemDiv);
        };
        reader.readAsDataURL(file);
    });
});

window.removeImage = function(index) {
    uploadedImages.splice(index, 1);
    const previewContainer = document.getElementById('image-preview');
    previewContainer.children[index].remove();
};

document.getElementById('search-questions')?.addEventListener('input', filterQuestions);
document.getElementById('filter-difficulty')?.addEventListener('change', filterQuestions);
document.getElementById('filter-emotion-type')?.addEventListener('change', filterQuestions);

function filterQuestions() {
    const search = document.getElementById('search-questions').value.toLowerCase();
    const difficulty = document.getElementById('filter-difficulty').value;
    const emotion = document.getElementById('filter-emotion-type').value;
    
    let filtered = currentQuestions.filter(q => {
        const matchSearch = q.text.toLowerCase().includes(search);
        const matchDifficulty = !difficulty || q.difficulty === difficulty;
        const matchEmotion = !emotion || q.emotion === emotion;
        
        return matchSearch && matchDifficulty && matchEmotion;
    });
    
    renderQuestionsTable(filtered);
}

document.getElementById('add-question-btn')?.addEventListener('click', () => {
    editingQuestionId = null;
    document.getElementById('question-modal-title').textContent = '➕ Thêm Câu hỏi Mới';
    document.getElementById('question-form').reset();
    openModal('question-modal');
});

// Delete question
window.deleteQuestion = async function(id) {
    if (!confirm('⚠️ Bạn có chắc chắn muốn xóa câu hỏi này?')) {
        return;
    }
    
    try {
        console.log(`🔵 [DEBUG] DELETE → ${API_URL}/game_contents/${id}`);
        
        const res = await fetchWithAuth(`${API_URL}/game_contents/${id}`, {
            method: "DELETE"
        });
        
        console.log("🟣 [DEBUG] DELETE Response status:", res.status);
        
        if (!res.ok) {
            const err = await res.json();
            console.error("🔴 [DEBUG] DELETE Error response:", err);
            throw new Error(err.detail || "Lỗi xóa question");
        }
        
        showNotification('✅ Đã xóa câu hỏi thành công!', 'success');
        await loadQuestions();
        await updateDashboardStats();
        
    } catch (err) {
        console.error("❌ [DEBUG] deleteQuestion catch:", err);
        showNotification(`❌ ${err.message}`, 'error');
    }
};

// Load questions from API
async function loadQuestions() {
    try {
        console.log('📡 Loading questions from API...');
        
        const res = await fetchWithAuth(`${API_URL}/game_contents`);
        
        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || `HTTP ${res.status}`);
        }
        
        const data = await res.json();
        console.log('✅ Questions loaded:', data);
        
        // Map API data to internal format
        currentQuestions = (data.data?.contents || []).map(item => ({
            id: item.content_id,
            type: Object.keys(GAME_TYPES).find(key => GAME_TYPES[key].id === item.game_id) || 'unknown',
            text: item.question_text,
            difficulty: item.level === 1 ? 'easy' : (item.level === 2 ? 'medium' : 'hard'),
            emotion: item.emotion,
            correctAnswer: item.correct_answer,
            explanation: item.explanation,
            media_path: item.media_path,
            content_type: item.content_type,
            playCount: item.play_count || 0,
            created_at: item.created_at
        }));
        
        renderQuestionsTable(currentQuestions);
        
    } catch (err) {
        console.error("❌ Load questions error:", err);
        showNotification(`Lỗi tải questions: ${err.message}`, 'error');
        
        // Fallback to localStorage if API fails
        currentQuestions = getQuestionsFromLocalStorage();
        renderQuestionsTable(currentQuestions);
    }
}

// Fallback: Get from localStorage (for offline/dev mode)
function getQuestionsFromLocalStorage() {
    const stored = localStorage.getItem('adminQuestions');
    if (stored) return JSON.parse(stored);
    
    return [];
}

// Save to localStorage (backup only, primary storage is API)
function saveQuestions(questions) {
    localStorage.setItem('adminQuestions', JSON.stringify(questions));
}

// Render questions table
function renderQuestionsTable(questions) {
    const tbody = document.getElementById('questions-tbody');
    
    if (!tbody) {
        console.error("Không tìm thấy #questions-tbody trong DOM!");
        return;
    }
    
    if (questions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 30px;">Không có dữ liệu</td></tr>';
        return;
    }
    
    const typeLabels = {
        'face-recognition': '👤 Nhìn mặt đoán',
        'text-scenario': '📝 Tình huống text',
        'mimic-expression': '🎭 Bắt chước',
        'camera-detection': '📷 Camera AI',
        'situation-image': '🖼️ Tình huống ảnh',
        'cv-advanced': '🤖 CV Advanced'
    };
    
    tbody.innerHTML = questions.map(q => `
        <tr>
            <td>${String(q.id).substring(0, 8)}...</td>
            <td><span class="badge badge-info">${typeLabels[q.type] || q.type}</span></td>
            <td style="max-width: 300px;">${q.text || 'N/A'}</td>
            <td><span class="badge badge-${q.difficulty}">${q.difficulty.toUpperCase()}</span></td>
            <td>${getAnswerPreview(q)}</td>
            <td>${q.playCount || 0}</td>
            <td class="actions">
                <button class="btn btn-warning" onclick="editQuestion('${q.id}')">✏️</button>
                <button class="btn btn-danger" onclick="deleteQuestion('${q.id}')">🗑️</button>
            </td>
        </tr>
    `).join('');
}

function getAnswerPreview(q) {
    const emotionEmojis = {
        'happy': '😊', 'Vui vẻ': '😊',
        'sad': '😢', 'Buồn bã': '😢',
        'angry': '😠', 'Tức giận': '😠',
        'scared': '😨', 'Sợ hãi': '😨',
        'surprised': '😲', 'Ngạc nhiên': '😲',
        'disgusted': '🤢', 'Ghê tởm': '🤢'
    };
    
    const emoji = emotionEmojis[q.emotion] || emotionEmojis[q.correctAnswer] || '';
    const text = q.correctAnswer || q.emotion || 'N/A';
    
    return emoji + ' ' + text;
}

// Edit question
window.editQuestion = function(id) {
    editingQuestionId = id;
    const question = currentQuestions.find(q => q.id === id);
    
    if (!question) return;
    
    document.getElementById('question-modal-title').textContent = '✏️ Chỉnh sửa Câu hỏi';
    document.getElementById('question-text').value = question.text || '';
    document.getElementById('question-type').value = question.type || '';
    document.getElementById('question-difficulty').value = question.difficulty || 'easy';
    document.getElementById('question-explanation').value = question.explanation || '';
    
    // Trigger change để render đúng form
    handleQuestionTypeChange();
    
    // Load media if exists
    if (question.media_path && question.media_path !== '/fe/assets/images/cv_guide.jpg') {
        uploadedImages = [{
            name: 'existing_media',
            type: question.content_type === 'video' ? 'video/mp4' : 'image/jpeg',
            data: question.media_path
        }];
        
        const previewContainer = document.getElementById('image-preview');
        const isVideo = question.content_type === 'video';
        const mediaTag = isVideo 
            ? `<video src="${question.media_path}" controls></video>`
            : `<img src="${question.media_path}" alt="Preview">`;
        
        previewContainer.innerHTML = `
            <div class="image-preview-item">
                ${mediaTag}
                <button type="button" class="remove-image" onclick="removeImage(0)">×</button>
            </div>
        `;
    }
    
    // Set emotion answer
    setTimeout(() => {
        const emotionSelect = document.getElementById('emotion-answer');
        if (emotionSelect) {
            // Map Vietnamese to English key
            const emotionKey = Object.keys(EMOTION_MAP).find(
                key => EMOTION_MAP[key] === question.correctAnswer || key === question.emotion
            ) || question.emotion || question.correctAnswer;
            
            emotionSelect.value = emotionKey || '';
        }
        
        // Set hint if exists (for situation-image)
        const hintInput = document.getElementById('question-hint');
        if (hintInput && question.explanation && question.explanation.includes('| Gợi ý:')) {
            const parts = question.explanation.split('| Gợi ý:');
            document.getElementById('question-explanation').value = parts[0].trim();
            hintInput.value = parts[1].trim();
        }
    }, 100);
    
    openModal('question-modal');
};

// Submit form (Create/Update)
document.getElementById('question-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const type = document.getElementById('question-type').value;
    
    if (!type) {
        alert('⚠️ Vui lòng chọn loại game!');
        document.getElementById('question-type').focus();
        return;
    }
    
    // Chuẩn bị data theo format SQL
    const gameInfo = GAME_TYPES[type];
    const contentData = {
        game_id: gameInfo.id,
        level: parseInt(document.getElementById('question-difficulty').value === 'easy' ? 1 : 
                       document.getElementById('question-difficulty').value === 'medium' ? 2 : 3),
        content_type: null,
        media_path: null,
        question_text: document.getElementById('question-text').value,
        correct_answer: null,
        emotion: null,
        explanation: document.getElementById('question-explanation').value || null
    };
    
    // Nếu đang edit, thêm content_id
    if (editingQuestionId) {
        contentData.content_id = editingQuestionId;
    }
    
    // Xử lý theo loại game
    switch(type) {
        case 'face-recognition':
            if (uploadedImages.length === 0) {
                alert('⚠️ Vui lòng upload ảnh khuôn mặt!');
                return;
            }
            
            const emotion1 = document.getElementById('emotion-answer')?.value;
            if (!emotion1) {
                alert('⚠️ Vui lòng chọn cảm xúc!');
                return;
            }
            
            contentData.content_type = 'image';
            contentData.media_path = await uploadImageToServer(uploadedImages[0]);
            contentData.correct_answer = EMOTION_MAP[emotion1];
            contentData.emotion = EMOTION_MAP[emotion1];
            break;
            
        case 'text-scenario':
            const emotion2 = document.getElementById('emotion-answer')?.value;
            if (!emotion2) {
                alert('⚠️ Vui lòng chọn cảm xúc!');
                return;
            }
            
            contentData.content_type = 'text';
            contentData.media_path = null;
            contentData.correct_answer = EMOTION_MAP[emotion2];
            contentData.emotion = EMOTION_MAP[emotion2];
            break;
            
        case 'mimic-expression':
            if (uploadedImages.length === 0) {
                alert('⚠️ Vui lòng upload video demo!');
                return;
            }
            
            const emotion3 = document.getElementById('emotion-answer')?.value;
            if (!emotion3) {
                alert('⚠️ Vui lòng chọn cảm xúc!');
                return;
            }
            
            contentData.content_type = 'video';
            contentData.media_path = await uploadImageToServer(uploadedImages[0]);
            contentData.correct_answer = null;
            contentData.emotion = EMOTION_MAP[emotion3];
            break;
            
        case 'camera-detection':
            const emotion4 = document.getElementById('emotion-answer')?.value;
            
            contentData.content_type = 'image';
            if (uploadedImages.length > 0) {
                contentData.media_path = await uploadImageToServer(uploadedImages[0]);
            } else {
                contentData.media_path = '/fe/assets/images/cv_guide.jpg';
            }
            contentData.correct_answer = null;
            contentData.emotion = emotion4 ? EMOTION_MAP[emotion4] : null;
            break;
            
        case 'situation-image':
            if (uploadedImages.length === 0) {
                alert('⚠️ Vui lòng upload ảnh tình huống!');
                return;
            }
            
            const emotion5 = document.getElementById('emotion-answer')?.value;
            if (!emotion5) {
                alert('⚠️ Vui lòng chọn cảm xúc!');
                return;
            }
            
            contentData.content_type = 'image';
            contentData.media_path = await uploadImageToServer(uploadedImages[0]);
            contentData.correct_answer = EMOTION_MAP[emotion5];
            contentData.emotion = EMOTION_MAP[emotion5];
            
            const hint = document.getElementById('question-hint').value;
            if (hint && contentData.explanation) {
                contentData.explanation += ' | Gợi ý: ' + hint;
            } else if (hint) {
                contentData.explanation = 'Gợi ý: ' + hint;
            }
            break;
            
        case 'cv-advanced':
            if (uploadedImages.length === 0) {
                alert('⚠️ Vui lòng upload ảnh tình huống!');
                return;
            }
            
            const emotion6 = document.getElementById('emotion-answer')?.value;
            if (!emotion6) {
                alert('⚠️ Vui lòng chọn cảm xúc!');
                return;
            }
            
            if (!contentData.explanation) {
                alert('⚠️ Vui lòng nhập mô tả chi tiết tình huống!');
                return;
            }
            
            contentData.content_type = 'image';
            contentData.media_path = await uploadImageToServer(uploadedImages[0]);
            contentData.correct_answer = emotion6;
            contentData.emotion = emotion6;
            break;
    }
    
    // Gửi lên server
    try {
        let res;
        let url;
        let method;
        
        if (editingQuestionId) {
            method = "PUT";
            url = `${API_URL}/game_contents/${editingQuestionId}`;
        } else {
            method = "POST";
            url = `${API_URL}/game_contents`;
        }
        
        console.log(`🔵 [DEBUG] ${method} → ${url}`);
        console.log('🔵 [DEBUG] Data:', contentData);
        
        res = await fetchWithAuth(url, {
            method: method,
            body: JSON.stringify(contentData)
        });
        
        if (!res.ok) {
            const err = await res.json();
            console.error("🔴 [DEBUG] API Error:", err);
            throw new Error(err.detail || err.message || "Lỗi khi lưu");
        }
        
        const result = await res.json();
        console.log("🟢 [DEBUG] Success:", result);
        
        showNotification(`✅ ${editingQuestionId ? 'Đã cập nhật' : 'Đã thêm'} câu hỏi thành công!`, 'success');
        
        closeModal('question-modal');
        await loadQuestions();
        await updateDashboardStats();
        
    } catch (error) {
        console.error('❌ Error saving:', error);
        showNotification('❌ ' + error.message, 'error');
    }
});

// Helper function: Tạo UUID
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Helper function: Upload ảnh lên server
async function uploadImageToServer(imageData) {
    try {
        // Nếu đã là URL (đang edit), giữ nguyên
        if (typeof imageData.data === 'string' && imageData.data.startsWith('/')) {
            return imageData.data;
        }
        
        const formData = new FormData();
        
        // Convert base64 to blob
        const response = await fetch(imageData.data);
        const blob = await response.blob();
        
        formData.append('file', blob, imageData.name);
        formData.append('type', imageData.type);
        
        const uploadResponse = await fetchWithAuth(`${API_URL}/upload`, {
            method: 'POST',
            headers: {}, // Remove Content-Type để browser tự set với boundary
            body: formData
        });
        
        const result = await uploadResponse.json();
        
        if (result.success || result.status === 'success') {
            return result.filePath || result.data?.path;
        } else {
            throw new Error('Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        // Fallback: lưu base64 tạm thời
        return imageData.data;
    }
}

// ==========================================
// MODAL FUNCTIONS
// ==========================================
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
    document.body.style.overflow = 'auto';
}

document.querySelectorAll('.close').forEach(btn => {
    btn.addEventListener('click', () => {
        closeModal(btn.closest('.modal').id);
    });
});

document.getElementById('cancel-user-btn')?.addEventListener('click', () => closeModal('user-modal'));
document.getElementById('cancel-emotion-btn')?.addEventListener('click', () => closeModal('emotion-modal'));
document.getElementById('cancel-question-btn')?.addEventListener('click', () => closeModal('question-modal'));

document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal(modal.id);
    });
});

// ==========================================
// NOTIFICATION
// ==========================================
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
`;
document.head.appendChild(style);

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
    `;
    noti.textContent = message;
    document.body.appendChild(noti);

    setTimeout(() => {
        noti.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => noti.remove(), 300);
    }, 3000);
}

// ==========================================
// LOGOUT
// ==========================================
$('logout-btn')?.addEventListener('click', () => {
    if (confirm("Bạn có chắc chắn muốn đăng xuất?")) {
        localStorage.removeItem("currentUser");
        localStorage.removeItem("token");
        window.location.href = "../pages/login.html";
    }
});

// ==========================================
// DASHBOARD & CHARTS
// ==========================================
async function updateDashboardStats() {
    try {
        // Lấy dữ liệu từ API thay vì localStorage
        const res = await fetchWithAuth(`${API_URL}/dashboard/stats`);
        
        if (res.ok) {
            const result = await res.json();
            
            // Kiểm tra response format
            if (result.status === 'success' && result.data) {
                const data = result.data;
                $('total-users').textContent = data.total_users || 0;
                $('total-emotions').textContent = data.total_emotions || 0;
                $('total-questions').textContent = data.total_questions || 0;
                $('total-active').textContent = data.total_active || 0;
            } else {
                throw new Error('Invalid response format');
            }
        } else if (res.status === 401) {
            // Token hết hạn - redirect về login
            alert('⛔ Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!');
            localStorage.clear();
            window.location.href = '../pages/login.html';
        } else {
            throw new Error(`HTTP ${res.status}`);
        }
    } catch (err) {
        console.error('Error updating dashboard stats:', err);
        
        // Fallback: tính từ dữ liệu đã load
        const users = currentUsers;
        const emotions = getEmotions();
        const questions = currentQuestions;

        $('total-users').textContent = users.length;
        $('total-emotions').textContent = emotions.length;
        $('total-questions').textContent = questions.length;
        $('total-active').textContent = users.filter(u => u.status === 'active').length;
    }
}

// Biểu đồ Users theo Role
function createUsersRoleChart() {
    const users = currentUsers;
    const roleCounts = users.reduce((acc, user) => {
        acc[user.role] = (acc[user.role] || 0) + 1;
        return acc;
    }, {});

    const ctx = document.getElementById('usersRoleChart');
    if (!ctx) return;

    new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(roleCounts),
            datasets: [{
                data: Object.values(roleCounts),
                backgroundColor: [
                    '#667eea',
                    '#f093fb',
                    '#4facfe',
                    '#43e97b'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Biểu đồ Cảm xúc
function createEmotionsChart() {
    const emotions = getEmotions();
    const categoryCounts = emotions.reduce((acc, emotion) => {
        acc[emotion.category] = (acc[emotion.category] || 0) + 1;
        return acc;
    }, {});

    const ctx = document.getElementById('emotionsChart');
    if (!ctx) return;

    new Chart(ctx.getContext('2d'), {
        type: 'pie',
        data: {
            labels: Object.keys(categoryCounts),
            datasets: [{
                data: Object.values(categoryCounts),
                backgroundColor: [
                    '#ffd700',
                    '#4a90e2',
                    '#e74c3c',
                    '#9b59b6',
                    '#f39c12'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Biểu đồ Độ khó Câu hỏi
function createQuestionsDifficultyChart() {
    const questions = currentQuestions;
    const difficultyCounts = questions.reduce((acc, q) => {
        acc[q.difficulty] = (acc[q.difficulty] || 0) + 1;
        return acc;
    }, {});

    const ctx = document.getElementById('questionsDifficultyChart');
    if (!ctx) return;

    new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: Object.keys(difficultyCounts),
            datasets: [{
                label: 'Số lượng câu hỏi',
                data: Object.values(difficultyCounts),
                backgroundColor: [
                    '#2ecc71',
                    '#f39c12',
                    '#e74c3c'
                ],
                borderRadius: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Biểu đồ Trạng thái Users
function createUsersStatusChart() {
    const users = currentUsers;
    const statusCounts = users.reduce((acc, user) => {
        acc[user.status] = (acc[user.status] || 0) + 1;
        return acc;
    }, {});

    const ctx = document.getElementById('usersStatusChart');
    if (!ctx) return;

    new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(statusCounts).map(s => s === 'active' ? 'Hoạt động' : 'Không hoạt động'),
            datasets: [{
                data: Object.values(statusCounts),
                backgroundColor: [
                    '#2ecc71',
                    '#e74c3c'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Biểu đồ Tăng trưởng Users
function createUsersGrowthChart() {
    const users = currentUsers;
    const monthlyData = {};
    
    users.forEach(user => {
        if (user.created_at) {
            const month = new Date(user.created_at).toLocaleDateString('vi-VN', { month: 'short', year: 'numeric' });
            monthlyData[month] = (monthlyData[month] || 0) + 1;
        }
    });

    const ctx = document.getElementById('usersGrowthChart');
    if (!ctx) return;

    new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: Object.keys(monthlyData),
            datasets: [{
                label: 'Users mới',
                data: Object.values(monthlyData),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Biểu đồ Top Câu hỏi
function createTopQuestionsChart() {
    const questions = currentQuestions;
    const sorted = questions.sort((a, b) => (b.playCount || 0) - (a.playCount || 0)).slice(0, 10);

    const ctx = document.getElementById('topQuestionsChart');
    if (!ctx) return;

    new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: sorted.map((q, i) => `Câu ${i + 1}`),
            datasets: [{
                label: 'Lượt chơi',
                data: sorted.map(q => q.playCount || 0),
                backgroundColor: '#4facfe',
                borderRadius: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Khởi tạo tất cả biểu đồ
function initCharts() {
    createUsersRoleChart();
    createEmotionsChart();
    createQuestionsDifficultyChart();
    createUsersStatusChart();
    createUsersGrowthChart();
    createTopQuestionsChart();
}

// ==========================================
// LOAD SECTION DATA
// ==========================================
function loadDashboard() {
    loadUsers();
    loadEmotions();
    loadQuestions();
    
    // Đợi dữ liệu load xong rồi mới vẽ biểu đồ
    setTimeout(() => {
        updateDashboardStats();
        initCharts();
    }, 500);
}

function loadSectionData(section) {
    switch(section) {
        case 'dashboard':
            updateDashboardStats();
            initCharts();
            break;
        case 'users':
            loadUsers();
            break;
        case 'emotions':
            loadEmotions();
            break;
        case 'questions':
            loadQuestions();
            break;
    }
}

// ==========================================
// INITIALIZE
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    if (checkAdminRole()) {
        loadDashboard();
    }
});