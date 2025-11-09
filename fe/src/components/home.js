// Logout & game navigation logic
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.querySelector('#logout-button');
    const profilebutton = document.querySelector('#profile-button');
    const goToGameSelectBtn = document.querySelector('#go-to-game-select'); // Nút Vào chơi mới

    logoutBtn?.addEventListener('click', () => {
        localStorage.removeItem('currentUser');
        window.location.href = '/src/pages/login.html';
    });

    // Xử lý chuyển hướng cho nút 'Vào chơi'
    goToGameSelectBtn?.addEventListener('click', () => {
        window.location.href = '/src/pages/select_game.html';
    });

});
