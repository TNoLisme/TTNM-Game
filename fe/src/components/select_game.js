// File: fe/src/components/select_game.js

document.addEventListener('DOMContentLoaded', () => {
    // 1. Logic Đăng xuất
    const logoutBtn = document.querySelector('#logout-button');
    logoutBtn?.addEventListener('click', () => {
        localStorage.removeItem('currentUser');
        window.location.href = '/src/pages/login.html'; 
    });
    
    // 2. Logic chuyển hướng game khi bấm nút Play
    const gameBlocks = document.querySelectorAll('.game-block');
    gameBlocks.forEach(block => {
        const playButton = block.querySelector('.play-btn');
        // Thay vì lấy URL, ta lấy ID của Game
        const gameId = block.getAttribute('data-game-id'); 

        playButton.addEventListener('click', () => {
            if (gameId) {
                // Chuyển hướng đến trang setup, truyền Game ID qua query parameter
                window.location.href = `./level_select.html?gameId=${gameId}`;
            } else {
                alert('Không tìm thấy ID trò chơi. Vui lòng kiểm tra lại cấu hình.');
            }
        });
    });
});