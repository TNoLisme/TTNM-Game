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
        modal: document.getElementById('feedback-modal'),
        warning: document.getElementById('warning-modal'),
        title: document.getElementById('modal-title'),
        msg: document.getElementById('modal-message'),
        nextHintBtn: document.getElementById('next-question-btn'),
        closeWarn: document.getElementById('close-warning'),
        score: document.getElementById('score-display'),
        questionArea: document.getElementById('question-area'),
        hintText: document.getElementById('hint-content'),
        hintBtn: document.getElementById('hint-btn'),
        soundBtn: document.getElementById('sound-btn'),
        exitBtn: document.getElementById('exit-btn'),
        answers: document.querySelectorAll('.answer-option')
    };

    // START SESSION API
    try {
        const res = await fetch(`/games/start/${gameId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: user.user_id, level })
        });

        const data = await res.json();

        sessionId = data.session_id;
        questions = data.questions;
        learningCards = data.learning_cards || {};

        // Fake emotion errors để test
        emotionErrors = {
            "Sợ hãi": 2,
            "Buồn bã": 1,
            "Tức giận": 3,
            "Ghê tởm": 0,
            "Ngạc nhiên": 4,
            "Vui vẻ": 0
        };

        loadQuestion(0);

    } catch (err) {
        alert("Lỗi khởi động game");
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

        elements.questionArea.innerHTML = '';

        if (q.media_path && q.media_path.match(/\.(jpeg|jpg|gif|png)$/)) {
            const img = document.createElement('img');
            img.src = q.media_path;
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
        elements.modal.classList.add('hidden');
    }

    // FEEDBACK POPUP
    function showFeedback(correct, correctAns, emotion) {
        elements.modal.classList.remove('hidden');
        elements.title.textContent = correct ? 'CHÍNH XÁC!' : 'SAI RỒI!';
        elements.title.style.color = correct ? '#10b981' : '#ef4444';
        elements.msg.textContent = correct ? 'Giỏi lắm!' : `Đáp án đúng: ${correctAns}`;

        const btnContainer = elements.modal.querySelector('.modal-actions');
        btnContainer.innerHTML = ''; // Xóa nút cũ để render mới

        const bottomContainer = elements.modal.querySelector('.modal-buttons');
        bottomContainer.innerHTML = '';

        // Trường hợp SAI & đạt max lỗi → chỉ hiện nút Học lại
        if (!correct && emotionErrors[emotion] >= maxErrors) {
            const learnBtn = document.createElement('button');
            learnBtn.textContent = "Học lại cảm xúc";
            learnBtn.className = "modal-btn learn-btn";
            learnBtn.onclick = () => showLearningCard(emotion);

            bottomContainer.appendChild(learnBtn);
            return;
        }

        // === CÁC TRƯỜNG HỢP CÒN LẠI ===
        // Bao gồm: trả lời đúng OR trả lời sai nhưng chưa đạt maxError
        // => hiển thị 2 nút: Xem lại & Câu tiếp theo

        const reviewBtn = document.createElement('button');
        reviewBtn.textContent = "Xem lại";
        reviewBtn.className = "modal-btn review-btn";
        reviewBtn.onclick = () => {
            elements.modal.classList.add('hidden');
            // tuỳ bạn muốn xử lý gì trong phần xem lại
        };

        const nextBtn = document.createElement('button');
        nextBtn.textContent = "Câu tiếp theo";
        nextBtn.className = "modal-btn next-btn";
        nextBtn.onclick = handleNextAfterPopup;

        btnContainer.appendChild(reviewBtn);
        btnContainer.appendChild(nextBtn);
    }


    // NEXT QUESTION from popup
    function handleNextAfterPopup() {
        elements.modal.classList.add('hidden');
        currentIndex++;
        loadQuestion(currentIndex);
    }

    // POPUP HỌC LẠI
    function showLearningCard(emotion) {
        const card = learningCards[emotion]?.[level];
        if (!card) {
            alert("Không có thẻ học cho cảm xúc này!");
            return;
        }

    // Ẩn feedback cũ
        elements.modal.classList.remove('hidden');
        const modalContent = elements.modal.querySelector('.modal-content');

        // Thay nội dung modal thành thẻ học
        modalContent.innerHTML = `
        <h2>${card.title}</h2>
        <p>${card.description}</p>
        ${card.image_path ? `<img src="${card.image_path}" class="learn-img">` : ''}
        ${card.audio_path && card.audio_path.length > 0
                ? `<h3>Video/Audio:</h3>
            <ul>${card.audio_path.map(a => `<li><a href="${a}" target="_blank">${a.split('/').pop()}</a></li>`).join('')}</ul>`
                : ''}
        <div class="modal-buttons">
            <button id="learn-close-btn" class="btn-next">Tiếp tục</button>
        </div>
    `;

        // Tiếp tục
        document.getElementById('learn-close-btn').onclick = () => {
            currentIndex++;
            loadQuestion(currentIndex);
            elements.modal.classList.add('hidden');
        };
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
            const emotion = q.correct_answer;

            if (correct) score += 10;

            localResults.push({
                question_id: q.question_id,
                answer: chosen,
                is_correct: correct,
                used_hint: usedHint,
                response_time_ms: 5000
            });

            if (!correct) {
                emotionErrors[emotion] = (emotionErrors[emotion] || 0) + 1;

                if (emotionErrors[emotion] >= maxErrors) {
                    learnedEmotions.push(emotion);
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
