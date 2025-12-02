// Dữ liệu nhân vật
const CHARACTERS_POOL = [{
        id: '1',
        name: 'An',
        emotion: 'vui vẻ',
        image: 'https://images.unsplash.com/photo-1610103278906-6c96a3b2c1f0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoYXBweSUyMGNoaWxkJTIwZmFjZXxlbnwxfHx8fDE3NjM2Mjg0ODl8MA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
        id: '2',
        name: 'Bình',
        emotion: 'buồn',
        image: 'https://images.unsplash.com/photo-1610103278906-6c96a3b2c1f0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzYWQlMjBjaGlsZCUyMGZhY2V8ZW58MXx8fHwxNzYzNjg4NzYwfDA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
        id: '3',
        name: 'Chi',
        emotion: 'giận',
        image: 'https://images.unsplash.com/photo-1620415061840-07c8e4928959?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhbmdyeSUyMGNoaWxkJTIwZmFjZXxlbnwxfHx8fDE3NjM2ODg3NjB8MA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
        id: '4',
        name: 'Dũng',
        emotion: 'ngạc nhiên',
        image: 'https://images.unsplash.com/photo-1621451683587-8be65b8b975c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdXJwcmlzZWQlMjBjaGlsZCUyMGZhY2V8ZW58MXx8fHwxNzYzNjg4NzYwfDA&ixlib=rb-4.1.0&q=80&w=1080',
    },
];

// Trạng thái game
let gameState = {
    difficulty: 'easy',
    characters: [],
    answers: {},
    submitted: false,
    results: {},
    currentLevel: 1, // Level hiện tại (1 = dễ, 2 = vừa, 3 = khó)
};

// Tự động bắt đầu game khi trang load
window.addEventListener('DOMContentLoaded', () => {
    initializeRound();
});

// Khởi tạo vòng chơi mới
function initializeRound() {
    const numFaces = gameState.difficulty === 'easy' ? 2 : gameState.difficulty === 'medium' ? 3 : 4;

    // Trộn và chọn nhân vật ngẫu nhiên
    const shuffled = [...CHARACTERS_POOL].sort(() => Math.random() - 0.5);
    gameState.characters = shuffled.slice(0, numFaces);

    gameState.answers = {};
    gameState.submitted = false;
    gameState.results = {};

    renderGame();
}

// Render giao diện game
function renderGame() {
    // Hiển thị mức độ
    const difficultyText = gameState.difficulty === 'easy' ? 'Dễ 🙂' :
        gameState.difficulty === 'medium' ? 'Vừa 😊' : 'Khó 🤩';
    document.getElementById('difficulty-badge').textContent = `Mức độ: ${difficultyText}`;

    // Render hints
    renderHints();

    // Render khuôn mặt
    renderFaces();

    // Render thẻ tên
    renderNameCards();

    // Render buttons
    renderButtons();

    // Ẩn kết quả
    document.getElementById('result-message').classList.add('hidden');
}

// Render phần gợi ý
function renderHints() {
    const hintsContainer = document.getElementById('hints-list');
    hintsContainer.innerHTML = gameState.characters.map((char, index) =>
        `<p>${index + 1}. <strong>${char.name}</strong> đang <strong>${char.emotion}</strong>, đâu là <strong>${char.name}</strong>?</p>`
    ).join('');
}

// Render khuôn mặt
function renderFaces() {
    const facesGrid = document.getElementById('faces-grid');
    facesGrid.innerHTML = gameState.characters.map(char => {
        const droppedName = gameState.answers[char.id];
        const isCorrect = gameState.results[char.id];
        const showAnswer = gameState.submitted && isCorrect === false;

        return `
            <div class="face-card">
                <img src="${char.image}" alt="${char.emotion}" class="face-image">
                <div class="drop-zone ${droppedName ? 'filled' : ''}" 
                     data-character-id="${char.id}"
                     ondrop="handleDrop(event)" 
                     ondragover="handleDragOver(event)"
                     ondragleave="handleDragLeave(event)">
                    ${droppedName ? `
                        <div class="dropped-name">
                            <span>${droppedName}</span>
                            ${isCorrect === undefined ? `
                                <button class="remove-btn" onclick="removeName('${char.id}')">✕</button>
                            ` : ''}
                            ${isCorrect === true ? '<span class="status-icon">✓</span>' : ''}
                            ${isCorrect === false ? '<span class="status-icon">✗</span>' : ''}
                        </div>
                    ` : '<span class="drop-zone-placeholder">Thả tên vào đây</span>'}
                </div>
                ${showAnswer ? `<div class="answer-hint">✓ Đáp án: ${char.name}</div>` : ''}
            </div>
        `;
    }).join('');
}

// Render thẻ tên
function renderNameCards() {
    const usedNames = Object.values(gameState.answers);
    const availableNames = gameState.characters
        .map(c => c.name)
        .filter(name => !usedNames.includes(name));

    const container = document.getElementById('name-cards-container');

    if (availableNames.length === 0 && !gameState.submitted) {
        container.innerHTML = '<p class="no-names-msg">Tất cả thẻ tên đã được sử dụng</p>';
    } else {
        container.innerHTML = availableNames.map(name => `
            <div class="name-card ${gameState.submitted ? 'disabled' : ''}" 
                 draggable="${!gameState.submitted}"
                 ondragstart="handleDragStart(event, '${name}')"
                 ondragend="handleDragEnd(event)">
                <button class="name-speaker-btn" onclick="speak('${name}')">🔊</button>
                <span class="name-text">${name}</span>
            </div>
        `).join('');
    }
}

// Render buttons
function renderButtons() {
    const allAnswered = Object.keys(gameState.answers).length === gameState.characters.length;
    const allCorrect = gameState.submitted && Object.values(gameState.results).every(r => r);

    document.getElementById('submit-btn').style.display = !gameState.submitted ? 'block' : 'none';
    document.getElementById('submit-btn').disabled = !allAnswered;

    const showRetry = gameState.submitted && !allCorrect && gameState.canRetry && !gameState.retryUsed;
    document.getElementById('retry-btn').style.display = showRetry ? 'block' : 'none';

    const showReset = gameState.submitted;
    document.getElementById('reset-btn').style.display = showReset ? 'block' : 'none';

    const showNext = gameState.submitted && allCorrect;
    document.getElementById('next-btn').style.display = showNext ? 'block' : 'none';
}

// Drag and Drop handlers
let draggedName = null;

function handleDragStart(event, name) {
    if (gameState.submitted) return;
    draggedName = name;
    event.currentTarget.classList.add('dragging');
}

function handleDragEnd(event) {
    event.currentTarget.classList.remove('dragging');
}

function handleDragOver(event) {
    event.preventDefault();
    const dropZone = event.currentTarget;
    if (!dropZone.classList.contains('filled')) {
        dropZone.classList.add('drag-over');
    }
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('drag-over');
}

function handleDrop(event) {
    event.preventDefault();
    const dropZone = event.currentTarget;
    dropZone.classList.remove('drag-over');

    if (gameState.submitted) return;

    const characterId = dropZone.dataset.characterId;
    if (gameState.answers[characterId]) return;

    gameState.answers[characterId] = draggedName;
    draggedName = null;

    renderGame();
}

// Xóa tên
function removeName(characterId) {
    if (gameState.submitted) return;
    delete gameState.answers[characterId];
    renderGame();
}

// Text-to-speech
function speak(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'vi-VN';
        utterance.rate = 0.9;
        window.speechSynthesis.speak(utterance);
    }
}

function speakHints() {
    const hints = gameState.characters.map(char =>
        `${char.name} đang ${char.emotion}, đâu là ${char.name}?`
    ).join('. ');
    speak(hints);
}

// Nộp bài
function submitAnswer() {
    if (Object.keys(gameState.answers).length !== gameState.characters.length) {
        alert('Hãy đặt tên cho tất cả các khuôn mặt trước khi nộp bài!');
        return;
    }

    let allCorrect = true;
    let correctCount = 0;

    gameState.characters.forEach(char => {
        const isCorrect = gameState.answers[char.id] === char.name;
        gameState.results[char.id] = isCorrect;
        if (isCorrect) {
            correctCount++;
        } else {
            allCorrect = false;
        }
    });

    gameState.submitted = true;

    renderGame();
    showResultPopup(allCorrect, correctCount);
}

// Hiển thị popup kết quả
function showResultPopup(allCorrect, correctCount) {
    const popup = document.getElementById('result-popup');
    const icon = document.getElementById('popup-icon');
    const title = document.getElementById('popup-title');
    const message = document.getElementById('popup-message');
    const nextBtn = document.getElementById('popup-next-btn');

    const totalQuestions = gameState.characters.length;

    if (allCorrect) {
        icon.textContent = '🎉';
        title.textContent = 'Bạn đã trả lời đúng!';
        message.textContent = `Xuất sắc! Bạn đã trả lời đúng ${correctCount}/${totalQuestions} câu hỏi!`;
        title.style.color = '#22c55e';
        nextBtn.style.display = 'block';

        // Đọc kết quả
        setTimeout(() => {
            speak('Chúc mừng! Bạn đã trả lời đúng tất cả!');
        }, 500);
    } else {
        icon.textContent = '😢';
        title.textContent = 'Bạn đã trả lời sai!';
        message.textContent = `Bạn đã trả lời đúng ${correctCount}/${totalQuestions} câu hỏi. Hãy thử lại nhé!`;
        title.style.color = '#ef4444';

        // Ẩn nút Next nếu trả lời sai
        nextBtn.style.display = 'none';

        // Đọc kết quả
        setTimeout(() => {
            speak(`Bạn đã trả lời đúng ${correctCount} trên ${totalQuestions} câu hỏi. Hãy thử lại nhé!`);
        }, 500);
    }

    popup.classList.remove('hidden');
}

// Đóng popup và chơi lại
function closePopupAndReplay() {
    document.getElementById('result-popup').classList.add('hidden');
    initializeRound();
    speak('Chơi lại!');
}

// Đóng popup và câu hỏi tiếp theo
function closePopupAndNext() {
    document.getElementById('result-popup').classList.add('hidden');

    // Tăng level
    if (gameState.currentLevel === 1) {
        gameState.currentLevel = 2;
        gameState.difficulty = 'medium';
        speak('Chuyển sang mức độ vừa!');
    } else if (gameState.currentLevel === 2) {
        gameState.currentLevel = 3;
        gameState.difficulty = 'hard';
        speak('Chuyển sang mức độ khó!');
    } else {
        // Reset về level 1 nếu đã hoàn thành level 3
        gameState.currentLevel = 1;
        gameState.difficulty = 'easy';
        speak('Hoàn thành! Bắt đầu lại từ mức độ dễ!');
    }

    initializeRound();
}

// Thử lại
function retryAnswer() {
    gameState.submitted = false;
    gameState.retryUsed = true;
    renderGame();
    speak('Hãy thử lại nhé!');
}

// Chơi lại vòng hiện tại
function resetGame() {
    initializeRound();
}

// Câu hỏi tiếp theo
function nextQuestion() {
    initializeRound();
    speak('Câu hỏi mới!');
}

// Quay về menu
function backToMenu() {
    document.getElementById('game-screen').classList.add('hidden');
    document.getElementById('menu-screen').classList.remove('hidden');
    window.speechSynthesis.cancel();
}