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
        const res = await fetch(`${API_URL}/login`, { // Sử dụng endpoint /auth/login
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
});