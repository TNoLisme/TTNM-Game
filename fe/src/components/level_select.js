// Dữ liệu cấu hình giao diện Levels
const levelsConfig = [
  { num: 1, icon: "😊", name: "Dễ" },
  { num: 2, icon: "❤️", name: "Vui" },
  { num: 3, icon: "⭐", name: "Hay" },
  { num: 4, icon: "✨", name: "Giỏi" },
  { num: 5, icon: "☀️", name: "Xuất sắc" },
  { num: 6, icon: "🌸", name: "Tuyệt vời" },
  { num: 7, icon: "🌈", name: "Siêu đẳng" },
  { num: 8, icon: "🎮", name: "Cao thủ" },
];

// Cấu hình 6 cảm xúc cho game "Thử thách cảm xúc" (game_cv_2)
const EMOTION_OPTIONS = [
  { key: "vui", icon: "😊", name: "Vui vẻ" },
  { key: "buồn", icon: "😢", name: "Buồn bã" },
  { key: "ngạc nhiên", icon: "😲", name: "Ngạc nhiên" },
  { key: "tức giận", icon: "😠", name: "Tức giận" },
  { key: "sợ hãi", icon: "😨", name: "Sợ hãi" },
  { key: "ghê tởm", icon: "🤢", name: "Ghê tởm" },
];

// gameId trong DB của game "Thử thách cảm xúc" (game_cv_2)
const GAME_CV_REQUEST_ID = "61f5e09e-eefa-44c1-86e1-87dfceac3b8e".toLowerCase();

if (!window.egInlineConfirm) {
  window.egEnsureInlineConfirmModal = function () {
    if (document.getElementById("eg-confirm-overlay")) return;

    if (!document.getElementById("eg-confirm-style")) {
      const style = document.createElement("style");
      style.id = "eg-confirm-style";
      style.textContent = `
                .eg-confirm-overlay{position:fixed;inset:0;background:rgba(15,23,42,.55);backdrop-filter:blur(6px);display:none;align-items:center;justify-content:center;z-index:9999;padding:20px;}
                .eg-confirm-overlay.is-open{display:flex;}
                .eg-confirm-modal{width:min(520px,92vw);background:#fff;border-radius:16px;box-shadow:0 24px 60px rgba(15,23,42,.35);border:1px solid rgba(148,163,184,.35);overflow:hidden;}
                .eg-confirm-header{padding:16px 18px;background:linear-gradient(135deg,rgba(25,118,210,.12),rgba(59,130,246,.08));font-weight:800;color:#0b3c7d;}
                .eg-confirm-body{padding:16px 18px;color:#0f172a;line-height:1.5;white-space:pre-line;}
                .eg-confirm-actions{display:flex;gap:10px;justify-content:flex-end;padding:14px 18px;background:#f8fafc;border-top:1px solid rgba(148,163,184,.28);}
                .eg-confirm-btn{border:0;border-radius:999px;padding:10px 16px;font-weight:700;cursor:pointer;}
                .eg-confirm-btn.cancel{background:#e2e8f0;color:#0f172a;}
                .eg-confirm-btn.ok{background:linear-gradient(135deg,#2563eb,#3b82f6);color:#fff;}
                .eg-confirm-btn:active{transform:scale(.98);}
            `;
      document.head.appendChild(style);
    }

    const overlay = document.createElement("div");
    overlay.id = "eg-confirm-overlay";
    overlay.className = "eg-confirm-overlay";
    overlay.innerHTML = `
            <div class="eg-confirm-modal" role="dialog" aria-modal="true" aria-labelledby="eg-confirm-title">
                <div class="eg-confirm-header" id="eg-confirm-title"></div>
                <div class="eg-confirm-body" id="eg-confirm-message"></div>
                <div class="eg-confirm-actions">
                    <button type="button" class="eg-confirm-btn cancel" id="eg-confirm-cancel"></button>
                    <button type="button" class="eg-confirm-btn ok" id="eg-confirm-ok"></button>
                </div>
            </div>
        `;
    document.body.appendChild(overlay);
  };

  window.egInlineConfirm = function (message, title, okText, cancelText) {
    window.egEnsureInlineConfirmModal();

    const overlay = document.getElementById("eg-confirm-overlay");
    const titleEl = document.getElementById("eg-confirm-title");
    const msgEl = document.getElementById("eg-confirm-message");
    const okBtn = document.getElementById("eg-confirm-ok");
    const cancelBtn = document.getElementById("eg-confirm-cancel");

    if (!overlay || !titleEl || !msgEl || !okBtn || !cancelBtn) {
      return Promise.resolve(confirm(message));
    }

    titleEl.textContent = title || "Xác nhận";
    msgEl.textContent = message || "";
    okBtn.textContent = okText || "OK";
    cancelBtn.textContent = cancelText || "Hủy";

    return new Promise((resolve) => {
      const close = (result) => {
        overlay.classList.remove("is-open");
        okBtn.onclick = null;
        cancelBtn.onclick = null;
        overlay.onclick = null;
        document.removeEventListener("keydown", onKeyDown);
        resolve(result);
      };

      const onKeyDown = (e) => {
        if (e.key === "Escape") close(false);
      };

      okBtn.onclick = () => close(true);
      cancelBtn.onclick = () => close(false);
      overlay.onclick = (e) => {
        if (e.target === overlay) close(false);
      };
      document.addEventListener("keydown", onKeyDown);

      overlay.classList.add("is-open");
      cancelBtn.focus();
    });
  };
}

function getGameHtmlFile(gameId) {
  const map = {
    "3bcb2108-721c-4a15-a585-31f3084ed000": "./recognize_emotion.html",
    "9fd1e82c-d831-4f56-b062-e6c16bcd8d0a": "./game_click_2.html",
    "08bbffbf-d147-4556-bccb-b7621cafbf15": "./game_click_3.html",
    "aacaf79e-e15e-42a9-a3d1-a522720d919b": "./game_click_4.html",
    "e05909f3-3dee-42a6-9a75-fd985b1bdf47": "./gameCV.html",
    "61f5e09e-eefa-44c1-86e1-87dfceac3b8e": "./game_cv_2.html",
  };
  if (!gameId) return null;
  return map[gameId.toLowerCase()] || null;
}

document.addEventListener("DOMContentLoaded", async () => {
  // 1. Lấy thông tin từ URL và LocalStorage
  const urlParams = new URLSearchParams(window.location.search);
  const gameId = urlParams.get("gameId");
  const user = JSON.parse(localStorage.getItem("currentUser"));

  const isCvRequestGame = gameId && gameId.toLowerCase() === GAME_CV_REQUEST_ID;

  console.log("Level Select - gameId:", gameId, "user:", user);

  if (!gameId || !user) {
    const goBack = () => {
      window.location.href = "./select_game.html";
    };
    if (window.egModal && typeof window.egModal.alert === "function") {
      window.egModal
        .alert("Thiếu thông tin game hoặc người dùng", "Thiếu thông tin")
        .then(goBack);
    } else {
      alert("Thiếu thông tin game hoặc người dùng");
      goBack();
    }
    return;
  }

  // 2. Khởi tạo biến trạng thái
  let unlockedLevel = 1;
  let selectedLevel = null;
  let selectedEmotion = null;
  let gameInfo = {};
  let emotionScores = {};

  // 3. Fetch dữ liệu từ API
  try {
    const gameRes = await fetch(`/games/${gameId}`);
    if (!gameRes.ok) throw new Error("Không thể tải thông tin game");
    gameInfo = await gameRes.json();

    // Cập nhật tiêu đề theo tên game trong DB
    const headerTitle = document.querySelector(".header h1");
    if (headerTitle && gameInfo.name)
      headerTitle.textContent = `🎮 ${gameInfo.name} 🎮`;

    if (isCvRequestGame) {
      // Game "Thử thách cảm xúc": lấy điểm cao nhất cho từng cảm xúc
      const scoresRes = await fetch(
        `/games/cv/emotion-scores?user_id=${user.user_id}`
      );
      if (scoresRes.ok) {
        const scoresData = await scoresRes.json();
        emotionScores = scoresData.scores || {};
      }

      const subtitle = document.querySelector(".subtitle");
      if (subtitle) {
        subtitle.textContent = "Chọn một cảm xúc để chơi";
      }

      // Game CV không dùng level, ẩn badge "Level đã mở"
      const progressBadge = document.querySelector(".progress-badge");
      if (progressBadge) {
        progressBadge.style.display = "none";
      }
    } else {
      // Các game còn lại: dùng tiến trình level như cũ
      const progressRes = await fetch(
        `/games/progress/${gameId}?user_id=${user.user_id}`
      );
      if (progressRes.ok) {
        const progressData = await progressRes.json();
        if (progressData) {
          unlockedLevel = progressData.level || 1;
        }
      }
    }
  } catch (err) {
    console.error("Lỗi tải dữ liệu:", err);
    // Fallback nếu lỗi API: mặc định level 1
    unlockedLevel = 1;
  }

  // 4. Render giao diện
  const levelGrid = document.getElementById("levelGrid");
  const unlockedCountElem = document.getElementById("unlockedCount");
  const container = document.querySelector(".container");
  const levelContainer = document.querySelector(".level-container");
  const header = document.querySelector(".header");

  const startButton = document.getElementById("startButton");
  const selectedMessage = document.getElementById("selectedMessage");
  const selectedLevelNum = document.getElementById("selectedLevelNum");

  // Cập nhật số lượng level đã mở trên UI (chỉ dùng cho game theo level)
  if (!isCvRequestGame && unlockedCountElem)
    unlockedCountElem.textContent = unlockedLevel;

  // Hàm tạo nút level (cho các game theo level thông thường)
  function renderLevels() {
    if (levelGrid) {
      levelGrid.classList.remove("emotion-grid");
    }
    levelGrid.innerHTML = ""; // Xóa nội dung cũ

    levelsConfig.forEach((level) => {
      const button = document.createElement("div");
      button.className = `level-button level-${level.num}`;
      button.dataset.level = level.num;

      const isUnlocked = level.num <= unlockedLevel;
      const isCompleted = level.num < unlockedLevel;

      // Xử lý trạng thái khóa/mở
      if (!isUnlocked) {
        button.classList.add("locked");
      }

      // Badge hoàn thành
      if (isCompleted) {
        const badge = document.createElement("div");
        badge.className = "completed-badge";
        badge.innerHTML = "🏆";
        button.appendChild(badge);
      }

      // Icon
      const icon = document.createElement("div");
      icon.className = "level-icon";
      icon.textContent = level.icon;
      button.appendChild(icon);

      // Nếu đang khóa: icon vẫn là emoji nhưng mờ đi, thêm badge khóa nhỏ ở góc
      if (!isUnlocked) {
        const lockBadge = document.createElement("div");
        lockBadge.className = "lock-badge";
        lockBadge.textContent = "🔒";
        button.appendChild(lockBadge);
      }

      // Số level
      const number = document.createElement("div");
      number.className = "level-number";
      number.textContent = level.num;
      button.appendChild(number);

      // Tên level
      const name = document.createElement("div");
      name.className = "level-name";
      name.textContent = isUnlocked ? level.name : "Đã khóa";
      button.appendChild(name);

      // Sự kiện click chọn level
      if (isUnlocked) {
        button.addEventListener("click", () => selectLevel(level.num));
      }

      levelGrid.appendChild(button);
    });
  }

  // Hàm tạo 6 ô cảm xúc cho game "Thử thách cảm xúc"
  function renderEmotionTiles() {
    if (!levelGrid) return;
    levelGrid.classList.add("emotion-grid");
    levelGrid.innerHTML = "";

    EMOTION_OPTIONS.forEach((emotion) => {
      const button = document.createElement("div");
      // Dùng thêm class emotion-tile để style riêng cho game Thử thách cảm xúc
      button.className = "level-button emotion-tile";
      button.dataset.emotion = emotion.key;

      const rawScore =
        typeof emotionScores[emotion.key] === "number"
          ? emotionScores[emotion.key]
          : 0;
      const score = Math.max(0, Math.min(100, rawScore));
      const displayPercent = Math.round(score);

      // Dùng biến CSS để đổ màu theo % (không dùng hiệu ứng "nước")
      button.style.setProperty("--score", `${score}%`);
      if (displayPercent >= 100) {
        button.classList.add("is-full");
      }

      // Nội dung phía trên nước
      const content = document.createElement("div");
      content.className = "level-content";

      const icon = document.createElement("div");
      icon.className = "level-icon";
      icon.textContent = emotion.icon;
      content.appendChild(icon);

      const name = document.createElement("div");
      name.className = "level-name";
      name.textContent = emotion.name;
      content.appendChild(name);

      button.appendChild(content);

      // Hiển thị điểm cao nhất
      const scoreBadge = document.createElement("div");
      scoreBadge.className = "score-display";
      scoreBadge.textContent = `${displayPercent}%`;

      button.appendChild(scoreBadge);

      // Chọn cảm xúc
      button.addEventListener("click", () => selectEmotion(emotion.key));

      levelGrid.appendChild(button);
    });
  }

  // Hàm xử lý khi chọn level
  function selectLevel(levelNum) {
    selectedLevel = levelNum;

    // Update visual selected state
    document.querySelectorAll(".level-button").forEach((btn) => {
      if (parseInt(btn.dataset.level) === selectedLevel) {
        btn.classList.add("selected");
      } else {
        btn.classList.remove("selected");
      }
    });

    // Update Start Button state
    startButton.disabled = false;
    startButton.classList.remove("disabled");
    startButton.textContent = `🚀 Bắt Đầu Cấp ${selectedLevel}!`;

    // Show message
    selectedMessage.classList.remove("hidden");
    selectedLevelNum.textContent = selectedLevel;
  }

  // Hàm xử lý khi chọn cảm xúc cho game_cv_2
  function selectEmotion(emotionKey) {
    selectedEmotion = emotionKey;

    // Cập nhật trạng thái selected trên UI
    document.querySelectorAll(".level-button").forEach((btn) => {
      if (btn.dataset.emotion === emotionKey) {
        btn.classList.add("selected");
      } else {
        btn.classList.remove("selected");
      }
    });

    // Kích hoạt nút bắt đầu
    startButton.disabled = false;
    startButton.classList.remove("disabled");

    const emotionConfig = EMOTION_OPTIONS.find((e) => e.key === emotionKey);
    const label = emotionConfig ? emotionConfig.name : emotionKey;
    startButton.textContent = `🚀 Bắt đầu luyện ${label}`;

    // Thông điệp đã chọn
    if (selectedMessage) {
      selectedMessage.classList.remove("hidden");
      selectedLevelNum.textContent = label;
    }
  }

  // 5. Xử lý nút Bắt đầu Game (ĐÃ SỬA: CHỈ CHUYỂN TRANG, KHÔNG GỌI API)
  startButton.addEventListener("click", () => {
    // Lấy đường dẫn file HTML tương ứng
    const gameFile = getGameHtmlFile(gameId);
    if (!gameFile) {
      const back = () => (window.location.href = "./select_game.html");
      if (window.egModal && typeof window.egModal.alert === "function") {
        window.egModal
          .alert(
            "Không xác định được trang game tương ứng. Vui lòng chọn lại game.",
            "Lỗi"
          )
          .then(back);
      } else {
        alert(
          "Không xác định được trang game tương ứng. Vui lòng chọn lại game."
        );
        back();
      }
      return;
    }

    // Game "Thử thách cảm xúc": cần chọn cảm xúc
    if (isCvRequestGame) {
      if (!selectedEmotion) return;

      startButton.textContent = "🚀 Đang vào game...";
      const emotionParam = encodeURIComponent(selectedEmotion);

      window.location.href = `${gameFile}?gameId=${gameId}&emotion=${emotionParam}`;
      return;
    }

    // Các game khác: chọn level như cũ
    if (!selectedLevel) return;

    // Hiệu ứng bấm nút
    startButton.textContent = "🚀 Đang vào game...";

    // Chuyển hướng ngay lập tức kèm tham số
    // recognize_emotion.js sẽ tự lo việc gọi API start
    window.location.href = `${gameFile}?level=${selectedLevel}&gameId=${gameId}`;
  });

  // 6. Xử lý Đăng xuất
  document
    .getElementById("logout-button")
    ?.addEventListener("click", async () => {
      const doLogout = () => {
        localStorage.removeItem("currentUser");
        window.location.href = "/src/pages/login.html";
      };

      if (window.egModal && typeof window.egModal.confirm === "function") {
        window.egModal
          .confirm(
            "Bạn có chắc chắn muốn đăng xuất không?",
            "Xác nhận đăng xuất",
            "Đăng xuất",
            "Hủy"
          )
          .then((ok) => {
            if (!ok) return;
            doLogout();
          });
        return;
      }

      const ok = await window.egInlineConfirm(
        "Bạn có chắc chắn muốn đăng xuất không?",
        "Xác nhận đăng xuất",
        "Đăng xuất",
        "Hủy"
      );
      if (!ok) return;
      doLogout();
    });

  // Khởi chạy render lần đầu
  if (isCvRequestGame) {
    if (container) {
      container.classList.add("cv2-mode");
    }
    if (header) {
      header.classList.add("cv2-mode");
    }
    if (levelContainer) {
      levelContainer.classList.add("cv2-mode");
    }

    const levelTitle = document.querySelector(".level-title");
    if (levelTitle) levelTitle.textContent = "Chọn cảm xúc";

    if (startButton) startButton.textContent = "👆 Chọn cảm xúc để chơi";

    // Đổi nội dung thông báo đã chọn cho đúng ngữ cảnh cảm xúc
    if (selectedMessage) {
      selectedMessage.innerHTML =
        '✨ Bạn đã chọn cảm xúc <span id="selectedLevelNum"></span>! ✨';
    }

    renderEmotionTiles();
  } else {
    if (container) {
      container.classList.remove("cv2-mode");
    }
    if (header) {
      header.classList.remove("cv2-mode");
    }
    if (levelContainer) {
      levelContainer.classList.remove("cv2-mode");
    }
    renderLevels();
  }
});
