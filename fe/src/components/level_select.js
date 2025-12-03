// Dữ liệu cấu hình giao diện Levels
const levelsConfig = [
    { num: 1, icon: '😊', name: 'Dễ' },
    { num: 2, icon: '❤️', name: 'Vui' },
    { num: 3, icon: '⭐', name: 'Hay' },
    { num: 4, icon: '✨', name: 'Giỏi' },
    { num: 5, icon: '☀️', name: 'Xuất sắc' },
    { num: 6, icon: '🌸', name: 'Tuyệt vời' },
    { num: 7, icon: '🌈', name: 'Siêu đẳng' },
    { num: 8, icon: '🎮', name: 'Cao thủ' }
];

// Mapping game ID sang file HTML
function getGameHtmlFile(gameId) {
    const map = {
        '6c2358b3-9720-446a-94a3-111edf1ce9e1': './recognize_emotion.html',
        'd74bbd1c-8940-4e98-94cf-5d2f29ee57a8': './game_click_2.html',
        'bc95c5d8-e01a-4895-96fa-ccae65a18dc2': './game_click_3.html',
        '91c00bab-78bf-4a2c-8d75-ee0b787fec1e': './game_click_4.html',
        'd9f34ee9-583c-453f-89ff-50f24aaa663b': './gameCV.html',
        '1c7a0065-7652-4f1f-bdf4-fdcb07cd4fc9': './game_cv_2.html'
    };
    return map[gameId];
}

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Lấy thông tin từ URL và LocalStorage
    const urlParams = new URLSearchParams(window.location.search);
    const gameId = urlParams.get('gameId');
    const user = JSON.parse(localStorage.getItem('currentUser'));

    console.log('Level Select - gameId:', gameId, 'user:', user);

    if (!gameId || !user) {
        alert('Thiếu thông tin game hoặc người dùng');
        window.location.href = './select_game.html';
        return;
    }

    // 2. Khởi tạo biến trạng thái
    let unlockedLevel = 1;
    let selectedLevel = null;
    let gameInfo = {};

    // 3. Fetch dữ liệu từ API (Logic của HEAD)
    try {
        const [gameRes, progressRes] = await Promise.all([
            fetch(`/games/${gameId}`),
            fetch(`/games/progress/${gameId}?user_id=${user.user_id}`)
        ]);

        if (!gameRes.ok) throw new Error('Không thể tải thông tin game');

        gameInfo = await gameRes.json();

        // Xử lý trường hợp chưa có progress (trả về null hoặc empty)
        if (progressRes.ok) {
            const progressData = await progressRes.json();
            if (progressData) {
                unlockedLevel = progressData.level || 1;
            }
        }

        // Cập nhật giao diện thông tin Game
        const headerTitle = document.querySelector('.header h1');
        if (headerTitle && gameInfo.name) headerTitle.textContent = `🎮 ${gameInfo.name} 🎮`;

    } catch (err) {
        console.error('Lỗi tải dữ liệu:', err);
        // Fallback nếu lỗi API: mặc định level 1
        unlockedLevel = 1;
    }

    // 4. Render giao diện
    const levelGrid = document.getElementById('levelGrid');
    const unlockedCountElem = document.getElementById('unlockedCount');
    const startButton = document.getElementById('startButton');
    const selectedMessage = document.getElementById('selectedMessage');
    const selectedLevelNum = document.getElementById('selectedLevelNum');

    // Cập nhật số lượng level đã mở trên UI
    if (unlockedCountElem) unlockedCountElem.textContent = unlockedLevel;

    // Hàm tạo nút level
    function renderLevels() {
        levelGrid.innerHTML = ''; // Xóa nội dung cũ

        levelsConfig.forEach(level => {
            const button = document.createElement('div');
            button.className = `level-button level-${level.num}`;
            button.dataset.level = level.num;

            const isUnlocked = level.num <= unlockedLevel;
            const isCompleted = level.num < unlockedLevel;

            // Xử lý trạng thái khóa/mở
            if (!isUnlocked) {
                button.classList.add('locked');
            }

            // Badge hoàn thành
            if (isCompleted) {
                const badge = document.createElement('div');
                badge.className = 'completed-badge';
                badge.innerHTML = '🏆';
                button.appendChild(badge);
            }

            // Icon
            const icon = document.createElement('div');
            icon.className = 'level-icon';
            icon.textContent = isUnlocked ? level.icon : '🔒';
            button.appendChild(icon);

            // Số level
            const number = document.createElement('div');
            number.className = 'level-number';
            number.textContent = level.num;
            button.appendChild(number);

            // Tên level
            const name = document.createElement('div');
            name.className = 'level-name';
            name.textContent = isUnlocked ? level.name : 'Đã khóa';
            button.appendChild(name);

            // Sự kiện click chọn level
            if (isUnlocked) {
                button.addEventListener('click', () => selectLevel(level.num));
            }

            levelGrid.appendChild(button);
        });
    }

    // Hàm xử lý khi chọn level
    function selectLevel(levelNum) {
        selectedLevel = levelNum;

        // Update visual selected state
        document.querySelectorAll('.level-button').forEach(btn => {
            if (parseInt(btn.dataset.level) === selectedLevel) {
                btn.classList.add('selected');
            } else {
                btn.classList.remove('selected');
            }
        });

        // Update Start Button state
        startButton.disabled = false;
        startButton.classList.remove('disabled');
        startButton.textContent = `🚀 Bắt Đầu Cấp ${selectedLevel}!`;

        // Show message
        selectedMessage.classList.remove('hidden');
        selectedLevelNum.textContent = selectedLevel;
    }

    // 5. Xử lý nút Bắt đầu Game (ĐÃ SỬA: CHỈ CHUYỂN TRANG, KHÔNG GỌI API)
    startButton.addEventListener('click', () => {
        if (!selectedLevel) return;

        // Hiệu ứng bấm nút
        startButton.textContent = '🚀 Đang vào game...';

        // Lấy đường dẫn file HTML tương ứng
        const gameFile = getGameHtmlFile(gameId);

        // Chuyển hướng ngay lập tức kèm tham số
        // recognize_emotion.js sẽ tự lo việc gọi API start
        window.location.href = `${gameFile}?level=${selectedLevel}&gameId=${gameId}`;
    });

    // 6. Xử lý Đăng xuất
    document.getElementById('logout-button')?.addEventListener('click', () => {
        localStorage.removeItem('currentUser');
        window.location.href = '/src/pages/login.html';
    });

    // Khởi chạy render lần đầu
    renderLevels();
});