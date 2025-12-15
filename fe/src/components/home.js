// Logout & game navigation logic
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.querySelector('#logout-button');
    const profilebutton = document.querySelector('#profile-button');
    const goToGameSelectBtn = document.querySelector('#go-to-game-select'); // Nút Vào chơi mới

    logoutBtn?.addEventListener('click', () => {
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

    // Xử lý chuyển hướng cho nút 'Vào chơi'
    goToGameSelectBtn?.addEventListener('click', () => {
        window.location.href = '/src/pages/select_game.html';
    });

});

