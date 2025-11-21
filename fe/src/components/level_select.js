// Dữ liệu levels
const levels = [
    { num: 1, icon: '😊', name: 'Dễ' },
    { num: 2, icon: '❤️', name: 'Vui' },
    { num: 3, icon: '⭐', name: 'Hay' },
    { num: 4, icon: '✨', name: 'Giỏi' },
    { num: 5, icon: '☀️', name: 'Xuất sắc' },
    { num: 6, icon: '🌸', name: 'Tuyệt vời' },
    { num: 7, icon: '🌈', name: 'Siêu đẳng' },
    { num: 8, icon: '🎮', name: 'Cao thủ' }
];

// Trạng thái game
let unlockedLevel = 1; // Level cao nhất đã mở khóa
let selectedLevel = null;

// Khởi tạo game
function initGame() {
    const levelGrid = document.getElementById('levelGrid');
    
    // Tạo các nút level
    levels.forEach(level => {
        const levelButton = createLevelButton(level);
        levelGrid.appendChild(levelButton);
    });
    
    updateUI();
}

// Tạo nút level
function createLevelButton(level) {
    const button = document.createElement('div');
    button.className = `level-button level-${level.num}`;
    button.dataset.level = level.num;
    
    const isUnlocked = level.num <= unlockedLevel;
    const isCompleted = level.num < unlockedLevel;
    
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
    
    // Sự kiện click
    if (isUnlocked) {
        button.addEventListener('click', () => selectLevel(level.num));
    }
    
    return button;
}

// Chọn level
function selectLevel(levelNum) {
    selectedLevel = levelNum;
    updateUI();
}

// Cập nhật giao diện
function updateUI() {
    // Cập nhật các nút level
    const allButtons = document.querySelectorAll('.level-button');
    allButtons.forEach(button => {
        const levelNum = parseInt(button.dataset.level);
        
        if (levelNum === selectedLevel) {
            button.classList.add('selected');
        } else {
            button.classList.remove('selected');
        }
    });
    
    // Cập nhật nút bắt đầu
    const startButton = document.getElementById('startButton');
    if (selectedLevel) {
        startButton.disabled = false;
        startButton.classList.remove('disabled');
        startButton.textContent = `🚀 Bắt Đầu Cấp ${selectedLevel}!`;
    } else {
        startButton.disabled = true;
        startButton.classList.add('disabled');
        startButton.textContent = '👆 Chọn level để chơi';
    }
    
    // Cập nhật thông báo đã chọn
    const selectedMessage = document.getElementById('selectedMessage');
    const selectedLevelNum = document.getElementById('selectedLevelNum');
    if (selectedLevel) {
        selectedMessage.classList.remove('hidden');
        selectedLevelNum.textContent = selectedLevel;
    } else {
        selectedMessage.classList.add('hidden');
    }
    
    // Cập nhật thanh tiến độ
    document.getElementById('unlockedCount').textContent = unlockedLevel;
    document.getElementById('currentLevel').textContent = unlockedLevel;
}

// Bắt đầu game
function startGame() {
    if (!selectedLevel) return;
    
    alert(`🎮 Bắt đầu cấp độ ${selectedLevel}!\n\n(Demo: Sau khi chơi xong, level tiếp theo sẽ tự động mở khóa)`);
    
    // Nếu hoàn thành level hiện tại, mở khóa level tiếp theo
    if (selectedLevel === unlockedLevel && unlockedLevel < 8) {
        setTimeout(() => {
            unlockedLevel++;
            alert(`🎉 Chúc mừng! Bạn đã mở khóa Level ${unlockedLevel}!`);
            
            // Làm mới giao diện
            const levelGrid = document.getElementById('levelGrid');
            levelGrid.innerHTML = '';
            levels.forEach(level => {
                const levelButton = createLevelButton(level);
                levelGrid.appendChild(levelButton);
            });
            
            selectedLevel = null;
            updateUI();
        }, 1000);
    }
}

// Sự kiện nút bắt đầu
document.getElementById('startButton').addEventListener('click', startGame);

// Khởi động game khi trang load
document.addEventListener('DOMContentLoaded', function() {
    initGame();
});