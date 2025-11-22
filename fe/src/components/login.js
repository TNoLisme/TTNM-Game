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

const redirectBasedOnRole = (userFromAPI, accessToken) => {
    if (!userFromAPI || typeof userFromAPI !== 'object') {
        showError('Không thể đọc dữ liệu người dùng.');
        return;
    }

    const user_id = userFromAPI.user_id || userFromAPI.id || userFromAPI.user?.user_id;
    if (!user_id) {
        showError('Thiếu mã người dùng từ máy chủ. Vui lòng thử lại.');
        return;
    }

    // Lấy role từ accountType hoặc role field
    const role = (userFromAPI.accountType || userFromAPI.role || '').toLowerCase();
    
    // Lưu user info đầy đủ vào localStorage
    const saveUser = { ...userFromAPI, user_id, role };
    localStorage.setItem('currentUser', JSON.stringify(saveUser));
    
    // ⭐⭐⭐ LƯU ACCESS_TOKEN RIÊNG (QUAN TRỌNG!) ⭐⭐⭐
    if (accessToken) {
        localStorage.setItem('token', accessToken);
        console.log('%c✅ ACCESS_TOKEN ĐÃ LƯU:', 'color: green; font-weight: bold; font-size: 14px;', accessToken);
    } else {
        console.warn('⚠️ WARNING: No access_token received!');
    }

    console.log('%c🚀 LƯU USER:', 'color: blue; font-weight: bold;', saveUser);
    console.log('%c🔑 ROLE:', 'color: green; font-weight: bold;', role);

    // Redirect dựa trên role
    let redirectUrl = '/src/pages/home.html'; // Default cho child
    let welcomeMsg = 'Chào mừng ' + (saveUser.fullName || saveUser.name || saveUser.username || 'bạn');

    if (role === 'admin') {
        redirectUrl = '/src/pages/admin.html'; 
        welcomeMsg = '👋 Chào Admin ' + (saveUser.fullName || saveUser.username);
        console.log('%c🎯 REDIRECT TO ADMIN DASHBOARD', 'color: red; font-weight: bold;');
    } else if (role === 'child') {
        redirectUrl = '/src/pages/home.html'; // Trang home cho child
        console.log('%c🎯 REDIRECT TO HOME', 'color: blue; font-weight: bold;');
    } else {
        // Unknown role - redirect to default
        console.warn('⚠️ Unknown role:', role, '- redirecting to home');
    }

    showToast(welcomeMsg, 'success');
    
    // Redirect sau 1.5 giây
    setTimeout(() => {
        location.href = redirectUrl;
    }, 1500);
};

// HANDLE LOGIN CHUẨN (FIXED)
const handleLogin = async (e) => {
    e.preventDefault();
    showError('');
    const username = document.querySelector('#username').value.trim();
    const password = document.querySelector('#password').value.trim();
    
    if (!username || !password) {
        return showError('Nhập đầy đủ thông tin!');
    }

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
        console.log('%c📥 LOGIN RESPONSE:', 'color: purple; font-weight: bold;', data);
        console.log('%c📥 FULL DATA STRUCTURE:', 'color: orange; font-weight: bold;', JSON.stringify(data, null, 2));

        if (res.ok && (data.success || data.user || data.data)) {
            // ⭐ XỬ LÝ NHIỀU CẤU TRÚC RESPONSE KHÁC NHAU
            let user = null;
            let accessToken = null;
            
            // Cấu trúc 1: {success: true, user: {...}, access_token: "..."}
            if (data.user) {
                user = data.user;
                accessToken = data.access_token || data.token;
            }
            // Cấu trúc 2: {data: {user: {...}, access_token: "..."}}
            else if (data.data) {
                user = data.data.user || data.data;
                accessToken = data.data.access_token || data.data.token;
            }
            // Cấu trúc 3: Flat object {user_id, username, ..., access_token}
            else {
                user = data;
                accessToken = data.access_token || data.token;
            }
            
            // Kiểm tra có đủ dữ liệu không
            if (!user || !user.user_id) {
                throw new Error('Response thiếu thông tin user');
            }
            
            if (!accessToken) {
                console.error('⚠️ CRITICAL: No access_token in response!');
                throw new Error('Server không trả về access token');
            }
            
            console.log('%c✅ EXTRACTED USER:', 'color: blue; font-weight: bold;', user);
            console.log('%c✅ EXTRACTED TOKEN:', 'color: green; font-weight: bold;', accessToken);
            
            // Redirect dựa trên role (TRUYỀN TOKEN VÀO)
            redirectBasedOnRole(user, accessToken);
            return;
        } else {
            throw new Error(data.message || data.detail || 'Sai tài khoản hoặc mật khẩu.');
        }
    } catch (err) {
        console.error('%c❌ LOGIN ERROR:', 'color: red; font-weight: bold;', err);
        showError(err.message || 'Lỗi kết nối server.');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Đăng nhập';
    }
};

// === QUÊN MẬT KHẨU (GIỮ NGUYÊN) ===
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
    
    // DEBUG: Log current storage on page load
    console.log('%c🔍 DEBUG - Current Storage:', 'color: purple; font-weight: bold;');
    console.log('access_token:', localStorage.getItem('access_token'));
    console.log('currentUser:', localStorage.getItem('currentUser'));
});