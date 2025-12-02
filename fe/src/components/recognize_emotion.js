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

document.addEventListener('DOMContentLoaded', async () => {
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
        const res = await fetch(`/games/start/${gameId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: user.user_id, level })
        });

        if (!res.ok) throw new Error("Lỗi khởi động game");

        const data = await res.json();

        sessionId = data.session_id;
        questions = data.questions;
        learningCards = data.learning_cards || {};

        // Chuẩn hóa key cảm xúc về chữ thường
        const normalizedLearningCards = {};
        for (const key in learningCards) {
            if (learningCards.hasOwnProperty(key)) {
                normalizedLearningCards[key.trim().toLowerCase()] = learningCards[key];
            }
        }
        learningCards = normalizedLearningCards;

        // Khởi tạo emotionErrors với các key đã chuẩn hóa
        emotionErrors = {
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
        return;
    }

    async function sendFinalResults() {
        try {
            await fetch('/games/end-level', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    results: localResults
                })
            });
        } catch (err) {
            console.error(err);
        }
    }

    // LOAD QUESTION
    async function loadQuestion(i) {
        if (i >= questions.length) {
            await sendFinalResults();
            alert('Hoàn thành level!');
            window.location.href = './select_game.html';
            return;
        }

        usedHint = false;
        const q = questions[i];

        // Reset Question Area
        elements.questionArea.innerHTML = '';

        if (q.media_path && q.media_path.match(/\.(jpeg|jpg|gif|png)$/)) {
            const img = document.createElement('img');
            // Dùng logic thay thế đường dẫn tương đối đã sửa ở bước trước
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
            // Reset style và trạng thái nút
            btn.className = 'answer-option';
            btn.disabled = false;
        });

        elements.hintText.textContent = 'Hãy chọn đáp án của bạn.';
        elements.score.textContent = `Câu ${i + 1}/${questions.length} | Điểm: ${score}`;

        answered = false;
        elements.feedbackModal.classList.add('hidden'); // Đảm bảo Modal Feedback ẩn
        elements.learningModal.classList.add('hidden'); // Đảm bảo Modal Học tập ẩn
    }

    // FEEDBACK POPUP
    function showFeedback(correct, correctAns, emotionKey) {
        elements.modalTitle.textContent = correct ? 'CHÍNH XÁC!' : 'SAI RỒI!';
        elements.modalTitle.style.color = correct ? '#10b981' : '#ef4444';
        elements.modalMsg.textContent = correct ? 'Giỏi lắm!' : `Đáp án đúng: ${correctAns}`;

        // Reset container
        elements.modalActionsContainer.innerHTML = '';

        // Trường hợp SAI & đạt max lỗi → chỉ hiện nút Học lại
        if (!correct && emotionErrors[emotionKey.trim().toLowerCase()] >= maxErrors) {
            const learnBtn = document.createElement('button');
            learnBtn.textContent = "Học lại cảm xúc";
            learnBtn.className = "modal-btn learn-btn";
            learnBtn.onclick = () => showLearningCard(emotionKey);

            elements.modalActionsContainer.appendChild(learnBtn);
        } else {
            // === CÁC TRƯỜNG HỢP CÒN LẠI ===
            // Hiển thị 2 nút: Xem lại & Câu tiếp theo

            const reviewBtn = document.createElement('button');
            reviewBtn.textContent = "Xem lại";
            reviewBtn.className = "modal-btn review-btn";
            reviewBtn.onclick = () => elements.feedbackModal.classList.add('hidden'); // Đóng modal

            const nextBtn = document.createElement('button');
            nextBtn.textContent = "Câu tiếp theo";
            nextBtn.className = "modal-btn next-btn";
            nextBtn.onclick = handleNextAfterPopup;

            elements.modalActionsContainer.appendChild(reviewBtn);
            elements.modalActionsContainer.appendChild(nextBtn);
        }

        elements.feedbackModal.classList.remove('hidden');
    }


    // NEXT QUESTION from popup
    function handleNextAfterPopup() {
        elements.feedbackModal.classList.add('hidden');
        currentIndex++;
        loadQuestion(currentIndex);
    }

    // POPUP HỌC LẠI
    function showLearningCard(emotion) {
        elements.feedbackModal.classList.add('hidden'); // Ẩn Modal Feedback

        const emotionKey = emotion.trim().toLowerCase();
        const cards = learningCards[emotionKey]?.[level]; // Lấy danh sách thẻ học theo level

        elements.learningTitle.textContent = emotion; // Hiển thị tên cảm xúc
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

        // Gán sự kiện cho nút Đã hiểu/Tiếp tục của Modal Học tập
        elements.learningCloseBtn.onclick = () => {
            elements.learningModal.classList.add('hidden');
            currentIndex++;
            loadQuestion(currentIndex);
        };

        elements.learningModal.classList.remove('hidden');
    }


    // HINT
    elements.hintBtn.onclick = () => {
        usedHint = true;
        elements.hintText.textContent = questions[currentIndex].explanation;
    };

    // SOUND
    elements.soundBtn.onclick = () => {
        const msg = new SpeechSynthesisUtterance(questions[currentIndex].question_text);
        msg.lang = 'vi-VN';
        speechSynthesis.speak(msg);
    };

    // EXIT
    elements.exitBtn.onclick = () => {
        if (confirm('Thoát game không lưu tiến trình?')) {
            window.location.href = './select_game.html';
        }
    };

    // CLICK ANSWER
    elements.answers.forEach(btn => {
        btn.onclick = () => {
            if (answered) return;
            answered = true;

            const q = questions[currentIndex];
            const chosen = btn.dataset.answer;
            const correct = (chosen === q.correct_answer);
            const emotion = q.correct_answer; // Emotion key (Ví dụ: "Vui vẻ")
            const emotionKey = emotion.trim().toLowerCase(); // Key đã chuẩn hóa ("vui vẻ")

            if (correct) score += 10;

            localResults.push({
                question_id: q.question_id,
                answer: chosen,
                is_correct: correct,
                used_hint: usedHint,
                response_time_ms: 5000
            });

            if (!correct) {
                // Tăng lỗi cho cảm xúc, sử dụng key đã chuẩn hóa
                emotionErrors[emotionKey] = (emotionErrors[emotionKey] || 0) + 1;

                if (emotionErrors[emotionKey] >= maxErrors && !learnedEmotions.includes(emotionKey)) {
                    // Đánh dấu là đã học và không hiện lại
                    learnedEmotions.push(emotionKey);
                // Hiển thị Modal Feedback với nút Học lại
                    showFeedback(false, q.correct_answer, emotion);
                    return; // Chặn logic hiển thị đáp án và chuyển sang feedback thường
                }
            }

            // Logic tô màu nút (chỉ chạy nếu không bị chặn bởi Học lại bắt buộc)
            elements.answers.forEach(b => {
                if (b.dataset.answer === q.correct_answer) b.classList.add('correct');
                else if (b === btn && !correct) b.classList.add('incorrect');
                b.disabled = true;
            });

            // Hiển thị Modal Feedback thông thường
            showFeedback(correct, q.correct_answer, emotion);
        };
    });
});