// frontend/js/learn.js

// ================ CẤU HÌNH ================
export const apiBase = "http://127.0.0.1:8000"; // đổi nếu backend khác

// Nếu có API /lessons trả về danh sách bài (ảnh/video), file sẽ ưu tiên dùng API.
// Nếu không có, dùng fallback DEMO bên dưới.
const FALLBACK_MEDIA = [
  // Video cho cảm xúc VUI
  {
    id: 1,
    type: "video",
    src: "../../assets/videos/happy.mp4",
    caption: "Video cảm xúc Vui",
    emotion: "happy",
  },
  // Một số nội dung khác (ảnh hoặc video) cho các cảm xúc còn lại
  {
    id: 2,
    type: "video",
    src: "../../assets/videos/fear.mp4",
    caption: "Video cảm xúc sợ hãi",
    emotion: "fear",
  },
  {
    id: 3,
    type: "video",
    src: "../../assets/videos/sad.mp4",
    caption: "Video cảm xúc buồn",
    emotion: "sad",
  },
  {
    id: 4,
    type: "video",
    src: "../../assets/videos/surprise.mp4",
    caption: "Video cảm xúc ngạc nhiên",
    emotion: "surprise",
  },
  {
    id: 5,
    type: "video",
    src: "../../assets/videos/disgust.mp4",
    caption: "Video cảm xúc ghê tởm",
    emotion: "disgust",
  },
  {
    id: 6,
    type: "video",
    src: "../../assets/videos/angry.mp4",
    caption: "Video cảm xúc tức giận",
    emotion: "angry",
  },
];

// ================ TÌNH HUỐNG THEO CẢM XÚC ================
const SITUATIONS = {
  happy: {
    image: "../../assets/images/happy/situation_happy.png",
    text: "Lan được tặng một món quà bất ngờ nên Lan rất vui và mỉm cười.",
  },
  sad: {
    image: "../../assets/images/sad/situation_sad.png",
    text: "An đánh rơi kem rồi, nên An buồn và khóc.",
  },
  angry: {
    image: "../../assets/images/angry/situation_angry.png",
    text: "Nam bị bạn giật đồ chơi mà không xin phép nên Nam tức giận.",
  },
  fear: {
    image: "../../assets/images/fear/situation_fear.png",
    text: "Bé Mai đi lạc mẹ trong siêu thị nên cảm thấy rất sợ hãi.",
  },
  surprise: {
    image: "../../assets/images/surprise/situation_surprise.png",
    text: "Huy mở hộp quà ra và thấy món đồ chơi mình rất thích nên rất ngạc nhiên.",
  },
  disgust: {
    image: "../../assets/images/disgust/situation_disgust.png",
    text: "Minh ngửi thấy mùi rác thối nên cảm thấy rất ghê tởm.",
  },
};

function buildSituationItem(emotion) {
  const info = SITUATIONS[emotion];
  if (!info) return null;
  return {
    id: `situation-${emotion}`,
    type: "image",
    emotion: emotion,
    src: info.image,
    caption: info.text, // chỉ dùng cho panel dưới, không hiển thị trong figure nữa
  };
}

// ================ TRẠNG THÁI ================
let allItems = []; // Toàn bộ media (ảnh + video)
let filtered = []; // Media đã lọc theo emotion
let current = 0; // index hiện tại trong 'filtered'
let currentEmotion = null; // emotion đang lọc; null = tất cả

// ================ TRỢ GIÚP DOM ================
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

// Element chính
const stage = $(".media-carousel__stage");
const btnPrev = $('.media-carousel__nav[data-action="prev"]');
const btnNext = $('.media-carousel__nav[data-action="next"]');
const dotsWrap = $(".media-carousel__dots");
const emotionList = $("#emotion-list");
const mediaOverlayLabel = $(".media-carousel__label");
//const situationImage = document.getElementById("situation-image");
const situationText = document.getElementById("situation-text");
const situationAudioBtn = document.getElementById("situation-audio-btn");
const situationPanel = document.getElementById("situation-panel");

// ================ MEDIA CAROUSEL ================

function renderStage(item) {
  if (!stage) return;
  // Xóa nội dung cũ
  stage.innerHTML = "";

  // Trang 1: VIDEO (KHÔNG caption)
  if (item.type === "video") {
    const fig = document.createElement("figure");
    fig.className = "w-full h-full grid place-items-center m-0";

    const video = document.createElement("video");
    video.className = "media-carousel__video";
    video.setAttribute("controls", "controls");
    video.setAttribute("preload", "metadata");

    const src = document.createElement("source");
    src.src = item.src;
    src.type = "video/mp4";
    video.appendChild(src);

    fig.appendChild(video);
    stage.appendChild(fig);

    // Trang 2: ẢNH TÌNH HUỐNG (CHỈ ảnh, KHÔNG caption trong figure)
  } else if (item.type === "image") {
    const fig = document.createElement("figure");
    fig.className = "w-full h-full grid place-items-center m-0";

    const img = document.createElement("img");
    img.src = item.src;
    //img.alt = item.caption || "Hình minh họa cảm xúc";
    img.style.width = "100%";
    img.style.height = "100%";
    img.style.objectFit = "cover";
    img.style.borderRadius = "18px";

    fig.appendChild(img);
    stage.appendChild(fig);
  }
}

function renderDots() {
  if (!dotsWrap) return;
  dotsWrap.innerHTML = "";
  filtered.forEach((_, idx) => {
    const b = document.createElement("button");
    b.type = "button";
    b.setAttribute("aria-label", `Chuyển tới mục ${idx + 1}`);
    if (idx === current) b.setAttribute("aria-current", "true");
    b.addEventListener("click", () => {
      current = idx;
      updateCarousel();
      maybeSpeakSituationFromUserAction();
    });
    dotsWrap.appendChild(b);
  });
}

function renderSituationPanel() {
  if (!situationPanel || !situationText) return;

  //  Chưa chọn cảm xúc → ẩn panel, không text, không loa
  if (!currentEmotion) {
    situationPanel.style.display = "none";
    situationText.textContent =
      "Hãy chọn một cảm xúc ở bên trái để xem tình huống minh họa nhé.";
    return;
  }

  const key = currentEmotion.toLowerCase();
  const info = SITUATIONS[key];

  if (!info) {
    situationPanel.style.display = "none";
    situationText.textContent = "";
    return;
  }

  if (current === 0) {
    // 👉 Trang 1: VIDEO → chỉ có video, ẩn panel (không text, không loa)
    situationPanel.style.display = "none";
    situationText.textContent = "";
  } else {
    // 👉 Trang 2: ẢNH TÌNH HUỐNG → hiện panel với text + loa
    situationPanel.style.display = "flex"; // hoặc "" nếu CSS set sẵn display:flex
    situationText.textContent = info.text; // An đánh rơi kem rồi, nên An buồn và khóc.
  }
}

// Chỉ tự đọc khi người dùng thật sự thao tác (next/prev/chọn chấm)
function maybeSpeakSituationFromUserAction() {
  if (!situationPanel || !situationText) return;
  if (!currentEmotion) return;
  if (current === 0) return; // đang ở trang video thì không đọc

  const text = situationText.textContent.trim();
  if (!text) return;

  speakVietnamese(text);
}

function updateCarousel() {
  if (filtered.length === 0) {
    if (stage) {
      stage.innerHTML = `<div class="media-carousel__caption">Không có nội dung cho cảm xúc này.</div>`;
    }
    if (dotsWrap) dotsWrap.innerHTML = "";
    return;
  }
  current = (current + filtered.length) % filtered.length;
  const item = filtered[current];
  renderStage(item);
  renderSituationPanel(currentEmotion, current);
  renderDots();
}

function goPrev() {
  current--;
  updateCarousel();
  maybeSpeakSituationFromUserAction();
}

function goNext() {
  current++;
  updateCarousel();
  maybeSpeakSituationFromUserAction();
}

// ================ LỌC THEO CẢM XÚC ================
function applyFilter(emotion) {
  currentEmotion = emotion;
  if (!emotion) {
    filtered = [...allItems];
  } else {
    const e = emotion.toLowerCase();
    const media = allItems.filter((x) => (x.emotion || "").toLowerCase() === e);

    // chỉ lấy video đầu tiên cho mỗi cảm xúc (nếu có)
    const pages = [];
    const video = media.find((x) => x.type === "video");
    if (video) pages.push(video);

    // thêm TRANG 2: ảnh tình huống
    const situation = buildSituationItem(e);
    if (situation) pages.push(situation);

    filtered = pages;
  }

  current = 0;
  updateEmotionUI();

  if (mediaOverlayLabel) {
    const map = {
      happy: "vui",
      sad: "buồn",
      angry: "tức giận",
      fear: "sợ hãi",
      surprise: "ngạc nhiên",
      disgust: "ghê tởm",
      neutral: "trung tính",
    };
    mediaOverlayLabel.textContent = emotion
      ? `Cảm xúc ${map[emotion] || emotion}`
      : "";
  }

  updateCarousel();
}

// ================ UI EMOTION PILL ================
function updateEmotionUI() {
  $$(".emotion-pill", emotionList).forEach((btn) => {
    const e = btn.getAttribute("data-emotion");
    if (!currentEmotion && !e) {
      btn.classList.add("active");
    } else if (
      currentEmotion &&
      e &&
      e.toLowerCase() === currentEmotion.toLowerCase()
    ) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });
}

function initEmotionFilters() {
  if (!emotionList) return;

  emotionList.addEventListener("click", (ev) => {
    const btn = ev.target.closest(".emotion-pill");
    if (!btn) return;
    const emotion = btn.getAttribute("data-emotion") || null;
    applyFilter(emotion);
  });
}
function normalizeEmotion(raw) {
  if (!raw) return "neutral";

  const normalized = raw.trim().toLowerCase();

  const mapping = {
    vui: "happy",
    "vui vẻ": "happy",
    "vui ve": "happy",
    happy: "happy",
    buồn: "sad",
    "buồn bã": "sad",
    buon: "sad",
    "buon ba": "sad",
    sad: "sad",
    "tức giận": "angry",
    "tuc gian": "angry",
    angry: "angry",
    sợ: "fear",
    "sợ hãi": "fear",
    so: "fear",
    "so hai": "fear",
    fear: "fear",
    "ngạc nhiên": "surprise",
    "ngac nhien": "surprise",
    surprise: "surprise",
    "ghê tởm": "disgust",
    "ghe tom": "disgust",
    disgust: "disgust",
    "trung tính": "neutral",
    "trung tinh": "neutral",
    neutral: "neutral",
  };

  return mapping[normalized] || normalized;
}

function buildMediaUrl(path) {
  if (!path) return "";

  // Nếu path đã là absolute URL thì giữ nguyên
  if (/^https?:\/\//i.test(path)) return path;

  // Chuẩn hóa các đường dẫn trong DB đang lưu dạng "/fe/assets/..."
  if (/^\/fe\/assets\//i.test(path)) {
    return path.replace(/^\/fe\/assets\//i, "../../assets/");
  }

  // Nếu path bắt đầu bằng '/' hoặc '../' thì để nguyên để FE tự resolve
  if (/^(\.\.\/|\/)/.test(path)) return path;

  // Mặc định gắn với API base (dùng cho trường hợp backend trả relative)
  return `${apiBase}/${path}`;
}

function mapConceptsToMedia(concepts = []) {
  const items = [];

  for (const c of concepts) {
    const emotion = normalizeEmotion(c.emotion);
    const title = c.title || "";

    if (c.video_path) {
      items.push({
        id: `v-${c.concept_id || c.title || Math.random()}`,
        type: "video",
        src: buildMediaUrl(c.video_path),
        caption: title,
        emotion,
      });
    }

    if (c.image_path) {
      items.push({
        id: `i-${c.concept_id || c.title || Math.random()}`,
        type: "image",
        src: buildMediaUrl(c.image_path),
        caption: title,
        emotion,
      });
    }
  }

  return items;
}

// ================ TẢI DỮ LIỆU MEDIA ================
async function fetchLessonsOrFallback() {
  try {
    const res = await fetch(`${apiBase}/emotions/concepts/`, {
      method: "GET",
    });
    if (!res.ok) throw new Error("API emo/concepts trả lỗi");
    const data = await res.json();
    const concepts = data?.data?.concepts || [];
    const items = mapConceptsToMedia(concepts);

    return items.length ? items : FALLBACK_MEDIA;
  } catch (e) {
    console.error("❌ Không lấy được dữ liệu học từ DB, dùng fallback:", e);
    return FALLBACK_MEDIA;
  }
}

// ================ KHỞI TẠO ================
async function init() {
  initEmotionFilters();

  allItems = await fetchLessonsOrFallback();

  // Cho phép mở trực tiếp theo emotion từ query param (vd: ?emotion=happy)
  const params = new URLSearchParams(window.location.search);
  const initialEmotion = (params.get("emotion") || "happy").toLowerCase();
  currentEmotion = initialEmotion;
  applyFilter(initialEmotion);

  // ban đầu: chưa chọn cảm xúc → ẩn panel
  if (situationPanel) {
    situationPanel.style.display = "none";
  }

  // Gán sự kiện prev/next
  if (btnPrev) btnPrev.addEventListener("click", goPrev);
  if (btnNext) btnNext.addEventListener("click", goNext);

  // Hỗ trợ phím mũi tên trái/phải
  window.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") goPrev();
    if (e.key === "ArrowRight") goNext();
  });

  // 🔊 Nút phát giọng cho câu tình huống (panel dưới)
  if (situationAudioBtn) {
    situationAudioBtn.addEventListener("click", () => {
      const text = situationText ? situationText.textContent.trim() : "";
      if (text) {
        speakVietnamese(text);
      }
    });
  }
}

document.addEventListener("DOMContentLoaded", init);
async function speakVietnamese(text) {
  const res = await fetch("https://api.fpt.ai/hmi/tts/v5", {
    method: "POST",
    headers: {
      "api-key": "OXvPopJqIJgON0AglCE0KPkBvOovWSoy",
      speed: "",
      voice: "banmai",
    },
    body: text,
  });

  const data = await res.json();
  const audioUrl = data.async;
  const audio = new Audio(audioUrl);
  audio.play();
}
