// fe/src/components/select_game.js
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

        if (data.status !== 'success') throw new Error(data.message || 'Lỗi dữ liệu');

        games = data.games || [];
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
            <img src="${game.thumbnail || '/fe/assets/images/default_thumb.png'}" alt="${game.name}" class="game-thumb">
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