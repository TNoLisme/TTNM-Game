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
    e.preventDefault(); // Ngăn hành vi submit mặc định
    showError('');

    const username = document.querySelector('#username').value.trim();
    const password = document.querySelector('#password').value.trim();

    if (!username || !password) {
        return showError('Vui lòng nhập đầy đủ Username và Password.');
    }

    try {
        const res = await fetch(`${API_URL}/login`, {  // Thêm /users
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
        loginForm.addEventListener('submit', handleLogin); // Gắn sự kiện submit vào form
    }

    // Thêm cho quên mật khẩu
    const forgotLink = document.getElementById('forgot-password-link');
    if (forgotLink) {
        forgotLink.addEventListener('click', handleForgotPassword);
        console.log('Forgot link attached');  // Debug: In ra nếu load OK
    } else {
        console.error('Forgot link not found - check ID in HTML');  // Debug nếu id sai
    }
});

// Thêm vào login.js
async function handleForgotPassword() {
    const email = prompt('Nhập email:');
    if (email) {
        const response = await fetch('http://127.0.0.1:8000/forgot-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await response.json();
        if (response.ok) {
            alert(data.message + ' (OTP in BE console)');  // Copy OTP từ console server
        } else {
            alert('Lỗi: ' + data.detail);
        }
    }
}