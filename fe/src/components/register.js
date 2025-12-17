const API_URL = 'http://localhost:8000/users';

const showError = (msg) => {
    document.querySelector('#reg-error-message').textContent = msg || '';
    if (!document.querySelector('#reg-error-message')) {
        const errorDiv = document.createElement('div');
        errorDiv.id = 'reg-error-message';
        errorDiv.style.color = 'red';
        document.querySelector('.auth-form').insertBefore(errorDiv, document.querySelector('button'));
    }
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

const collectFormData = () => {
    const phoneInput = document.querySelector('#phone');
    const rawPhoneValue = phoneInput?.value;
    const gender = document.querySelector('#gender')?.value.trim() || 'other';
    const date_of_birth = document.querySelector('#birthdate')?.value || '';
    const birthDate = new Date(date_of_birth);
    const age = date_of_birth ? Math.max(0, Math.floor((new Date() - birthDate) / (365.25 * 24 * 60 * 60 * 1000))) : 0;
    const userData = {
        username: document.querySelector('#reg-username')?.value.trim() || '',
        email: document.querySelector('#email')?.value.trim() || '',
        password: document.querySelector('#reg-password')?.value || '',
        name: document.querySelector('#fullname')?.value.trim() || '',
        gender: gender,
        date_of_birth: date_of_birth ? new Date(date_of_birth).toISOString().split('T')[0] : '',
        phone_number: phoneInput?.value.trim() || '',
        role: 'child',
        age: age
    };
    console.log('Collected user data:', userData); // Log dữ liệu thu thập
    return userData;
};

const validateForm = (user) => {
    console.log('Validating user:', user);

    const valuesToCheck = Object.keys(user)
        .filter(key => key !== 'age') // Loại trừ trường age
        .map(key => user[key]);

    if (valuesToCheck.some(v => !v)) {
        console.log('Empty fields found:', user);
        return 'Vui lòng điền đầy đủ thông tin.';
    }

    if (!user.phone_number || !/^\d{10}$/.test(user.phone_number)) {
        console.log('Phone number issue:', user.phone_number);
        return 'Số điện thoại phải là 10 chữ số.';
    }
    if (new Date(user.date_of_birth) > new Date()) {
        return 'Ngày sinh không thể là tương lai.';
    }

    // Chắc chắn kiểm tra tuổi ở đây (sau khi kiểm tra đầy đủ thông tin)
    if (user.age <= 2) {
        return 'Tuổi của trẻ phải lớn hơn 2.';
    }

    if (!user.password || user.password.length <= 8 || !/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~`]+/.test(user.password)) {
        return 'Mật khẩu phải lớn hơn 8 ký tự và chứa ít nhất 1 ký tự đặc biệt.';
    }
    return null;
};

const handleRegister = async () => {
    showError('');
    const user = collectFormData();
    console.log('User data before send:', user); // Log dữ liệu trước khi gửi
    const errorMsg = validateForm(user);
    if (errorMsg) return showError(errorMsg);

    try {
        const res = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(user),
        });
        const data = await res.json();
        console.log('Response from server:', data); // Log phản hồi từ server
        if (res.ok && data.status === 'success') {
            showToast('Đăng ký thành công! Vui lòng đăng nhập.', 'success');
            setTimeout(() => {
                window.location.href = '/src/pages/login.html';
            }, 1200);
        } else {
            showError(data.message || 'Đăng ký thất bại. Vui lòng thử lại.');
        }
    } catch (err) {
        console.error('Fetch error:', err);
        showError('Lỗi kết nối server. Vui lòng kiểm tra lại.');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            handleRegister();
        });
    }
});