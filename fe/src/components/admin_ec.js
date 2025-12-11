// emotions.js - Quản lý Video Cảm xúc (Emotion Concepts)

import {
  API_URL,
  $,
  openModal,
  closeModal,
  showNotification,
} from "./admin.js";

// Data từ DB emotion_concepts
// mỗi item: { concept_id, emotion, level, title, video_path, ... }
let EMOTION_VIDEOS = [];

let currentVideoFile = null;
let editingConceptId = null;
let editingEmotionName = null;

// ====================== LOAD & RENDER ======================

async function loadEmotionVideos() {
  try {
    const res = await fetch(`${API_URL}/emotion-concepts`, {
      cache: "no-store",
    });
    const data = await res.json();

    if (!res.ok || data.status !== "success") {
      throw new Error(
        data.message || "Không tải được danh sách emotion concepts"
      );
    }

    EMOTION_VIDEOS = data.data || [];
    renderVideoGrid();
  } catch (err) {
    console.error(err);
    showNotification(`❌ ${err.message}`, "error");
  }
}

function renderVideoGrid() {
  const grid = $("emotions-grid");
  if (!grid) return;

  grid.innerHTML = EMOTION_VIDEOS.map((item) => {
    const videoPath = item.video_path || "";
    const hasVideo = !!videoPath;

    return `
      <div class="video-card" data-concept-id="${item.concept_id}">
        <div class="video-preview">
          ${
            hasVideo
              ? `<video src="${videoPath}?t=${Date.now()}" controls style="width:100%;height:200px;object-fit:cover;border-radius:8px;">
                  Video không tải được
                </video>`
              : `<div style="height: 200px; display: flex; align-items: center; justify-content: center; background: #f8f9fa; border-radius: 8px; color: #7f8c8d;">
                  Chưa có video
                </div>`
          }
        </div>
        <div class="video-info">
          <h3>${item.emotion}</h3>
          <p style="font-size:12px;color:#7f8c8d;margin:5px 0;">
            Level ${item.level} – ${item.title || ""}
          </p>
          <p style="font-size:12px;color:#95a5a6;margin:5px 0;word-break:break-all;">
            📹 ${videoPath || "—"}
          </p>
        </div>
        <div class="actions" style="margin-top:10px; display:flex; gap:8px;">
          <button class="btn btn-warning" onclick="window.replaceConceptVideo('${
            item.concept_id
          }')">
            ${hasVideo ? "🔄 Thay video" : "➕ Tải video"}
          </button>
          <button class="btn btn-danger" onclick="window.deleteConceptVideo('${
            item.concept_id
          }')" ${hasVideo ? "" : "disabled"}>
            🗑️ Xóa video
          </button>
        </div>
      </div>
    `;
  }).join("");
}

// ====================== EVENTS ======================

function setupEmotionEvents() {
  // ----- Chọn file video -----
  const fileInput = $("video-file-input");
  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];

      if (!file) {
        currentVideoFile = null;
        const previewContainer = $("video-preview-container");
        if (previewContainer) previewContainer.style.display = "none";
        return;
      }

      // Validate loại file
      if (!file.type.startsWith("video/")) {
        alert("❌ Vui lòng chọn file video!");
        e.target.value = "";
        currentVideoFile = null;
        const previewContainer = $("video-preview-container");
        if (previewContainer) previewContainer.style.display = "none";
        return;
      }

      // Validate kích thước (50MB)
      if (file.size > 50 * 1024 * 1024) {
        alert("❌ Video quá lớn! Tối đa 50MB.");
        e.target.value = "";
        currentVideoFile = null;
        const previewContainer = $("video-preview-container");
        if (previewContainer) previewContainer.style.display = "none";
        return;
      }

      // Lưu lại file đang chọn
      currentVideoFile = file;

      // Preview video
      const reader = new FileReader();
      reader.onload = (ev) => {
        const videoPlayer = $("video-preview-player");
        const previewContainer = $("video-preview-container");
        const nameEl = $("video-file-name");
        const sizeEl = $("video-file-size");

        if (videoPlayer) videoPlayer.src = ev.target.result;
        if (previewContainer) previewContainer.style.display = "block";
        if (nameEl) nameEl.textContent = file.name;
        if (sizeEl)
          sizeEl.textContent = (file.size / (1024 * 1024)).toFixed(2) + " MB";
      };
      reader.readAsDataURL(file);
    });
  }

  // ----- Submit form upload video -----
  const form = $("video-form");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      if (!currentVideoFile) {
        alert("❌ Vui lòng chọn video!");
        return;
      }
      if (!editingConceptId || !editingEmotionName) {
        alert("❌ Chưa chọn Emotion Concept!");
        return;
      }

      const concept = EMOTION_VIDEOS.find(
        (c) => c.concept_id === editingConceptId
      );

      const formData = new FormData();
      formData.append("video_file", currentVideoFile);
      formData.append("concept_id", editingConceptId);
      formData.append("emotion", editingEmotionName);
      formData.append("old_path", concept?.video_path || "");

      const uploadBtn = form.querySelector('button[type="submit"]');
      if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.textContent = "⏳ Đang tải lên...";
      }

      try {
        const res = await fetch(`${API_URL}/emotion-concepts/upload-video`, {
          method: "POST",
          body: formData,
        });
        const data = await res.json();

        if (!res.ok || data.status !== "success") {
          throw new Error(data.message || "Lỗi upload video");
        }

        showNotification(
          `✅ Đã thay thế video cho "${editingEmotionName}"!`,
          "success"
        );
        closeModal("video-modal");
        currentVideoFile = null;
        await loadEmotionVideos(); // reload lại từ DB
      } catch (err) {
        console.error(err);
        showNotification(`❌ ${err.message}`, "error");
      } finally {
        if (uploadBtn) {
          uploadBtn.disabled = false;
          uploadBtn.textContent = "💾 Lưu video";
        }
      }
    });
  }

  // ----- Nút Huỷ -----
  const cancelBtn = $("cancel-video-btn");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
      closeModal("video-modal");
      const fileInput = $("video-file-input");
      if (fileInput) fileInput.value = "";
      currentVideoFile = null;
      const previewContainer = $("video-preview-container");
      if (previewContainer) previewContainer.style.display = "none";
    });
  }
}

// ====================== GLOBAL HANDLER ======================

window.replaceConceptVideo = function (conceptId) {
  const item = EMOTION_VIDEOS.find((c) => c.concept_id === conceptId);
  if (!item) return;

  editingConceptId = conceptId;
  editingEmotionName = item.emotion;

  const titleEl = $("video-modal-title");
  const nameEl = $("video-emotion-name");
  const currentPathEl = $("video-current-path");
  const fileInput = $("video-file-input");
  const previewContainer = $("video-preview-container");
  const videoPlayer = $("video-preview-player");
  const fileNameEl = $("video-file-name");
  const fileSizeEl = $("video-file-size");

  if (titleEl) titleEl.textContent = `🔄 Thay Video: ${item.emotion}`;
  if (nameEl) nameEl.textContent = item.emotion;
  if (currentPathEl) currentPathEl.textContent = item.video_path || "(Chưa có)";

  // Reset trạng thái chọn file
  if (fileInput) fileInput.value = "";
  currentVideoFile = null;

  if (previewContainer) previewContainer.style.display = "none";
  if (videoPlayer) videoPlayer.src = "";
  if (fileNameEl) fileNameEl.textContent = "";
  if (fileSizeEl) fileSizeEl.textContent = "";

  openModal("video-modal");
};

// 🔥 Thêm nút XÓA video cho Emotion Concept
window.deleteConceptVideo = function (conceptId) {
  const item = EMOTION_VIDEOS.find((c) => c.concept_id === conceptId);
  if (!item) return;

  if (!item.video_path) {
    showNotification("⚠️ Emotion này chưa có video để xóa.", "warning");
    return;
  }

  if (
    !confirm(
      `⚠️ Bạn có chắc chắn muốn xóa video cho emotion "${item.emotion}"?\n\nVideo sẽ bị xóa khỏi hệ thống.`
    )
  ) {
    return;
  }

  fetch(`${API_URL}/emotion-concepts/delete-video`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      concept_id: item.concept_id,
      video_path: item.video_path,
    }),
  })
    .then((res) => res.json().then((data) => ({ res, data })))
    .then(({ res, data }) => {
      if (!res.ok || data.status !== "success") {
        throw new Error(data.message || "Lỗi xóa video");
      }

      showNotification(`✅ Đã xóa video cho "${item.emotion}"!`, "success");
      // Reload lại danh sách từ DB
      loadEmotionVideos();
    })
    .catch((err) => {
      console.error(err);
      showNotification(
        `❌ ${err?.message || "Có lỗi xảy ra khi xóa video"}`,
        "error"
      );
    });
};

// ====================== EXPORT ======================

export { loadEmotionVideos, setupEmotionEvents };
