const API_BASE = "http://localhost:8000";
const API_URL = `${API_BASE}/admin`;

function $(id) {
    return document.getElementById(id);
}

function getAuthToken() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        console.error('❌ No access token found!');
        if (window.egModal && typeof window.egModal.alert === 'function') {
            window.egModal
                .alert('⛔ Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!', 'Thông báo')
                .then(() => {
                    window.location.href = '../pages/login.html';
                });
        } else {
            alert('⛔ Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại!');
            window.location.href = '../pages/login.html';
        }
        return null;
    }
    return token;
}

async function fetchWithAuth(url, options = {}) {
    const token = getAuthToken();
    if (!token) throw new Error('No authentication token');

    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, // ⭐ GỬI TOKEN
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
    const accessToken = localStorage.getItem('access_token');

    console.log('%c🔍 CHECKING ADMIN ROLE:', 'color: blue; font-weight: bold;');
    console.log('currentUser:', currentUserStr);
    console.log('access_token:', accessToken ? 'EXISTS ✅' : 'MISSING ❌');

    if (!currentUserStr || !accessToken) {
        if (window.egModal && typeof window.egModal.alert === 'function') {
            window.egModal.alert('⛔ Bạn chưa đăng nhập!', 'Thông báo').then(() => {
                window.location.href = '../pages/login.html';
            });
        } else {
            alert('⛔ Bạn chưa đăng nhập!');
            window.location.href = '../pages/login.html';
        }
        return false;
    }

    const userData = JSON.parse(currentUserStr);
    const role = (userData.role || userData.accountType || '').toLowerCase().trim();

    if (role !== 'admin') {
        const msg = `⛔ Bạn không có quyền truy cập! Role của bạn: ${role}`;
        if (window.egModal && typeof window.egModal.alert === 'function') {
            window.egModal.alert(msg, 'Không có quyền').then(() => {
                window.location.href = '../pages/login.html';
            });
        } else {
            alert(msg);
            window.location.href = '../pages/login.html';
        }
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
        
        // Nếu lỗi 401/403, redirect về login
        if (err.message.includes('401') || err.message.includes('403')) {
            setTimeout(() => {
                localStorage.clear();
                window.location.href = '../pages/login.html';
            }, 2000);
        }
    }
}

function renderUsersTable(users) {
    const tbody = document.getElementById('users-tbody'); // FIXED

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

    $('user-password').required = false;
    $('user-password').placeholder = 'Để trống nếu không đổi';

    openModal('user-modal');
};

window.deleteUser = async (id) => {
    if (window.egModal && typeof window.egModal.confirm === 'function') {
        const ok = await window.egModal.confirm('⚠️ Bạn có chắc chắn muốn xóa user này?', 'Xác nhận xóa', 'Xóa', 'Hủy');
        if (!ok) return;
    } else {
        if (!confirm("⚠️ Bạn có chắc chắn muốn xóa user này?")) return;
    }

    try {
        
        const res = await fetchWithAuth(`${API_URL}/users/${id}`, {
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

// SUBMIT USER FORM
$('user-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
        username: $('user-username').value,
        email: $('user-email').value,
        name: $('user-name').value,
        role: $('user-role').value,
        age: $('user-age').value ? parseInt($('user-age').value) : null,
        gender: $('user-gender').value,
        status: $('user-status').value,
    };

    const passwordValue = $('user-password').value;
    if (passwordValue) data.password = passwordValue;

    try {
        let res;

        if (editingUserId) {
            
            res = await fetchWithAuth(`${API_URL}/users/${editingUserId}`, {
                method: "PUT",
                body: JSON.stringify(data),
            });
        } else {
            res = await fetchWithAuth(`${API_URL}/users`, {
                method: "POST",
                body: JSON.stringify(data),
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
// EMOTIONS / QUESTIONS
// (KHÔNG ĐỤNG TỚI – GIỮ NGUYÊN CODE CŨ CỦA ANH)
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
    
    // Default demo data
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

// Search Emotions
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

// Add Emotion
document.getElementById('add-emotion-btn')?.addEventListener('click', () => {
    editingEmotionId = null;
    document.getElementById('emotion-modal-title').textContent = '➕ Thêm Cảm xúc Mới';
    document.getElementById('emotion-form').reset();
    openModal('emotion-modal');
});

// Edit Emotion
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

// Delete Emotion
window.deleteEmotion = function(id) {
    if (window.egModal && typeof window.egModal.confirm === 'function') {
        window.egModal
            .confirm('⚠️ Bạn có chắc chắn muốn xóa cảm xúc này?', 'Xác nhận xóa', 'Xóa', 'Hủy')
            .then((ok) => {
                if (!ok) return;
                currentEmotions = currentEmotions.filter(e => e.id !== id);
                saveEmotions(currentEmotions);
                renderEmotionsGrid(currentEmotions);
                showNotification('✅ Đã xóa cảm xúc thành công!', 'success');
            });
        return;
    }
    if (confirm('⚠️ Bạn có chắc chắn muốn xóa cảm xúc này?')) {
        currentEmotions = currentEmotions.filter(e => e.id !== id);
        saveEmotions(currentEmotions);
        renderEmotionsGrid(currentEmotions);
        showNotification('✅ Đã xóa cảm xúc thành công!', 'success');
    }
};

// Save Emotion Form
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

let currentQuestions = [];
let editingQuestionId = null;

function loadQuestions() {
    currentQuestions = getQuestions();
    renderQuestionsTable(currentQuestions);
}

function getQuestions() {
    const stored = localStorage.getItem('adminQuestions');
    if (stored) return JSON.parse(stored);
    
    // Default demo data
    return [
        {
            id: 1,
            text: 'Khi bạn cảm thấy vui, bạn thường làm gì?',
            emotion: 'happy',
            difficulty: 'easy',
            answers: ['Cười', 'Khóc', 'La hét', 'Ngủ'],
            correctAnswer: 1,
            explanation: 'Khi vui, người ta thường cười',
            playCount: 150
        },
        {
            id: 2,
            text: 'Biểu hiện nào cho thấy bạn đang buồn?',
            emotion: 'sad',
            difficulty: 'medium',
            answers: ['Nhảy múa', 'Khóc', 'Hát hò', 'Chạy'],
            correctAnswer: 2,
            explanation: 'Khóc là biểu hiện phổ biến khi buồn',
            playCount: 120
        }
    ];
}

function saveQuestions(questions) {
    localStorage.setItem('adminQuestions', JSON.stringify(questions));
}

function renderQuestionsTable(questions) {
    const tbody = document.getElementById('questions-tbody');
    
    if (questions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 30px;">Không có dữ liệu</td></tr>';
        return;
    }
    
    const emotionEmojis = {
        happy: '😊',
        sad: '😢',
        angry: '😠',
        scared: '😨',
        surprised: '😲'
    };
    
    tbody.innerHTML = questions.map(q => `
        <tr>
            <td>${q.id}</td>
            <td style="max-width: 300px;">${q.text}</td>
            <td>${emotionEmojis[q.emotion] || ''} ${q.emotion}</td>
            <td><span class="badge badge-${q.difficulty}">${q.difficulty}</span></td>
            <td>${q.answers[q.correctAnswer - 1]}</td>
            <td>${q.playCount || 0}</td>
            <td class="actions">
                <button class="btn btn-warning" onclick="editQuestion(${q.id})">✏️</button>
                <button class="btn btn-danger" onclick="deleteQuestion(${q.id})">🗑️</button>
            </td>
        </tr>
    `).join('');
}

// Search & Filter Questions
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

// Add Question
document.getElementById('add-question-btn')?.addEventListener('click', () => {
    editingQuestionId = null;
    document.getElementById('question-modal-title').textContent = '➕ Thêm Câu hỏi Mới';
    document.getElementById('question-form').reset();
    openModal('question-modal');
});

// Edit Question
window.editQuestion = function(id) {
    editingQuestionId = id;
    const question = currentQuestions.find(q => q.id === id);
    
    if (question) {
        document.getElementById('question-modal-title').textContent = '✏️ Chỉnh sửa Câu hỏi';
        document.getElementById('question-text').value = question.text;
        document.getElementById('question-emotion').value = question.emotion;
        document.getElementById('question-difficulty').value = question.difficulty;
        
        question.answers.forEach((answer, i) => {
            document.getElementById(`answer-${i + 1}`).value = answer;
        });
        
        document.querySelector(`input[name="correct-answer"][value="${question.correctAnswer}"]`).checked = true;
        document.getElementById('question-explanation').value = question.explanation || '';
        
        openModal('question-modal');
    }
};

// Delete Question
window.deleteQuestion = function(id) {
    if (window.egModal && typeof window.egModal.confirm === 'function') {
        window.egModal
            .confirm('⚠️ Bạn có chắc chắn muốn xóa câu hỏi này?', 'Xác nhận xóa', 'Xóa', 'Hủy')
            .then((ok) => {
                if (!ok) return;
                currentQuestions = currentQuestions.filter(q => q.id !== id);
                saveQuestions(currentQuestions);
                renderQuestionsTable(currentQuestions);
                showNotification('✅ Đã xóa câu hỏi thành công!', 'success');
            });
        return;
    }
    if (confirm('⚠️ Bạn có chắc chắn muốn xóa câu hỏi này?')) {
        currentQuestions = currentQuestions.filter(q => q.id !== id);
        saveQuestions(currentQuestions);
        renderQuestionsTable(currentQuestions);
        showNotification('✅ Đã xóa câu hỏi thành công!', 'success');
    }
};

// Save Question Form
document.getElementById('question-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const questionData = {
        text: document.getElementById('question-text').value,
        emotion: document.getElementById('question-emotion').value,
        difficulty: document.getElementById('question-difficulty').value,
        answers: [
            document.getElementById('answer-1').value,
            document.getElementById('answer-2').value,
            document.getElementById('answer-3').value,
            document.getElementById('answer-4').value
        ],
        correctAnswer: parseInt(document.querySelector('input[name="correct-answer"]:checked').value),
        explanation: document.getElementById('question-explanation').value,
        playCount: 0
    };
    
    if (editingQuestionId) {
        const index = currentQuestions.findIndex(q => q.id === editingQuestionId);
        currentQuestions[index] = { ...currentQuestions[index], ...questionData };
        showNotification('✅ Đã cập nhật câu hỏi thành công!', 'success');
    } else {
        const newQuestion = { id: Date.now(), ...questionData };
        currentQuestions.push(newQuestion);
        showNotification('✅ Đã thêm câu hỏi mới thành công!', 'success');
    }
    
    saveQuestions(currentQuestions);
    renderQuestionsTable(currentQuestions);
    closeModal('question-modal');
});

function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
    document.body.style.overflow = 'auto';
}

// Close buttons
document.querySelectorAll('.close').forEach(btn => {
    btn.addEventListener('click', () => {
        closeModal(btn.closest('.modal').id);
    });
});

// Cancel buttons
document.getElementById('cancel-user-btn')?.addEventListener('click', () => closeModal('user-modal'));
document.getElementById('cancel-emotion-btn')?.addEventListener('click', () => closeModal('emotion-modal'));
document.getElementById('cancel-question-btn')?.addEventListener('click', () => closeModal('question-modal'));

// Close on outside click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal(modal.id);
    });
});

document.addEventListener('DOMContentLoaded', () => {
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
`;
document.head.appendChild(style);

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
    if (window.egModal && typeof window.egModal.confirm === 'function') {
        window.egModal.confirm('Bạn có chắc chắn muốn đăng xuất không?', 'Xác nhận đăng xuất', 'Đăng xuất', 'Hủy').then((ok) => {
            if (!ok) return;
            localStorage.removeItem("currentUser");
            localStorage.removeItem("access_token");
            window.location.href = "../pages/login.html";
        });
        return;
    }
    if (confirm("Bạn có chắc chắn muốn đăng xuất?")) {
        localStorage.removeItem("currentUser");
        localStorage.removeItem("access_token");
        window.location.href = "../pages/login.html";
    }
});

// ==========================================
// DASHBOARD LOAD
// ==========================================
function loadDashboard() {
    loadUsers();
    loadEmotions();
    loadQuestions();
}

function loadSectionData(section) {
    switch(section) {
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

document.addEventListener("DOMContentLoaded", () => {
    if (checkAdminRole()) {
        loadDashboard();
    }
});
