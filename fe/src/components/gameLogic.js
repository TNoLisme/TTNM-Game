document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.querySelector('#logout-button');
    const backBtn = document.querySelector('#back-button');

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            const doLogout = () => {
                localStorage.removeItem('currentUser');
                window.location.href = '/src/pages/login.html';
            };

            if (window.egModal && typeof window.egModal.confirm === 'function') {
                window.egModal
                    .confirm('Bạn có chắc chắn muốn đăng xuất không?', 'Xác nhận đăng xuất', 'Đăng xuất', 'Hủy')
                    .then((ok) => {
                        if (!ok) return;
                        doLogout();
                    });
                return;
            }

            if (!confirm('Bạn có chắc chắn muốn đăng xuất không?')) return;
            doLogout();
        });
    }

    if (backBtn) {
        backBtn.addEventListener('click', () => {
            window.history.back();
        });
    }
});