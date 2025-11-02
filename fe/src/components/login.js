const API_URL = 'http://localhost:8000';

const showError = (message) => {
    const errorEl = document.querySelector('#error-message');
    if (errorEl) {
        errorEl.textContent = message || '';
    }
};

const showToast = (message, type = 'success') => {
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ',
        warning: '⚠'
    };
    
    toast.innerHTML = `
        <div class="toast-icon">${icons[type]}</div>
        <div class="toast-message">${message}</div>
    `;
    
    toastContainer.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

const redirectToHome = (user) => { 
    localStorage.setItem('currentUser', JSON.stringify(user)); 
    
    showToast('Đăng nhập thành công! Chào mừng ' + (user.fullname || user.username), 'success');
    
    setTimeout(() => {
        window.location.href = '/src/pages/home.html';
    }, 1000);
}; 

const handleLogin = async (e) => { 
    e.preventDefault();
    showError(''); 

    const username = document.querySelector('#username').value.trim(); 
    const password = document.querySelector('#password').value.trim(); 

    if (!username || !password) { 
        return showError('Vui lòng nhập đầy đủ Username và Password.'); 
    } 

    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Đang đăng nhập...';

    try { 
        const res = await fetch(`${API_URL}/login`, {  
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify({ username, password }), 
        }); 
        const data = await res.json(); 

        if (res.ok && data.success) { 
            redirectToHome(data.user); 
        } else { 
            showError(data.message || 'Sai tên đăng nhập hoặc mật khẩu.');
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        } 
    } catch (err) { 
        console.error(err); 
        showError('Lỗi kết nối server. Vui lòng thử lại.');
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    } 
};

// ============ QUÊN MẬT KHẨU ============
function openForgotModal(e) {
    e.preventDefault();
    const modal = document.getElementById('forgot-modal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('otp-pass-section').style.display = 'none';
        document.getElementById('reset-error').textContent = '';
        document.getElementById('forgot-email').value = '';
        document.getElementById('send-otp-btn').style.display = 'block';
    }
}

function closeForgotModal() {
    const modal = document.getElementById('forgot-modal');
    if (modal) {
        modal.style.display = 'none';
        document.getElementById('otp-pass-section').style.display = 'none';
        document.getElementById('reset-error').textContent = '';
        document.getElementById('forgot-email').value = '';
        document.getElementById('forgot-otp').value = '';
        document.getElementById('new-password').value = '';
        document.getElementById('confirm-password').value = '';
        document.getElementById('send-otp-btn').style.display = 'block';
    }
}

// GỬI OTP
async function sendOTP() {
    const email = document.getElementById('forgot-email').value.trim();
    if (!email) {
        showModalError('Vui lòng nhập email.');
        return;
    }

    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showModalError('Email không hợp lệ.');
        return;
    }

    const sendBtn = document.getElementById('send-otp-btn');
    sendBtn.disabled = true;
    sendBtn.textContent = 'Đang gửi...';

    try {
        const res = await fetch(`${API_URL}/users/forgot-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await res.json();

        if (res.ok) {
            document.getElementById('otp-pass-section').style.display = 'block';
            sendBtn.style.display = 'none';
            showModalError('OTP đã gửi! Kiểm tra email.', 'green');
            showToast('✉️ Mã OTP đã được gửi đến email của bạn!', 'success');
        } else {
            showModalError(data.detail || 'Lỗi gửi OTP.');
            sendBtn.disabled = false;
            sendBtn.textContent = 'Gửi OTP';
        }
    } catch (err) {
        console.error(err);
        showModalError('Lỗi kết nối server.');
        sendBtn.disabled = false;
        sendBtn.textContent = 'Gửi OTP';
    }
}

// ĐỔI MẬT KHẨU
async function resetPasswordWithOTP() {
    const email = document.getElementById('forgot-email').value.trim();
    const otp = document.getElementById('forgot-otp').value.trim();
    const newPass = document.getElementById('new-password').value.trim();
    const confirmPass = document.getElementById('confirm-password').value.trim();

    if (!otp || otp.length !== 6) {
        showModalError('OTP phải 6 số.');
        return;
    }
    if (newPass.length < 8) {
        showModalError('Mật khẩu mới phải ≥ 8 ký tự.');
        return;
    }
    if (newPass !== confirmPass) {
        showModalError('Mật khẩu xác nhận không khớp.');
        return;
    }

    const resetBtn = document.getElementById('reset-pass-btn');
    resetBtn.disabled = true;
    resetBtn.textContent = 'Đang xử lý...';

    try {
        const res = await fetch(`${API_URL}/users/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, otp, new_password: newPass })
        });
        const data = await res.json();

        if (res.ok) {
            showToast('✅ Đổi mật khẩu thành công!', 'success');
            closeForgotModal();
        } else {
            const msg = data.detail?.[0]?.msg || data.detail || 'OTP sai hoặc hết hạn.';
            showModalError(msg);
            resetBtn.disabled = false;
            resetBtn.textContent = 'Đổi Mật Khẩu';
        }
    } catch (err) {
        console.error(err);
        showModalError('Lỗi kết nối server.');
        resetBtn.disabled = false;
        resetBtn.textContent = 'Đổi Mật Khẩu';
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

// ============ EVENT LISTENERS ============
document.addEventListener('DOMContentLoaded', () => {
    // Login form
    const loginForm = document.querySelector('#login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Forgot password link
    const forgotLink = document.getElementById('forgot-password-link');
    if (forgotLink) {
        forgotLink.addEventListener('click', openForgotModal);
    }

    // Close modal button
    const closeBtn = document.getElementById('close-modal');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeForgotModal);
    }

    // Send OTP button
    const sendOtpBtn = document.getElementById('send-otp-btn');
    if (sendOtpBtn) {
        sendOtpBtn.addEventListener('click', sendOTP);
    }

    // Reset password button
    const resetPassBtn = document.getElementById('reset-pass-btn');
    if (resetPassBtn) {
        resetPassBtn.addEventListener('click', resetPasswordWithOTP);
    }

    // Click outside modal to close
    const modal = document.getElementById('forgot-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeForgotModal();
            }
        });
    }

    // Enter key support for forgot email
    const forgotEmailInput = document.getElementById('forgot-email');
    if (forgotEmailInput) {
        forgotEmailInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendOTP();
            }
        });
    }
});