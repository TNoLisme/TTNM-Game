// fe/src/components/recognize_emotion.js

let sessionId = null;
let questions = [];
let localResults = []; // <-- THÊM: Mảng lưu kết quả local
let currentIndex = 0;
let score = 0; // <-- THÊM: Điểm local
let answered = false;
let elements = {};
let user = null;
let gameId = null; // <-- THÊM: Lưu gameId
let level = null; // <-- THÊM: Lưu level

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

    // DOM Elements (Lấy trước)
    elements = {
        modal: document.getElementById('feedback-modal'),
        warning: document.getElementById('warning-modal'),
        title: document.getElementById('modal-title'),
        msg: document.getElementById('modal-message'),
        reviewBtn: document.getElementById('review-btn'),
        nextBtn: document.getElementById('next-btn'),
        closeWarn: document.getElementById('close-warning'),
        score: document.getElementById('score-display'),
        questionArea: document.getElementById('question-area'), // Sửa: Lấy ID
        hintText: document.getElementById('hint-content'),
        hintBtn: document.getElementById('hint-btn'),
        soundBtn: document.getElementById('sound-btn'),
        exitBtn: document.getElementById('exit-btn'),
        nextHintBtn: document.getElementById('next-question-btn'),
        answers: document.querySelectorAll('.answer-option') // Lấy 4 nút
    };

    // Bắt đầu session (SỬA URL thành endpoint chung)
    try {
        const res = await fetch(`/games/start/${gameId}`, { // <-- SỬA ENDPOINT
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: user.user_id, level: level })
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || 'Lỗi khởi động game');
        }

        const data = await res.json();
        sessionId = data.session_id;
        questions = data.questions;
        localResults = []; // Reset mảng kết quả
        score = 0; // Reset điểm
        if (!questions || questions.length === 0) {
            throw new Error("Không thể tải câu hỏi cho level này. (Mảng rỗng)");
        }
        loadQuestion(0);

    } catch (err) {
        alert(err.message);
        console.error(err);
    }

    // === HÀM MỚI: GỬI KẾT QUẢ KHI KẾT THÚC ===
    async function sendFinalResults() {
        console.log("Đang gửi kết quả cuối cùng:", localResults);
        try {
            const res = await fetch('/games/end-level', { // <-- ENDPOINT MỚI
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // 'Authorization': `Bearer ${user.token}`
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    results: localResults // Gửi mảng kết quả
                })
            });

            if (!res.ok) {
                throw new Error("Lỗi khi gửi kết quả cuối cùng.");
            }

            console.log("Đã lưu tiến trình thành công.");

        } catch (err) {
            console.error("Lỗi khi gửi kết quả cuối cùng:", err);
            alert("Đã xảy ra lỗi khi lưu tiến trình của bạn.");
        }
    }

    // === HÀM LOAD CÂU HỎI (ĐÃ SỬA RENDER) ===
    async function loadQuestion(i) {
        // === XỬ LÝ KHI KẾT THÚC LEVEL ===
        if (i >= questions.length) {
            await sendFinalResults(); // Gửi kết quả
            alert('Hoàn thành level! Đã lưu tiến trình của bạn.');
            window.location.href = './select_game.html';
            return;
        }

        const q = questions[i];

        // --- SỬA RENDER ---
        // 1. Xóa nội dung cũ
        elements.questionArea.innerHTML = '';

        // 2. Thêm ảnh (nếu có)
        // (Giả sử media_path là đường dẫn tương đối hoặc tuyệt đối đến ảnh)
        if (q.media_path && q.media_path.match(/\.(jpeg|jpg|gif|png)$/)) {
            const img = document.createElement('img');
            img.src = q.media_path; // (FE cần xử lý đường dẫn này, ví dụ: `../${q.media_path}`)
            img.alt = q.question_text;
            img.className = 'question-image'; // (Cần CSS cho class này)
            elements.questionArea.appendChild(img);
        }

        // 3. Thêm text câu hỏi
        const textEl = document.createElement('p');
        textEl.className = 'question-text';
        textEl.textContent = q.question_text;
        elements.questionArea.appendChild(textEl);

        // 4. Render 4 đáp án (Lấy từ q.options)
        elements.answers.forEach((btn, idx) => {
            if (q.options[idx]) {
                const option = q.options[idx];
                btn.textContent = option.answer_text; // Lấy text từ API
                // Lưu câu trả lời đúng vào dataset để check
                btn.dataset.answer = option.answer_text;
                btn.style.display = 'block';
            } else {
                btn.style.display = 'none'; // Ẩn nếu game có ít hơn 4 đáp án
            }
            btn.className = 'answer-option';
            btn.disabled = false;
        });
        // --- KẾT THÚC SỬA RENDER ---

        elements.hintText.textContent = 'Hãy chọn đáp án của bạn.';
        elements.score.textContent = `Câu ${i + 1}/${questions.length} | ĐIỂM: ${score}`;

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

    elements.hintBtn.onclick = () => {
        elements.hintText.textContent = questions[currentIndex].explanation;
    };

    elements.soundBtn.onclick = () => {
        const utter = new SpeechSynthesisUtterance(questions[currentIndex].question_text);
        utter.lang = 'vi-VN';
        speechSynthesis.speak(utter);
    };

    elements.exitBtn.onclick = () => {
        if (confirm('Thoát game? (Tiến trình sẽ không được lưu)')) {
            window.location.href = './select_game.html';
        }
    };

    // === HÀM CLICK ĐÁP ÁN (ĐÃ SỬA: XÓA FETCH) ===
    elements.answers.forEach(btn => {
        btn.onclick = async () => {
            if (answered) return;
            answered = true;

            const selected = btn.dataset.answer; // Lấy từ dataset
            const q = questions[currentIndex];
            const correct = (selected === q.correct_answer);

            // Cập nhật điểm local
            if (correct) {
                score += 10;
                elements.score.textContent = `Câu ${currentIndex + 1}/${questions.length} | ĐIỂM: ${score}`;
            }

            // === THÊM: LƯU KẾT QUẢ VÀO MẢNG LOCAL ===
            localResults.push({
                question_id: q.question_id,
                answer: selected,
                is_correct: correct,
                response_time_ms: 5000 // (Tạm thời, bạn cần logic đo thời gian)
            });

            // Hiệu ứng UI
            btn.classList.add(correct ? 'correct' : 'incorrect');
            if (!correct) {
                elements.answers.forEach(b => {
                    if (b.dataset.answer === q.correct_answer) b.classList.add('correct');
                });
            }
            elements.answers.forEach(b => b.disabled = true);
            elements.nextHintBtn.disabled = false;
            elements.nextHintBtn.style.opacity = '1';

            // === XÓA: KHÔNG CẦN GỌI API Ở ĐÂY NỮA ===
            // await fetch('/api/games/recognize-emotion/answer', ...);

            showFeedback(correct, q.correct_answer);
        };
    });

    // (Các hàm xử lý modal giữ nguyên)
    elements.nextHintBtn.onclick = () => {
        if (!answered) {
            elements.warning.classList.remove('hidden');
            return;
        }
        currentIndex++;
        loadQuestion(currentIndex);
    };
    elements.reviewBtn.onclick = () => elements.modal.classList.add('hidden');
    elements.nextBtn.onclick = () => {
        elements.modal.classList.add('hidden');
        currentIndex++;
        loadQuestion(currentIndex);
    };
    elements.closeWarn.onclick = () => elements.warning.classList.add('hidden');
});