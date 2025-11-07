const API_URL = 'http://localhost:8000';

// TOAST + ERROR
const showError = (message) => {
    const errorEl = document.querySelector('#error-message');
    if (errorEl) errorEl.textContent = message || '';
};

const showToast = (message, type = 'success') => {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-icon">${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</div>
        <div class="toast-message">${message}</div>
    `;
    container.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

// REDIRECT + LƯU USER ĐẦY ĐỦ
const redirectToHome = (userFromAPI) => {
    if (!userFromAPI || typeof userFromAPI !== 'object') {
        showError('Không thể đọc dữ liệu người dùng.');
        return;
    }

    const user_id = userFromAPI.user_id || userFromAPI.id || userFromAPI.user?.user_id;
    if (!user_id) {
        showError('Thiếu mã người dùng từ máy chủ. Vui lòng thử lại.');
        return;
    }

    const saveUser = { ...userFromAPI, user_id };
    localStorage.setItem('currentUser', JSON.stringify(saveUser));
    console.log('%c🚀 LƯU USER_ID:', 'color: blue;', saveUser);
    showToast('Chào mừng ' + (saveUser.name || saveUser.username || 'bạn'), 'success');
    setTimeout(() => location.href = '/src/pages/home.html', 1500);
};

// HANDLE LOGIN CHUẨN
const handleLogin = async (e) => {
    e.preventDefault();
    showError('');
    const username = document.querySelector('#username').value.trim();
    const password = document.querySelector('#password').value.trim();
    if (!username || !password) return showError('Nhập đầy đủ thông tin!');

    const btn = e.target.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Đang đăng nhập...';

    try {
        const res = await fetch(`${API_URL}/users/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();
        console.log('Login response:', data);  // DEBUG

        if (res.ok && (data.success || data.user)) {
            const user = data.user || data.data || data;
            redirectToHome(user);
            return;
        } else {
            throw new Error(data.message || data.detail || 'Sai tài khoản hoặc mật khẩu.');
        }
    } catch (err) {
        console.error('Login error:', err);
        showError(err.message || 'Lỗi kết nối server.');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Đăng nhập';
    }
};

// === QUÊN MẬT KHẨU (GIỮ NGUYÊN, CHỈ FIX NHỎ) ===
function openForgotModal(e) {
    e.preventDefault();
    const modal = document.getElementById('forgot-modal');
    modal.style.display = 'flex';
    document.getElementById('otp-pass-section').style.display = 'none';
    document.getElementById('reset-error').textContent = '';
    document.getElementById('forgot-email').value = '';
}

function closeForgotModal() {
    document.getElementById('forgot-modal').style.display = 'none';
    document.getElementById('otp-pass-section').style.display = 'none';
    document.getElementById('reset-error').textContent = '';
    document.getElementById('forgot-email').value = '';
    document.getElementById('forgot-otp').value = '';
    document.getElementById('new-password').value = '';
    document.getElementById('confirm-password').value = '';
}

async function sendOTP() {
    const email = document.getElementById('forgot-email').value.trim();
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        showModalError('Email không hợp lệ.');
        return;
    }
    const btn = document.getElementById('send-otp-btn');
    btn.disabled = true;
    btn.textContent = 'Đang gửi...';

    try {
        const res = await fetch(`${API_URL}/users/forgot-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById('otp-pass-section').style.display = 'block';
            btn.style.display = 'none';
            showModalError('OTP đã gửi! Kiểm tra email.', 'green');
            showToast('OTP sent!', 'success');
        } else {
            showModalError(data.detail || 'Lỗi gửi OTP.');
        }
    } catch (err) {
        showModalError('Lỗi kết nối.');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Gửi OTP';
    }
}

async function resetPasswordWithOTP() {
    const email = document.getElementById('forgot-email').value.trim();
    const otp = document.getElementById('forgot-otp').value.trim();
    const newPass = document.getElementById('new-password').value;
    const confirm = document.getElementById('confirm-password').value;

    if (otp.length !== 6 || newPass.length < 8 || newPass !== confirm) {
        showModalError('Kiểm tra OTP/Mật khẩu!');
        return;
    }

    const btn = document.getElementById('reset-pass-btn');
    btn.disabled = true;
    btn.textContent = 'Đang đổi...';

    try {
        const res = await fetch(`${API_URL}/users/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, otp, new_password: newPass })
        });
        const data = await res.json();
        if (res.ok) {
            showToast('Đổi mật khẩu thành công!', 'success');
            closeForgotModal();
        } else {
            showModalError(data.detail || 'OTP sai.');
        }
    } catch (err) {
        showModalError('Lỗi kết nối.');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Đổi Mật Khẩu';
    }
}

function showModalError(msg, color = 'red') {
    const el = document.getElementById('reset-error');
    el.textContent = msg;
    el.style.color = color;
}

// EVENT LISTENERS
document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#login-form')?.addEventListener('submit', handleLogin);
    document.getElementById('forgot-password-link')?.addEventListener('click', openForgotModal);
    document.getElementById('close-modal')?.addEventListener('click', closeForgotModal);
    document.getElementById('send-otp-btn')?.addEventListener('click', sendOTP);
    document.getElementById('reset-pass-btn')?.addEventListener('click', resetPasswordWithOTP);
    document.getElementById('forgot-modal')?.addEventListener('click', (e) => e.target === e.currentTarget && closeForgotModal());
});