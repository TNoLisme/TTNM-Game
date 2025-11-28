

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
    'GV1': './gameCV.html',
    'GV2': './game_cv_2.html',
};

const EMOTION_OPTIONS = [
    { emotion: 'vui', label: 'Vui vẻ', icon: '😊' },
    { emotion: 'ngạc nhiên', label: 'Ngạc nhiên', icon: '😲' },
    { emotion: 'buồn', label: 'Buồn bã', icon: '😢' },
    { emotion: 'tức giận', label: 'Tức giận', icon: '😠' },
    { emotion: 'sợ hãi', label: 'Sợ hãi', icon: '😨' },
    { emotion: 'ghê tởm', label: 'Ghê tởm', icon: '🤢' },
];

const API_URL = "http://localhost:8000";

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const gameId = urlParams.get('gameId');
    const gameInfo = GAME_DATA[gameId];
    const gameHtmlFile = GAME_HTML_FILES[gameId];

    const levelGrid = document.getElementById('level-grid');
    const startGameBtn = document.getElementById('start-game-btn');
    const selectionPrompt = document.querySelector('.selection-prompt');
    let selectedLevel = null;
    let selectedEmotion = null;
    const NUMBER_OF_LEVELS = 8; // Tổng số cấp độ mặc định

    if (!gameId || !gameInfo || !gameHtmlFile) {
        document.getElementById('selected-game-name').textContent = 'Lỗi: Không tìm thấy game hoặc đường dẫn.';
        document.getElementById('game-description').textContent = 'Vui lòng quay lại trang chọn game.';
        return;
    }

    document.getElementById('selected-game-name').textContent = gameInfo.name;
    document.getElementById('game-description').textContent = gameInfo.description;

    if (gameId === 'GV2') {
        loadEmotionScores().then(() => {
            renderEmotionButtons();
        });
    } else {
        // Load completed levels for GV1 (Biểu Cảm Theo Tình Huống)
        loadCompletedLevels().then(() => {
            renderLevelButtons();
        });
    }

    startGameBtn.addEventListener('click', () => {
        if (gameId === 'GV2') {
            if (!selectedEmotion) {
                alert('Vui lòng chọn cảm xúc muốn chơi.');
                return;
            }
            window.location.href = `${gameHtmlFile}?gameId=${gameId}&emotion=${encodeURIComponent(selectedEmotion)}`;
        } else if (selectedLevel !== null) {
            window.location.href = `${gameHtmlFile}?gameId=${gameId}&level=${selectedLevel}`;
        } else {
            alert('Vui lòng chọn một cấp độ trước khi bắt đầu.');
        }
    });

    document.querySelector('#logout-button')?.addEventListener('click', () => {
        localStorage.removeItem('currentUser');
        window.location.href = '/src/pages/login.html';
    });

    async function loadCompletedLevels() {
        try {
            const userStr = localStorage.getItem('currentUser');
            if (!userStr) return;
            
            const user = JSON.parse(userStr);
            const userId = user.user_id || user.id;
            
            if (!userId) return;
            
            const response = await fetch(`${API_URL}/games/cv/completed-levels?user_id=${userId}`);
            if (response.ok) {
                const data = await response.json();
                completedLevels = data.completed_levels || [];
                console.log('📊 Completed levels:', completedLevels);
            } else {
                console.error('Failed to load completed levels:', response.status, response.statusText);
            }
        } catch (error) {
            console.error('Error loading completed levels:', error);
        }
    }

    function renderLevelButtons() {
        for (let i = 1; i <= NUMBER_OF_LEVELS; i++) {
            const button = document.createElement('button');
            button.classList.add('level-btn');
            button.setAttribute('data-level', i);
            
            // Level 1 luôn unlock, level N chỉ unlock nếu level N-1 đã completed
            const isUnlocked = i === 1 || completedLevels.includes(i - 1);
            
            if (isUnlocked) {
                button.textContent = i;
                button.disabled = false;
            } else {
                button.innerHTML = '🔒';
                button.classList.add('level-locked');
                button.disabled = true;
                button.title = `Hoàn thành level ${i - 1} để mở khóa level ${i}`;
            }

            if (isUnlocked) {
                button.addEventListener('click', () => {
                    levelGrid.querySelectorAll('.level-btn').forEach(btn => btn.classList.remove('active'));
                    button.classList.add('active');
                    selectedLevel = i;
                    startGameBtn.disabled = false;
                });
            }

            levelGrid.appendChild(button);
        }
    }

    let emotionScores = {}; // Lưu điểm cao nhất của các cảm xúc
    let completedLevels = []; // Lưu danh sách level đã hoàn thành (cho GV1)

    async function loadEmotionScores() {
        try {
            const userStr = localStorage.getItem('currentUser');
            if (!userStr) return;
            
            const user = JSON.parse(userStr);
            const userId = user.user_id || user.id;
            
            if (!userId) return;
            
            const response = await fetch(`${API_URL}/games/cv/emotion-scores?user_id=${userId}`);
            if (response.ok) {
                const data = await response.json();
                emotionScores = data.scores || {};
                console.log('📊 Raw emotion scores from API:', emotionScores);
                
                // Normalize emotion names to lowercase for matching
                const normalizedScores = {};
                for (const [emotion, score] of Object.entries(emotionScores)) {
                    const emotionLower = emotion.toLowerCase().trim();
                    normalizedScores[emotionLower] = score;
                    console.log(`   Mapped: "${emotion}" -> "${emotionLower}" = ${score}%`);
                }
                emotionScores = normalizedScores;
                console.log('📊 Normalized emotion scores:', emotionScores);
                
                // Debug: Check if all emotions have scores
                const expectedEmotions = ['vui', 'buồn', 'ngạc nhiên', 'tức giận', 'sợ hãi', 'ghê tởm'];
                expectedEmotions.forEach(emotion => {
                    if (!(emotion in emotionScores)) {
                        console.log(`   ⚠️ Missing score for emotion: "${emotion}"`);
                    }
                });
            } else {
                console.error('Failed to load emotion scores:', response.status, response.statusText);
            }
        } catch (error) {
            console.error('Error loading emotion scores:', error);
        }
    }

    function renderEmotionButtons() {
        levelGrid.classList.add('emotion-grid');
        selectionPrompt.textContent = 'Chọn cảm xúc muốn chơi';
        startGameBtn.textContent = 'Bắt đầu chơi';
        startGameBtn.disabled = true;

        EMOTION_OPTIONS.forEach(option => {
            const button = document.createElement('button');
            button.classList.add('level-btn', 'emotion-btn');
            button.setAttribute('data-emotion', option.emotion);
            
            // Lấy điểm cao nhất (0-100), normalize emotion name
            const emotionKey = option.emotion.toLowerCase().trim();
            
            // Thử match với nhiều cách: exact match, với dấu, không dấu
            let bestScore = emotionScores[emotionKey] || 
                           emotionScores[option.emotion] || 
                           emotionScores[option.emotion.toLowerCase()] || 
                           emotionScores[option.emotion.trim()] || 0;
            
            // Nếu vẫn không tìm thấy, thử tìm trong tất cả keys
            if (bestScore === 0 && Object.keys(emotionScores).length > 0) {
                const allKeys = Object.keys(emotionScores);
                console.log(`   🔍 Searching for "${emotionKey}" in emotionScores keys:`, allKeys);
                
                // Thử match bằng cách so sánh từng từ
                for (const key of allKeys) {
                    const keyLower = key.toLowerCase().trim();
                    const emotionWords = emotionKey.split(/\s+/);
                    const keyWords = keyLower.split(/\s+/);
                    
                    // Nếu có từ nào trùng thì match
                    if (emotionWords.some(word => keyWords.includes(word)) || 
                        keyWords.some(word => emotionWords.includes(word))) {
                        bestScore = emotionScores[key];
                        console.log(`   ✅ Matched "${emotionKey}" with "${key}" = ${bestScore}%`);
                        break;
                    }
                }
            }
            
            // Đảm bảo điểm trong khoảng 0-100
            bestScore = Math.max(0, Math.min(100, parseFloat(bestScore) || 0));
            
            console.log(`🎨 Emotion: ${option.emotion} (key: "${emotionKey}"), Score: ${bestScore.toFixed(2)}% (thang 100)`);
            
            // Debug: Log nếu score = 0 để biết có phải do chưa chơi không
            if (bestScore === 0) {
                console.log(`   ⚠️ Score is 0 for "${option.emotion}" - may not have been played yet`);
            }
            
            // Nếu đạt 100%, thêm class để đổi màu xanh lá cây
            if (bestScore >= 100) {
                button.classList.add('emotion-perfect');
            }
            
            button.innerHTML = `
                <span class="emotion-icon">${option.icon}</span>
                <span class="emotion-label">${option.label}</span>
                <div class="water-fill"></div>
            `;
            
            // Set height sau khi render để animation hoạt động
            requestAnimationFrame(() => {
                const waterFill = button.querySelector('.water-fill');
                if (waterFill) {
                    // Reset về 0 trước, sau đó animate lên
                    waterFill.style.height = '0%';
                    requestAnimationFrame(() => {
                        // Đảm bảo height là % (0-100)
                        // Nếu bestScore > 0 thì set height, nếu = 0 thì giữ 0% (không đổ nước)
                        if (bestScore > 0) {
                            waterFill.style.height = `${bestScore}%`;
                            console.log(`   💧 Set water-fill height to ${bestScore}% for ${option.emotion}`);
                        } else {
                            waterFill.style.height = '0%';
                            console.log(`   ⚠️ No water-fill for ${option.emotion} (score = 0)`);
                        }
                    });
                } else {
                    console.error(`   ❌ Water-fill element not found for ${option.emotion}`);
                }
            });

            button.addEventListener('click', () => {
                levelGrid.querySelectorAll('.emotion-btn').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                selectedEmotion = option.emotion;
                startGameBtn.disabled = false;
            });

            levelGrid.appendChild(button);
        });
    }
});