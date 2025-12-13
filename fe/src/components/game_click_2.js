// ========================
// CẤU HÌNH ẢNH CẢM XÚC
// ========================

// Đường dẫn thư mục chứa 6 ảnh sprite (mỗi ảnh = 3 cảm xúc theo CHIỀU NGANG)
const IMAGE_BASE_PATH = "../../assets/images/";

// 6 ảnh, ví dụ: happy.png, sad.png, ...
// Mỗi ảnh: 1/3 trái = lông mày, 1/3 giữa = mắt, 1/3 phải = miệng
const emotionSprites = [{
        id: "happy",
        label: "Vui vẻ",
        file: "happy/ensemble.png"
    }, // index 0
    {
        id: "sad",
        label: "Buồn",
        file: "sad/ensemble.png"
    }, // index 1
    {
        id: "angry",
        label: "Tức giận",
        file: "angry/ensemble.png"
    }, // index 2
    {
        id: "surprise",
        label: "Ngạc nhiên",
        file: "surprise/ensemble.png"
    }, // index 3
    {
        id: "fear",
        label: "Sợ hãi",
        file: "fear/ensemble.png"
    }, // index 4
    {
        id: "disgust",
        label: "Ghê tởm",
        file: "disgust/ensemble.png"
    }, // index 5
];

// 3 bộ phận đều chọn trong cùng 1 mảng 6 cảm xúc
const eyebrowOptions = emotionSprites;
const eyeOptions = emotionSprites;
const lipOptions = emotionSprites;

// ========================
// CÁC TÌNH HUỐNG TRONG GAME
// ========================

const situations = [{
        text: "It's your birthday and you got a puppy! 🎁",
        emoji: "🎉",
        emotion: "happy",
        eyebrows: 0,
        eyes: 0,
        lips: 0,
    },
    {
        text: "Your ice cream fell on the ground! 🍦",
        emoji: "😢",
        emotion: "sad",
        eyebrows: 1,
        eyes: 1,
        lips: 1,
    },
    {
        text: "Someone took your favorite toy without asking! 🧸",
        emoji: "😠",
        emotion: "angry",
        eyebrows: 2,
        eyes: 2,
        lips: 2,
    },
    {
        text: "You opened a present and found exactly what you wanted! 🎁",
        emoji: "😲",
        emotion: "surprise",
        eyebrows: 3,
        eyes: 3,
        lips: 3,
    },
    {
        text: "It's time to go to the park and play! 🎈",
        emoji: "🤩",
        emotion: "fear",
        eyebrows: 4,
        eyes: 4,
        lips: 4,
    },
    {
        text: "You heard a strange noise in the dark! 🌙",
        emoji: "😨",
        emotion: "disgust",
        eyebrows: 5,
        eyes: 5,
        lips: 5,
    },
    {
        text: "Your friend shared their candy with you! 🍬",
        emoji: "😊",
        emotion: "happy",
        eyebrows: 0,
        eyes: 0,
        lips: 0,
    },
    {
        text: "You have to leave the playground when you were having fun! 🛝",
        emoji: "☹️",
        emotion: "sad",
        eyebrows: 1,
        eyes: 1,
        lips: 1,
    },
];

// ========================
// TRẠNG THÁI GAME
// ========================

let currentQuestion = 0;

// -1 = chưa chọn, để ban đầu KHÔNG có gì
let selectedEyebrows = -1;
let selectedEyes = -1;
let selectedLips = -1;

let score = 0;
let questionsAnswered = 0;
let showingFeedback = false;

// ========================
// DOM ELEMENTS
// ========================

const questionNumber = document.getElementById("questionNumber");
const scoreElement = document.getElementById("score");
const situationEmoji = document.getElementById("situationEmoji");
const situationText = document.getElementById("situationText");
const feedbackCorrect = document.getElementById("feedbackCorrect");
const feedbackIncorrect = document.getElementById("feedbackIncorrect");

const eyebrowBtn = document.getElementById("eyebrowBtn");
const eyesBtn = document.getElementById("eyesBtn");
const lipsBtn = document.getElementById("lipsBtn");
const eyebrowLabel = document.getElementById("eyebrowLabel");
const eyesLabel = document.getElementById("eyesLabel");
const lipsLabel = document.getElementById("lipsLabel");

const resetBtn = document.getElementById("resetBtn");
const checkBtn = document.getElementById("checkBtn");
const skipBtn = document.getElementById("skipBtn");
// Popup elements
const resultPopup = document.getElementById("result-popup");
const popupIcon = document.getElementById("popup-icon");
const popupTitle = document.getElementById("popup-title");
const popupMessage = document.getElementById("popup-message");
const popupReplayBtn = document.getElementById("popup-replay-btn");
const popupNextBtn = document.getElementById("popup-next-btn");

// 3 lớp ảnh chồng nhau
let faceWrapper;
let sliceEyebrow;
let sliceEyes;
let sliceMouth;

// ========================
// TẠO KHUNG TRÒN & 3 LỚP ẢNH
// ========================

// ========================
// TẠO Ô HÌNH CHỮ NHẬT & 3 LỚP ẢNH 1024x195
// ========================

function setupFaceSlices() {
    const faceContainer = document.querySelector(".face-container");
    if (!faceContainer) return;

    // Khung hình chữ nhật trắng 1024x585
    faceContainer.innerHTML = `
    <div id="faceWrapper"
      style="
        position: relative;
        width: 640px;
        height: 360px;
        max-width: 100%;
        margin: 0 auto;
        background: #ffffff;   /* trắng tinh */
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        border: 2px solid #e5e7eb;
        display: flex;
        flex-direction: column;
      ">
      <div id="sliceEyebrow"></div>
      <div id="sliceEyes"></div>
      <div id="sliceMouth"></div>
    </div>
  `;

    faceWrapper = document.getElementById("faceWrapper");

    sliceEyebrow = document.getElementById("sliceEyebrow");
    sliceEyes = document.getElementById("sliceEyes");
    sliceMouth = document.getElementById("sliceMouth");

    // 3 hàng 1024x195 xếp chồng từ trên xuống
    [sliceEyebrow, sliceEyes, sliceMouth].forEach((el) => {
        el.style.flex = "0 0 120px"; // đúng 195px chiều cao
        el.style.width = "100%"; // 1024px (hoặc thu nhỏ theo max-width)
        el.style.backgroundRepeat = "no-repeat";
        el.style.backgroundSize = "100% 300%"; // ảnh cao gấp 3 phần
        el.style.backgroundPosition = "0 0";
    });

    // Ban đầu không có gì
    sliceEyebrow.style.backgroundImage = "none";
    sliceEyes.style.backgroundImage = "none";
    sliceMouth.style.backgroundImage = "none";
}

// ========================
// HÀM CẮT ĐÚNG 1/3 ẢNH
// ========================
// partIndex: 0 = 1/3 đầu (trái), 1 = 1/3 giữa, 2 = 1/3 cuối (phải)

// ========================
// HÀM CẮT ĐÚNG 1/3 ẢNH THEO CHIỀU DỌC
// ========================
// fileName: "happy/ensemble.jpg" ...
// partIndex: 0 = 1/3 trên (lông mày), 1 = 1/3 giữa (mắt), 2 = 1/3 dưới (miệng)

function setSliceBackground(slice, fileName, partIndex) {
    if (!fileName) {
        slice.style.backgroundImage = "none";
        return;
    }

    slice.style.backgroundImage = `url(${IMAGE_BASE_PATH}${fileName})`;
    slice.style.backgroundSize = "100% 300%"; // 3 phần theo chiều dọc

    if (partIndex === 0) {
        slice.style.backgroundPosition = "0 0%"; // top 1/3
    } else if (partIndex === 1) {
        slice.style.backgroundPosition = "0 50%"; // middle 1/3
    } else {
        slice.style.backgroundPosition = "0 100%"; // bottom 1/3
    }
}

// ========================
// INIT GAME
// ========================

function init() {
    setupFaceSlices();
    updateSituation();
    updateFace();
    updateLabels();
    updateStats();
    updateButtonStates();

    // NÚT LÔNG MÀY
    eyebrowBtn.addEventListener("click", () => {
        if (!showingFeedback) {
            if (selectedEyebrows === -1) selectedEyebrows = 0;
            else selectedEyebrows = (selectedEyebrows + 1) % eyebrowOptions.length;
            updateFace();
            updateLabels();
        }
    });

    // NÚT MẮT
    eyesBtn.addEventListener("click", () => {
        if (!showingFeedback) {
            if (selectedEyes === -1) selectedEyes = 0;
            else selectedEyes = (selectedEyes + 1) % eyeOptions.length;
            updateFace();
            updateLabels();
        }
    });

    // NÚT MIỆNG
    lipsBtn.addEventListener("click", () => {
        if (!showingFeedback) {
            if (selectedLips === -1) selectedLips = 0;
            else selectedLips = (selectedLips + 1) % lipOptions.length;
            updateFace();
            updateLabels();
        }
    });

    resetBtn.addEventListener("click", resetFace);
    checkBtn.addEventListener("click", checkAnswer);
    skipBtn.addEventListener("click", skipQuestion);

    if (popupReplayBtn) {
        popupReplayBtn.addEventListener("click", () => {
            hideResultPopup();
            resetFace();
            showingFeedback = false;
            updateButtonStates();
        });
    }

    // Nút popup: sang câu tiếp theo (chỉ hiện khi đúng)
    if (popupNextBtn) {
        popupNextBtn.addEventListener("click", () => {
            hideResultPopup();
            nextQuestion();
        });
    }
}

// ========================
// CẬP NHẬT TÌNH HUỐNG
// ========================

function updateSituation() {
    const situation = situations[currentQuestion];
    situationEmoji.textContent = situation.emoji;
    situationText.textContent = situation.text;

    situationEmoji.classList.remove("fade-in");
    void situationEmoji.offsetWidth;
    situationEmoji.classList.add("fade-in");
}

// ========================
// CẬP NHẬT KHUÔN MẶT (3 LỚP)
// ========================

function updateFace() {
    if (!sliceEyebrow || !sliceEyes || !sliceMouth || !faceWrapper) return;

    const anySelected =
        selectedEyebrows >= 0 || selectedEyes >= 0 || selectedLips >= 0;

    // Nếu chưa chọn gì, làm mờ nhẹ khung để thấy là "trống"
    faceWrapper.style.opacity = anySelected ? "1" : "0.25";

    // Lông mày: 1/3 đầu
    // Lông mày: partIndex = 0
    if (selectedEyebrows >= 0) {
        const spr = eyebrowOptions[selectedEyebrows];
        setSliceBackground(sliceEyebrow, spr.file, 0);
    } else {
        setSliceBackground(sliceEyebrow, null, 0);
    }

    // Mắt: partIndex = 1
    if (selectedEyes >= 0) {
        const spr = eyeOptions[selectedEyes];
        setSliceBackground(sliceEyes, spr.file, 1);
    } else {
        setSliceBackground(sliceEyes, null, 1);
    }

    // Miệng: partIndex = 2
    if (selectedLips >= 0) {
        const spr = lipOptions[selectedLips];
        setSliceBackground(sliceMouth, spr.file, 2);
    } else {
        setSliceBackground(sliceMouth, null, 2);
    }
}

// ========================
// LABEL NÚT
// ========================

function updateLabels() {
    eyebrowLabel.textContent =
        selectedEyebrows === -1 ? "(chưa chọn)" : "🔴 PUSH";

    eyesLabel.textContent = selectedEyes === -1 ? "(chưa chọn)" : "🔴 PUSH";

    lipsLabel.textContent = selectedLips === -1 ? "(chưa chọn)" : "🔴 PUSH";
}

// ========================
// STATS
// ========================

function updateStats() {
    questionNumber.textContent = questionsAnswered + 1;
    scoreElement.textContent = score;
}

// ========================
// RESET
// ========================

function resetFace() {
    if (!showingFeedback) {
        selectedEyebrows = -1;
        selectedEyes = -1;
        selectedLips = -1;
        updateFace();
        updateLabels();
    }
}

// ========================
// CHECK ANSWER
// ========================

function checkAnswer() {
    if (showingFeedback) return;

    // Chưa chọn đủ 3 phần
    if (selectedEyebrows === -1 || selectedEyes === -1 || selectedLips === -1) {
        feedbackIncorrect.classList.add("show");
        feedbackIncorrect.querySelector(".feedback-text").textContent =
            "Hãy chọn đủ lông mày, mắt và miệng nhé!";
        setTimeout(() => {
            feedbackIncorrect.classList.remove("show");
            feedbackIncorrect.querySelector(".feedback-text").textContent = "Thử lại";
        }, 1500);
        return;
    }

    const situation = situations[currentQuestion];
    const isCorrect =
        selectedEyebrows === situation.eyebrows &&
        selectedEyes === situation.eyes &&
        selectedLips === situation.lips;

    showingFeedback = true;

    if (isCorrect) {
        score++;
        updateStats();
    }

    // Hiển thị popup kết quả
    showResultPopup(isCorrect);
    updateButtonStates();
}


// ========================
// SKIP / NEXT
// ========================

function skipQuestion() {
    if (!showingFeedback) {
        nextQuestion();
    }
}

function nextQuestion() {
    questionsAnswered++;
    currentQuestion = (currentQuestion + 1) % situations.length;
    resetFace();
    updateSituation();
    showingFeedback = false;
    updateStats();
    updateButtonStates();
}

// ========================
// BUTTON STATES
// ========================

function updateButtonStates() {
    const disabled = showingFeedback;
    resetBtn.disabled = disabled;
    checkBtn.disabled = disabled;
    skipBtn.disabled = disabled;
}

// ========================
// POPUP KẾT QUẢ
// ========================

function showResultPopup(isCorrect) {
    if (!resultPopup) return;

    if (isCorrect) {
        popupIcon.textContent = "🎉";
        popupTitle.textContent = "Tuyệt vời!";
        popupMessage.textContent =
            "Bạn đã xây đúng khuôn mặt cho cảm xúc này. Nhấn \"Câu tiếp theo\" để tiếp tục nhé!";
        if (popupNextBtn) popupNextBtn.style.display = "inline-block";
    } else {
        popupIcon.textContent = "🙂";
        popupTitle.textContent = "Chưa chính xác lắm";
        popupMessage.textContent =
            "Khuôn mặt này chưa đúng với cảm xúc. Bạn có muốn thử lại câu này không?";
        if (popupNextBtn) popupNextBtn.style.display = "none";
    }

    resultPopup.classList.add("show");
}

function hideResultPopup() {
    if (!resultPopup) return;
    resultPopup.classList.remove("show");
}


// ========================
// START GAME
// ========================

init();