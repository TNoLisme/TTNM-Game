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

const LEVEL_THRESHOLD = 40;

const TARGET_QUESTIONS = 5;

// 3 bộ phận đều chọn trong cùng 1 mảng 6 cảm xúc

// Khi đã "xem đáp án" của câu hiện tại thì skipBtn bỏ qua luôn (không confirm)

// ========================

// TRẠNG THÁI GAME

// ========================

// -1 = chưa chọn, để ban đầu KHÔNG có gì

let selectedEyebrows = -1;

let selectedEyes = -1;

let selectedLips = -1;

let currentQuestionIndex = 0;

let questionsAnswered = 0;
let currentStep = 0;

function isLastStep() {
  return currentStep >= TARGET_QUESTIONS - 1;
}

async function advanceToNextQuestion() {
  if (isLastStep()) {
    // đang ở câu cuối -> không có câu tiếp theo
    await finalizeSession("completed");
    return;
  }
  currentStep += 1;
  await nextQuestion();
}

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

let isForcedLearning = false; // ✅ cờ để bắt buộc học khi sai >= 3 lần

let forcedLearningEmotion = null; // ✅ cảm xúc cần học lại

let ratio = [...DEFAULT_RATIO];

let isAnswerRevealed = false; // đã bấm Xem đáp án chưa

let isCurrentQuestionLocked = false;

let hasCheckedThisQuestion = false; // ✅ NEW: đã bấm Kiểm tra (checkAnswer) chưa

// ========================

// POPUP ACTION HANDLERS (NEW)

// ========================

let popupReplayAction = null; // nút trái

let popupNextAction = null; // nút phải
function getEmotionErrorsStorageKey() {
  const uid = currentUser?.user_id || "guest";
  const gid = gameId || "unknown_game";
  const lvl = sessionContext?.level || 1;
  return `emotion_errors:${uid}:${gid}:L${lvl}`;
}

function loadEmotionErrorsFromStorage() {
  try {
    const key = getEmotionErrorsStorageKey();
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return null;
    return { ...defaultEmotionErrors(), ...parsed };
  } catch {
    return null;
  }
}

function saveEmotionErrorsToStorage() {
  try {
    const key = getEmotionErrorsStorageKey();
    localStorage.setItem(
      key,
      JSON.stringify(sessionContext.emotionErrors || {})
    );
  } catch {}
}

function setPopupActions({ onReplay, onNext }) {
  popupReplayAction = typeof onReplay === "function" ? onReplay : null;

  popupNextAction = typeof onNext === "function" ? onNext : null;
}

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

let skipInProgress = false;

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

    // Thêm nút loa đọc câu hỏi (chỉ khi bấm mới phát)
    try {
      const situationBox = document.querySelector(".situation-box");
      if (situationBox && !document.getElementById("speak-question-btn")) {
        const btn = document.createElement("button");
        btn.id = "speak-question-btn";
        btn.type = "button";
        btn.className = "btn btn-ghost speak-btn";
        btn.title = "Nghe câu hỏi";
        btn.style.marginLeft = "8px";
        btn.textContent = "🔊";

        btn.addEventListener("click", () => {
          const text = situationText ? situationText.textContent.trim() : "";
          if (text) speakVietnamese(text);
        });

        // đặt ở góc phải của situationBox
        situationBox.appendChild(btn);
      }
    } catch (e) {
      console.warn("Không thể tạo nút loa:", e);
    }
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
    if (popupReplayAction) popupReplayAction();
  });

  popupNextBtn?.addEventListener("click", () => {
    // giữ logic next-level nếu bạn có dùng

    if (popupNextMode === "next-level" && nextLevelTarget) {
      window.location.href = `./level_select.html?gameId=${gameId}`;

      return;
    }

    if (popupNextAction) popupNextAction();
  });
}

function showConfirmSkipPopup() {
  if (!resultPopup) return;

  popupNextMode = "question";

  nextLevelTarget = null;

  popupIcon.textContent = "⏭️";

  popupTitle.textContent = "Bỏ qua câu này?";

  popupMessage.textContent = "Bạn có chắc muốn bỏ qua không?";

  popupReplayBtn.style.display = "inline-block";

  popupNextBtn.style.display = "inline-block";

  popupReplayBtn.textContent = "Không";

  popupNextBtn.textContent = "Có";

  setPopupActions({
    onReplay: () => {
      hideResultPopup(); // Không bỏ qua -> quay lại câu hiện tại
    },

    onNext: () => {
      hideResultPopup();

      applySkipCurrentQuestion(); // Có -> thực sự bỏ qua
      //lỗi sai cảm xúc đó + 1  sessionContext.emotionErrors[emotionName] += 1;
    },
  });

  resultPopup.classList.add("show");
}

// tách logic bỏ qua thật sự ra 1 hàm để dùng lại

function applySkipCurrentQuestion(force = false) {
  if (skipInProgress) return;
  skipInProgress = true;

  try {
    if (
      sessionContext.finished ||
      (!force && showingFeedback) ||
      !currentQuestionData
    )
      return;

    // ✅ ĐÃ bấm kiểm tra rồi: sai/đúng đã được tính vào emotionErrors trong recordAnswer()
    // => skip chỉ để chuyển câu, KHÔNG cộng thêm lần sai nữa
    if (hasCheckedThisQuestion) {
      if (!isLastStep()) advanceToNextQuestion();
      else showSkipEndGamePopup(); // (tuỳ bạn: câu cuối đã có popup endgame từ checkAnswer rồi)
      return;
    }

    // ✅ CHƯA bấm kiểm tra mà bỏ qua: tính là 1 lần sai để đếm tới 3 -> bật thẻ học
    const responseTime = questionStartTime
      ? Math.round(performance.now() - questionStartTime)
      : 0;

    questionResults.push({
      question_id: currentQuestionData.questionId,
      answer: "Bỏ qua",
      is_correct: false,
      response_time_ms: responseTime,
      used_hint: false,
    });

    if (isLastStep()) {
      recordAnswer(false, "Bỏ qua", responseTime, { autoAdvance: false });
      showSkipEndGamePopup();
      return;
    }

    recordAnswer(false, "Bỏ qua", responseTime, { autoAdvance: true });
  } finally {
    setTimeout(() => (skipInProgress = false), 250);
  }
}

// ========================

// BỎ QUA NGAY (NEW) - KHÔNG CONFIRM

// ========================

function skipImmediately() {
  // ✅ chỉ skip đúng 1 lần

  applySkipCurrentQuestion(true);
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
    if (!progress) return;

    // ❌ đừng overwrite sessionContext.level ở đây
    // ✅ chỉ lưu level mở khóa
    sessionContext.unlockedLevel =
      progress.level ?? sessionContext.unlockedLevel;

    ratio =
      Array.isArray(progress.ratio) && progress.ratio.length === 6
        ? progress.ratio
        : [...DEFAULT_RATIO];

    // (tuỳ backend) nếu progress có last_score/last_completed_level thì set để UI show
    if (progress.last_completed_level != null)
      sessionContext.lastCompletedLevel = progress.last_completed_level;
    if (progress.last_score != null)
      sessionContext.lastCompletedScore = progress.last_score;
  } catch (e) {
    console.warn("Không thể tải tiến trình", e);
  }
}

// Nút popup: sang câu tiếp theo (chỉ hiện khi đúng)

async function startSession() {
  sessionContext.finished = false;
  showingFeedback = false;
  setPopupActions({ onReplay: null, onNext: null });

  currentStep = 0; // ✅ bắt đầu lại từ câu 1 cho session mới

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
      ...(sessionContext.emotionErrors || {}), // ✅ giữ lỗi đang tích luỹ
      ...(data.emotion_errors || {}), // ✅ nếu backend có trả, merge thêm
    };
    saveEmotionErrorsToStorage(); // ✅ persist

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
function goToLevelSelectPage(completedLevel, score) {
  // ✅ vừa lưu localStorage vừa truyền query để trang đích dễ đọc
  saveLastCompletedResult(completedLevel, score);

  window.location.href =
    `./level_select.html?gameId=${gameId}` +
    `&completedLevel=${encodeURIComponent(completedLevel)}` +
    `&score=${encodeURIComponent(score)}`;
}

function saveLastCompletedResult(completedLevel, score) {
  try {
    const uid = currentUser?.user_id || "guest";
    const gid = gameId || "unknown_game";
    localStorage.setItem(
      `last_completed:${uid}:${gid}`,
      JSON.stringify({
        completed_level: completedLevel,
        score: score,
        saved_at: Date.now(),
      })
    );
  } catch {}
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

  // ✅ Auto-prefetch question + instruction text (matches game_click_3.js)
  const textToSpeak =
    currentQuestionData.question_text +
    ". Hãy xây dựng khuôn mặt cho cảm xúc này.";
  prefetchTTS(textToSpeak, "thuminh", 0);
}

// ===== TTS: speakVietnamese (matches game_click_3.js) =====
const ttsCache = new Map();
const ttsPending = new Map();

function ttsKey(text, voice = "thuminh", speed = 0) {
  return `${voice}:${speed}:${(text || "").trim().toLowerCase()}`;
}

async function playAudioUrl(url, retries = 6, delayMs = 300) {
  let ttsAudio = new Audio();
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

        ttsAudio.addEventListener("canplaythrough", ok, { once: true });
        ttsAudio.addEventListener("error", bad, { once: true });
      });

      await ttsAudio.play();
      return;
    } catch (e) {
      if (i === retries) throw e;
      await new Promise((r) => setTimeout(r, delayMs));
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
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: clean,
        voice,
        speed,
      }),
    });

    if (!res.ok) {
      const msg = await res.text().catch(() => "");
      throw new Error(msg || "TTS error");
    }

    const { audioUrl } = await res.json();
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

async function speakVietnamese(
  text,
  fromButton = false,
  voice = "thuminh",
  speed = 0
) {
  try {
    const audioUrl = await prefetchTTS(text, voice, speed);
    if (!audioUrl) return;
    await playAudioUrl(audioUrl);
  } catch (e) {
    console.warn("TTS failed:", e);
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

// HIỆN MẶT ĐÚNG (NEW)

// ========================

function showCorrectFaceOnBoard() {
  if (!currentQuestionData || !currentQuestionData.correct_emotion) return;

  const correctIdx = currentQuestionData.correct_emotion.index;

  selectedEyebrows = correctIdx;

  selectedEyes = correctIdx;

  selectedLips = correctIdx;

  isAnswerRevealed = true; // ✅ đã xem đáp án

  isCurrentQuestionLocked = true;

  hasCheckedThisQuestion = true;

  showingFeedback = false; // thoát feedback để skip không bị chặn

  updateFace();

  updateLabels();

  // khoá chỉnh sửa

  eyebrowBtn.disabled = true;

  eyesBtn.disabled = true;

  lipsBtn.disabled = true;

  // ✅ cập nhật nút

  updateButtonStates();
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
    Array.isArray(questionsPool) && questionsPool.length
      ? questionsPool.length
      : TARGET_QUESTIONS
  );

  // ✅ dùng currentStep để hiển thị số câu
  const current = Math.min(currentStep + 1, totalQuestions);
  questionNumber.textContent = current;

  if (questionTotal) questionTotal.textContent = totalQuestions;
  scoreElement.textContent = sessionContext.score;

  // Cập nhật thanh tiến độ (phần trăm)
  const progressFill = document.getElementById("click-progress-fill");
  const progressLabel = document.getElementById("progress-label");
  const percentage =
    totalQuestions > 0 ? Math.round((current / totalQuestions) * 100) : 0;

  if (progressFill) {
    progressFill.style.width = `${percentage}%`;
  }

  if (progressLabel) {
    progressLabel.textContent = `Câu ${current}/${totalQuestions}`;
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
  if (disabledAll) {
    resetBtn.disabled = true;

    checkBtn.disabled = true;

    skipBtn.disabled = true;

    if (exitBtn) exitBtn.disabled = true;

    return;
  }

  // ✅ TRẠNG THÁI SAU KHI XEM ĐÁP ÁN: chỉ mở BỎ QUA

  if (isAnswerRevealed) {
    resetBtn.disabled = true;

    checkBtn.disabled = true;

    skipBtn.disabled = false;

    if (exitBtn) exitBtn.disabled = false;

    return;
  }

  // bình thường

  const disabled = showingFeedback;

  resetBtn.disabled = disabled;

  checkBtn.disabled = disabled;

  skipBtn.disabled = disabled;

  if (exitBtn) exitBtn.disabled = false;
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

  isAnswerRevealed = false;

  isCurrentQuestionLocked = false;

  hasCheckedThisQuestion = false;

  // mở lại điều khiển

  eyebrowBtn && (eyebrowBtn.disabled = false);

  eyesBtn && (eyesBtn.disabled = false);

  lipsBtn && (lipsBtn.disabled = false);

  resetFace();

  updateSituation();

  updateStats();

  updateButtonStates();
}

async function nextQuestion() {
  if (sessionContext.finished) return;
  const nextIdx = (currentQuestionIndex + 1) % questionsPool.length;
  loadQuestionByIndex(nextIdx);
}

function skipQuestion() {
  if (sessionContext.finished || showingFeedback || !currentQuestionData)
    return;

  // ✅ Nếu đã xem đáp án -> bỏ qua luôn, KHÔNG confirm

  if (isAnswerRevealed) {
    applySkipCurrentQuestion();

    return;
  }

  // ✅ Nếu chưa bấm kiểm tra mà đòi bỏ qua -> hỏi confirm

  if (!hasCheckedThisQuestion) {
    showConfirmSkipPopup();

    return;
  }

  // ✅ còn lại (đã bấm kiểm tra nhưng không xem đáp án) -> bạn muốn confirm hay bỏ luôn?

  // Theo yêu cầu hiện tại: cứ confirm cho an toàn

  showConfirmSkipPopup();
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

  hasCheckedThisQuestion = true;

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

  // ✅ CÂU CUỐI: vẫn phải hiện đúng/sai
  if (isLastStep()) {
    // Với câu cuối: luôn hiện popup kết thúc level (hiển thị điểm và trạng thái qua level)
    showEndGamePopup(isCorrect);
    return;
  }

  if (sessionContext.finished) return;
  showResultPopup(isCorrect);
}

function resetLevelStateForReplay() {
  sessionContext.finished = false;
  sessionContext.score = 0;

  reviewEmotions = [];
  questionResults = [];
  playedQuestions = [];
  questionCycle = [];
  showingFeedback = false;
  isAnswerRevealed = false;
  isCurrentQuestionLocked = false;
  hasCheckedThisQuestion = false;
  skipInProgress = false;
  currentStep = 0; // ✅ quay về câu 1
}

function showEndGamePopup(isCorrect) {
  if (!resultPopup) return;

  popupNextMode = "question";
  nextLevelTarget = null;
  // quyết định vượt level dựa trên ngưỡng trong context
  const isWin =
    sessionContext.score >= (sessionContext.levelThreshold || LEVEL_THRESHOLD);

  popupIcon.textContent = isWin ? "🏆" : "🙂";
  popupTitle.textContent = isWin
    ? `Bạn đã vượt level! — Tổng điểm: ${sessionContext.score}`
    : `Kết thúc level — Tổng điểm: ${sessionContext.score}`;

  popupMessage.textContent = isWin
    ? "Chúc mừng! Điểm đạt ngưỡng, bạn có thể sang level tiếp theo hoặc chơi lại."
    : "Điểm chưa đủ để qua level. Bạn có thể chơi lại để cải thiện điểm.";

  popupReplayBtn.style.display = "inline-block";
  popupNextBtn.style.display = "inline-block";
  popupReplayBtn.textContent = "Chơi lại level";
  popupNextBtn.textContent = "Level mới";

  setPopupActions({
    onReplay: async () => {
      hideResultPopup();
      await finalizeSession("completed");

      resetLevelStateForReplay();
      sessionContext.sessionId = null;
      await startSession();
    },
    onNext: async () => {
      hideResultPopup();

      const completedLevel = sessionContext.level; // ✅ level vừa chơi xong
      const completedScore = sessionContext.score; // ✅ điểm vừa đạt

      await finalizeSession("completed");

      // ✅ sang trang chọn level, vẫn hiển thị level 2 - 40 điểm
      goToLevelSelectPage(completedLevel, completedScore);
    },
  });

  resultPopup.classList.add("show");
}

function showSkipEndGamePopup() {
  if (!resultPopup) return;

  // dọn extra button nếu có
  if (extraExitBtn && extraExitBtn.parentNode) {
    extraExitBtn.parentNode.removeChild(extraExitBtn);
  }
  extraExitBtn = null;

  popupNextMode = "question";
  nextLevelTarget = null;

  const isWin =
    sessionContext.score >= (sessionContext.levelThreshold || LEVEL_THRESHOLD);

  popupIcon.textContent = isWin ? "🏆" : "⏭️";
  popupTitle.textContent = isWin
    ? `Bạn đã vượt level! — Tổng điểm: ${sessionContext.score}`
    : `Kết thúc level — Tổng điểm: ${sessionContext.score}`;

  popupMessage.textContent = isWin
    ? "Bạn đã bỏ qua câu cuối nhưng điểm vẫn đạt ngưỡng. Bạn có thể chơi lại hoặc chọn level tiếp theo."
    : "Bạn đã bỏ qua câu cuối. Điểm chưa đủ để qua level — bạn vẫn có thể quay lại trang chọn level.";

  popupReplayBtn.style.display = "inline-block";
  popupNextBtn.style.display = "inline-block";

  popupReplayBtn.textContent = "Chơi lại";
  popupNextBtn.textContent = "Level tiếp";

  setPopupActions({
    onReplay: async () => {
      hideResultPopup();
      await finalizeSession("completed");

      resetLevelStateForReplay();
      sessionContext.sessionId = null;
      await startSession();
    },

    onNext: async () => {
      hideResultPopup();
      await finalizeSession("completed");

      // ✅ LUÔN sang trang chọn level, không ép chơi lại nữa
      goToLevelSelectPage();
    },
  });

  resultPopup.classList.add("show");
}

function recordAnswer(isCorrect, answerLabel, responseTime, options = {}) {
  const { autoAdvance = false } = options;

  showingFeedback = !autoAdvance;

  lastAnswerCorrect = isCorrect;

  // Cộng điểm / cộng lỗi

  isForcedLearning = false;
  forcedLearningEmotion = null;

  if (isCorrect) {
    sessionContext.score += 10;
  } else {
    const emotionName = currentQuestionData.correct_emotion.label;

    sessionContext.emotionErrors[emotionName] =
      (sessionContext.emotionErrors[emotionName] || 0) + 1;

    saveEmotionErrorsToStorage(); // ✅ lưu ngay sau khi cộng

    // ✅ Kiểm tra xem lỗi này có vừa đạt ngưỡng 3 không
    if (
      sessionContext.emotionErrors[emotionName] >= 3 &&
      !reviewEmotions.includes(emotionName)
    ) {
      isForcedLearning = true;
      forcedLearningEmotion = currentQuestionData.correct_emotion;
      reviewEmotions.push(emotionName);
      // ✅ reset counter sau khi đạt 3
      sessionContext.emotionErrors[emotionName] = 0;
      saveEmotionErrorsToStorage();
    }
  }

  // Tăng số câu đã trả lời

  updateStats();

  // Nếu đã tới câu 10 thì KHÔNG tự finalize, để checkAnswer xử lý popup
  if (isLastStep()) {
    updateButtonStates(true);
    return;
  }
  updateButtonStates();

  // ✅ chỉ auto-advance khi bạn muốn (skip auto) - còn đúng thì đợi bấm "Câu tiếp theo"
  if (autoAdvance) {
    advanceToNextQuestion();
  }
}

// ========================

// POPUP KẾT QUẢ

// ========================

function showResultPopup(isCorrect) {
  if (!resultPopup) return;

  popupNextMode = "question";

  nextLevelTarget = null;

  // ✅ KIỂM TRA FORCED LEARNING (giống recognize_emotion.js)
  if (isForcedLearning && forcedLearningEmotion) {
    popupIcon.textContent = "📚";
    popupTitle.textContent = "CẦN HỌC LẠI CẢM XÚC NÀY!";
    popupTitle.style.color = "#f65c80";
    popupMessage.textContent = `Bạn sai nhiều lần ở cảm xúc "${forcedLearningEmotion.label}". Hãy học lại để ôn tập kiến thức trước khi tiếp tục.`;

    popupReplayBtn.style.display = "none";
    popupNextBtn.style.display = "inline-block";
    popupNextBtn.textContent = "HỌC LẠI CẢM XÚC NÀY";

    setPopupActions({
      onReplay: null,
      onNext: () => {
        hideResultPopup();
        showLearningVideo(forcedLearningEmotion);
      },
    });

    resultPopup.classList.add("show");
    return;
  }

  if (isCorrect) {
    // ✅ ĐÚNG: popup có nút Câu tiếp theo

    popupIcon.textContent = "🎉";

    popupTitle.textContent = "Tuyệt vời!";
    popupTitle.style.color = "";

    popupMessage.textContent =
      'Bạn đã xây đúng khuôn mặt cho cảm xúc này. Nhấn "Câu tiếp theo" để tiếp tục nhé!';

    popupReplayBtn.style.display = "none";

    popupNextBtn.style.display = "inline-block";

    popupNextBtn.textContent = "Câu tiếp theo";

    setPopupActions({
      onReplay: null,

      onNext: () => {
        hideResultPopup();

        advanceToNextQuestion(); // ✅ chỉ next tại đây
      },
    });

    resultPopup.classList.add("show");

    return;
  }

  // ✅ SAI: popup chỉ cho "Xem đáp án" hoặc "Bỏ qua"

  popupIcon.textContent = "❌";

  popupTitle.textContent = "Sai rồi!";

  popupMessage.textContent =
    "Hãy xem đáp án, sau đó bấm nút Bỏ qua (ở dưới) để sang câu tiếp theo.";

  popupReplayBtn.style.display = "inline-block";

  popupNextBtn.style.display = "inline-block";

  popupReplayBtn.textContent = "Xem đáp án";

  popupNextBtn.textContent = "Bỏ qua";

  setPopupActions({
    onReplay: () => {
      hideResultPopup(); // ✅ đóng popup để không che mặt

      showCorrectFaceOnBoard(); // ✅ hiện đáp án + mở skipBtn
    },

    onNext: () => {
      hideResultPopup();
      // ✅ bấm "Bỏ qua" trong popup sai => sang câu khác luôn, không confirm
      applySkipCurrentQuestion(true);
    },
  });

  resultPopup.classList.add("show");
}

function hideResultPopup() {
  if (!resultPopup) return;
  resultPopup.classList.remove("show");

  // ✅ clear action để tránh click bị chạy handler cũ
  setPopupActions({ onReplay: null, onNext: null });

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
  const completedLevel = sessionContext.level; // ✅ level vừa chơi xong
  const completedScore = sessionContext.score; // ✅ điểm của level vừa chơi xong

  // ✅ lưu để UI hiển thị đúng (kể cả khi progress API trả "level mới mở khóa")
  sessionContext.lastCompletedLevel = completedLevel;
  sessionContext.lastCompletedScore = completedScore;

  const payload = {
    session_id: sessionContext.sessionId,

    results: filteredResults,

    review_emotions: reviewEmotions,
    level: completedLevel,
    score: completedScore,
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

      // ✅ progress_level là level mới mở khóa, KHÔNG phải level vừa chơi xong
      sessionContext.unlockedLevel =
        data.progress_level || sessionContext.level;

      // ✅ giữ nguyên level đã chơi (previousLevel)
      sessionContext.level = previousLevel;
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

  closeBtn.addEventListener("click", () => {
    video.pause();
    overlay.remove();

    // ✅ Nếu là forced learning, tiếp tục sang câu tiếp theo
    if (isForcedLearning) {
      isForcedLearning = false;
      forcedLearningEmotion = null;
      advanceToNextQuestion();
    }
  });

  modal.appendChild(title);

  modal.appendChild(video);

  modal.appendChild(closeBtn);

  overlay.appendChild(modal);

  document.body.appendChild(overlay);
}
