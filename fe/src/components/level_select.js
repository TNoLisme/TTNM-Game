

const GAME_DATA = {
    'GC1': { name: 'Nhận diện cảm xúc (Cơ bản)', description: 'Nhận diện các cảm xúc cơ bản qua hình ảnh, âm thanh, video.' },
    'GC2': { name: 'Xưởng Lắp Ghép Cảm Xúc', description: 'Lắp ghép các bộ phận khuôn mặt để tạo ra cảm xúc được yêu cầu.' },
    'GC3': { name: 'Ai đang biểu hiện cảm xúc gì', description: 'Ghép tên người với biểu cảm khuôn mặt phù hợp trong nhóm.' },
    'GC4': { name: 'Chọn cảm xúc theo tình huống', description: 'Xem các tình huống đời sống và chọn cảm xúc phù hợp.' },
    'GV1': { name: 'Biểu Cảm Theo Tình Huống', description: 'Biểu hiện cảm xúc khuôn mặt đúng với tình huống cho trước qua camera.' },
    'GV2': { name: 'Biểu Cảm Theo Yêu Cầu', description: 'Thể hiện cảm xúc khuôn mặt cụ thể được yêu cầu qua camera.' }
};

// Map gameId tới file HTML thực tế của game
const GAME_HTML_FILES = {
    'GC1': './game_click_1.html',
    'GC2': './game_click_2.html',
    'GC3': './game_click_3.html',
    'GC4': './game_click_4.html',
    'GV1': './game_cv_1.html',
    'GV2': './game_cv_2.html',
};

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const gameId = urlParams.get('gameId');
    const gameInfo = GAME_DATA[gameId];
    const gameHtmlFile = GAME_HTML_FILES[gameId]; 

    const levelGrid = document.getElementById('level-grid');
    const startGameBtn = document.getElementById('start-game-btn');
    let selectedLevel = null;
    const NUMBER_OF_LEVELS = 8; // Tổng số cấp độ

    if (!gameId || !gameInfo || !gameHtmlFile) {
        document.getElementById('selected-game-name').textContent = 'Lỗi: Không tìm thấy game hoặc đường dẫn.';
        document.getElementById('game-description').textContent = 'Vui lòng quay lại trang chọn game.';
        return;
    }

    // Cập nhật thông tin game
    document.getElementById('selected-game-name').textContent = gameInfo.name;
    document.getElementById('game-description').textContent = gameInfo.description;

    // Tạo các nút cấp độ (1-8)
    for (let i = 1; i <= NUMBER_OF_LEVELS; i++) {
        const button = document.createElement('button');
        button.textContent = i;
        button.classList.add('level-btn');
        button.setAttribute('data-level', i);
        
        button.addEventListener('click', () => {
            document.querySelectorAll('.level-btn').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            selectedLevel = i;
            startGameBtn.disabled = false;
        });
        levelGrid.appendChild(button);
    }

    // Xử lý nút Bắt đầu Game
    startGameBtn.addEventListener('click', () => {
        if (selectedLevel !== null) {
            // Chuyển hướng đến trang game thực tế, truyền ID game và cấp độ đã chọn
            window.location.href = `${gameHtmlFile}?gameId=${gameId}&level=${selectedLevel}`;
        } else {
            alert('Vui lòng chọn một cấp độ trước khi bắt đầu.');
        }
    });
    
    // Xử lý nút Đăng xuất (Nav bar)
    document.querySelector('#logout-button')?.addEventListener('click', () => {
        localStorage.removeItem('currentUser');
        window.location.href = '/src/pages/login.html'; 
    });
});