// ========================
// CẤU HÌNH ẢNH CẢM XÚC
// ========================

// Đường dẫn thư mục chứa 6 ảnh sprite (mỗi ảnh = 3 cảm xúc theo CHIỀU NGANG)
const IMAGE_BASE_PATH = "../../assets/images/";

const emotionSprites = [
  { id: "happy", label: "Vui vẻ", file: "happy/ensemble.png", video: "happy" },
  { id: "sad", label: "Buồn bã", file: "sad/ensemble.png", video: "sad" },
  {
    id: "angry",
    label: "Tức giận",
    file: "angry/ensemble.png",
    video: "angry",
  },
  {
    id: "surprise",
    label: "Ngạc nhiên",
    file: "surprise/ensemble.png",
    video: "surprise",
  },
  { id: "fear", label: "Sợ hãi", file: "fear/ensemble.png", video: "fear" },
  {
    id: "disgust",
    label: "Ghê tởm",
    file: "disgust/ensemble.png",
    video: "disgust",
  },
];
const DEFAULT_RATIO = [1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6];
const LEVEL_THRESHOLD = 70;
const TARGET_QUESTIONS = 10;
// 3 bộ phận đều chọn trong cùng 1 mảng 6 cảm xúc

// ========================
// TRẠNG THÁI GAME
// ========================

// -1 = chưa chọn, để ban đầu KHÔNG có gì
let selectedEyebrows = -1;
let selectedEyes = -1;
let selectedLips = -1;

let currentQuestionIndex = 0;
let questionsAnswered = 0;
let showingFeedback = false;
let currentQuestionData = null;
let questionStartTime = null;

let currentUser = null;
let gameId = null;

let questionsPool = [];
let playedQuestions = [];
let questionResults = [];
let reviewEmotions = [];
let lastAnswerCorrect = null;
let extraExitBtn = null; // nút "Thoát game" trong popup cuối cùng
let popupNextMode = "question";
let nextLevelTarget = null;
let ratio = [...DEFAULT_RATIO];

const sessionContext = {
  sessionId: null,
  level: 1,
  score: 0,
  maxErrors: 3,
  levelThreshold: LEVEL_THRESHOLD,
  emotionErrors: {
    "Ghê tởm": 0,
    "Ngạc nhiên": 0,
    "Buồn bã": 0,
    "Vui vẻ": 0,
    "Sợ hãi": 0,
    "Tức giận": 0,
  },
  startTime: null,
  finished: false,
};

let questionCycle = [];

// ========================
// DOM ELEMENTS
// ========================

const questionNumber = document.getElementById("questionNumber");
const questionTotal = document.getElementById("questionTotal");
const scoreElement = document.getElementById("score");
const situationEmoji = document.getElementById("situationEmoji");
const situationText = document.getElementById("situationText");
const feedbackCorrect = document.getElementById("feedbackCorrect");
const feedbackIncorrect = document.getElementById("feedbackIncorrect");
const instructionBox = document.querySelector(".instruction-box");
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
const exitBtn = document.getElementById("exitBtn");
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

let situationMediaImg;

// ========================
// HÀM TIỆN ÍCH
// ========================

function normalizeEmotion(rawEmotion) {
  if (!rawEmotion) return null;
  const key = rawEmotion.toString().trim().toLowerCase();
  const mapping = {
    "vui vẻ": "happy",
    vui: "happy",
    happy: "happy",
    buồn: "sad",
    "buồn bã": "sad",
    sad: "sad",
    "tức giận": "angry",
    "giận dữ": "angry",
    angry: "angry",
    "ngạc nhiên": "surprise",
    surprise: "surprise",
    "sợ hãi": "fear",
    sợ: "fear",
    fear: "fear",
    "ghê tởm": "disgust",
    disgust: "disgust",
  };
  return mapping[key] || null;
}
// ========================
// TẠO Ô HÌNH CHỮ NHẬT & 3 LỚP ẢNH 1024x195
// ========================
function getEmotionInfo(rawEmotion) {
  const normalized = normalizeEmotion(rawEmotion);
  const idx = emotionSprites.findIndex((e) => e.id === normalized);
  if (idx === -1) return null;
  return { ...emotionSprites[idx], index: idx };
}

function defaultEmotionErrors() {
  return {
    "Ghê tởm": 0,
    "Ngạc nhiên": 0,
    "Buồn bã": 0,
    "Vui vẻ": 0,
    "Sợ hãi": 0,
    "Tức giận": 0,
  };
}

function mapIndexToLabel(index) {
  if (index < 0 || index >= emotionSprites.length) return "";
  return emotionSprites[index].label;
}

function shuffleArray(list) {
  const copy = [...list];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}
function resolveMediaPath(mediaPath) {
  if (!mediaPath) return null;
  if (/^https?:\/\//i.test(mediaPath)) return mediaPath;
  if (mediaPath.startsWith("/fe/")) return mediaPath.replace("/fe/", "../../");
  return mediaPath;
}

function isValidUUID(value) {
  return (
    typeof value === "string" &&
    /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
      value
    )
  );
}

function ensureSituationMedia() {
  if (situationMediaImg || !instructionBox) return;
  situationMediaImg = document.createElement("img");
  situationMediaImg.id = "situationMedia";
  situationMediaImg.alt = "Minh họa câu hỏi";
  situationMediaImg.style.display = "none";
  situationMediaImg.style.marginTop = "12px";
  situationMediaImg.style.width = "100%";
  situationMediaImg.style.borderRadius = "12px";
  situationMediaImg.style.objectFit = "cover";
  instructionBox.appendChild(situationMediaImg);
}
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
document.addEventListener("DOMContentLoaded", async () => {
  try {
    setupFaceSlices();
    bindControls();
    ensureSituationMedia();
    await bootstrapGameData();
    updateLabels();
    updateStats();
    updateButtonStates();
  } catch (error) {
    console.error("Lỗi khởi tạo game:", error);
    alert("Không thể khởi động game. Vui lòng thử lại.");
  }
});

// NÚT LÔNG MÀY
function bindControls() {
  eyebrowBtn?.addEventListener("click", () => {
    if (!showingFeedback) {
      if (selectedEyebrows === -1) selectedEyebrows = 0;
      else selectedEyebrows = (selectedEyebrows + 1) % emotionSprites.length;
      updateFace();
      updateLabels();
    }
  });

  // NÚT MẮT
  eyesBtn?.addEventListener("click", () => {
    if (!showingFeedback) {
      if (selectedEyes === -1) selectedEyes = 0;
      else selectedEyes = (selectedEyes + 1) % emotionSprites.length;
      updateFace();
      updateLabels();
    }
  });

  // NÚT MIỆNG
  lipsBtn?.addEventListener("click", () => {
    if (!showingFeedback) {
      if (selectedLips === -1) selectedLips = 0;
      else selectedLips = (selectedLips + 1) % emotionSprites.length;
      updateFace();
      updateLabels();
    }
  });

  resetBtn?.addEventListener("click", resetFace);
  checkBtn?.addEventListener("click", checkAnswer);
  skipBtn?.addEventListener("click", skipQuestion);
  exitBtn?.addEventListener("click", showExitConfirm);
  popupReplayBtn?.addEventListener("click", () => {
    hideResultPopup();
    showingFeedback = false;
    resetFace();
    updateButtonStates();
  });

  popupNextBtn?.addEventListener("click", () => {
    if (popupNextMode === "next-level" && nextLevelTarget) {
      window.location.href = `./game_click_2.html?gameId=${gameId}&level=${nextLevelTarget}`;
      return;
    }
    hideResultPopup();
    nextQuestion();
  });
}

async function bootstrapGameData() {
  currentUser = JSON.parse(localStorage.getItem("currentUser"));
  if (!currentUser) {
    alert("Vui lòng đăng nhập trước khi chơi!");
    window.location.href = "./login.html";
    return;
  }

  const urlParams = new URLSearchParams(window.location.search);
  gameId = urlParams.get("gameId");
  const levelParam = parseInt(urlParams.get("level"), 10);
  if (!gameId) {
    alert("Thiếu thông tin game.");
    window.location.href = "./select_game.html";
    return;
  }

  sessionContext.level = Number.isFinite(levelParam) ? levelParam : 1;

  await loadProgress();
  await startSession();
}
async function loadProgress() {
  try {
    const res = await fetch(
      `/games/progress/${gameId}?user_id=${currentUser.user_id}`
    );
    if (!res.ok) return;
    const progress = await res.json();
    if (progress) {
      sessionContext.level = progress.level || sessionContext.level;
      ratio =
        Array.isArray(progress.ratio) && progress.ratio.length === 6
          ? progress.ratio
          : [...DEFAULT_RATIO];
    }
  } catch (error) {
    console.warn("Không thể tải tiến trình, dùng giá trị mặc định", error);
  }
}

// Nút popup: sang câu tiếp theo (chỉ hiện khi đúng)
async function startSession() {
  try {
    const res = await fetch(`/games/start/${gameId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: currentUser.user_id,
        level: sessionContext.level,
      }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    sessionContext.sessionId = data.session_id;
    sessionContext.maxErrors = data.max_errors ?? sessionContext.maxErrors;
    sessionContext.emotionErrors = {
      ...defaultEmotionErrors(),
      ...(data.emotion_errors || {}),
    };
    questionsAnswered = 0;
    playedQuestions = [];
    questionResults = [];
    reviewEmotions = [];
    questionCycle = [];
    showingFeedback = false;
    questionsPool = normalizeQuestions(data.questions || []);
    if (!questionsPool.length) {
      console.warn("Không có câu hỏi từ API, dùng tình huống mặc định");
      questionsPool = normalizeQuestions(buildFallbackQuestions());
    }

    sessionContext.startTime = Date.now();
    loadQuestionByIndex(0);
  } catch (error) {
    console.error("Lỗi khởi tạo session:", error);
    questionsPool = normalizeQuestions(buildFallbackQuestions());
    loadQuestionByIndex(0);
  }
}
function normalizeQuestions(rawQuestions) {
  const seenIds = new Set();

  return rawQuestions
    .map((q, idx) => {
      const emotionInfo = getEmotionInfo(q.correct_answer || q.emotion || "");
      if (!emotionInfo) return null;
      const resolvedQuestionId =
        q.question_id ||
        q.questionId ||
        q.id ||
        q.content_id ||
        q.contentId ||
        `local-${idx}`;
      if (seenIds.has(resolvedQuestionId)) return null;
      seenIds.add(resolvedQuestionId);
      return {
        questionId: resolvedQuestionId,
        question_text: q.question_text || q.text || `Câu hỏi ${idx + 1}`,
        media_path: resolveMediaPath(
          q.media_path || q.mediaPath || q.media || null
        ),
        correct_emotion: emotionInfo,
        explanation: q.explanation || "",
        emoji: q.emoji || "🙂",
      };
    })
    .filter(Boolean);
}

function buildFallbackQuestions() {
  return [
    {
      text: "Bạn vừa được tặng một chú cún dễ thương!",
      emoji: "🎁",
      emotion: "Vui vẻ",
    },
    { text: "Que kem rơi xuống đất rồi!", emoji: "🍦", emotion: "Buồn bã" },
    {
      text: "Bạn bị lấy mất đồ chơi yêu thích!",
      emoji: "🧸",
      emotion: "Tức giận",
    },
    {
      text: "Món quà mở ra đúng thứ bạn muốn!",
      emoji: "🎉",
      emotion: "Ngạc nhiên",
    },
    {
      text: "Bạn nghe tiếng động lạ trong bóng tối!",
      emoji: "🌙",
      emotion: "Sợ hãi",
    },
    {
      text: "Bạn ngửi thấy mùi rất khó chịu!",
      emoji: "🤢",
      emotion: "Ghê tởm",
    },
  ];
}
function showExitConfirm() {
  if (sessionContext.finished) return;

  const overlay = document.createElement("div");
  overlay.style.position = "fixed";
  overlay.style.inset = "0";
  overlay.style.background = "rgba(0,0,0,0.55)";
  overlay.style.display = "flex";
  overlay.style.alignItems = "center";
  overlay.style.justifyContent = "center";
  overlay.style.zIndex = "9999";

  const modal = document.createElement("div");
  modal.style.background = "#fff";
  modal.style.padding = "20px";
  modal.style.borderRadius = "12px";
  modal.style.width = "min(92%, 480px)";
  modal.style.boxShadow = "0 12px 30px rgba(0,0,0,0.22)";

  const title = document.createElement("h3");
  title.textContent = "Thoát game?";
  title.style.marginBottom = "8px";

  const desc = document.createElement("p");
  desc.textContent =
    "Tiến trình của level này sẽ không được lưu. Bạn chắc chắn muốn thoát?";
  desc.style.marginBottom = "16px";

  const actions = document.createElement("div");
  actions.style.display = "flex";
  actions.style.gap = "8px";
  actions.style.justifyContent = "flex-end";

  const stayBtn = document.createElement("button");
  stayBtn.textContent = "Ở lại";
  stayBtn.style.padding = "8px 12px";
  stayBtn.style.border = "1px solid #d1d5db";
  stayBtn.style.borderRadius = "8px";
  stayBtn.style.background = "#fff";
  stayBtn.style.cursor = "pointer";
  stayBtn.addEventListener("click", () => overlay.remove());

  const quitBtn = document.createElement("button");
  quitBtn.textContent = "Thoát game";
  quitBtn.style.padding = "8px 14px";
  quitBtn.style.border = "none";
  quitBtn.style.borderRadius = "8px";
  quitBtn.style.background = "#ef4444";
  quitBtn.style.color = "#fff";
  quitBtn.style.cursor = "pointer";
  quitBtn.addEventListener("click", async () => {
    overlay.remove();
    await finalizeSession("quit", {
      skipSubmit: true,
      customTitle: "Bạn đã thoát game",
      customMessage:
        "Bạn có thể quay lại chọn level và chơi tiếp khi sẵn sàng.",
      customIcon: "👋",
    });
  });

  actions.appendChild(stayBtn);
  actions.appendChild(quitBtn);

  modal.appendChild(title);
  modal.appendChild(desc);
  modal.appendChild(actions);
  overlay.appendChild(modal);
  document.body.appendChild(overlay);
}

// ========================
// CẬP NHẬT TÌNH HUỐNG
// ========================

function updateSituation() {
  if (!currentQuestionData) return;
  if (situationEmoji) {
    situationEmoji.textContent = currentQuestionData.emoji || "🙂";
  }
  situationText.textContent = currentQuestionData.question_text;

  ensureSituationMedia();
  if (situationMediaImg) {
    const mediaPath = currentQuestionData.media_path;
    if (mediaPath) {
      situationMediaImg.src = mediaPath;
      situationMediaImg.style.display = "block";
    } else {
      situationMediaImg.style.display = "none";
      situationMediaImg.removeAttribute("src");
    }
  }
  if (situationEmoji) {
    situationEmoji.classList.remove("fade-in");
    void situationEmoji.offsetWidth;
    situationEmoji.classList.add("fade-in");
  }
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
    const spr = emotionSprites[selectedEyebrows];
    setSliceBackground(sliceEyebrow, spr.file, 0);
  } else {
    setSliceBackground(sliceEyebrow, null, 0);
  }

  // Mắt: partIndex = 1
  if (selectedEyes >= 0) {
    const spr = emotionSprites[selectedEyes];
    setSliceBackground(sliceEyes, spr.file, 1);
  } else {
    setSliceBackground(sliceEyes, null, 1);
  }

  // Miệng: partIndex = 2
  if (selectedLips >= 0) {
    const spr = emotionSprites[selectedLips];
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
  const totalQuestions = Math.min(
    TARGET_QUESTIONS,
    Array.isArray(questionsPool) && questionsPool.length ? questionsPool.length : TARGET_QUESTIONS
  );
  questionNumber.textContent = Math.min(questionsAnswered + 1, totalQuestions);
  if (questionTotal) {
    questionTotal.textContent = totalQuestions;
  }
  scoreElement.textContent = sessionContext.score;

  const progressFill = document.getElementById("click-progress-fill");
  if (progressFill) {
    const current = Math.min(questionsAnswered + 1, totalQuestions);
    const percentage = (current / totalQuestions) * 100;
    progressFill.style.width = `${percentage}%`;
  }
}

function resetFace() {
  if (showingFeedback) return;
  selectedEyebrows = -1;
  selectedEyes = -1;
  selectedLips = -1;
  updateFace();
  updateLabels();
}

function updateButtonStates(disabledAll = false) {
  const disabled = showingFeedback || disabledAll;
  resetBtn.disabled = disabled;
  checkBtn.disabled = disabled;
  skipBtn.disabled = disabled;
  if (exitBtn) exitBtn.disabled = disabledAll;
}

// ========================
// RESET
// ========================

function loadQuestionByIndex(idx) {
  if (!questionsPool.length) return;

  if (!questionCycle.length) {
    const unused = questionsPool.filter(
      (q) => !playedQuestions.includes(q.questionId)
    );
    const source = unused.length ? unused : questionsPool;
    questionCycle = shuffleArray(source);

    if (!unused.length && currentQuestionData) {
      questionCycle = questionCycle.filter(
        (q) => q.questionId !== currentQuestionData.questionId
      );
      if (!questionCycle.length) questionCycle = shuffleArray(source);
    }
  }
  const chosen = questionCycle.shift();
  currentQuestionIndex = questionsPool.indexOf(chosen);
  currentQuestionData = chosen;
  if (!playedQuestions.includes(chosen.questionId)) {
    playedQuestions.push(chosen.questionId);
  }
  questionStartTime = performance.now();
  showingFeedback = false;
  resetFace();
  updateSituation();
  updateStats();
  updateButtonStates();
}

async function nextQuestion() {
  if (questionsAnswered >= TARGET_QUESTIONS) {
    await finalizeSession("completed");
    return;
  }

  const nextIdx = (currentQuestionIndex + 1) % questionsPool.length;
  loadQuestionByIndex(nextIdx);
}

function skipQuestion() {
  if (sessionContext.finished || showingFeedback || !currentQuestionData)
    return;

  const responseTime = questionStartTime
    ? Math.round(performance.now() - questionStartTime)
    : 0;

  // Lưu kết quả "Bỏ qua" cho backend
  questionResults.push({
    question_id: currentQuestionData.questionId,
    answer: "Bỏ qua",
    is_correct: false,
    response_time_ms: responseTime,
    used_hint: false,
  });

  // Đang ở câu thứ mấy? (questionsAnswered = số câu đã trả lời xong)
  const isLastQuestion = questionsAnswered >= TARGET_QUESTIONS - 1;

  // Nếu chưa phải câu 10 -> auto next như bình thường
  // Nếu là câu 10 -> không auto next, để mình show popup đặc biệt
  recordAnswer(false, "Bỏ qua", responseTime, {
    autoAdvance: !isLastQuestion,
  });

  if (isLastQuestion) {
    // Đã tăng questionsAnswered lên 10 rồi trong recordAnswer
    showSkipEndGamePopup();
  }
}

// ========================
// CHECK ANSWER
// ========================
function getSelectedEmotionIndex() {
  if (selectedEyebrows === -1 || selectedEyes === -1 || selectedLips === -1)
    return -1;
  if (selectedEyebrows === selectedEyes && selectedEyes === selectedLips) {
    return selectedEyebrows;
  }
  return -2;
}

function checkAnswer() {
  if (sessionContext.finished || showingFeedback || !currentQuestionData)
    return;

  // Chưa chọn đủ 3 phần
  if (selectedEyebrows === -1 || selectedEyes === -1 || selectedLips === -1) {
    feedbackIncorrect.classList.add("show");
    const textNode =
      feedbackIncorrect.querySelector(".feedback-text") || feedbackIncorrect;
    textNode.textContent = "Hãy chọn đủ lông mày, mắt và miệng nhé!";
    setTimeout(() => {
      feedbackIncorrect.classList.remove("show");
      textNode.textContent = "Thử lại";
    }, 1500);
    return;
  }

  const selectedIndex = getSelectedEmotionIndex();
  const expectedIndex = currentQuestionData.correct_emotion.index;
  const isCorrect = selectedIndex === expectedIndex;
  const responseTime = questionStartTime
    ? Math.round(performance.now() - questionStartTime)
    : 0;
  const answerLabel =
    selectedIndex >= 0 ? mapIndexToLabel(selectedIndex) : "Không khớp";
  // Lưu kết quả cho endpoint /games/end-level
  questionResults.push({
    question_id: currentQuestionData.questionId,
    answer: answerLabel,
    is_correct: isCorrect,
    response_time_ms: responseTime,
    used_hint: false,
  });
  recordAnswer(isCorrect, answerLabel, responseTime);

  // Nếu đã tới câu 10 ⇒ hiển thị popup cuối game theo đúng/sai
  if (questionsAnswered >= TARGET_QUESTIONS) {
    showEndGamePopup(isCorrect);
    return;
  }

  if (sessionContext.finished) return;
  showResultPopup(isCorrect);
}
function showEndGamePopup(isCorrect) {
  if (!resultPopup) return;

  // Xoá nút extraExitBtn cũ nếu có
  if (extraExitBtn && extraExitBtn.parentNode) {
    extraExitBtn.parentNode.removeChild(extraExitBtn);
  }
  extraExitBtn = null;

  // Luôn hiện 2 nút sẵn có
  popupReplayBtn.style.display = "inline-block";
  popupNextBtn.style.display = "inline-block";

  if (isCorrect) {
    // CÂU 10 ĐÚNG → 2 nút: Thoát game + Chơi lại (cả level)
    popupIcon.textContent = "🏆";
    popupTitle.textContent = "Hoàn thành level!";
    popupMessage.textContent =
      "Bạn đã trả lời đúng câu cuối. Bạn muốn thoát game hay chơi lại level này?";

    // Nút "Chơi lại" (cả level)
    popupReplayBtn.textContent = "Chơi lại";
    popupReplayBtn.onclick = async () => {
      hideResultPopup();
      // Gửi kết quả lên server rồi chơi lại
      await finalizeSession("completed");
      // Reset trạng thái và bắt đầu lại
      sessionContext.finished = false;
      sessionContext.score = 0;
      questionsAnswered = 0;
      playedQuestions = [];
      questionResults = [];
      reviewEmotions = [];
      questionCycle = [];
      showingFeedback = false;
      updateButtonStates();
      startSession();
    };

    // Nút "Thoát game"
    popupNextBtn.textContent = "Thoát game";
    popupNextBtn.onclick = async () => {
      hideResultPopup();
      await finalizeSession("completed");
      // Tuỳ route của bạn:
      window.location.href = "./select_game.html";
    };
  } else {
    // CÂU 10 SAI → 3 nút: Thoát game + Chơi lại câu này + Chơi lại (cả level)
    popupIcon.textContent = "🙂";
    popupTitle.textContent = "Câu cuối chưa chính xác";
    popupMessage.textContent =
      "Bạn muốn chơi lại câu này, chơi lại cả level hay thoát game?";

    // Nút "Chơi lại câu này"
    popupReplayBtn.textContent = "Chơi lại câu này";
    popupReplayBtn.onclick = () => {
      // Cho chơi lại đúng câu 10
      hideResultPopup();
      questionsAnswered = TARGET_QUESTIONS - 1; // quay về hiển thị là câu 9 + 1 = 10
      updateStats();
      showingFeedback = false;
      sessionContext.finished = false;
      updateButtonStates();
      resetFace();
      questionStartTime = performance.now();
      // currentQuestionData giữ nguyên, nên vẫn là câu 10 vừa rồi
    };

    // Nút "Chơi lại" (cả level)
    popupNextBtn.textContent = "Chơi lại";
    popupNextBtn.onclick = async() => {
      hideResultPopup();
      await finalizeSession("completed");
      sessionContext.finished = false;
      sessionContext.score = 0;
      questionsAnswered = 0;
      playedQuestions = [];
      questionResults = [];
      reviewEmotions = [];
      questionCycle = [];
      showingFeedback = false;
      updateButtonStates();
      startSession();
    };

    // Tạo nút thứ 3: "Thoát game"
    extraExitBtn = document.createElement("button");
    extraExitBtn.id = "popup-exit-btn-inner";
    extraExitBtn.textContent = "Thoát game";
    extraExitBtn.style.marginLeft = "8px";
    extraExitBtn.style.padding = "8px 14px";
    extraExitBtn.style.borderRadius = "8px";
    extraExitBtn.style.border = "none";
    extraExitBtn.style.background = "#ef4444";
    extraExitBtn.style.color = "#fff";
    extraExitBtn.style.cursor = "pointer";
    extraExitBtn.onclick = async () => {
      hideResultPopup();
      await finalizeSession("completed");
      window.location.href = "./select_game.html";
    };

    // Gắn nút vào popup (cuối cùng)
    resultPopup.appendChild(extraExitBtn);
  }

  resultPopup.classList.add("show");
}
function showSkipEndGamePopup() {
  if (!resultPopup) return;

  // Xoá nút extraExitBtn cũ nếu có (trường hợp vừa làm câu 10 sai trước đó)
  if (extraExitBtn && extraExitBtn.parentNode) {
    extraExitBtn.parentNode.removeChild(extraExitBtn);
  }
  extraExitBtn = null;

  // Luôn dùng 2 nút sẵn có
  popupReplayBtn.style.display = "inline-block";
  popupNextBtn.style.display = "inline-block";

  popupIcon.textContent = "⏭️";
  popupTitle.textContent = "Bạn đã bỏ qua câu cuối";
  popupMessage.textContent = "Bạn muốn thoát game hay chơi lại level này?";

  // Nút "Chơi lại level này"
  popupReplayBtn.textContent = "Chơi lại";
  popupReplayBtn.onclick = async () => {
    hideResultPopup();
    // Gửi kết quả level hiện tại lên server
    await finalizeSession("completed");
    // Reset state để chơi lại từ đầu level
    sessionContext.finished = false;
    sessionContext.score = 0;
    questionsAnswered = 0;
    playedQuestions = [];
    questionResults = [];
    reviewEmotions = [];
    questionCycle = [];
    showingFeedback = false;
    updateButtonStates();
    startSession();
  };

  // Nút "Thoát game"
  popupNextBtn.textContent = "Thoát game";
  popupNextBtn.onclick = async () => {
    hideResultPopup();
    await finalizeSession("completed");
    window.location.href = "./select_game.html";
  };

  resultPopup.classList.add("show");
}

function recordAnswer(isCorrect, answerLabel, responseTime, options = {}) {
  const { autoAdvance = false } = options;
  showingFeedback = !autoAdvance;
  lastAnswerCorrect = isCorrect;

  // Cộng điểm / cộng lỗi
  if (isCorrect) {
    sessionContext.score += 10;
  } else {
    const emotionName = currentQuestionData.correct_emotion.label;
    sessionContext.emotionErrors[emotionName] =
      (sessionContext.emotionErrors[emotionName] || 0) + 1;

    if (sessionContext.emotionErrors[emotionName] >= 3) {
      reviewEmotions.push(emotionName);
      sessionContext.emotionErrors[emotionName] = 0;
      showLearningVideo(currentQuestionData.correct_emotion);
    }
  }

  // Tăng số câu đã trả lời
  questionsAnswered += 1;
  updateStats();

  // Nếu đã tới câu 10 thì KHÔNG tự finalize, để checkAnswer xử lý popup
  if (questionsAnswered >= TARGET_QUESTIONS) {
    updateButtonStates(true);
    return;
  }

  // Các câu chưa phải câu 10
  if (autoAdvance) {
    updateButtonStates();
    nextQuestion();
  } else {
    updateButtonStates();
  }
}

// ========================
// POPUP KẾT QUẢ
// ========================

function showResultPopup(isCorrect) {
  if (!resultPopup) return;
  popupNextMode = "question";
  nextLevelTarget = null;
  if (isCorrect) {
    popupIcon.textContent = "🎉";
    popupTitle.textContent = "Tuyệt vời!";
    popupMessage.textContent =
      'Bạn đã xây đúng khuôn mặt cho cảm xúc này. Nhấn "Câu tiếp theo" để tiếp tục nhé!';
    popupNextBtn.style.display = "inline-block";
  } else {
    popupIcon.textContent = "🙂";
    popupTitle.textContent = "Chưa chính xác lắm";
    popupMessage.textContent =
      "Khuôn mặt này chưa đúng với cảm xúc. Bạn có muốn thử lại câu này không?";
    popupNextBtn.style.display = "inline-block";
  }

  resultPopup.classList.add("show");
}
function hideResultPopup() {
  if (!resultPopup) return;
  resultPopup.classList.remove("show");
  if (extraExitBtn && extraExitBtn.parentNode) {
    extraExitBtn.parentNode.removeChild(extraExitBtn);
  }
  extraExitBtn = null;
}

// ========================
// START GAME
// ========================
async function finalizeSession(reason, options = {}) {
  const {
    skipSubmit = false,
    customTitle,
    customMessage,
    customIcon,
  } = options;

  if (sessionContext.finished) return;
  sessionContext.finished = true;
  showingFeedback = true;

  updateButtonStates(true);

  const filteredResults = questionResults.filter((r) =>
    isValidUUID(r.question_id)
  );

  const payload = {
    session_id: sessionContext.sessionId,
    results: filteredResults,
    review_emotions: reviewEmotions,
  };
  const previousLevel = sessionContext.level;
  try {
    if (sessionContext.sessionId && !skipSubmit) {
      const res = await fetch(`/games/end-level`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(
          `Kết thúc session thất bại: ${res.status} - ${errorText}`
        );
      }
      const data = await res.json();
      sessionContext.level = data.progress_level || sessionContext.level;
    }
  } catch (error) {
    console.error("Không thể lưu session:", error);
  }

  const isWin = sessionContext.score >= sessionContext.levelThreshold;
  const advancedLevel = sessionContext.level > previousLevel;
  // Nếu là kết thúc bình thường (câu 10) thì không hiện popup nữa (đã hiện trong showEndGamePopup)
  if (reason === "completed" && !customTitle && !customMessage && !customIcon) {
    return;
  }

  // Các trường hợp khác (thoát giữa chừng) vẫn dùng popup này
  popupIcon.textContent = customIcon || (isWin ? "🏆" : "😢");
  popupTitle.textContent =
    customTitle || (isWin ? "Bạn đã vượt level!" : "Chưa đạt yêu cầu");
  popupMessage.textContent =
    customMessage ||
    (isWin
      ? "Điểm đủ cao, bạn sẽ tiến tới thử thách tiếp theo."
      : "Điểm chưa đạt ngưỡng, hãy luyện tập thêm.");
  if (isWin && advancedLevel) {
    popupNextMode = "next-level";
    nextLevelTarget = sessionContext.level;
    popupNextBtn.textContent = `🚀 Sang level ${nextLevelTarget}`;
    popupNextBtn.style.display = "inline-block";
  } else {
    popupNextBtn.style.display = "none";
  }
  resultPopup.classList.add("show");
}

// ========================
// POPUP VIDEO HỌC LẠI
// ========================

function showLearningVideo(emotionInfo) {
  const overlay = document.createElement("div");
  overlay.style.position = "fixed";
  overlay.style.inset = "0";
  overlay.style.background = "rgba(0,0,0,0.6)";
  overlay.style.display = "flex";
  overlay.style.alignItems = "center";
  overlay.style.justifyContent = "center";
  overlay.style.zIndex = "9999";

  const modal = document.createElement("div");
  modal.style.background = "#fff";
  modal.style.padding = "16px";
  modal.style.borderRadius = "12px";
  modal.style.width = "min(90%, 640px)";
  modal.style.boxShadow = "0 12px 30px rgba(0,0,0,0.25)";

  const title = document.createElement("h3");
  title.textContent = `Ôn lại cảm xúc: ${emotionInfo.label}`;

  const video = document.createElement("video");
  video.src = `../../assets/videos/${emotionInfo.video}.mp4`;
  video.controls = true;
  video.autoplay = true;
  video.style.width = "100%";
  video.style.borderRadius = "8px";

  const closeBtn = document.createElement("button");
  closeBtn.textContent = "Đã hiểu";
  closeBtn.style.marginTop = "12px";
  closeBtn.style.padding = "8px 12px";
  closeBtn.style.background = "#2563eb";
  closeBtn.style.color = "#fff";
  closeBtn.style.border = "none";
  closeBtn.style.borderRadius = "6px";
  closeBtn.style.cursor = "pointer";
  closeBtn.addEventListener("click", () => overlay.remove());

  modal.appendChild(title);
  modal.appendChild(video);
  modal.appendChild(closeBtn);
  overlay.appendChild(modal);
  document.body.appendChild(overlay);
}
