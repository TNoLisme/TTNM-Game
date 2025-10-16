const API_URL = 'http://localhost:5000/api';

const showError = (msg) => {
    document.querySelector('#reg-error-message').textContent = msg || '';
};

const collectFormData = () => ({
    username: document.querySelector('#reg-username').value.trim(),
    email: document.querySelector('#reg-email').value.trim(),
    password: document.querySelector('#reg-password').value,
    confirmPassword: document.querySelector('#reg-confirm-password').value,
    fullName: document.querySelector('#reg-fullname').value.trim(),
    birthDate: document.querySelector('#reg-birthdate').value,
    phone: document.querySelector('#reg-phone').value.trim(),
    address: document.querySelector('#reg-address').value.trim(),
});

const handleRegister = async () => {
    showError('');
    const user = collectFormData();
    const emptyField = Object.values(user).some(v => !v);

    if (emptyField) return showError('Vui lòng điền đầy đủ thông tin.');
    if (user.password !== user.confirmPassword) return showError('Mật khẩu nhập lại không khớp.');

    try {
        const res = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(user),
        });

        const data = await res.json();
        if (res.ok && data.success) {
            alert('Đăng ký thành công! Vui lòng đăng nhập.');
            window.location.href = '/src/pages/login.html';
        } else {
            showError(data.message || 'Đăng ký thất bại.');
        }
    } catch (err) {
        console.error(err);
        showError('Lỗi kết nối server.');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#register-button')?.addEventListener('click', handleRegister);
});
