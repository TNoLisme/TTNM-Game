// frontend/js/learn.js

// ================ CẤU HÌNH ================
export const apiBase = "http://127.0.0.1:8000"; // đổi nếu backend khác

// Nếu có API /lessons trả về danh sách bài (ảnh/video), file sẽ ưu tiên dùng API.
// Nếu không có, dùng fallback DEMO bên dưới.
const FALLBACK_MEDIA = [
    // Ví dụ ảnh
    {
        id: 1,
        type: "image",
        src: "../../assets/images/happykids.jpg",
        caption: "Vui - ảnh minh họa",
        emotion: "happy"
    },
    {
        id: 2,
        type: "image",
        src: "../../assets/images/smile.jpg",
        caption: "Buồn - ảnh minh họa",
        emotion: "sad"
    },
    // Ví dụ video
    {
        id: 3,
        type: "video",
        src: "../../assets/videos/happy.mp4",
        caption: "Giới thiệu cảm xúc",
        emotion: "neutral"
    },
    {
        id: 4,
        type: "video",
        src: "./videos/basic.mp4",
        caption: "Phân biệt vui/buồn/giận",
        emotion: "happy"
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
const sideToggle = $(".sidebar__toggle");
const emotionList = $("#emotion-list");

// ================ SIDEBAR COLLAPSE ================
// Thu nhỏ/mở rộng sidebar bằng cách thay đổi grid-template-columns của body.
// Lưu trạng thái vào localStorage để nhớ giữa các lần mở trang.

const SIDEBAR_WIDE = "280px 1fr";
const SIDEBAR_NARROW = "72px 1fr";
const STORE_KEY = "emogarden.sidebarCollapsed";

function applySidebarLayout(collapsed) {
    document.body.style.gridTemplateColumns = collapsed ? SIDEBAR_NARROW : SIDEBAR_WIDE;
    if (sideToggle) sideToggle.setAttribute("aria-expanded", String(!collapsed));
}

function loadSidebarState() {
    const v = localStorage.getItem(STORE_KEY);
    return v === "1";
}

function saveSidebarState(collapsed) {
    localStorage.setItem(STORE_KEY, collapsed ? "1" : "0");
}

function initSidebarToggle() {
    const collapsed = loadSidebarState();
    applySidebarLayout(collapsed);
    if (!sideToggle) return;
    sideToggle.addEventListener("click", () => {
        const now = !loadSidebarState();
        saveSidebarState(now);
        applySidebarLayout(now);
    });
}

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
    initSidebarToggle();
    initEmotionFilters();

    allItems = await fetchLessonsOrFallback();
    // Mặc định hiển thị tất cả
    filtered = [...allItems];
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