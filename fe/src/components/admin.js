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
        'vui vẻ': '😊',
        'buồn bã': '😢',
        'tức giận': '😠',
        'sợ hãi': '😨',
        'ngạc nhiên': '😲',
        'ghê tởm': '🤢'
    };
    return emojis[emotion] || '❓';
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
$('logout-btn')?.addEventListener('click', async () => {
    const doLogout = () => {
        sessionStorage.removeItem("currentUser");
        localStorage.removeItem("currentUser");
        window.location.href = "../pages/login.html";
    };

    if (window.egModal && typeof window.egModal.confirm === 'function') {
        const ok = await window.egModal.confirm(
            'Bạn có chắc chắn muốn đăng xuất không?',
            'Xác nhận đăng xuất',
            'Đăng xuất',
            'Hủy'
        );
        if (!ok) return;
        doLogout();
        return;
    }

    if (!window.egInlineConfirm) {
        window.egEnsureInlineConfirmModal = function () {
            if (document.getElementById('eg-confirm-overlay')) return;

            if (!document.getElementById('eg-confirm-style')) {
                const style = document.createElement('style');
                style.id = 'eg-confirm-style';
                style.textContent = `
                    .eg-confirm-overlay{position:fixed;inset:0;background:rgba(15,23,42,.55);backdrop-filter:blur(6px);display:none;align-items:center;justify-content:center;z-index:9999;padding:20px;}
                    .eg-confirm-overlay.is-open{display:flex;}
                    .eg-confirm-modal{width:min(520px,92vw);background:#fff;border-radius:16px;box-shadow:0 24px 60px rgba(15,23,42,.35);border:1px solid rgba(148,163,184,.35);overflow:hidden;}
                    .eg-confirm-header{padding:16px 18px;background:linear-gradient(135deg,rgba(25,118,210,.12),rgba(59,130,246,.08));font-weight:800;color:#0b3c7d;}
                    .eg-confirm-body{padding:16px 18px;color:#0f172a;line-height:1.5;white-space:pre-line;}
                    .eg-confirm-actions{display:flex;gap:10px;justify-content:flex-end;padding:14px 18px;background:#f8fafc;border-top:1px solid rgba(148,163,184,.28);}
                    .eg-confirm-btn{border:0;border-radius:999px;padding:10px 16px;font-weight:700;cursor:pointer;}
                    .eg-confirm-btn.cancel{background:#e2e8f0;color:#0f172a;}
                    .eg-confirm-btn.ok{background:linear-gradient(135deg,#2563eb,#3b82f6);color:#fff;}
                    .eg-confirm-btn:active{transform:scale(.98);}
                `;
                document.head.appendChild(style);
            }

            const overlay = document.createElement('div');
            overlay.id = 'eg-confirm-overlay';
            overlay.className = 'eg-confirm-overlay';
            overlay.innerHTML = `
                <div class="eg-confirm-modal" role="dialog" aria-modal="true" aria-labelledby="eg-confirm-title">
                    <div class="eg-confirm-header" id="eg-confirm-title"></div>
                    <div class="eg-confirm-body" id="eg-confirm-message"></div>
                    <div class="eg-confirm-actions">
                        <button type="button" class="eg-confirm-btn cancel" id="eg-confirm-cancel"></button>
                        <button type="button" class="eg-confirm-btn ok" id="eg-confirm-ok"></button>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);
        };

        window.egInlineConfirm = function (message, title, okText, cancelText) {
            window.egEnsureInlineConfirmModal();

            const overlay = document.getElementById('eg-confirm-overlay');
            const titleEl = document.getElementById('eg-confirm-title');
            const msgEl = document.getElementById('eg-confirm-message');
            const okBtn = document.getElementById('eg-confirm-ok');
            const cancelBtn = document.getElementById('eg-confirm-cancel');

            if (!overlay || !titleEl || !msgEl || !okBtn || !cancelBtn) {
                return Promise.resolve(confirm(message));
            }

            titleEl.textContent = title || 'Xác nhận';
            msgEl.textContent = message || '';
            okBtn.textContent = okText || 'OK';
            cancelBtn.textContent = cancelText || 'Hủy';

            return new Promise((resolve) => {
                const close = (result) => {
                    overlay.classList.remove('is-open');
                    okBtn.onclick = null;
                    cancelBtn.onclick = null;
                    overlay.onclick = null;
                    document.removeEventListener('keydown', onKeyDown);
                    resolve(result);
                };

                const onKeyDown = (e) => {
                    if (e.key === 'Escape') close(false);
                };

                okBtn.onclick = () => close(true);
                cancelBtn.onclick = () => close(false);
                overlay.onclick = (e) => {
                    if (e.target === overlay) close(false);
                };
                document.addEventListener('keydown', onKeyDown);

                overlay.classList.add('is-open');
                cancelBtn.focus();
            });
        };
    }

    const ok = await window.egInlineConfirm(
        'Bạn có chắc chắn muốn đăng xuất không?',
        'Xác nhận đăng xuất',
        'Đăng xuất',
        'Hủy'
    );
    if (!ok) return;
    doLogout();
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