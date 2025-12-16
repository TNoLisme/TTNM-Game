// fe/src/components/select_game.js

// Ảnh nền cho từng game (dùng sẵn các ảnh ensemble trong assets)
const GAME_THUMBNAILS = {
    '3bcb2108-721c-4a15-a585-31f3084ed000': '/fe/assets/images/happy/ensemble.png',    // Chiếc hộp cảm xúc
    'aacaf79e-e15e-42a9-a3d1-a522720d919b': '/fe/assets/images/angry/ensemble.png',    // Thám tử cảm xúc
    '08bbffbf-d147-4556-bccb-b7621cafbf15': '/fe/assets/images/surprise/ensemble.png', // Cảm xúc đúng chỗ
    '33ecafaa-ec7e-40d2-9c67-ed0a29ac0051': '/fe/assets/images/disgust/ensemble.png',  // Xưởng lắp ghép cảm xúc
    '61f5e09e-eefa-44c1-86e1-87dfceac3b8e': '/fe/assets/images/fear/ensemble.png',     // Thử thách cảm xúc (CV2)
    'e05909f3-3dee-42a6-9a75-fd985b1bdf47': '/fe/assets/images/index_image.png',       // Câu chuyện trên khuôn mặt
};

function getGameThumbnail(game) {
    if (game.thumbnail) return game.thumbnail; // ưu tiên ảnh từ backend nếu có
    const id = (game.game_id || '').toLowerCase();
    if (GAME_THUMBNAILS[id]) return GAME_THUMBNAILS[id];
    // fallback chung
    return '/fe/assets/images/index_image.png';
}

document.addEventListener('DOMContentLoaded', async () => {
    const user = JSON.parse(localStorage.getItem('currentUser'));
    if (!user) {
        alert('Vui lòng đăng nhập!');
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
        alert('Không thể tải danh sách game. Vui lòng thử lại.');
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
        localStorage.removeItem('currentUser');
        window.location.href = '/src/pages/login.html';
    });
});