// fe/src/components/recognize_emotion.js

let sessionId = null;
let questions = [];
let localResults = [];
let currentIndex = 0;
let score = 0;
let answered = false;
let usedHint = false;

let elements = {};
let user = null;
let gameId = null;
let level = null;
let maxErrors = 1;

let emotionErrors = {};
let learnedEmotions = [];

let learningCards = {};

// --- SỬA LỖI QUAN TRỌNG: DÙNG WINDOW ĐỂ CHẶN GỌI KÉP ---
// Nếu file JS này bị load 2 lần, biến cục bộ sẽ bị tạo lại. 
// Dùng window.isGameSessionStarted để đảm bảo cờ này là duy nhất trên toàn trang.
if (window.isGameSessionStarted === undefined) {
    window.isGameSessionStarted = false;
}

document.addEventListener('DOMContentLoaded', async () => {
    // Kiểm tra biến Global thay vì biến cục bộ
    if (window.isGameSessionStarted) {
        console.warn("⛔ Session init skipped: Already started in another instance.");
        return;
    }
    // Đánh dấu là đã bắt đầu ngay lập tức
    window.isGameSessionStarted = true;

    console.log("🚀 Initializing Game Session...");

    user = JSON.parse(localStorage.getItem('currentUser'));
    if (!user) {
        alert('Vui lòng đăng nhập!');
        window.location.href = './login.html';
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    gameId = urlParams.get('gameId');
    level = parseInt(urlParams.get('level'));

    if (!gameId || !level) {
        alert('Thiếu thông tin game hoặc level');
        window.location.href = './select_game.html';
        return;
    }

    elements = {
        // Game elements
        score: document.getElementById('score-display'),
        questionArea: document.getElementById('question-area'),
        hintText: document.getElementById('hint-content'),
        hintBtn: document.getElementById('hint-btn'),
        soundBtn: document.getElementById('sound-btn'),
        exitBtn: document.getElementById('exit-btn'),
        answers: document.querySelectorAll('.answer-option'),
        nextHintBtn: document.getElementById('next-question-btn'),

        // Modals
        feedbackModal: document.getElementById('feedback-modal'),
        warningModal: document.getElementById('warning-modal'),
        learningModal: document.getElementById('learning-modal'),

        // Modal Contents
        modalTitle: document.getElementById('modal-title'),
        modalMsg: document.getElementById('modal-message'),
        modalActionsContainer: document.getElementById('feedback-modal-actions'),

        learningTitle: document.getElementById('learning-emotion-title'),
        learningBody: document.getElementById('learning-card-body'),
        learningCloseBtn: document.getElementById('learning-close-btn'),
        closeWarn: document.getElementById('close-warning'),
    };

    // START SESSION API
    try {
        console.log("📡 Calling Start Session API...");
        const res = await fetch(`/games/start/${gameId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: user.user_id, level })
        });

        if (!res.ok) throw new Error("Lỗi khởi động game");

        const data = await res.json();
        console.log("✅ Session Started Successfully:", data.session_id);

        sessionId = data.session_id;
        questions = data.questions;
        // maxErrors = data.max_errors || 1;
        maxErrors = 3; // Test
        learningCards = data.learning_cards || {};

        // Chuẩn hóa key cảm xúc về chữ thường
        const normalizedLearningCards = {};
        for (const key in learningCards) {
            if (learningCards.hasOwnProperty(key)) {
                normalizedLearningCards[key.trim().toLowerCase()] = learningCards[key];
            }
        }
        learningCards = normalizedLearningCards;
        emotionErrors = data.emotion_errors || {
            "sợ hãi": 0,
            "buồn bã": 0,
            "tức giận": 0,
            "ghê tởm": 0,
            "ngạc nhiên": 0,
            "vui vẻ": 0
        };

        loadQuestion(0);

    } catch (err) {
        console.error(err);
        alert("Lỗi khởi động game: " + err.message);
        // Reset flag nếu lỗi để user có thể reload thử lại (tùy chọn)
        // window.isGameSessionStarted = false; 
        return;
    }

    async function sendFinalResults() {
        try {
            await fetch('/games/end-level', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    results: localResults,
                    review_emotions: learnedEmotions
                })
            });
        } catch (err) {
            console.error(err);
        }
    }

    async function loadQuestion(i) {
        if (i >= questions.length) {
            await sendFinalResults();
            alert('Hoàn thành level!');
            window.location.href = './select_game.html';
            return;
        }

        usedHint = false;
        const q = questions[i];

        elements.questionArea.innerHTML = '';

        if (q.media_path && q.media_path.match(/\.(jpeg|jpg|gif|png)$/)) {
            const img = document.createElement('img');
            const relativePath = q.media_path.replace('/fe/', '../../');
            img.src = relativePath;
            img.className = 'question-image';
            elements.questionArea.appendChild(img);
        }

        const text = document.createElement('p');
        text.className = 'question-text';
        text.textContent = q.question_text;
        elements.questionArea.appendChild(text);

        elements.answers.forEach((btn, idx) => {
            if (q.options[idx]) {
                btn.textContent = q.options[idx].answer_text;
                btn.dataset.answer = q.options[idx].answer_text;
                btn.style.display = 'block';
            } else {
                btn.style.display = 'none';
            }
            btn.className = 'answer-option';
            btn.disabled = false;
        });

        elements.hintText.textContent = 'Hãy chọn đáp án của bạn.';
        elements.score.textContent = `Câu ${i + 1}/${questions.length} | Điểm: ${score}`;

        answered = false;
        elements.feedbackModal.classList.add('hidden');
        elements.learningModal.classList.add('hidden');
    }

    function showFeedback(correct, correctAns, emotionKey) {
        elements.modalTitle.textContent = correct ? 'CHÍNH XÁC!' : 'SAI RỒI!';
        elements.modalTitle.style.color = correct ? '#10b981' : '#ef4444';
        elements.modalMsg.textContent = correct ? 'Giỏi lắm!' : `Đáp án đúng: ${correctAns}`;

        elements.modalActionsContainer.innerHTML = '';

        if (!correct && emotionErrors[emotionKey.trim().toLowerCase()] >= maxErrors) {
            const learnBtn = document.createElement('button');
            learnBtn.textContent = "Học lại cảm xúc";
            learnBtn.className = "modal-btn learn-btn";
            learnBtn.onclick = () => showLearningCard(emotionKey);
            elements.modalActionsContainer.appendChild(learnBtn);
        } else {
            const reviewBtn = document.createElement('button');
            reviewBtn.textContent = "Xem lại";
            reviewBtn.className = "modal-btn review-btn";
            reviewBtn.onclick = () => elements.feedbackModal.classList.add('hidden');

            const nextBtn = document.createElement('button');
            nextBtn.textContent = "Câu tiếp theo";
            nextBtn.className = "modal-btn next-btn";
            nextBtn.onclick = handleNextAfterPopup;

            elements.modalActionsContainer.appendChild(reviewBtn);
            elements.modalActionsContainer.appendChild(nextBtn);
        }
        elements.feedbackModal.classList.remove('hidden');
    }

    function handleNextAfterPopup() {
        elements.feedbackModal.classList.add('hidden');
        currentIndex++;
        loadQuestion(currentIndex);
    }

    function showLearningCard(emotion) {
        elements.feedbackModal.classList.add('hidden');
        const emotionKey = emotion.trim().toLowerCase();
        const cards = learningCards[emotionKey]?.[level];
        elements.learningTitle.textContent = emotion;
        elements.learningBody.innerHTML = '';

        if (!cards || cards.length === 0) {
            elements.learningBody.innerHTML = `<p>Hiện không có thẻ học cho cảm xúc <strong>${emotion}</strong> ở level ${level}. Vui lòng tiếp tục.</p>`;
        } else {
            cards.forEach(card => {
                const cardHtml = `
                    <div class="concept-card">
                        <h3>${card.title || emotion}</h3>
                        <p>${card.description || ""}</p>
                        ${card.image_path ? `<img src="${card.image_path.replace('/fe/', '../../')}" class="learn-img">` : ''}
                    </div>
                `;
                elements.learningBody.insertAdjacentHTML('beforeend', cardHtml);
            });
        }
        elements.learningCloseBtn.onclick = () => {
            elements.learningModal.classList.add('hidden');
            currentIndex++;
            loadQuestion(currentIndex);
        };
        elements.learningModal.classList.remove('hidden');
    }

    elements.hintBtn.onclick = () => {
        usedHint = true;
        elements.hintText.textContent = questions[currentIndex].explanation;
    };

    elements.soundBtn.onclick = () => {
        const msg = new SpeechSynthesisUtterance(questions[currentIndex].question_text);
        msg.lang = 'vi-VN';
        speechSynthesis.speak(msg);
    };

    elements.exitBtn.onclick = () => {
        if (confirm('Thoát game không lưu tiến trình?')) {
            window.location.href = './select_game.html';
        }
    };

    elements.answers.forEach(btn => {
        btn.onclick = () => {
            if (answered) return;
            answered = true;

            const q = questions[currentIndex];
            const chosen = btn.dataset.answer;
            const correct = (chosen === q.correct_answer);
            const emotion = q.correct_answer;
            const emotionKey = emotion.trim().toLowerCase();

            if (correct) score += 10;

            localResults.push({
                question_id: q.question_id,
                answer: chosen,
                is_correct: correct,
                used_hint: usedHint,
                response_time_ms: 5000
            });

            if (!correct) {
                emotionErrors[emotionKey] = (emotionErrors[emotionKey] || 0) + 1;
                if (emotionErrors[emotionKey] >= maxErrors && !learnedEmotions.includes(emotionKey)) {
                    learnedEmotions.push(emotionKey);
                    showFeedback(false, q.correct_answer, emotion);
                    return;
                }
            }

            elements.answers.forEach(b => {
                if (b.dataset.answer === q.correct_answer) b.classList.add('correct');
                else if (b === btn && !correct) b.classList.add('incorrect');
                b.disabled = true;
            });

            showFeedback(correct, q.correct_answer, emotion);
        };
    });
});