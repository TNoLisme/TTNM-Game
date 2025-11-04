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
        emotion: "happy"
    },
    // Một số nội dung khác (ảnh hoặc video) cho các cảm xúc còn lại
    {
        id: 2,
        type: "video",
        src: "../../assets/videos/fear.mp4",
        caption: "Video cảm xúc sợ hãi",
        emotion: "fear"
    },
    {
        id: 3,
        type: "video",
        src: "../../assets/videos/sad.mp4",
        caption: "Video cảm xúc buồn",
        emotion: "sad"
    },
    {
        id: 4,
        type: "video",
        src: "../../assets/videos/surprise.mp4",
        caption: "Video cảm xúc ngạc nhiên",
        emotion: "surprise"
    },
    {
        id: 5,
        type: "video",
        src: "../../assets/videos/disgust.mp4",
        caption: "Video cảm xúc ghê tởm",
        emotion: "disgust"
    },
    {
        id: 6,
        type: "video",
        src: "../../assets/videos/angry.mp4",
        caption: "Video cảm xúc tức giận",
        emotion: "angry"
    },

];

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

// ================ MEDIA CAROUSEL ================

function renderStage(item) {
    if (!stage) return;
    // Xóa nội dung cũ
    stage.innerHTML = "";

    // Tạo node tùy theo loại
    if (item.type === "video") {
        const fig = document.createElement("figure");
        fig.className = "w-full h-full grid place-items-center m-0";

        const video = document.createElement("video");
        video.className = "media-carousel__video";
        video.setAttribute("controls", "controls");
        video.setAttribute("preload", "metadata");

        const src = document.createElement("source");
        src.src = item.src;
        src.type = "video/mp4"; // có thể thay đổi nếu bạn dùng webm/ogg
        video.appendChild(src);

        const cap = document.createElement("figcaption");
        cap.className = "media-carousel__caption";
        cap.textContent = item.caption || "";

        fig.appendChild(video);
        fig.appendChild(cap);
        stage.appendChild(fig);
    } else {
        // image
        const fig = document.createElement("figure");
        fig.className = "w-full h-full grid place-items-center m-0";

        const img = document.createElement("img");
        img.src = item.src;
        img.alt = item.caption || "Hình minh họa cảm xúc";
        img.style.width = "100%";
        img.style.height = "100%";
        img.style.objectFit = "cover";
        img.style.borderRadius = "18px";

        const cap = document.createElement("figcaption");
        cap.className = "media-carousel__caption";
        cap.textContent = item.caption || "";

        fig.appendChild(img);
        fig.appendChild(cap);
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
        });
        dotsWrap.appendChild(b);
    });
}

function updateCarousel() {
    // đảm bảo current nằm trong khoảng
    if (filtered.length === 0) {
        stage.innerHTML = `<div class="media-carousel__caption">Không có nội dung cho cảm xúc này.</div>`;
        dotsWrap.innerHTML = "";
        return;
    }
    current = (current + filtered.length) % filtered.length;
    renderStage(filtered[current]);
    renderDots();
}

function goPrev() {
    current--;
    updateCarousel();
}

function goNext() {
    current++;
    updateCarousel();
}

// ================ LỌC THEO CẢM XÚC ================
function applyFilter(emotion /* string | null */ ) {
    currentEmotion = emotion;
    if (!emotion) filtered = [...allItems];
    else filtered = allItems.filter(x => (x.emotion || "").toLowerCase() === emotion.toLowerCase());

    current = 0;
    updateEmotionUI();
    if (mediaOverlayLabel) {
        if (!emotion) mediaOverlayLabel.textContent = "";
        else {
            const map = {
                happy: "vui",
                sad: "buồn",
                angry: "tức giận",
                fear: "sợ hãi",
                surprise: "ngạc nhiên",
                disgust: "ghê tởm",
                neutral: "trung tính"
            };
            const phrase = map[(emotion || "").toLowerCase()] || (emotion || "");
            mediaOverlayLabel.textContent = `Cảm xúc ${phrase}`;
        }
    }
    updateCarousel();
}

function updateEmotionUI() {
    // set active cho nút emotion-pill
    $$(".emotion-pill", emotionList).forEach(btn => {
        const e = btn.getAttribute("data-emotion");
        if (!currentEmotion && !e) {
            btn.classList.add("active");
        } else if (currentEmotion && e && e.toLowerCase() === currentEmotion.toLowerCase()) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });
}

function initEmotionFilters() {
    if (!emotionList) return;
    // Thêm một nút "Tất cả" ở đầu nếu muốn
    // (Bỏ comment nếu cần)
    // const li = document.createElement("li");
    // li.innerHTML = `<button class="emotion-pill" data-emotion="">Tất cả</button>`;
    // emotionList.prepend(li);

    emotionList.addEventListener("click", (ev) => {
        const btn = ev.target.closest(".emotion-pill");
        if (!btn) return;
        const emotion = btn.getAttribute("data-emotion") || null;
        applyFilter(emotion);
    });
}

// ================ TẢI DỮ LIỆU MEDIA ================
async function fetchLessonsOrFallback() {
    try {
        const res = await fetch(`${apiBase}/lessons/`, {
            method: "GET"
        });
        if (!res.ok) throw new Error("API /lessons trả lỗi");
        const data = await res.json();

        // Chuẩn hóa về {type, src, caption, emotion}
        // Giả định backend trả: {lesson_id, title, video_url, image_url?, emotion?}
        const items = [];
        for (const x of data) {
            if (x.video_url) {
                items.push({
                    id: `v-${x.lesson_id}`,
                    type: "video",
                    src: x.video_url,
                    caption: x.title || "",
                    emotion: (x.emotion || "neutral")
                });
            }
            if (x.image_url) {
                items.push({
                    id: `i-${x.lesson_id}`,
                    type: "image",
                    src: x.image_url,
                    caption: x.title || "",
                    emotion: (x.emotion || "neutral")
                });
            }
        }
        return items.length ? items : FALLBACK_MEDIA;
    } catch (e) {
        // Không có API → dùng fallback
        return FALLBACK_MEDIA;
    }
}

// ================ KHỞI TẠO ================
async function init() {
    initEmotionFilters();

    allItems = await fetchLessonsOrFallback();
    // Mặc định hiển thị tất cả
    filtered = [...allItems];
    if (mediaOverlayLabel) mediaOverlayLabel.textContent = "";
    updateCarousel();

    // Gán sự kiện prev/next
    if (btnPrev) btnPrev.addEventListener("click", goPrev);
    if (btnNext) btnNext.addEventListener("click", goNext);

    // Hỗ trợ phím mũi tên trái/phải
    window.addEventListener("keydown", (e) => {
        if (e.key === "ArrowLeft") goPrev();
        if (e.key === "ArrowRight") goNext();
    });
}

document.addEventListener("DOMContentLoaded", init);