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

function normalizeEmotion(text) {
    return (text || '').trim().toLowerCase();
}

const EMOTION_ICONS = {
    'vui vẻ': '😊', 'vui': '😊',
    'buồn bã': '😢', 'buồn': '😢',
    'ngạc nhiên': '😲',
    'tức giận': '😠',
    'sợ hãi': '😨',
    'ghê tởm': '🤢'
};

const EMOTION_CHOICES = [
    'Vui vẻ', 'Buồn bã', 'Ngạc nhiên', 'Tức giận', 'Sợ hãi', 'Ghê tởm'
];

if (window.isGameSessionStarted === undefined) {
    window.isGameSessionStarted = false;
}

document.addEventListener('DOMContentLoaded', async () => {
    if (window.isGameSessionStarted) {
        console.warn("⛔ Session init skipped.");
        return;
    }
    window.isGameSessionStarted = true;

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
        score: document.getElementById('score-display'),
        questionArea: document.getElementById('question-area'),
        hintText: document.getElementById('hint-content'),
        hintBtn: document.getElementById('hint-btn'),
        soundBtn: document.getElementById('sound-btn'),
        exitBtn: document.getElementById('exit-btn'),
        answers: document.querySelectorAll('.answer-option'),
        nextHintBtn: document.getElementById('next-question-btn'),
        feedbackModal: document.getElementById('feedback-modal'),
        warningModal: document.getElementById('warning-modal'),
        learningModal: document.getElementById('learning-modal'),
        modalTitle: document.getElementById('modal-title'),
        modalMsg: document.getElementById('modal-message'),
        modalActionsContainer: document.getElementById('feedback-modal-actions'),
        learningTitle: document.getElementById('learning-emotion-title'),
        learningBody: document.getElementById('learning-card-body'),
        learningCloseBtn: document.getElementById('learning-close-btn'),
        closeWarn: document.getElementById('close-warning'),
    };

    try {
        const res = await fetch(`/games/start/${gameId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: user.user_id, level })
        });

        if (!res.ok) throw new Error("Lỗi khởi động game");

        const data = await res.json();
        sessionId = data.session_id;
        questions = data.questions;
        // maxErrors = data.max_errors || 1;
        maxErrors = 1; // Test config

        learningCards = data.learning_cards || {};
        const normalizedLearningCards = {};
        for (const key in learningCards) {
            if (learningCards.hasOwnProperty(key)) {
                normalizedLearningCards[key.trim().toLowerCase()] = learningCards[key];
            }
        }
        learningCards = normalizedLearningCards;

        emotionErrors = data.emotion_errors || {
            "sợ hãi": 0, "buồn bã": 0, "tức giận": 0, "ghê tởm": 0, "ngạc nhiên": 0, "vui vẻ": 0
        };

        loadQuestion(0);

    } catch (err) {
        console.error(err);
        alert("Lỗi khởi động game: " + err.message);
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
            const emo = EMOTION_CHOICES[idx];
            if (emo) {
                const key = normalizeEmotion(emo);
                const icon = EMOTION_ICONS[key];
                const label = icon ? `${icon} ${emo}` : emo;
                btn.textContent = label;
                btn.dataset.answer = emo;
                btn.style.display = 'inline-flex';
                btn.disabled = false;
            } else {
                btn.style.display = 'none';
                btn.dataset.answer = '';
                btn.disabled = true;
            }
            btn.className = 'answer-option';
        });

        elements.hintText.textContent = 'Hãy chọn đáp án của bạn.';
        elements.score.textContent = `Câu ${i + 1}/${questions.length} | Điểm: ${score}`;

        answered = false;
        elements.feedbackModal.classList.add('hidden');
        elements.learningModal.classList.add('hidden');
    }

    // Popup Sai/Đúng (Đã sửa logic hiển thị nút)
    function showFeedback(correct, correctAns, emotion) {
        const emotionKey = normalizeEmotion(emotion);

        elements.modalTitle.textContent = correct ? 'CHÍNH XÁC!' : 'SAI RỒI!';
        elements.modalTitle.style.color = correct ? '#10b981' : '#ef4444';
        elements.modalMsg.textContent = correct ? 'Giỏi lắm!' : `Đáp án đúng: ${correctAns}`;

        elements.modalActionsContainer.innerHTML = '';

        // Kiểm tra xem lỗi này có vừa đạt ngưỡng học lại bắt buộc không
        const isForcedLearning = !correct &&
            emotionErrors[emotionKey] >= maxErrors &&
            learnedEmotions.includes(emotionKey);

        if (isForcedLearning) {
            // --- UI BẮT BUỘC HỌC LẠI (Chỉ có 1 nút) ---
            elements.modalTitle.textContent = 'CẦN HỌC LẠI CẢM XÚC NÀY!';
            elements.modalTitle.style.color = '#f65c80ff';
            elements.modalMsg.textContent = `Sai nhiều lần ở cảm xúc "${emotion}". Hãy học lại để ôn tập kiến thức trước khi tiếp tục.`;

            const learnBtn = document.createElement('button');
            learnBtn.textContent = "HỌC LẠI CẢM XÚC NÀY";
            learnBtn.className = "modal-btn learn-btn";

            // Gán sự kiện gọi hàm showLearningCard để hiện popup thẻ học
            learnBtn.onclick = () => showLearningCard(emotion);

            elements.modalActionsContainer.appendChild(learnBtn);
        } else {
            // --- UI BÌNH THƯỜNG (Có Xem lại và Câu tiếp theo) ---
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
        const emotionKey = normalizeEmotion(emotion);

        let cards = [];
        const rawData = learningCards[emotionKey];

        if (Array.isArray(rawData)) {
            cards = rawData;
        } else if (rawData && typeof rawData === 'object') {
            cards = Object.values(rawData).flat();
        }

        elements.learningTitle.textContent = emotion;
        elements.learningBody.innerHTML = '';

        if (!cards || cards.length === 0) {
            elements.learningBody.innerHTML = `<p>Hiện không có video/thẻ học cho cảm xúc <strong>${emotion}</strong>. Vui lòng tiếp tục.</p>`;
        } else {
            cards.forEach(card => {
                let mediaHtml = '';

                if (card.video_path) {
                    const relativeVideoPath = card.video_path.replace('/fe/', '../../');
                    mediaHtml = `
                        <video controls autoplay class="learn-media" style="width:100%; max-height:300px; border-radius:12px;">
                            <source src="${relativeVideoPath}" type="video/mp4">
                            Trình duyệt không hỗ trợ video.
                        </video>
                    `;
                }
                else if (card.image_path) {
                    const relativeImgPath = card.image_path.replace('/fe/', '../../');
                    if (relativeImgPath.match(/\.(mp4|webm|ogg|mov)$/i)) {
                        mediaHtml = `
                            <video controls autoplay class="learn-media" style="width:100%; max-height:300px; border-radius:12px;">
                                <source src="${relativeImgPath}" type="video/mp4">
                            </video>
                        `;
                    } else {
                        mediaHtml = `<img src="${relativeImgPath}" class="learn-img" alt="${card.title}" style="max-width:100%; max-height:300px;">`;
                    }
                }

                const cardHtml = `
                    <div class="concept-card">
                        <h3>${card.title || emotion}</h3>
                        <p>${card.description || ""}</p>
                        ${mediaHtml}
                    </div>
                `;
                elements.learningBody.insertAdjacentHTML('beforeend', cardHtml);
            });
        }

        elements.learningCloseBtn.onclick = () => {
            const videos = elements.learningBody.querySelectorAll('video');
            videos.forEach(v => v.pause());

            elements.learningModal.classList.add('hidden');
            currentIndex++;
            loadQuestion(currentIndex);
        };
        elements.learningModal.classList.remove('hidden');
    }

    if (elements.exitBtn) {
        elements.exitBtn.onclick = () => {
            if (confirm('Thoát game không lưu tiến trình?')) {
                window.location.href = './select_game.html';
            }
        };
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

    elements.answers.forEach(btn => {
        if (!btn) return;
        btn.onclick = () => {
            if (answered) return;
            answered = true;

            const q = questions[currentIndex];
            const chosen = btn.dataset.answer;
            const correct = normalizeEmotion(chosen) === normalizeEmotion(q.correct_answer);
            const emotion = q.correct_answer;
            const emotionKey = normalizeEmotion(emotion);

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

                // --- LOGIC POPUP TỰ ĐỘNG KHI SAI NHIỀU ---
                if (emotionErrors[emotionKey] >= maxErrors && !learnedEmotions.includes(emotionKey)) {
                    learnedEmotions.push(emotionKey);

                    // KHÔNG RETURN: Sau khi push learnedEmotions, nó phải chạy xuống showFeedback
                    // showFeedback sẽ kiểm tra và hiển thị nút "Học Lại" duy nhất.
                }
            }

            // Disable nút sau khi chọn
            elements.answers.forEach(b => {
                if (b.dataset.answer === q.correct_answer) b.classList.add('correct');
                else if (b === btn && !correct) b.classList.add('incorrect');
                b.disabled = true;
            });

            // Gọi showFeedback. Hàm này sẽ tự động kiểm tra isForcedLearning
            showFeedback(correct, q.correct_answer, emotion);
        };
    });
});