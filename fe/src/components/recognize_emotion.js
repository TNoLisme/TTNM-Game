// fe/src/components/recognize_emotion.js

let sessionId = null;
let questions = [];
let localResults = [];
let currentIndex = 0;
let score = 0;
let answered = false;
let usedHint = false;
let selectedAnswer = null;
let selectedButton = null;

let elements = {};
let user = null;
let gameId = null;
let level = null;
let maxErrors = 1;

let emotionErrors = {};
let learnedEmotions = [];

let learningCards = {};

let ttsAudio = null;
const ttsCache = new Map();
const ttsPending = new Map();

function ttsKey(text, voice = "thuminh", speed = 0) {
    return `${voice}:${speed}:${(text || "").trim().toLowerCase()}`;
}

async function playAudioUrl(url, retries = 6, delayMs = 300) {
    if (!ttsAudio) ttsAudio = new Audio();
    ttsAudio.pause();

    for (let i = 0; i <= retries; i++) {
        try {
            const tryUrl = url + (url.includes("?") ? "&" : "?") + "t=" + Date.now();

            await new Promise((resolve, reject) => {
                ttsAudio.src = tryUrl;
                ttsAudio.load();

                const ok = () => {
                    cleanup();
                    resolve();
                };
                const bad = () => {
                    cleanup();
                    reject(new Error("audio load error"));
                };
                const cleanup = () => {
                    ttsAudio.removeEventListener("canplaythrough", ok);
                    ttsAudio.removeEventListener("error", bad);
                };

                ttsAudio.addEventListener("canplaythrough", ok, {
                    once: true
                });
                ttsAudio.addEventListener("error", bad, {
                    once: true
                });
            });

            await ttsAudio.play();
            return;
        } catch (e) {
            if (i === retries) throw e;
            await new Promise(r => setTimeout(r, delayMs));
        }
    }
}

async function prefetchTTS(text, voice = "thuminh", speed = 0) {
    const clean = (text || "").trim();
    if (!clean) return null;

    const key = ttsKey(clean, voice, speed);

    if (ttsCache.has(key)) return ttsCache.get(key);
    if (ttsPending.has(key)) return await ttsPending.get(key);

    const p = (async () => {
        const res = await fetch("http://localhost:8000/tts", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: clean,
                voice,
                speed
            }),
        });

        if (!res.ok) {
            const msg = await res.text().catch(() => "");
            throw new Error(msg || "TTS error");
        }

        const {
            audioUrl
        } = await res.json();
        if (!audioUrl) throw new Error("Missing audioUrl from /tts");
        ttsCache.set(key, audioUrl);
        return audioUrl;
    })();

    ttsPending.set(key, p);
    try {
        return await p;
    } finally {
        ttsPending.delete(key);
    }
}

async function speakVietnamese(text, voice = "thuminh", speed = 0) {
    const audioUrl = await prefetchTTS(text, voice, speed);
    if (!audioUrl) return;
    await playAudioUrl(audioUrl);
}

function normalizeEmotion(text) {
    return (text || '').trim().toLowerCase();
}

const EMOTION_ICONS = {
    'vui vẻ': '😊',
    'vui': '😊',
    'buồn bã': '😢',
    'buồn': '😢',
    'ngạc nhiên': '😲',
    'tức giận': '😠',
    'sợ hãi': '😨',
    'ghê tởm': '🤢'
};

const VI_EMOTION_MAP = {
    "vui vẻ": "happy",
    "buồn bã": "sad",
    "tức giận": "angry",
    "sợ hãi": "fear",
    "ngạc nhiên": "surprise",
    "ghê tởm": "disgust"
};

const EMOTION_COLORS = {
    happy: "#81c784",    // Soft Green
    sad: "#64b5f6",      // Soft Blue
    angry: "#e57373",    // Muted Red
    fear: "#ba68c8",     // Soft Purple
    surprise: "#ffd54f", // Soft Yellow
    disgust: "#ffb74d"   // Soft Orange
};


function getEnglishEmotionKey(rawEmotion) {
    if (!rawEmotion) return "";

    const normalizedInput = rawEmotion.trim().toLowerCase();

    return VI_EMOTION_MAP[normalizedInput] || normalizedInput;
}
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
        progressLabel: document.getElementById('progress-label'),
        scoreLabel: document.getElementById('score-label'),
        questionArea: document.getElementById('question-area'),
        hintText: document.getElementById('hint-content'),
        hintBtn: document.getElementById('hint-btn'),
        soundBtn: document.getElementById('sound-btn'),
        exitBtn: document.getElementById('exit-btn'),
        answers: document.querySelectorAll('.answer-option'),
        submitBtn: document.getElementById('next-question-btn'),
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
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: user.user_id,
                level
            })
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
        console.log("learning :", learningCards);

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
        return;
    }

    async function sendFinalResults() {
        try {
            await fetch('/games/end-level', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
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
            showSystemPopup('Hoàn thành', `Bạn đã hoàn thành! Tổng điểm: ${score}`, () => {
                window.location.href = `./level_select.html?gameId=${gameId}`;
            }, 'Quay lại chọn level');
            return;
        }

        usedHint = false;
        selectedAnswer = null;
        selectedButton = null;
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

        if (elements.submitBtn) {
            elements.submitBtn.disabled = true;
        }

        elements.hintText.textContent = '';
        if (elements.progressLabel) {
            elements.progressLabel.textContent = `Câu ${i + 1}/${questions.length}`;
        }
        if (elements.scoreLabel) {
            elements.scoreLabel.textContent = `Điểm: ${score}`;
        }

        const progressFill = document.getElementById('click-progress-fill');
        if (progressFill) {
            const percentage = ((i + 1) / questions.length) * 100;
            progressFill.style.width = `${percentage}%`;
        }

        answered = false;
        elements.feedbackModal.classList.add('hidden');
        elements.learningModal.classList.add('hidden');
        prefetchTTS(q.question_text, "thuminh", 0);
        const nextQ = questions[i + 1];
        if (nextQ) prefetchTTS(nextQ.question_text, "thuminh", 0);
    }

    function onSubmitAnswer() {
        if (answered) return;
        const q = questions[currentIndex];
        if (!q) return;

        if (!selectedAnswer || !selectedButton) {
            alert('Hãy chọn một cảm xúc trước khi trả lời.');
            return;
        }

        answered = true;

        const chosen = selectedAnswer;
        const correct = normalizeEmotion(chosen) === normalizeEmotion(q.correct_answer);
        const emotion = q.correct_answer;

        // ĐỒNG BỘ: Sử dụng English Key cho emotionErrors và learnedEmotions
        const emotionKey = getEnglishEmotionKey(emotion);

        if (correct) score += 10;
        if (elements.scoreLabel) {
            elements.scoreLabel.textContent = `Điểm: ${score}`;
        }

        localResults.push({
            question_id: q.question_id,
            answer: chosen,
            is_correct: correct,
            used_hint: usedHint,
            response_time_ms: 5000
        });

        if (!correct) {
            // Tăng đếm lỗi dựa trên English Key
            emotionErrors[emotionKey] = (emotionErrors[emotionKey] || 0) + 1;

            // Nếu đạt max lỗi, đưa vào danh sách bắt buộc học lại
            if (emotionErrors[emotionKey] >= maxErrors && !learnedEmotions.includes(emotionKey)) {
                learnedEmotions.push(emotionKey);
            }
        }

        // Hiệu ứng màu sắc nút bấm
        elements.answers.forEach(b => {
            b.classList.remove('selected');
            if (b.dataset.answer === q.correct_answer) b.classList.add('correct');
            else if (b === selectedButton && !correct) b.classList.add('incorrect');
            b.disabled = true;
        });

        if (elements.submitBtn) {
            elements.submitBtn.disabled = true;
        }

        // Gọi hàm hiện modal phản hồi (Bên trong hàm này sẽ check isForcedLearning)
        showFeedback(correct, q.correct_answer, emotion);
    }

    // Popup Sai/Đúng (Đã sửa logic hiển thị nút)
    function showFeedback(correct, correctAns, emotion) {
        const emotionKey = getEnglishEmotionKey(emotion);
        const correctKey = getEnglishEmotionKey(correctAns);

        // Lấy màu sắc nổi bật cho đáp án đúng
        const correctColor = EMOTION_COLORS[correctKey] || "#64b5f6";
        const emotionColor = EMOTION_COLORS[emotionKey] || "#64b5f6";


        // 1. Thiết lập Tiêu đề Modal
        elements.modalTitle.textContent = correct ? 'CHÍNH XÁC!' : 'CHƯA ĐÚNG RỒI!';
        elements.modalTitle.style.color = correct ? '#66bb6a' : '#ffa726';

        // 2. Xóa nội dung cũ trong container nút bấm
        elements.modalActionsContainer.innerHTML = '';

        // Kiểm tra ngưỡng học lại bắt buộc
        const isForcedLearning = !correct &&
            emotionErrors[emotionKey] >= maxErrors &&
            learnedEmotions.includes(emotionKey);

        if (isForcedLearning) {
            // --- TRƯỜNG HỢP: BẮT BUỘC ÔN TẬP ---
            elements.modalTitle.textContent = 'CẦN ÔN TẬP LẠI CẢM XÚC NÀY!';
            elements.modalTitle.style.color = "#4dd0e1"; // Cyan-600

            // Đồng bộ font với mặc định, chỉ giữ màu và in đậm
            elements.modalMsg.innerHTML = `
            <div class="text-center">
                <p class="mb-2">Đáp án chính xác là: <strong style="color: ${correctColor}; font-weight: bold;">"${emotion}"</strong></p>
                <p class="text-gray-600 text-sm">
                    Bạn đã trả lời chưa đúng nhiều lần ở cảm xúc <strong style="color: ${emotionColor}; font-weight: bold;">"${emotion}"</strong>.
                    <br>Hãy học lại để ôn tập kiến thức trước khi tiếp tục nhé!
                </p>
            </div>
        `;

            const learnBtn = document.createElement('button');
            learnBtn.textContent = "HỌC LẠI CẢM XÚC NÀY";
            learnBtn.className = "modal-btn learn-btn";
            learnBtn.style.backgroundColor = "#64b5f6";
            learnBtn.style.color = "white";
            learnBtn.onclick = () => showLearningCard(emotion);

            elements.modalActionsContainer.appendChild(learnBtn);
        } else {
            // --- TRƯỜNG HỢP: PHẢN HỒI BÌNH THƯỜNG ---
            if (correct) {
                elements.modalMsg.innerHTML = `
                <div class="text-center" style="color: #43a047; font-weight: 500;">
                    ✨ Bạn làm tốt lắm, tiếp tục phát huy nhé.
                </div>
            `;
            } else {
                // Đồng bộ font với mặc định, chỉ giữ màu và in đậm
                elements.modalMsg.innerHTML = `
                <div class="text-center" style="color: #546e7a;">
                    Đáp án đúng là: <strong style="color: ${correctColor}; font-weight: bold;">"${correctAns}"</strong>.
                    <br>
                    <span class="mt-2 block text-gray-500 italic text-sm">Hãy cố gắng hơn ở câu tiếp theo nhé!</span>
                </div>
            `;
            }

            // Tạo nút "Xem lại"
            const reviewBtn = document.createElement('button');
            reviewBtn.textContent = "Xem lại";
            reviewBtn.className = "modal-btn review-btn";
            reviewBtn.onclick = () => elements.feedbackModal.classList.add('hidden');

            // Tạo nút "Câu tiếp theo"
            const nextBtn = document.createElement('button');
            nextBtn.textContent = "Câu tiếp theo";
            nextBtn.className = "modal-btn next-btn";
            nextBtn.onclick = handleNextAfterPopup;

            elements.modalActionsContainer.appendChild(reviewBtn);
            elements.modalActionsContainer.appendChild(nextBtn);
        }

        // Hiển thị Modal
        elements.feedbackModal.classList.remove('hidden');
    }

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
    function handleNextAfterPopup() {
        elements.feedbackModal.classList.add('hidden');
        currentIndex++;
        loadQuestion(currentIndex);
    }

    function showLearningCard(emotion) {
        // 1. Ẩn modal phản hồi (sai/đúng) trước đó
        elements.feedbackModal.classList.add('hidden');

        // 2. Chuyển đổi sang key tiếng Anh và lấy mã màu
        const emotionKey = getEnglishEmotionKey(emotion);
        const emotionHexColor = EMOTION_COLORS[emotionKey] || "#64b5f6";

        // 3. Cập nhật thông báo nổi bật đáp án và lỗi (Đồng bộ font)
        if (elements.modalMsg) {
            elements.modalMsg.innerHTML = `
            <div class="mb-4">
                <span class="text-gray-500 block text-xs uppercase font-semibold mb-1">Kết quả đúng là:</span>
                <strong style="color: #16a34a; font-weight: bold; display: block;">"${emotion}"</strong>
            </div>
            <div class="text-gray-700 leading-relaxed">
                Bạn đã trả lời chưa chính xác nhiều lần với cảm xúc 
                <strong style="color: ${emotionHexColor}; font-weight: bold;">"${emotion}"</strong>. 
                <br><span class="text-sm opacity-90">Hãy cùng ôn tập lại để nhận diện tốt hơn nhé!</span>
            </div>
        `;
        }

        let cards = [];
        const rawData = learningCards[emotionKey];

        if (Array.isArray(rawData)) {
            cards = rawData;
        } else if (rawData && typeof rawData === 'object') {
            cards = Object.values(rawData).flat();
        }

        elements.learningTitle.textContent = `Góc ôn tập: ${emotion}`;
        elements.learningBody.innerHTML = '';

        if (!cards || cards.length === 0) {
            elements.learningBody.innerHTML = `
            <div class="text-center py-10">
                <p class="text-gray-500">Hiện không có video hoặc thẻ học cho cảm xúc <strong>${emotion}</strong>.</p>
                <p class="text-xs text-gray-400 mt-2">Vui lòng bấm đóng để tiếp tục bài luyện tập.</p>
            </div>`;
        } else {
            cards.forEach(card => {
                let mediaHtml = '';

                if (card.video_path) {
                    const relativeVideoPath = card.video_path.replace('/fe/', '../../') + '.mp4';
                    mediaHtml = `
                    <div class="relative rounded-xl overflow-hidden bg-black shadow mb-4">
                        <video controls autoplay class="learn-media w-full" style="max-height:300px;">
                            <source src="${relativeVideoPath}" type="video/mp4">
                            Trình duyệt không hỗ trợ video.
                        </video>
                    </div>`;
                } else if (card.image_path) {
                    const relativeImgPath = card.image_path.replace('/fe/', '../../');
                    if (relativeImgPath.match(/\.(mp4|webm|ogg|mov)$/i)) {
                        mediaHtml = `
                        <div class="relative rounded-xl overflow-hidden bg-black mb-4">
                            <video controls autoplay class="learn-media w-full" style="max-height:300px;">
                                <source src="${relativeImgPath}" type="video/mp4">
                            </video>
                        </div>`;
                    } else {
                        mediaHtml = `
                        <div class="rounded-xl overflow-hidden shadow mb-4">
                            <img src="${relativeImgPath}" class="learn-img w-full h-auto object-cover" 
                                 alt="${card.title}" style="max-height:300px;">
                        </div>`;
                    }
                }

                const cardHtml = `
                <div class="concept-card bg-white p-4 rounded-2xl border border-gray-100 mb-6 shadow-sm">
                    <h3 class="font-bold mb-2 flex items-center gap-2" style="color: ${emotionHexColor}">
                        <span>💡</span> ${card.title || emotion}
                    </h3>
                    <p class="text-gray-600 mb-4 text-sm">${card.description || "Hãy quan sát kỹ biểu cảm này nhé!"}</p>
                    ${mediaHtml}
                </div>`;

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

    elements.soundBtn.onclick = async () => {
        const q = questions[currentIndex];
        if (!q) return;
        try {
            if ("speechSynthesis" in window) window.speechSynthesis.cancel();
            await speakVietnamese(q.question_text, "thuminh", 0);
        } catch (e) {
            console.error("FPT TTS failed:", e);
        }
    };

    if (elements.submitBtn) {
        elements.submitBtn.onclick = onSubmitAnswer;
    }

    elements.answers.forEach(btn => {
        if (!btn) return;
        btn.onclick = () => {
            if (answered) return;
            const q = questions[currentIndex];
            if (!q) return;

            selectedButton = btn;
            selectedAnswer = btn.dataset.answer;

            elements.answers.forEach(b => {
                b.classList.toggle('selected', b === btn);
            });

            if (elements.submitBtn) {
                elements.submitBtn.disabled = !selectedAnswer;
            }
        };
    });
});