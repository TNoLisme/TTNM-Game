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

// === QUÊN MẬT KHẨU: 3 BƯỚC (EMAIL -> OTP -> ĐỔI MẬT KHẨU) ===
function openForgotModal(e) {
    e.preventDefault();
    const modal = document.getElementById('forgot-modal');
    modal.style.display = 'flex';
    document.getElementById('step-email').style.display = 'block';
    document.getElementById('step-otp').style.display = 'none';
    document.getElementById('step-reset').style.display = 'none';
    document.getElementById('reset-error').textContent = '';
    document.getElementById('forgot-email').value = '';
    document.getElementById('forgot-otp').value = '';
    document.getElementById('new-password').value = '';
    document.getElementById('confirm-password').value = '';
}

function closeForgotModal() {
    const modal = document.getElementById('forgot-modal');
    if (modal) modal.style.display = 'none';
    const stepEmail = document.getElementById('step-email');
    const stepOtp = document.getElementById('step-otp');
    const stepReset = document.getElementById('step-reset');
    if (stepEmail) stepEmail.style.display = 'block';
    if (stepOtp) stepOtp.style.display = 'none';
    if (stepReset) stepReset.style.display = 'none';
    const resetEl = document.getElementById('reset-error');
    if (resetEl) resetEl.textContent = '';
    const emailInput = document.getElementById('forgot-email');
    const otpInput = document.getElementById('forgot-otp');
    const newPassInput = document.getElementById('new-password');
    const confirmInput = document.getElementById('confirm-password');
    if (emailInput) emailInput.value = '';
    if (otpInput) otpInput.value = '';
    if (newPassInput) newPassInput.value = '';
    if (confirmInput) confirmInput.value = '';
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
            const stepEmail = document.getElementById('step-email');
            const stepOtp = document.getElementById('step-otp');
            if (stepEmail) stepEmail.style.display = 'none';
            if (stepOtp) stepOtp.style.display = 'block';
            showModalError('OTP đã gửi! Kiểm tra email.', 'green');
            showToast('OTP đã gửi, vui lòng kiểm tra email', 'success');
        } else {
            showModalError(data.detail || data.message || 'Lỗi gửi OTP.');
        }
    } catch (err) {
        showModalError('Lỗi kết nối.');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Gửi OTP';
    }
}

async function verifyOTP() {
    const email = document.getElementById('forgot-email').value.trim();
    const otp = document.getElementById('forgot-otp').value.trim();

    if (otp.length !== 6) {
        showModalError('OTP phải gồm 6 số.');
        return;
    }

    const btn = document.getElementById('verify-otp-btn');
    btn.disabled = true;
    btn.textContent = 'Đang kiểm tra...';

    try {
        const res = await fetch(`${API_URL}/users/verify-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, otp })
        });
        const data = await res.json();
        if (res.ok) {
            showModalError('OTP đúng, hãy tạo mật khẩu mới.', 'green');
            showToast('OTP chính xác!', 'success');
            const stepOtp = document.getElementById('step-otp');
            const stepReset = document.getElementById('step-reset');
            if (stepOtp) stepOtp.style.display = 'none';
            if (stepReset) stepReset.style.display = 'block';
        } else {
            showModalError(data.detail || data.message || 'OTP sai hoặc hết hạn.');
        }
    } catch (err) {
        showModalError('Lỗi kết nối.');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Xác nhận OTP';
    }
}

async function resetPasswordWithOTP() {
    const email = document.getElementById('forgot-email').value.trim();
    const otp = document.getElementById('forgot-otp').value.trim();
    const newPass = document.getElementById('new-password').value;
    const confirm = document.getElementById('confirm-password').value;

    if (otp.length !== 6) {
        showModalError('Mã OTP phải gồm 6 số.');
        return;
    }
    if (newPass.length < 8) {
        showModalError('Mật khẩu mới phải có ít nhất 8 ký tự.');
        return;
    }
    if (!/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>\/?`~]/.test(newPass)) {
        showModalError('Mật khẩu mới phải có ít nhất 8 ký tự và 1 ký tự đặc biệt.');
        return;
    }
    if (newPass !== confirm) {
        showModalError('Mật khẩu xác nhận không khớp.');
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
            let msg = 'Lỗi đổi mật khẩu.';
            if (res.status === 422) {
                msg = 'Mật khẩu mới không hợp lệ. Mật khẩu phải có ít nhất 8 ký tự và 1 ký tự đặc biệt.';
            } else if (data) {
                if (typeof data.detail === 'string') {
                    msg = data.detail;
                } else if (typeof data.message === 'string') {
                    msg = data.message;
                }
            }
            showModalError(msg);
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
    document.getElementById('verify-otp-btn')?.addEventListener('click', verifyOTP);
    document.getElementById('reset-pass-btn')?.addEventListener('click', resetPasswordWithOTP);
    document.getElementById('forgot-modal')?.addEventListener('click', (e) => e.target === e.currentTarget && closeForgotModal());
});