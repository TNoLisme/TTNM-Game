// fe/src/components/level_select.js
document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const gameId = urlParams.get('gameId');
    const user = JSON.parse(localStorage.getItem('currentUser'));

    console.log('Level Select - gameId:', gameId, 'user:', user); // DEBUG
    if (!gameId || !user) {
        alert('Thiếu thông tin game hoặc người dùng');
        window.location.href = './select_game.html';
        return;
    }

    let gameInfo = {};
    let currentLevel = 1;
    try {
        const [gameRes, progressRes] = await Promise.all([
            fetch(`/games/${gameId}`),
            fetch(`/games/progress/${gameId}?user_id=${user.user_id}`)
        ]);
        gameInfo = await gameRes.json();
        const progressData = await progressRes.json();
        currentLevel = progressData.level || 1;
    } catch (err) {
        alert('Lỗi tải dữ liệu game');
        console.error(err);
        return;
    }

    document.getElementById('selected-game-name').textContent = gameInfo.name || 'Game';
    document.getElementById('game-description').textContent = gameInfo.description || 'Chọn level để chơi';

    const levelGrid = document.getElementById('level-grid');
    const startBtn = document.getElementById('start-game-btn');
    let selectedLevel = null;
    const TOTAL_LEVELS = gameInfo.level || 8;

    for (let i = 1; i <= TOTAL_LEVELS; i++) {
        const btn = document.createElement('button');
        btn.textContent = i;
        btn.className = 'level-btn';
        btn.dataset.level = i;
        btn.disabled = i > currentLevel;

        btn.addEventListener('click', () => {
            document.querySelectorAll('.level-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedLevel = i;
            startBtn.disabled = false;
        });

        levelGrid.appendChild(btn);
    }

    startBtn.addEventListener('click', async () => {
        if (!selectedLevel) return;

        try {
            const res = await fetch(`/games/start/${gameId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user.user_id,
                    game_id: gameId,
                    level: selectedLevel
                })
            });
            const data = await res.json();
            if (!data.session_id) throw new Error('Không tạo được session');

            const gameFile = getGameHtmlFile(gameId);
            window.location.href = `${gameFile}?sessionId=${data.session_id}&level=${selectedLevel}&gameId=${gameId}`;
        } catch (err) {
            alert('Lỗi bắt đầu game');
            console.error(err);
        }
    });

    function getGameHtmlFile(gameId) {
        const map = {
            'GC1': './recognize_emotion.html',
            'GC2': './game_click_2.html',
            'GC3': './game_click_3.html',
            'GC4': './game_click_4.html',
            'GV1': './gameCV.html',
            'GV2': './game_cv_2.html'
        };
        return map[gameId] || './recognize_emotion.html';
    }

    // ĐĂNG XUẤT
    document.getElementById('logout-button')?.addEventListener('click', () => {
        localStorage.removeItem('currentUser');
        window.location.href = '/src/pages/login.html';
    });
});