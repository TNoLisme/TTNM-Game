document.addEventListener('DOMContentLoaded', () => {
    const loginBtn = document.querySelector('#login-button');
    const registerBtn = document.querySelector('#register-button');

    loginBtn?.addEventListener('click', () => {
        window.location.href = '/src/pages/login.html';
    });

    registerBtn?.addEventListener('click', () => {
        window.location.href = '/src/pages/register.html';
    });
});
