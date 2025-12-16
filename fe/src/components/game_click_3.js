let sessionId = null;
let user = null;
let gameId = null;
let level = null;
let questions = [];
let localResults = [];
let remainingQuestions = [];
let roundIndex = 0;

let score = 0;
let endLevelSent = false;
let draggedName = null;
let gameInfo = null;
let isEmotionMatchGame = false;
let pendingNextLevel = null;
let isLevelCompletePopup = false;
let isTTSManualOnly = true;

let maxErrors = 1;
let emotionErrors = {};
let learnedEmotions = [];
let learningCards = {};
let roundScored = false;
let reviewMode = false;
let lastRoundSnapshot = null;
let roundResults = [];
let gameState = {
  difficulty: "easy",
  shuffledCharacters: [],
  answers: {},
  submitted: false,
  results: {},
  currentLevel: 1,
  canRetry: true,
  retryUsed: false,
};
const TOTAL_ROUNDS = 5;
const LEVEL_META = [
  { num: 1, icon: "😊", name: "Dễ" },
  { num: 2, icon: "❤️", name: "Vui" },
  { num: 3, icon: "⭐", name: "Hay" },
  { num: 4, icon: "✨", name: "Giỏi" },
  { num: 5, icon: "☀️", name: "Xuất sắc" },
  { num: 6, icon: "🌸", name: "Tuyệt vời" },
  { num: 7, icon: "🌈", name: "Siêu đẳng" },
  { num: 8, icon: "🎮", name: "Cao thủ" },
];

function isLockedInteraction() {
  return gameState.submitted || reviewMode;
}

function getLevelMeta(lv) {
  return (
    LEVEL_META.find((l) => l.num === lv) || {
      num: lv,
      icon: "🎯",
      name: `Level ${lv}`,
    }
  );
}

function normalizeText(text) {
  return (text || "")
    .toString()
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/đ/g, "d");
}

function shuffleArray(array) {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}
function resolveImagePath(p) {
  if (!p) return "";
  return p.replace(/^\/fe\//, "/"); // "/fe/assets/..." -> "/assets/..."
}

function getNumQuestionsPerRound(lv) {
  if (lv <= 2) return 2;
  if (lv <= 4) return 3;
  if (lv <= 6) return 4;
  if (lv <= 8) return 5;
  return 5;
}

function pickQuestionsForCurrentLevelUnique(
  opts = { uniqueName: true, uniqueEmotion: true }
) {
  if (!remainingQuestions || remainingQuestions.length === 0) return [];

  const maxPerRound = getNumQuestionsPerRound(level);
  const num = Math.min(maxPerRound, remainingQuestions.length);
  const pool = shuffleArray(remainingQuestions);

  const usedNames = new Set();
  const usedEmotions = new Set();
  const selected = [];

  for (const q of pool) {
    if (selected.length >= num) break;

    const name = (q.correct_answer || "").trim().toLowerCase();
    const emo = (q.emotion || "").trim().toLowerCase();

    if (opts.uniqueName && name && usedNames.has(name)) continue;
    if (opts.uniqueEmotion && emo && usedEmotions.has(emo)) continue;

    selected.push(q);
    if (name) usedNames.add(name);
    if (emo) usedEmotions.add(emo);
  }
  if (selected.length < num) {
    for (const q of pool) {
      if (selected.length >= num) break;
      if (selected.some((x) => x.question_id === q.question_id)) continue;
      selected.push(q);
    }
  }
  const selectedIds = new Set(selected.map((q) => q.question_id));
  remainingQuestions = remainingQuestions.filter(
    (q) => !selectedIds.has(q.question_id)
  );

  return selected;
}

function pickQuestionsForCurrentLevel() {
  if (!remainingQuestions || remainingQuestions.length === 0) return [];

  const maxPerRound = getNumQuestionsPerRound(level);
  const num = Math.min(maxPerRound, remainingQuestions.length);

  const shuffled = shuffleArray(remainingQuestions);
  const selected = shuffled.slice(0, num);

  const selectedIds = new Set(selected.map((q) => q.question_id));
  remainingQuestions = remainingQuestions.filter(
    (q) => !selectedIds.has(q.question_id)
  );

  return selected;
}
function updateProgressUI() {
  const progressLabel = document.getElementById("progress-label");
  const scoreLabel = document.getElementById("score-label");

  // ✅ ID đúng theo HTML mới
  const progressBarFill = document.getElementById("click-progress-fill");

  const current = roundIndex + 1;
  const total = TOTAL_ROUNDS;
  const percentage = (current / total) * 100;

  if (progressLabel) {
    progressLabel.textContent = `Câu ${current}/${total}`;
  }

  if (scoreLabel) {
    scoreLabel.textContent = `Điểm: ${score}`;
  }

  if (progressBarFill) {
    progressBarFill.style.width = `${percentage}%`;
  }
}

window.addEventListener("DOMContentLoaded", async () => {
  user = JSON.parse(localStorage.getItem("currentUser"));
  if (!user) {
    alert("Vui lòng đăng nhập!");
    window.location.href = "./login.html";
    return;
  }

  const urlParams = new URLSearchParams(window.location.search);
  gameId = urlParams.get("gameId");
  level = parseInt(urlParams.get("level"));

  if (!gameId || !level) {
    alert("Thiếu thông tin game hoặc level");
    window.location.href = "./select_game.html";
    return;
  }

  try {
    const gameRes = await fetch(`/games/${gameId}`);
    if (gameRes.ok) {
      gameInfo = await gameRes.json();
      const normalizedName = normalizeText(gameInfo?.name);
      isEmotionMatchGame =
        normalizedName.includes("cam xuc dung cho") ||
        (normalizedName.includes("cam xuc") &&
          normalizedName.includes("dung cho")) ||
        (normalizedName.includes("chon") &&
          normalizedName.includes("cam xuc") &&
          normalizedName.includes("tinh huong"));

      if (gameInfo?.name) {
        document.title = gameInfo.name;
        const titleEl = document.querySelector(".game-title");
        if (titleEl) {
          titleEl.textContent = `${gameInfo.name} 🎭`;
        }
      }

      if (isEmotionMatchGame) {
        const hintTitle = document.querySelector(".hint-content h3");
        if (hintTitle) hintTitle.textContent = "💡 Tình huống:";
        const namesTitle = document.querySelector(".names-section h3");
        if (namesTitle)
          namesTitle.textContent =
            "🎴 Kéo thẻ cảm xúc vào ô phía dưới mỗi khuôn mặt:";
      }
    }
  } catch (e) {
    // ignore
  }

  try {
    const res = await fetch(`/games/start-dynamic/${gameId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: user.user_id,
        level: level,
      }),
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Lỗi khởi động game");
    }

    const data = await res.json();
    sessionId = data.session_id;
    questions = data.questions || [];
    maxErrors = data.max_errors || 3;
    learningCards = data.learning_cards || {};
    const normalizedLearningCards = {};
    for (const key in learningCards) {
      if (Object.prototype.hasOwnProperty.call(learningCards, key)) {
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
      "vui vẻ": 0,
    };
    learnedEmotions = [];

    if (!questions || questions.length === 0) {
      throw new Error("Không tải được câu hỏi cho level này (mảng rỗng)");
    }

    remainingQuestions = [...questions];
    roundIndex = 0;
    score = 0;
    localResults = [];
    roundResults = [];
    endLevelSent = false;
    updateProgressUI();
    const selectedQuestions = pickQuestionsForCurrentLevelUnique({
      uniqueName: true,
      uniqueEmotion: true,
    });

    if (selectedQuestions.length === 0) {
      throw new Error("Không còn câu hỏi nào cho level này");
    }

    gameState.characters = selectedQuestions.map((q) => ({
      id: q.question_id,
      name: q.correct_answer,
      emotion: q.emotion || "",
      image: resolveImagePath(q.media_path),
    }));

    gameState.shuffledCharacters = shuffleArray(gameState.characters);

    if (gameState.characters.length <= 2) {
      gameState.difficulty = "easy";
      gameState.currentLevel = 1;
    } else if (gameState.characters.length === 3) {
      gameState.difficulty = "medium";
      gameState.currentLevel = 2;
    } else {
      gameState.difficulty = "hard";
      gameState.currentLevel = 3;
    }

    initializeRound();
  } catch (err) {
    console.error(err);
    alert(err.message || "Lỗi khi khởi động game");
  }
});

async function sendFinalResults() {
  if (!sessionId) return;
  if (endLevelSent) return;
  endLevelSent = true;

  try {
    const res = await fetch("/games/end-level", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        results: localResults,
        review_emotions: learnedEmotions,
      }),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || "Lỗi end-level");
    }
  } catch (err) {
    console.error(err);
    alert("Đã xảy ra lỗi khi lưu tiến trình.");
  }
}

// ================== KHỞI TẠO VÒNG CHƠI ==================
function initializeRound() {
  gameState.answers = {};
  gameState.submitted = false;
  gameState.results = {};

  const progressFill = document.getElementById("click-progress-fill");
  if (progressFill && Array.isArray(questions) && questions.length) {
    const remaining = Array.isArray(remainingQuestions) ? remainingQuestions.length : 0;
    const currentRoundSize = Array.isArray(gameState.characters) ? gameState.characters.length : 0;
    const completed = Math.max(0, questions.length - remaining - currentRoundSize);
    const percentage = (completed / questions.length) * 100;
    progressFill.style.width = `${percentage}%`;
  }
  gameState.retryUsed = false;
  roundScored = false;
  reviewMode = false;
  renderGame();
  updateProgressUI();
}

// ================== RENDER GAME ==================
function renderGame() {
  const qTotal = 5;
  const qAnswered = Object.keys(gameState.answers || {}).length;

  renderHints();
  renderFaces();
  renderNameCards();
  renderButtons();

  document.getElementById("result-message").classList.add("hidden");
}

function renderHints() {
  const hintsContainer = document.getElementById("hints-list");
  hintsContainer.innerHTML = gameState.characters
    .map((char, index) => {
      const emo = char.emotion || char.name || "một cảm xúc nào đó";
      return `
            <p>
                ${index + 1}. 
                <strong>${char.name}</strong> đang cảm thấy 
                "<strong>${emo}</strong>", 
                hãy kéo thẻ tên để biết đâu là <strong>${char.name}</strong>.
            </p>
        `;
    })
    .join("");
}

// Render khuôn mặt
function renderFaces() {
  const facesGrid = document.getElementById("faces-grid");
  const faces = gameState.shuffledCharacters.length
    ? gameState.shuffledCharacters
    : gameState.characters;

  const locked = isLockedInteraction();

  facesGrid.innerHTML = faces
    .map((char) => {
      const droppedName = gameState.answers[char.id];
      const isCorrect = gameState.results[char.id];
      const showAnswer = gameState.submitted && isCorrect === false;

      // Khi locked => KHÔNG gắn ondrop/ondragover/ondragleave
      const dropHandlers = locked
        ? ""
        : `ondrop="handleDrop(event)"
           ondragover="handleDragOver(event)"
           ondragleave="handleDragLeave(event)"`;

      return `
        <div class="face-card">
          <img src="${char.image}" alt="${char.emotion}" class="face-image">

          <div class="drop-zone ${droppedName ? "filled" : ""} ${
        locked ? "locked" : ""
      }"
               data-character-id="${char.id}"
               ${dropHandlers}>
            ${
              droppedName
                ? `
                  <div class="dropped-name">
                    <span>${droppedName}</span>
                    ${
                      // KHÔNG bao giờ cho xóa khi locked
                      !locked && isCorrect === undefined
                        ? `<button class="remove-btn" onclick="removeName('${char.id}')">✕</button>`
                        : ""
                    }
                    ${
                      isCorrect === true
                        ? '<span class="status-icon">✓</span>'
                        : ""
                    }
                    ${
                      isCorrect === false
                        ? '<span class="status-icon">✗</span>'
                        : ""
                    }
                  </div>
                `
                : '<span class="drop-zone-placeholder">Thả tên vào đây</span>'
            }
          </div>

          ${
            showAnswer
              ? `<div class="answer-hint">Đáp án đúng: ${char.name}</div>`
              : ""
          }
        </div>
      `;
    })
    .join("");
}

function renderNameCards() {
  const usedNames = Object.values(gameState.answers);
  const availableNames = gameState.characters
    .map((c) => c.name)
    .filter((name) => !usedNames.includes(name));

  const container = document.getElementById("name-cards-container");
  const locked = isLockedInteraction();

  if (availableNames.length === 0 && !locked) {
    container.innerHTML =
      '<p class="no-names-msg">Tất cả thẻ tên đã được sử dụng</p>';
    return;
  }

  const shuffledNames = shuffleArray(availableNames);
  container.innerHTML = shuffledNames
    .map(
      (name) => `
        <div class="name-card ${locked ? "disabled" : ""}"
             draggable="${!locked}"
             ${locked ? "" : `ondragstart="handleDragStart(event, '${name}')"`}
             ${locked ? "" : `ondragend="handleDragEnd(event)"`}
             style="${locked ? "pointer-events:none; opacity:0.6;" : ""}">
          <button class="name-speaker-btn" onclick="speak('${name}', true)">🔊</button>
          <span class="name-text">${name}</span>
        </div>
      `
    )
    .join("");
}

function renderButtons() {
  const allAnswered =
    Object.keys(gameState.answers).length === gameState.characters.length;

  const allCorrect =
    gameState.submitted && Object.values(gameState.results).every((r) => r);
  const submitBtn = document.getElementById("submit-btn");
  submitBtn.style.display = !gameState.submitted ? "block" : "none";
  submitBtn.disabled = !allAnswered;

  const retryBtn = document.getElementById("retry-btn");
  retryBtn.style.display = "none";

  const resetBtn = document.getElementById("reset-btn");
  resetBtn.style.display = "none";
  const nextBtn = document.getElementById("next-btn");
  const showNextInGame = gameState.submitted && (allCorrect || reviewMode);
  if (nextBtn) {
    nextBtn.style.display = showNextInGame ? "block" : "none";
    nextBtn.textContent = "Câu tiếp theo";
    nextBtn.onclick = () => nextQuestion();
  }
}

function handleDragStart(event, name) {
  if (gameState.submitted || reviewMode) return;
  draggedName = name;
  event.currentTarget.classList.add("dragging");
}

function handleDragEnd(event) {
  event.currentTarget.classList.remove("dragging");
}

function handleDragOver(event) {
  event.preventDefault();
  const dropZone = event.currentTarget;
  if (!dropZone.classList.contains("filled")) {
    dropZone.classList.add("drag-over");
  }
}

function handleDragLeave(event) {
  event.currentTarget.classList.remove("drag-over");
}

function handleDrop(event) {
  event.preventDefault();
  const dropZone = event.currentTarget;
  dropZone.classList.remove("drag-over");

  if (gameState.submitted || reviewMode) return;

  const characterId = dropZone.dataset.characterId;
  if (gameState.answers[characterId]) return;

  gameState.answers[characterId] = draggedName;
  draggedName = null;

  renderGame();
}

function removeName(characterId) {
  if (gameState.submitted || reviewMode) return;
  delete gameState.answers[characterId];
  renderGame();
}

function speak(text, fromButton = false) {
  if (!("speechSynthesis" in window)) return;
  if (isTTSManualOnly && !fromButton) return;

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "vi-VN";
  utterance.rate = 0.9;
  window.speechSynthesis.speak(utterance);
}

function speakHints() {
  const hints = gameState.characters
    .map((char) => {
      const emo = char.emotion || "một cảm xúc nào đó";
      return `${char.name} đang cảm thấy ${emo}, hãy kéo thẻ tên để biết đâu là ${char.name}`;
    })
    .join(". ");
  speak(hints);
}

function showScoreFly(points) {
  const el = document.createElement("div");
  el.className = "score-fly";
  el.textContent = `+${points} ⭐`;
  document.body.appendChild(el);

  // force reflow để animation chạy
  requestAnimationFrame(() => el.classList.add("show"));

  setTimeout(() => el.remove(), 900);
}

async function submitAnswer() {
  if (Object.keys(gameState.answers).length !== gameState.characters.length) {
    alert("Hãy đặt tên cho tất cả các khuôn mặt trước khi nộp bài!");
    return;
  }

  let allCorrect = true;
  let correctCount = 0;
  if (gameState.submitted) return;
  gameState.characters.forEach((char) => {
    const isCorrect = gameState.answers[char.id] === char.name;
    gameState.results[char.id] = isCorrect;
    if (isCorrect) {
      correctCount++;
    } else {
      allCorrect = false;
    }
  });
  const allCorrectThisRound = correctCount === gameState.characters.length;
  const gainedScore = allCorrectThisRound ? 10 : 0;
  if (!roundScored) {
    roundResults.push(allCorrectThisRound);
  }
  if (!roundScored) {
    score += gainedScore;
    roundScored = true;

    updateProgressUI();

    if (gainedScore > 0) {
      showScoreFly(gainedScore);
    }
  } else {
    updateProgressUI();
  }

  gameState.submitted = true;
  lastRoundSnapshot = {
    answers: { ...gameState.answers },
    results: { ...gameState.results },
  };
  reviewMode = false;
  renderGame();

  const newLearnedThisRound = [];

  gameState.characters.forEach((char) => {
    const isCorrect = gameState.results[char.id];
    const chosen = gameState.answers[char.id];
    if (!isCorrect) {
      const emoKey = (char.emotion || "").trim().toLowerCase();
      if (emoKey) {
        emotionErrors[emoKey] = (emotionErrors[emoKey] || 0) + 1;

        if (
          emotionErrors[emoKey] >= maxErrors &&
          !learnedEmotions.includes(emoKey)
        ) {
          learnedEmotions.push(emoKey);
          newLearnedThisRound.push(emoKey);
        }
      }
    }

    localResults.push({
      question_id: char.id,
      answer: chosen,
      is_correct: isCorrect,
      used_hint: false,
      response_time_ms: 5000,
    });
  });

  if (newLearnedThisRound.length > 0) {
    const emoToLearn = newLearnedThisRound[0];
    showLearningCard(emoToLearn, () => {
      showResultPopup(allCorrect, correctCount);
    });
  } else {
    showResultPopup(allCorrect, correctCount);
  }
}

function enterReviewMode() {
  reviewMode = true;

  // Restore lại đáp án của lượt vừa submit
  if (lastRoundSnapshot) {
    gameState.answers = { ...lastRoundSnapshot.answers };
    gameState.results = { ...lastRoundSnapshot.results };
  }

  // đảm bảo đang ở trạng thái "đã nộp" để khóa submit
  gameState.submitted = true;

  renderGame();
}

function initializeRoundRetry() {
  gameState.answers = {};
  gameState.submitted = false;
  gameState.results = {};
  gameState.retryUsed = true;

  renderGame();
  updateProgressUI();
}

// ================== POPUP THẺ HỌC CẢM XÚC ==================
function showLearningCard(emotionKey, afterClose) {
  const modal = document.getElementById("learning-modal");
  const titleEl = document.getElementById("learning-emotion-title");
  const bodyEl = document.getElementById("learning-card-body");
  const closeBtn = document.getElementById("learning-close-btn");

  const normalizedKey = (emotionKey || "").trim().toLowerCase();
  const cards = learningCards[normalizedKey]?.[level];

  const displayEmotion =
    emotionKey.charAt(0).toUpperCase() + emotionKey.slice(1);

  titleEl.textContent = `Học lại cảm xúc: ${displayEmotion}`;
  bodyEl.innerHTML = "";

  if (!cards || cards.length === 0) {
    bodyEl.innerHTML = `<p>Hiện không có video học cho cảm xúc <strong>${displayEmotion}</strong> ở level ${level}.</p>`;
  } else {
    cards.forEach((card) => {
      if (card.video_path) {
        const videoSrc = card.video_path.replace("/fe/", "../../");
        const videoHtml = `
          <video class="learn-video" controls>
            <source src="${videoSrc}" type="video/mp4">
            Trình duyệt của bạn không hỗ trợ video.
          </video>
        `;
        bodyEl.insertAdjacentHTML("beforeend", videoHtml);
      }
    });
  }

  closeBtn.onclick = () => {
    modal.classList.add("hidden");
    if (typeof afterClose === "function") {
      afterClose();
    }
  };

  modal.classList.remove("hidden");
}

// ================== POPUP KẾT QUẢ & CÁC NÚT KHÁC ==================
function showResultPopup(allCorrect, correctCount) {
  const popup = document.getElementById("result-popup");
  const icon = document.getElementById("popup-icon");
  const title = document.getElementById("popup-title");
  const message = document.getElementById("popup-message");

  const nextBtn = document.getElementById("popup-next-btn");
  const replayBtn = document.getElementById("popup-replay-btn");

  const totalQuestions = gameState.characters.length;
  icon.classList.remove("bounce", "shake");
  isLevelCompletePopup = false;
  pendingNextLevel = null;
  if (nextBtn) nextBtn.style.display = "none";
  if (replayBtn) replayBtn.style.display = "none";

  if (replayBtn) {
    replayBtn.style.display = "block";
    replayBtn.textContent = "Xem lại";
    replayBtn.onclick = () => {
      popup.classList.remove("show");
      setTimeout(() => popup.classList.add("hidden"), 200);
      enterReviewMode();
    };
  }

  if (nextBtn) {
    nextBtn.style.display = "block";
    nextBtn.textContent = "Câu tiếp theo";
    nextBtn.onclick = () => nextQuestion();
  }

  const scoreLine = `\nĐiểm hiện tại: ${score} ⭐`;

  if (allCorrect) {
    icon.textContent = "🎉";
    icon.classList.add("bounce");
    title.textContent = "Bạn đã trả lời đúng!";
    title.style.color = "#22c55e";
    message.textContent = scoreLine;
  } else {
    icon.textContent = "😢";
    icon.classList.add("shake");
    title.textContent = "Bạn đã trả lời sai!";
    title.style.color = "#ef4444";
    message.textContent = scoreLine;
  }

  popup.classList.remove("hidden");
  requestAnimationFrame(() => popup.classList.add("show"));
}

function showLevelCompletePopup(nextLevel) {
  const popup = document.getElementById("result-popup");
  const icon = document.getElementById("popup-icon");
  const title = document.getElementById("popup-title");
  const message = document.getElementById("popup-message");

  const nextBtn = document.getElementById("popup-next-btn");
  const replayBtn = document.getElementById("popup-replay-btn");

  isLevelCompletePopup = true;
  pendingNextLevel = nextLevel;

  const currentMeta = getLevelMeta(level);
  const nextMeta = getLevelMeta(nextLevel);

  if (icon) icon.textContent = "🏁";
  if (title) {
    title.textContent = `${currentMeta.icon} Hoàn thành level!`;
    title.style.color = "#22c55e";
  }
  if (message) {
    message.textContent = `Tổng điểm: ${score} ⭐. `;
  }

  if (replayBtn) {
    replayBtn.style.display = "block";
    replayBtn.textContent = "Chơi lại level";
    replayBtn.onclick = async () => {
      popup.classList.remove("show");
      setTimeout(() => popup.classList.add("hidden"), 200);
      try {
        await restartCurrentLevel();
      } catch (err) {
        console.error(err);
        showErrorPopup(err?.message || "Không thể chơi lại level");
      }
    };
  }

  if (nextBtn) {
    nextBtn.style.display = "block";
    nextBtn.textContent = `${nextMeta.icon} Level mới`;
    nextBtn.onclick = async () => {
      popup.classList.remove("show");
      setTimeout(() => popup.classList.add("hidden"), 200);
      window.location.href = `./level_select.html?gameId=${encodeURIComponent(
        gameId
      )}&level=${encodeURIComponent(pendingNextLevel)}`;
    };
  }

  popup.classList.remove("hidden");
  requestAnimationFrame(() => popup.classList.add("show"));
}

function showLevelNotPassedPopup(correctRounds, totalRounds) {
  const popup = document.getElementById("result-popup");
  const icon = document.getElementById("popup-icon");
  const title = document.getElementById("popup-title");
  const message = document.getElementById("popup-message");

  const nextBtn = document.getElementById("popup-next-btn");
  const replayBtn = document.getElementById("popup-replay-btn");

  if (icon) icon.textContent = "🔁";
  if (title) {
    title.textContent = "Chưa đạt để qua level";
    title.style.color = "#ef4444";
  }

  if (nextBtn) nextBtn.style.display = "none";

  if (replayBtn) {
    replayBtn.style.display = "block";
    replayBtn.textContent = "Chơi lại level";
    replayBtn.onclick = async () => {
      popup.classList.remove("show");
      popup.classList.add("hidden");
      await restartCurrentLevel();
    };
  }

  popup.classList.remove("hidden");
  requestAnimationFrame(() => popup.classList.add("show"));
}

function showLevelFinishedPopupGoSelectLevel() {
  const popup = document.getElementById("result-popup");
  const icon = document.getElementById("popup-icon");
  const title = document.getElementById("popup-title");
  const message = document.getElementById("popup-message");

  const nextBtn = document.getElementById("popup-next-btn");
  const replayBtn = document.getElementById("popup-replay-btn");

  const currentMeta = getLevelMeta(level);

  if (icon) icon.textContent = "🏁";
  if (title) {
    title.textContent = `${currentMeta.icon} Hoàn thành level!`;
    title.style.color = "#22c55e";
  }
  if (message) {
    message.textContent = `Bạn đã hoàn thành level". Tổng điểm: ${score} ⭐`;
  }

  // Ẩn nút chơi lại (tuỳ bạn)
  if (replayBtn) replayBtn.style.display = "none";

  if (nextBtn) {
    nextBtn.style.display = "block";
    nextBtn.textContent = "Về chọn level";
    nextBtn.onclick = () => {
      // đóng popup cho gọn
      popup.classList.remove("show");
      setTimeout(() => popup.classList.add("hidden"), 150);

      // điều hướng
      window.location.href = "./level_select.html";
    };
  }

  popup.classList.remove("hidden");
  requestAnimationFrame(() => popup.classList.add("show"));
}

function showErrorPopup(text) {
  const popup = document.getElementById("result-popup");
  const icon = document.getElementById("popup-icon");
  const title = document.getElementById("popup-title");
  const message = document.getElementById("popup-message");
  const nextBtn = document.getElementById("popup-next-btn");
  const replayBtn = document.getElementById("popup-replay-btn");

  if (icon) icon.textContent = "⚠️";
  if (title) {
    title.textContent = "Có lỗi xảy ra";
    title.style.color = "#ef4444";
  }
  if (message) message.textContent = text;

  if (replayBtn) replayBtn.style.display = "none";
  if (nextBtn) {
    nextBtn.style.display = "block";
    nextBtn.textContent = "Về menu";
    nextBtn.onclick = () => {
      popup.classList.add("hidden");
      window.location.href = "./select_game.html";
    };
  }

  popup.classList.remove("hidden");
  requestAnimationFrame(() => popup.classList.add("show"));
}

function closePopupAndReplay() {
  const popup = document.getElementById("result-popup");
  popup.classList.remove("show");
  setTimeout(() => popup.classList.add("hidden"), 200);
  initializeRoundRetry();
  speak("Chơi lại!");
}

async function startLevel(newLevel) {
  level = newLevel;

  const res = await fetch(`/games/start-dynamic/${gameId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: user.user_id, level }),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Lỗi khởi động level mới");
  }

  const data = await res.json();
  sessionId = data.session_id;
  questions = data.questions || [];

  maxErrors = data.max_errors || 3;

  learningCards = data.learning_cards || {};
  const normalizedLearningCards = {};
  for (const key in learningCards) {
    if (Object.prototype.hasOwnProperty.call(learningCards, key)) {
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
    "vui vẻ": 0,
  };
  learnedEmotions = [];

  if (!questions.length) throw new Error("Level mới không có câu hỏi");

  remainingQuestions = [...questions];
  roundIndex = 0;
  score = 0;
  localResults = [];
  endLevelSent = false;
  roundResults = [];

  const selected = pickQuestionsForCurrentLevelUnique({
    uniqueName: true,
    uniqueEmotion: true,
  });
  if (!selected.length) throw new Error("Không đủ câu hỏi cho round");

  gameState.characters = selected.map((q) => ({
    id: q.question_id,
    name: q.correct_answer,
    emotion: q.emotion || "",
    image: resolveImagePath(q.media_path),
  }));
  gameState.shuffledCharacters = shuffleArray(gameState.characters);

  initializeRound();
}

async function restartCurrentLevel() {
  roundIndex = 0;
  score = 0;
  localResults = [];
  endLevelSent = false;
  learnedEmotions = [];
  roundResults = [];
  const res = await fetch(`/games/start-dynamic/${gameId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: user.user_id, level }),
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Lỗi khởi động lại level");
  }

  const data = await res.json();
  sessionId = data.session_id;
  questions = data.questions || [];

  maxErrors = data.max_errors || 3;

  learningCards = data.learning_cards || {};
  const normalizedLearningCards = {};
  for (const key in learningCards) {
    if (Object.prototype.hasOwnProperty.call(learningCards, key)) {
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
    "vui vẻ": 0,
  };

  if (!questions.length) throw new Error("Level này không có câu hỏi");

  remainingQuestions = [...questions];

  const selected = pickQuestionsForCurrentLevelUnique({
    uniqueName: true,
    uniqueEmotion: true,
  });
  if (!selected.length) throw new Error("Không đủ câu hỏi cho round");

  gameState.characters = selected.map((q) => ({
    id: q.question_id,
    name: q.correct_answer,
    emotion: q.emotion || "",
    image: resolveImagePath(q.media_path),
  }));
  gameState.shuffledCharacters = shuffleArray(gameState.characters);

  initializeRound();
}

async function closePopupAndNext() {
  const popup = document.getElementById("result-popup");
  popup.classList.remove("show");
  popup.classList.add("hidden");

  roundIndex++;
  if (roundIndex >= TOTAL_ROUNDS) {
    await sendFinalResults();
    const totalRounds = TOTAL_ROUNDS;
    const correctRounds = roundResults.filter(Boolean).length;
    const passPercent = (correctRounds / totalRounds) * 100;

    if (passPercent < 70) {
      showLevelNotPassedPopup(correctRounds, totalRounds);
      return;
    }
    const nextLevel = level + 1;

    if (gameInfo?.num_levels && nextLevel > gameInfo.num_levels) {
      showLevelFinishedPopupGoSelectLevel();
      return;
    }
    showLevelCompletePopup(nextLevel);
    return;
  }

  const nextQuestions = pickQuestionsForCurrentLevelUnique({
    uniqueName: true,
    uniqueEmotion: true,
  });
  if (nextQuestions.length === 0) {
    alert("Không đủ câu hỏi cho round tiếp theo của level này.");
    await sendFinalResults();
    window.location.href = "./select_game.html";
    return;
  }

  gameState.characters = nextQuestions.map((q) => ({
    id: q.question_id,
    name: q.correct_answer,
    emotion: q.emotion || "",
    image: resolveImagePath(q.media_path),
  }));
  gameState.shuffledCharacters = shuffleArray(gameState.characters);

  initializeRound();
  speak("Câu hỏi mới!");
}

function retryAnswer() {
  gameState.submitted = false;
  gameState.retryUsed = true;
  gameState.results = {};
  renderGame();
  speak("Hãy thử lại nhé!");
}

function resetGame() {
  initializeRound();
}

function nextQuestion() {
  closePopupAndNext();
}

function backToMenu() {
  document.getElementById("game-screen").classList.add("hidden");
  document.getElementById("menu-screen").classList.remove("hidden");
  window.speechSynthesis.cancel();
}
document.getElementById("popup-close-btn").onclick = () => {
  const popup = document.getElementById("result-popup");
  popup.classList.remove("show");
  setTimeout(() => popup.classList.add("hidden"), 200);
  window.speechSynthesis.cancel();
};
