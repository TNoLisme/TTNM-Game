import { loadUsers, setupUserEvents } from './admin_users.js';
import { loadEmotionVideos, setupEmotionEvents } from './admin_ec.js';
import { loadGameContents, setupGameContentEvents } from './admin_gc.js';
import { loadReports, setupReportEvents } from './admin_reports.js'; // ✅ ADDED

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

function calculateAge(dateOfBirth) {
    if (!dateOfBirth) return null;
    const birthDate = new Date(dateOfBirth);
    const today = new Date();
    const age = Math.floor((today - birthDate) / (365.25 * 24 * 60 * 60 * 1000));
    return Math.max(0, age);
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
    loadReports(); // ✅ ADDED
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
        case 'reports': // ✅ ADDED
            loadReports();
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
        setupUserEvents();
        setupEmotionEvents();
        setupGameContentEvents();
        setupReportEvents(); // ✅ ADDED
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
    
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .badge-primary { background: #3498db; color: white; }
    .badge-success { background: #2ecc71; color: white; }
    .badge-warning { background: #f39c12; color: white; }
    
    .btn-icon {
        background: none;
        border: none;
        font-size: 18px;
        cursor: pointer;
        padding: 5px;
        transition: transform 0.2s;
    }
    
    .btn-icon:hover {
        transform: scale(1.2);
    }
`;
document.head.appendChild(style);

export { API_URL, $, fetchAPI, openModal, closeModal, showNotification, calculateAge, getEmotionEmoji };