// ================== BIẾN LIÊN QUAN BACKEND (NEW) ==================
let sessionId = null;
let user = null;
let gameId = null;
let level = null;
let questions = []; // Mảng câu hỏi BE trả về
let localResults = []; // Mảng lưu kết quả để gửi lên /games/end-level
let remainingQuestions = [];
// ================== TRẠNG THÁI GAME ==================
let gameState = {
    difficulty: 'easy', // sẽ set lại theo level nếu muốn
    shuffledCharacters: [], // <-- Sẽ lấy từ questions của BE
    answers: {},
    submitted: false,
    results: {},
    currentLevel: 1,
    canRetry: true,
    retryUsed: false,
};

function shuffleArray(array) {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

// Chọn một nhóm câu hỏi cho level hiện tại, và loại chúng khỏi remainingQuestions
function pickQuestionsForCurrentLevel() {
    if (!remainingQuestions || remainingQuestions.length === 0) {
        return [];
    }

    // Số câu tối đa mỗi level
    let maxPerLevel;
    if (level === 1) {
        maxPerLevel = 2; // Level 1: 2 câu
    } else if (level === 2) {
        maxPerLevel = 3; // Level 2: 3 câu (tuỳ bạn)
    } else {
        maxPerLevel = 4; // Level 3+: 4 câu
    }

    const num = Math.min(maxPerLevel, remainingQuestions.length);

    // Shuffle remainingQuestions rồi lấy num câu
    const shuffled = shuffleArray(remainingQuestions);
    const selected = shuffled.slice(0, num);

    // Loại những câu đã chọn khỏi remainingQuestions
    const selectedIds = new Set(selected.map(q => q.question_id));
    remainingQuestions = remainingQuestions.filter(q => !selectedIds.has(q.question_id));

    return selected;
}


// ================== TỰ ĐỘNG BẮT ĐẦU GAME KHI TRANG LOAD ==================
window.addEventListener('DOMContentLoaded', async () => {
    // 1. Lấy user từ localStorage
    user = JSON.parse(localStorage.getItem('currentUser'));
    if (!user) {
        alert('Vui lòng đăng nhập!');
        window.location.href = './login.html';
        return;
    }

    // 2. Lấy gameId + level từ URL (?gameId=GC4&level=1 ...)
    const urlParams = new URLSearchParams(window.location.search);
    gameId = urlParams.get('gameId');
    level = parseInt(urlParams.get('level'));

    if (!gameId || !level) {
        alert('Thiếu thông tin game hoặc level');
        window.location.href = './select_game.html';
        return;
    }

    // 3. Gọi BE để START SESSION + LẤY DỮ LIỆU CÂU HỎI
    try {
        const res = await fetch(`/games/start/${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: user.user_id,
                level: level
            })
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || 'Lỗi khởi động game');
        }

        const data = await res.json();
        sessionId = data.session_id;
        questions = data.questions || [];

        if (!questions || questions.length === 0) {
            throw new Error('Không tải được câu hỏi cho level này (mảng rỗng)');
        }
        remainingQuestions = [...questions];
        const selectedQuestions = pickQuestionsForCurrentLevel();
        if (selectedQuestions.length === 0) {
            throw new Error('Không còn câu hỏi nào cho level này');
        }

        // 4. Map questions -> characters cho game WhoIsWho
        // Giả định structure:
        // q.question_id, q.media_path (ảnh mặt), q.correct_answer (tên), q.emotion (cảm xúc)
        gameState.characters = selectedQuestions.map(q => ({
            id: q.question_id,
            name: q.correct_answer, // Tên đúng cần ghép
            emotion: q.emotion || '', // Dùng cho hint: "An đang vui vẻ"
            image: q.media_path // Ảnh khuôn mặt
        }));

        gameState.shuffledCharacters = shuffleArray(gameState.characters);
        // Có thể set difficulty dựa trên số lượng nhân vật hoặc level
        if (gameState.characters.length <= 2) {
            gameState.difficulty = 'easy';
            gameState.currentLevel = 1;
        } else if (gameState.characters.length === 3) {
            gameState.difficulty = 'medium';
            gameState.currentLevel = 2;
        } else {
            gameState.difficulty = 'hard';
            gameState.currentLevel = 3;
        }

        initializeRound();

    } catch (err) {
        console.error(err);
        alert(err.message || 'Lỗi khi khởi động game');
    }
});

// ================== HÀM GỬI KẾT QUẢ LÊN BACKEND (NEW) ==================
async function sendFinalResults() {
    if (!sessionId) {
        console.warn('Không có sessionId, bỏ qua gửi kết quả.');
        return;
    }
    console.log('Đang gửi kết quả cuối cùng:', localResults);

    try {
        const res = await fetch('/games/end-level', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                results: localResults
            })
        });

        if (!res.ok) {
            throw new Error('Lỗi khi gửi kết quả cuối cùng.');
        }
        console.log('Đã lưu tiến trình thành công.');
    } catch (err) {
        console.error('Lỗi khi gửi kết quả cuối cùng:', err);
        alert('Đã xảy ra lỗi khi lưu tiến trình của bạn.');
    }
}

// ================== KHỞI TẠO VÒNG CHƠI (CHANGED) ==================
function initializeRound() {
    // Ở đây KHÔNG random từ CHARACTERS_POOL nữa,
    // mà dùng thẳng gameState.characters đã lấy từ BE.
    // Nếu muốn mỗi round ít mặt hơn thì có thể slice lại ở đây.

    gameState.answers = {};
    gameState.submitted = false;
    gameState.results = {};
    gameState.retryUsed = false;
    localResults = []; // reset mảng kết quả cho vòng chơi
    renderGame();
}

// ================== RENDER GAME ==================
function renderGame() {
    const difficultyText = gameState.difficulty === 'easy' ? 'Dễ 🙂' :
        gameState.difficulty === 'medium' ? 'Vừa 😊' : 'Khó 🤩';
    document.getElementById('difficulty-badge').textContent = `Mức độ: ${difficultyText}`;

    renderHints();
    renderFaces();
    renderNameCards();
    renderButtons();

    document.getElementById('result-message').classList.add('hidden');
}

// Render phần gợi ý
function renderHints() {
    const hintsContainer = document.getElementById('hints-list');
    hintsContainer.innerHTML = gameState.characters.map((char, index) => {
        const emo = char.emotion || 'một cảm xúc nào đó';
        return `
            <p>
                ${index + 1}. 
                <strong>${char.name}</strong> đang cảm thấy 
                "<strong>${emo}</strong>", 
                hãy kéo thẻ tên để biết đâu là <strong>${char.name}</strong>.
            </p>
        `;
    }).join('');
}


// Render khuôn mặt
function renderFaces() {
    const facesGrid = document.getElementById('faces-grid');
    const faces = gameState.shuffledCharacters.length ?
        gameState.shuffledCharacters :
        gameState.characters;

    facesGrid.innerHTML = faces.map(char => {
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
        const shuffledNames = shuffleArray(availableNames);
        container.innerHTML = shuffledNames.map(name => `
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

// Drag and Drop
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
    const hints = gameState.characters.map(char => {
        const emo = char.emotion || 'một cảm xúc nào đó';
        return `${char.name} đang cảm thấy ${emo}, hãy kéo thẻ tên để biết đâu là ${char.name}`;
    }).join('. ');
    speak(hints);
}

// ================== NỘP BÀI (CHANGED: THÊM LƯU KẾT QUẢ + GỬI BE) ==================
async function submitAnswer() {
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

    // ====== LƯU KẾT QUẢ ĐỂ GỬI BE ======
    localResults = [];
    gameState.characters.forEach(char => {
        localResults.push({
            question_id: char.id, // chính là question_id BE trả
            answer: gameState.answers[char.id], // tên user đã chọn
            is_correct: gameState.results[char.id],
            response_time_ms: 5000 // TODO: có thể đo thời gian thực
        });
    });

    // Gửi kết quả lên BE (giống recognize_emotion.js)
    await sendFinalResults();

    showResultPopup(allCorrect, correctCount);
}

// ================== POPUP KẾT QUẢ & CÁC NÚT KHÁC GIỮ NGUYÊN ==================
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

        setTimeout(() => {
            speak('Chúc mừng! Bạn đã trả lời đúng tất cả!');
        }, 500);
    } else {
        icon.textContent = '😢';
        title.textContent = 'Bạn đã trả lời sai!';
        message.textContent = `Bạn đã trả lời đúng ${correctCount}/${totalQuestions} câu hỏi. Hãy thử lại nhé!`;
        title.style.color = '#ef4444';
        nextBtn.style.display = 'none';

        setTimeout(() => {
            speak(`Bạn đã trả lời đúng ${correctCount} trên ${totalQuestions} câu hỏi. Hãy thử lại nhé!`);
        }, 500);
    }

    popup.classList.remove('hidden');
}

function closePopupAndReplay() {
    document.getElementById('result-popup').classList.add('hidden');
    initializeRound();
    speak('Chơi lại!');
}

function closePopupAndNext() {
    document.getElementById('result-popup').classList.add('hidden');
    const nextQuestions = pickQuestionsForCurrentLevel();
    // Ở đây hiện tại chỉ đổi difficulty local.
    // Nếu sau này bạn muốn sang level mới thực sự,
    // thì FE có thể redirect sang URL ?level=level+1 để tạo session mới.
    if (nextQuestions.length === 0) {
        speak('Bạn đã hoàn thành tất cả câu hỏi của level này!');
        alert('Bạn đã làm hết câu hỏi cho level này rồi!');
        // Tuỳ bạn: quay về menu
        // backToMenu();
        return;
    }

    gameState.characters = nextQuestions.map(q => ({
        id: q.question_id,
        name: q.correct_answer,
        emotion: q.emotion || '',
        image: q.media_path
    }));

    gameState.shuffledCharacters = shuffleArray(gameState.characters);

    if (gameState.characters.length <= 2) {
        gameState.difficulty = 'easy';
        gameState.currentLevel = 1;
    } else if (gameState.characters.length === 3) {
        gameState.difficulty = 'medium';
        gameState.currentLevel = 2;
    } else {
        gameState.difficulty = 'hard';
        gameState.currentLevel = 3;
    }

    initializeRound();
    speak('Câu hỏi mới!');
}

function retryAnswer() {
    gameState.submitted = false;
    gameState.retryUsed = true;
    gameState.results = {};
    renderGame();
    speak('Hãy thử lại nhé!');
}

function resetGame() {
    initializeRound();
}

function nextQuestion() {
    initializeRound();
    speak('Câu hỏi mới!');
}

function backToMenu() {
    document.getElementById('game-screen').classList.add('hidden');
    document.getElementById('menu-screen').classList.remove('hidden');
    window.speechSynthesis.cancel();
}