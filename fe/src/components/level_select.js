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

// Cấu hình 6 cảm xúc cho game "Thử thách cảm xúc" (game_cv_2)
const EMOTION_OPTIONS = [
    { key: 'vui',        icon: '😊', name: 'Vui vẻ' },
    { key: 'buồn',       icon: '😢', name: 'Buồn bã' },
    { key: 'ngạc nhiên', icon: '😲', name: 'Ngạc nhiên' },
    { key: 'tức giận',   icon: '😠', name: 'Tức giận' },
    { key: 'sợ hãi',     icon: '😨', name: 'Sợ hãi' },
    { key: 'ghê tởm',    icon: '🤢', name: 'Ghê tởm' }
];

// gameId trong DB của game "Thử thách cảm xúc" (game_cv_2)
const GAME_CV_REQUEST_ID = '61f5e09e-eefa-44c1-86e1-87dfceac3b8e'.toLowerCase();

function getGameHtmlFile(gameId) {
    const map = {
        '6c2358b3-9720-446a-94a3-111edf1ce9e1': './recognize_emotion.html',
        'd74bbd1c-8940-4e98-94cf-5d2f29ee57a8': './game_click_2.html',
        'bc95c5d8-e01a-4895-96fa-ccae65a18dc2': './game_click_3.html',
        '91c00bab-78bf-4a2c-8d75-ee0b787fec1e': './game_click_4.html',
        'd9f34ee9-583c-453f-89ff-50f24aaa663b': './gameCV.html',
        '1c7a0065-7652-4f1f-bdf4-fdcb07cd4fc9': './game_cv_2.html'
    };
    return map[gameId.toLowerCase()];
}

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Lấy thông tin từ URL và LocalStorage
    const urlParams = new URLSearchParams(window.location.search);
    const gameId = urlParams.get('gameId');
    const user = JSON.parse(localStorage.getItem('currentUser'));

    const isCvRequestGame = gameId && gameId.toLowerCase() === GAME_CV_REQUEST_ID; // game_cv_2

    console.log('Level Select - gameId:', gameId, 'user:', user);

    if (!gameId || !user) {
        const goBack = () => {
            window.location.href = './select_game.html';
        };
        if (window.egModal && typeof window.egModal.alert === 'function') {
            window.egModal.alert('Thiếu thông tin game hoặc người dùng', 'Thiếu thông tin').then(goBack);
        } else {
            alert('Thiếu thông tin game hoặc người dùng');
            goBack();
        }
        return;
    }

    // 2. Khởi tạo biến trạng thái
    let unlockedLevel = 1;
    let selectedLevel = null;
    let selectedEmotion = null;
    let gameInfo = {};
    let emotionScores = {};

    // 3. Fetch dữ liệu từ API
    try {
        const gameRes = await fetch(`/games/${gameId}`);
        if (!gameRes.ok) throw new Error('Không thể tải thông tin game');
        gameInfo = await gameRes.json();

        // Cập nhật tiêu đề theo tên game trong DB
        const headerTitle = document.querySelector('.header h1');
        if (headerTitle && gameInfo.name) headerTitle.textContent = `🎮 ${gameInfo.name} 🎮`;

        if (isCvRequestGame) {
            // Game "Thử thách cảm xúc": lấy điểm cao nhất cho từng cảm xúc
            const scoresRes = await fetch(`/games/cv/emotion-scores?user_id=${user.user_id}`);
            if (scoresRes.ok) {
                const scoresData = await scoresRes.json();
                emotionScores = scoresData.scores || {};
            }

            const subtitle = document.querySelector('.subtitle');
            if (subtitle) {
                subtitle.textContent = 'Chọn một cảm xúc để chơi';
            }

            // Game CV không dùng level, ẩn badge "Level đã mở"
            const progressBadge = document.querySelector('.progress-badge');
            if (progressBadge) {
                progressBadge.style.display = 'none';
            }
        } else {
            // Các game còn lại: dùng tiến trình level như cũ
            const progressRes = await fetch(`/games/progress/${gameId}?user_id=${user.user_id}`);
            if (progressRes.ok) {
                const progressData = await progressRes.json();
                if (progressData) {
                    unlockedLevel = progressData.level || 1;
                }
            }
        }

    } catch (err) {
        console.error('Lỗi tải dữ liệu:', err);
        // Fallback nếu lỗi API: mặc định level 1
        unlockedLevel = 1;
    }

    // 4. Render giao diện
    const levelGrid = document.getElementById('levelGrid');
    const unlockedCountElem = document.getElementById('unlockedCount');
    const container = document.querySelector('.container');
    const levelContainer = document.querySelector('.level-container');
    const header = document.querySelector('.header');

    const startButton = document.getElementById('startButton');
    const selectedMessage = document.getElementById('selectedMessage');
    const selectedLevelNum = document.getElementById('selectedLevelNum');

    // Cập nhật số lượng level đã mở trên UI (chỉ dùng cho game theo level)
    if (!isCvRequestGame && unlockedCountElem) unlockedCountElem.textContent = unlockedLevel;

    // Hàm tạo nút level (cho các game theo level thông thường)
    function renderLevels() {
        if (levelGrid) {
            levelGrid.classList.remove('emotion-grid');
        }
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
            icon.textContent = level.icon;
            button.appendChild(icon);

            // Nếu đang khóa: icon vẫn là emoji nhưng mờ đi, thêm badge khóa nhỏ ở góc
            if (!isUnlocked) {
                const lockBadge = document.createElement('div');
                lockBadge.className = 'lock-badge';
                lockBadge.textContent = '🔒';
                button.appendChild(lockBadge);
            }

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

    // Hàm tạo 6 ô cảm xúc cho game "Thử thách cảm xúc"
    function renderEmotionTiles() {
        if (!levelGrid) return;
        levelGrid.classList.add('emotion-grid');
        levelGrid.innerHTML = '';

        EMOTION_OPTIONS.forEach((emotion) => {
            const button = document.createElement('div');
            // Dùng thêm class emotion-tile để style riêng cho game Thử thách cảm xúc
            button.className = 'level-button emotion-tile';
            button.dataset.emotion = emotion.key;

            const rawScore = typeof emotionScores[emotion.key] === 'number' ? emotionScores[emotion.key] : 0;
            const score = Math.max(0, Math.min(100, rawScore));
            const displayPercent = Math.round(score);

            // Dùng biến CSS để đổ màu theo % (không dùng hiệu ứng "nước")
            button.style.setProperty('--score', `${score}%`);
            if (displayPercent >= 100) {
                button.classList.add('is-full');
            }

            // Nội dung phía trên nước
            const content = document.createElement('div');
            content.className = 'level-content';

            const icon = document.createElement('div');
            icon.className = 'level-icon';
            icon.textContent = emotion.icon;
            content.appendChild(icon);

            const name = document.createElement('div');
            name.className = 'level-name';
            name.textContent = emotion.name;
            content.appendChild(name);

            button.appendChild(content);

            // Hiển thị điểm cao nhất
            const scoreBadge = document.createElement('div');
            scoreBadge.className = 'score-display';
            scoreBadge.textContent = `${displayPercent}%`;

            button.appendChild(scoreBadge);

            // Chọn cảm xúc
            button.addEventListener('click', () => selectEmotion(emotion.key));

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

    // Hàm xử lý khi chọn cảm xúc cho game_cv_2
    function selectEmotion(emotionKey) {
        selectedEmotion = emotionKey;

        // Cập nhật trạng thái selected trên UI
        document.querySelectorAll('.level-button').forEach(btn => {
            if (btn.dataset.emotion === emotionKey) {
                btn.classList.add('selected');
            } else {
                btn.classList.remove('selected');
            }
        });

        // Kích hoạt nút bắt đầu
        startButton.disabled = false;
        startButton.classList.remove('disabled');

        const emotionConfig = EMOTION_OPTIONS.find(e => e.key === emotionKey);
        const label = emotionConfig ? emotionConfig.name : emotionKey;
        startButton.textContent = `🚀 Bắt đầu luyện ${label}`;

        // Thông điệp đã chọn
        if (selectedMessage) {
            selectedMessage.classList.remove('hidden');
            selectedLevelNum.textContent = label;
        }
    }

    // 5. Xử lý nút Bắt đầu Game (ĐÃ SỬA: CHỈ CHUYỂN TRANG, KHÔNG GỌI API)
    startButton.addEventListener('click', () => {
        // Game "Thử thách cảm xúc": cần chọn cảm xúc
        if (isCvRequestGame) {
            if (!selectedEmotion) return;

            startButton.textContent = '🚀 Đang vào game...';
            const gameFile = getGameHtmlFile(gameId);
            const emotionParam = encodeURIComponent(selectedEmotion);

            window.location.href = `${gameFile}?gameId=${gameId}&emotion=${emotionParam}`;
            return;
        }

        // Các game khác: chọn level như cũ
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

    // Khởi chạy render lần đầu
    if (isCvRequestGame) {
        if (container) {
            container.classList.add('cv2-mode');
        }
        if (header) {
            header.classList.add('cv2-mode');
        }
        if (levelContainer) {
            levelContainer.classList.add('cv2-mode');
        }

        const levelTitle = document.querySelector('.level-title');
        if (levelTitle) levelTitle.textContent = 'Chọn cảm xúc';

        if (startButton) startButton.textContent = '👆 Chọn cảm xúc để chơi';

        // Đổi nội dung thông báo đã chọn cho đúng ngữ cảnh cảm xúc
        if (selectedMessage) {
            selectedMessage.innerHTML = '✨ Bạn đã chọn cảm xúc <span id="selectedLevelNum"></span>! ✨';
        }

        renderEmotionTiles();
    } else {
        if (container) {
            container.classList.remove('cv2-mode');
        }
        if (header) {
            header.classList.remove('cv2-mode');
        }
        if (levelContainer) {
            levelContainer.classList.remove('cv2-mode');
        }
        renderLevels();
    }
});