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
        const emotionKey = normalizeEmotion(emotion);

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
            emotionErrors[emotionKey] = (emotionErrors[emotionKey] || 0) + 1;

            if (emotionErrors[emotionKey] >= maxErrors && !learnedEmotions.includes(emotionKey)) {
                learnedEmotions.push(emotionKey);
            }
        }

        elements.answers.forEach(b => {
            b.classList.remove('selected');
            if (b.dataset.answer === q.correct_answer) b.classList.add('correct');
            else if (b === selectedButton && !correct) b.classList.add('incorrect');
            b.disabled = true;
        });

        if (elements.submitBtn) {
            elements.submitBtn.disabled = true;
        }

        showFeedback(correct, q.correct_answer, emotion);
    }

    // Popup Sai/Đúng (Đã sửa logic hiển thị nút)
    function showFeedback(correct, correctAns, emotion) {
        const emotionKey = normalizeEmotion(emotion);

        elements.modalTitle.textContent = correct ? 'CHÍNH XÁC!' : 'SAI RỒI!';
        elements.modalTitle.style.color = correct ? '#10b981' : '#fca055ff';
        elements.modalMsg.textContent = correct ? 'Bạn làm tốt lắm, tiếp tục phát huy nhé.' : `Đáp án đúng là: ${correctAns}. Hãy cố gắng hơn ở câu tiếp theo nhé!`;

        elements.modalActionsContainer.innerHTML = '';

        // Kiểm tra xem lỗi này có vừa đạt ngưỡng học lại bắt buộc không
        const isForcedLearning = !correct &&
            emotionErrors[emotionKey] >= maxErrors &&
            learnedEmotions.includes(emotionKey);

        if (isForcedLearning) {
            // --- UI BẮT BUỘC HỌC LẠI (Chỉ có 1 nút) ---
            elements.modalTitle.textContent = 'CẦN ÔN TẬP LẠI CẢM XÚC NÀY!';
            elements.modalTitle.style.color = '#86f8f4ff';
            elements.modalMsg.textContent = `Bạn không đúng nhiều lần ở cảm xúc "${emotion}". Hãy học lại để ôn tập kiến thức trước khi tiếp tục.`;

            const learnBtn = document.createElement('button');
            learnBtn.textContent = "HỌC LẠI CẢM XÚC NÀY";
            learnBtn.className = "modal-btn learn-btn color: #5c9cf6ff";

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
                } else if (card.image_path) {
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