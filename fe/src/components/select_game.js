// fe/src/components/select_game.js

// Ảnh nền cho từng game (dùng sẵn các ảnh ensemble trong assets)
const GAME_THUMBNAILS = {
    'ea2b5c7e-aec8-4f6e-a8bf-99d7b6a05dd8': '/fe/assets/images/recognize_emotion.png',    // Chiếc hộp cảm xúc
    '8573ebd6-23be-4ad9-bd4c-3794b1c4a4fa': '/fe/assets/images/game_click_4.png',    // Thám tử cảm xúc
    'e7b4826b-57ba-4569-953e-723da913d47c': '/fe/assets/images/game_click_3.png', // Cảm xúc đúng chỗ
    'ecefa8d8-b9f5-4d41-abf9-316e6b6cf25b': '/fe/assets/images/game_click_2.png',  // Xưởng lắp ghép cảm xúc
    'bbd1597f-02b1-4e20-b39b-31d27335d385': '/fe/assets/images/game_cv_2.png',     // Thử thách cảm xúc (CV2)
    '9b56e632-dd86-4868-9d74-e0c93125430a': '/fe/assets/images/gameCV.png',       // Câu chuyện trên khuôn mặt
};

function getGameThumbnail(game) {
    const id = (game.game_id || '').toLowerCase();
    if (GAME_THUMBNAILS[id]) return GAME_THUMBNAILS[id];
    // fallback chung
    return '/fe/assets/images/index_image.png';
}

document.addEventListener('DOMContentLoaded', async () => {
    const user = JSON.parse(localStorage.getItem('currentUser'));
    if (!user) {
        if (window.egModal && typeof window.egModal.alert === 'function') {
            await window.egModal.alert('Vui lòng đăng nhập!', 'Thông báo');
        } else {
            alert('Vui lòng đăng nhập!');
        }
        window.location.href = '/src/pages/login.html';
        return;
    }

    let games = [];
    try {
        // GỌI ĐÚNG: /api/games (nếu có prefix) HOẶC /games/ (nếu không)
        const res = await fetch('/games', {  // DÙNG /api/games
            headers: { 'Authorization': `Bearer ${user.token}` }
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();
        console.log('Dữ liệu game từ API:', data); // DEBUG

        if (!data) throw new Error(data.message || 'Lỗi dữ liệu');

        games = data || [];
    } catch (err) {
        console.error('Lỗi tải game:', err);
        if (window.egModal && typeof window.egModal.alert === 'function') {
            await window.egModal.alert('Không thể tải danh sách game. Vui lòng thử lại.', 'Lỗi');
        } else {
            alert('Không thể tải danh sách game. Vui lòng thử lại.');
        }
        return;
    }

    const clickList = document.getElementById('game-click-list');
    const cvList = document.getElementById('game-cv-list');

    games.forEach(game => {
        const block = document.createElement('div');
        block.className = 'game-block';
        block.dataset.gameId = game.game_id;

        block.innerHTML = `
            <img src="${getGameThumbnail(game)}" alt="${game.name}" class="game-thumb">
            <h3 class="game-name">${game.name}</h3>
            <p class="game-desc">${game.description || 'Chơi ngay!'}</p>
            <button class="play-btn">Chọn Level</button>
        `;

        const playBtn = block.querySelector('.play-btn');
        playBtn.addEventListener('click', () => {
            window.location.href = `./level_select.html?gameId=${game.game_id}`;
        });

        if (game.game_type === 'GameClick') {
            clickList.appendChild(block);
        } else if (game.game_type === 'GameCV') {
            cvList.appendChild(block);
        }
    });

    document.getElementById('logout-button')?.addEventListener('click', () => {
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
});