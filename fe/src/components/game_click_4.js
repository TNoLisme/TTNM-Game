const EMOTION_CHOICES = [
    { value: "Vui vẻ", label: "😊 Vui vẻ" },
    { value: "Buồn bã", label: "😢 Buồn bã" },
    { value: "Ngạc nhiên", label: "😲 Ngạc nhiên" },
    { value: "Tức giận", label: "😠 Tức giận" },
    { value: "Sợ hãi", label: "😨 Sợ hãi" },
    { value: "Ghê tởm", label: "🤢 Ghê tởm" }
];

function showSystemPopup(title, message, onClose, btnText = 'OK') {
    const modal = document.getElementById('system-modal');
    const titleEl = document.getElementById('system-modal-title');
    const msgEl = document.getElementById('system-modal-message');
    const btnEl = document.getElementById('system-modal-btn');

    if (!modal || !titleEl || !msgEl || !btnEl) {
        // Fallback nếu modal chưa sẵn sàng
        if (window.egModal && typeof window.egModal.alert === 'function') {
            window.egModal.alert(message, title).then(() => {
                if (onClose) onClose();
            });
            return;
        }
        alert(message);
        if (onClose) onClose();
        return;
    }

    titleEl.textContent = title;
    msgEl.textContent = message;
    btnEl.textContent = btnText;

    modal.classList.remove('hidden');
    btnEl.onclick = () => {
        modal.classList.add('hidden');
        if (onClose) onClose();
    };
}

let sessionId = null;
let questions = [];
let localResults = [];
let currentIndex = 0;
let score = 0;
let answered = false;
let usedHint = false;
let selectedAnswer = null;
let selectedButton = null;

let user = null;
let gameId = null;
let level = null;

let elements = {};

function initDetectiveGame() {
    user = JSON.parse(localStorage.getItem('currentUser'));
    if (!user) {
        showSystemPopup('Thông báo', 'Vui lòng đăng nhập!', () => {
            window.location.href = '/src/pages/login.html';
        });
        return;
    }

    const params = new URLSearchParams(window.location.search);
    gameId = params.get('gameId');
    level = parseInt(params.get('level') || '1', 10);

    if (!gameId || !level) {
        showSystemPopup('Thiếu thông tin', 'Thiếu thông tin game hoặc level', () => {
            window.location.href = './select_game.html';
        });
        return;
    }

    elements = {
        progressLabel: document.getElementById('progress-label'),
        scoreLabel: document.getElementById('score-label'),
        questionArea: document.getElementById('question-area'),
        hintText: document.getElementById('hint-content'),
        hintBtn: document.getElementById('hint-btn'),
        soundBtn: document.getElementById('sound-btn'),
        submitBtn: document.getElementById('submit-answer-btn'),
        answers: document.querySelectorAll('.answer-option'),
        feedbackModal: document.getElementById('feedback-modal'),
        modalIcon: document.getElementById('modal-icon'),
        modalTitle: document.getElementById('modal-title'),
        modalMessage: document.getElementById('modal-message'),
        nextQuestionBtn: document.getElementById('next-question-btn'),
    };

    if (elements.hintBtn) elements.hintBtn.addEventListener('click', onHintClick);
    if (elements.soundBtn) elements.soundBtn.addEventListener('click', speakCurrentQuestion);
    if (elements.nextQuestionBtn) elements.nextQuestionBtn.addEventListener('click', onNextQuestion);
    if (elements.submitBtn) {
        elements.submitBtn.addEventListener('click', onSubmitAnswer);
    }

    elements.answers.forEach(btn => {
        btn.addEventListener('click', () => onAnswerClick(btn));
    });

    startSession();
}

function formatQuestionText(text) {
    const s = (text || '').trim();
    if (s.length < 120) return s;
    return s.replace(/([.!?])\s+/g, '$1\n');
}

async function startSession() {
    try {
        const res = await fetch(`/games/start/${gameId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: user.user_id, level }),
        });

        if (!res.ok) {
            throw new Error('Lỗi khởi động game');
        }

        const data = await res.json();
        sessionId = data.session_id;
        questions = data.questions || [];
        score = 0;
        currentIndex = 0;
        localResults = [];

        if (!questions.length) {
            showSystemPopup('Chưa có dữ liệu', 'Hiện chưa có câu hỏi cho game này.', () => {
                window.location.href = `./level_select.html?gameId=${gameId}`;
            });
            return;
        }

        loadQuestion(0);
    } catch (err) {
        console.error(err);
        showSystemPopup('Lỗi', 'Không thể bắt đầu game: ' + err.message, () => {
            window.location.href = './select_game.html';
        });
    }
}

function loadQuestion(index) {
    if (index < 0 || index >= questions.length) return;

    const q = questions[index];
    answered = false;
    usedHint = false;
    selectedAnswer = null;
    selectedButton = null;
    if (elements.submitBtn) {
        elements.submitBtn.disabled = true;
    }

    if (elements.questionArea) {
        elements.questionArea.innerHTML = '';
        const textEl = document.createElement('p');
        textEl.className = 'question-text';
        textEl.textContent = formatQuestionText(q.question_text);
        elements.questionArea.appendChild(textEl);
    }

    if (elements.hintText) {
        elements.hintText.textContent = '';
    }

    elements.answers.forEach((btn, idx) => {
        const emo = EMOTION_CHOICES[idx];
        btn.classList.remove('correct', 'incorrect', 'selected');

        if (emo) {
            btn.style.display = 'inline-flex';
            btn.textContent = emo.label;
            btn.dataset.answer = emo.value;
            btn.disabled = false;
        } else {
            btn.style.display = 'none';
            btn.dataset.answer = '';
        }
    });

    if (elements.progressLabel) {
        elements.progressLabel.textContent = `Câu ${index + 1}/${questions.length}`;
    }
    if (elements.scoreLabel) {
        elements.scoreLabel.textContent = `Điểm: ${score}`;
    }
}

function normalizeEmotion(text) {
    return (text || '').trim().toLowerCase();
}

function onHintClick() {
    const q = questions[currentIndex];
    if (!q) return;
    usedHint = true;
    if (elements.hintText) {
        elements.hintText.textContent = q.explanation || 'Hiện chưa có gợi ý cho câu này.';
    }
}

function speakCurrentQuestion() {
    const q = questions[currentIndex];
    if (!q || !('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(q.question_text);
    utterance.lang = 'vi-VN';
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
}

function onAnswerClick(btn) {
    if (answered) return;
    const q = questions[currentIndex];
    if (!q) return;

    selectedButton = btn;
    selectedAnswer = btn.dataset.answer;

    elements.answers.forEach((b) => {
        b.classList.toggle('selected', b === btn);
    });

    if (elements.submitBtn) {
        elements.submitBtn.disabled = !selectedAnswer;
    }
}

function onSubmitAnswer() {
    if (answered) return;
    const q = questions[currentIndex];
    if (!q) return;
    if (!selectedAnswer || !selectedButton) {
        showSystemPopup('Thông báo', 'Hãy chọn một cảm xúc trước khi trả lời.');
        return;
    }

    answered = true;

    const correctAnswer = q.correct_answer;
    const isCorrect = normalizeEmotion(selectedAnswer) === normalizeEmotion(correctAnswer);

    if (isCorrect) {
        score += 10;
        elements.scoreLabel.textContent = `Điểm: ${score}`;
    }

    localResults.push({
        question_id: q.question_id,
        answer: selectedAnswer,
        is_correct: isCorrect,
        used_hint: usedHint,
        response_time_ms: 5000,
    });

    elements.answers.forEach((b) => {
        b.disabled = true;
        if (normalizeEmotion(b.dataset.answer) === normalizeEmotion(correctAnswer)) {
            b.classList.add('correct');
        } else if (b === selectedButton && !isCorrect) {
            b.classList.add('incorrect');
        }
    });

    if (elements.submitBtn) {
        elements.submitBtn.disabled = true;
    }

    showFeedback(isCorrect, correctAnswer);
}

function showFeedback(isCorrect, correctAnswer) {
    if (isCorrect) {
        elements.modalIcon.textContent = '🔍';
        elements.modalTitle.textContent = 'Chính xác!';
        elements.modalMessage.textContent = 'Bạn là một thám tử cảm xúc rất giỏi!';
    } else {
        elements.modalIcon.textContent = '🤔';
        elements.modalTitle.textContent = 'Chưa chính xác lắm';
        elements.modalMessage.textContent = `Đáp án đúng là: ${correctAnswer}`;
    }

    elements.feedbackModal.classList.remove('hidden');
}

function onNextQuestion() {
    elements.feedbackModal.classList.add('hidden');
    currentIndex += 1;

    if (currentIndex >= questions.length) {
        finishGame();
    } else {
        loadQuestion(currentIndex);
    }
}

async function finishGame() {
    try {
        if (sessionId) {
            await fetch('/games/end-level', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    results: localResults,
                    review_emotions: [],
                }),
            });
        }
    } catch (err) {
        console.error('Lỗi gửi kết quả:', err);
    }

    showSystemPopup('Hoàn thành', `Bạn đã hoàn thành! Tổng điểm: ${score}`, () => {
        window.location.href = `./level_select.html?gameId=${gameId}`;
    }, 'Quay lại chọn level');
}

window.addEventListener('DOMContentLoaded', initDetectiveGame);
