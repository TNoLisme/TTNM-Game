// fe/src/components/login.js
const API_URL = 'http://localhost:8000';

const showError = (message) => {
    document.querySelector('#error-message').textContent = message || '';
};

const redirectToHome = (user) => {
    localStorage.setItem('currentUser', JSON.stringify(user));
    alert('Đăng nhập thành công!');
    window.location.href = '/src/pages/home.html';
};

const handleLogin = async (e) => {
    e.preventDefault();
    showError('');

    const username = document.querySelector('#username').value.trim();
    const password = document.querySelector('#password').value.trim();

    if (!username || !password) {
        return showError('Vui lòng nhập đầy đủ Username và Password.');
    }

    try {
        const res = await fetch(`${API_URL}/users/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        const data = await res.json();

        if (res.ok && data.success) {
            redirectToHome(data.user);
        } else {
            showError(data.message || 'Sai tên đăng nhập hoặc mật khẩu.');
        }
    } catch (err) {
        console.error(err);
        showError('Lỗi kết nối server. Vui lòng thử lại.');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.querySelector('#login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    const forgotLink = document.getElementById('forgot-password-link');
    if (forgotLink) {
        forgotLink.addEventListener('click', openForgotModal);
        console.log('Forgot link attached');
    } else {
        console.error('Forgot link not found');
    }
});

// ============ QUÊN MẬT KHẨU (GỌP 1 BƯỚC) ============
function openForgotModal(e) {
    e.preventDefault();
    const modal = document.getElementById('forgot-modal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('otp-pass-section').style.display = 'none';
        document.getElementById('reset-error').textContent = '';
        document.getElementById('forgot-email').value = '';
    }
}

function closeForgotModal() {
    const modal = document.getElementById('forgot-modal');
    if (modal) modal.style.display = 'none';
    document.getElementById('otp-pass-section').style.display = 'none';
    document.getElementById('reset-error').textContent = '';
}

// GỬI OTP → HIỆN FORM NHẬP OTP + PASS
async function sendOTP() {
    const email = document.getElementById('forgot-email').value.trim();
    if (!email) {
        showModalError('Vui lòng nhập email.');
        return;
    }

    try {
        const res = await fetch(`${API_URL}/users/forgot-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await res.json();

        if (res.ok) {
            document.getElementById('otp-pass-section').style.display = 'block';
            document.getElementById('send-otp-btn').style.display = 'none';
            showModalError('OTP đã gửi! Kiểm tra email.', 'green');
        } else {
            showModalError(data.detail || 'Lỗi gửi OTP.');
        }
    } catch (err) {
        console.error(err);
        showModalError('Lỗi kết nối server.');
    }
}

// ĐỔI MẬT KHẨU (GỌI 1 LẦN DUY NHẤT)
async function resetPasswordWithOTP() {
    const email = document.getElementById('forgot-email').value.trim();
    const otp = document.getElementById('forgot-otp').value.trim();
    const newPass = document.getElementById('new-password').value.trim();
    const confirmPass = document.getElementById('confirm-password').value.trim();

    if (!otp || otp.length !== 6) return showModalError('OTP phải 6 số.');
    if (newPass.length < 8) return showModalError('Mật khẩu mới phải ≥ 8 ký tự.');
    if (newPass !== confirmPass) return showModalError('Mật khẩu xác nhận không khớp.');

    try {
        const res = await fetch(`${API_URL}/users/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, otp, new_password: newPass })
        });
        const data = await res.json();

        if (res.ok) {
            alert('Đổi mật khẩu thành công!');
            closeForgotModal();
        } else {
            const msg = data.detail?.[0]?.msg || data.detail || 'OTP sai hoặc hết hạn.';
            showModalError(msg);
        }
    } catch (err) {
        console.error(err);
        showModalError('Lỗi kết nối server.');
    }
}

// HIỂN THỊ LỖI TRONG MODAL
function showModalError(msg, color = 'red') {
    const el = document.getElementById('reset-error');
    if (el) {
        el.textContent = msg;
        el.style.color = color;
    }
}