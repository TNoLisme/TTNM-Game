// fe/src/components/game_click_1.js
const MOCK_GAME_DATA = [
    { question: 'Khi nhận được quà sinh nhật, bạn nhỏ thường biểu hiện cảm xúc gì?', answers: ['Vui vẻ', 'Tức giận', 'Sợ hãi', 'Ghê tởm'], correct: 'Vui vẻ', hint: 'Cảm xúc này thường làm khóe miệng cong lên.' },
    { question: 'Xem hình ảnh sau, bạn nhỏ đang cảm thấy thế nào?', answers: ['Buồn bã', 'Ngạc nhiên', 'Vui vẻ', 'Tức giận'], correct: 'Buồn bã', hint: 'Nét mặt này cho thấy bé vừa làm rơi đồ chơi yêu thích.' },
    // Thêm câu hỏi khác nếu cần
];

let currentIndex = 0;
let answered = false;
let elements = {};

document.addEventListener('DOMContentLoaded', () => {
    elements = {
        modal: document.getElementById('feedback-modal'),
        warning: document.getElementById('warning-modal'),
        title: document.getElementById('modal-title'),
        msg: document.getElementById('modal-message'),
        reviewBtn: document.getElementById('review-btn'),
        nextBtn: document.getElementById('next-btn'),
        closeWarn: document.getElementById('close-warning'),

        score: document.getElementById('score-display'),
        questionText: document.querySelector('#question-area .question-text'),
        hintText: document.getElementById('hint-content'),
        hintBtn: document.getElementById('hint-btn'),
        soundBtn: document.getElementById('sound-btn'),
        exitBtn: document.getElementById('exit-btn'),
        nextHintBtn: document.getElementById('next-question-btn'),
        answers: document.querySelectorAll('.answer-option')
    };

    function loadQuestion(i) {
        if (i >= MOCK_GAME_DATA.length) {
            alert('Hoàn thành game!');
            window.location.href = './select_game.html';
            return;
        }
        const q = MOCK_GAME_DATA[i];
        elements.questionText.textContent = q.question;
        elements.hintText.textContent = 'Hãy chọn đáp án của bạn.';
        elements.score.textContent = `Câu ${i + 1}/${MOCK_GAME_DATA.length} | ĐIỂM: ${i * 10}`;
        elements.answers.forEach((btn, idx) => {
            btn.textContent = q.answers[idx];
            btn.className = 'answer-option';
            btn.disabled = false;
        });
        elements.nextHintBtn.disabled = true;
        elements.nextHintBtn.style.opacity = '0.6';
        answered = false;
        elements.modal.classList.add('hidden');
    }

    function showFeedback(correct, correctAns) {
        elements.title.textContent = correct ? 'CHÍNH XÁC!' : 'SAI RỒI!';
        elements.title.style.color = correct ? '#10b981' : '#ef4444';
        elements.msg.textContent = correct ? 'Tuyệt vời!' : `Đáp án đúng là: ${correctAns}`;
        elements.modal.classList.remove('hidden');
    }

    // Hint
    elements.hintBtn.onclick = () => {
        elements.hintText.textContent = MOCK_GAME_DATA[currentIndex].hint;
    };

    // Âm thanh
    elements.soundBtn.onclick = () => {
        const utter = new SpeechSynthesisUtterance(MOCK_GAME_DATA[currentIndex].question);
        utter.lang = 'vi-VN';
        speechSynthesis.speak(utter);
    };

    // Thoát
    elements.exitBtn.onclick = () => {
        if (confirm('Thoát game?')) window.location.href = './select_game.html';
    };

    // Chọn đáp án
    elements.answers.forEach(btn => {
        btn.onclick = () => {
            if (answered) return;
            answered = true;
            const selected = btn.textContent;
            const correct = selected === MOCK_GAME_DATA[currentIndex].correct;

            btn.classList.add(correct ? 'correct' : 'incorrect');
            if (!correct) {
                elements.answers.forEach(b => {
                    if (b.textContent === MOCK_GAME_DATA[currentIndex].correct) b.classList.add('correct');
                });
            }
            elements.answers.forEach(b => b.disabled = true);
            elements.nextHintBtn.disabled = false;
            elements.nextHintBtn.style.opacity = '1';
            showFeedback(correct, MOCK_GAME_DATA[currentIndex].correct);
        };
    });

    // Nút "Câu tiếp theo" ở hint
    elements.nextHintBtn.onclick = () => {
        if (!answered) {
            elements.warning.classList.remove('hidden');
            return;
        }
        currentIndex++;
        loadQuestion(currentIndex);
    };

    // Modal buttons
    elements.reviewBtn.onclick = () => elements.modal.classList.add('hidden');
    elements.nextBtn.onclick = () => {
        elements.modal.classList.add('hidden');
        currentIndex++;
        loadQuestion(currentIndex);
    };
    elements.closeWarn.onclick = () => elements.warning.classList.add('hidden');

    loadQuestion(0);
});