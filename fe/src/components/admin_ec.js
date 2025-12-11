// emotions.js - Quản lý Video Cảm xúc

import {
  API_URL,
  $,
  openModal,
  closeModal,
  showNotification,
} from "./admin.js";

const DEFAULT_EMOTION_VIDEOS = [
  {
    id: "vui",
    name: "Vui vẻ",
    emoji: "😊",
    path: "../../assets/videos/happy.mp4",
    version: 0,
  },
  {
    id: "buon",
    name: "Buồn bã",
    emoji: "😢",
    path: "../../assets/videos/sad.mp4",
    version: 0,
  },
  {
    id: "tuc",
    name: "Tức giận",
    emoji: "😠",
    path: "../../assets/videos/angry.mp4",
    version: 0,
  },
  {
    id: "so",
    name: "Sợ hãi",
    emoji: "😨",
    path: "../../assets/videos/fear.mp4",
    version: 0,
  },
  {
    id: "ngac",
    name: "Ngạc nhiên",
    emoji: "😲",
    path: "../../assets/videos/surprise.mp4",
    version: 0,
  },
  {
    id: "ghe",
    name: "Ghê tởm",
    emoji: "🤢",
    path: "../../assets/videos/disgust.mp4",
    version: 0,
  },
];
let emotionVideos = [...DEFAULT_EMOTION_VIDEOS];
const DEFAULT_VERSION_KEY = "emotion_default_version";

function getDefaultVersion() {
  const saved = localStorage.getItem(DEFAULT_VERSION_KEY);

  if (saved) {
    const parsed = Number(saved);
    if (!Number.isNaN(parsed) && parsed > 0) return parsed;
  }

  const seed = Date.now();
  localStorage.setItem(DEFAULT_VERSION_KEY, seed.toString());
  return seed;
}

let currentVideoFile = null;
let editingVideoId = null;

async function loadEmotionVideos() {
  restoreVideoState();
  renderVideoGrid();
  updateVideoStats();
  await syncEmotionVideosFromServer();
}

function renderVideoGrid() {
  const grid = $("emotions-grid");

  grid.innerHTML = emotionVideos
    .map((video) => {
      const hasVideo = !!video.path;
      const displayPath = hasVideo
        ? `${video.path}${video.version ? `?v=${video.version}` : ""}`
        : "";

      return `
        <div class="video-card" data-video-id="${video.id}">
            <div class="video-preview">
                ${
                  hasVideo
                    ? `<video src="${displayPath}" controls style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;">
                        Video không tải được
                    </video>`
                    : `<div style="height: 200px; display: flex; align-items: center; justify-content: center; background: #f8f9fa; border-radius: 8px; color: #7f8c8d;">Chưa có video</div>`
                }
            </div>
            <div class="video-info">
                <h3>${video.emoji} ${video.name}</h3>
                <p style="font-size: 12px; color: #7f8c8d; margin: 5px 0;">
                    ${
                      hasVideo
                        ? `📹 ${video.path}`
                        : "⚠️ Video chưa được tải lên"
                    }
                </p>
            </div>
            <div class="actions" style="margin-top: 10px; display: flex; gap: 8px;">
                <button class="btn btn-warning" onclick="window.replaceVideo('${
                  video.id
                }')">
                    ${hasVideo ? "🔄 Thay thế video" : "➕ Tải video"}
                </button>
                <button class="btn btn-danger" onclick="window.deleteVideo('${
                  video.id
                }')" ${hasVideo ? "" : "disabled"}>
                    🗑️ Xóa video
                </button>
            </div>
        </div>`;
    })
    .join("");
}

function setupEmotionEvents() {
  $("video-file-input")?.addEventListener("change", (e) => {
    const file = e.target.files[0];

    if (!file) {
      currentVideoFile = null;
      $("video-preview-container").style.display = "none";
      return;
    }

    if (!file.type.startsWith("video/")) {
      alert("❌ Vui lòng chọn file video!");
      e.target.value = "";
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      alert("❌ Video quá lớn! Tối đa 50MB.");
      e.target.value = "";
      return;
    }

    currentVideoFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
      $("video-preview-player").src = e.target.result;
      $("video-preview-container").style.display = "block";
      $("video-file-name").textContent = file.name;
      $("video-file-size").textContent =
        (file.size / (1024 * 1024)).toFixed(2) + " MB";
    };
    reader.readAsDataURL(file);
  });

  $("video-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!currentVideoFile) {
      alert("❌ Vui lòng chọn video!");
      return;
    }

    const video = emotionVideos.find((v) => v.id === editingVideoId);
    if (!video) return;

    const formData = new FormData();
    formData.append("video_file", currentVideoFile);
    formData.append("emotion_id", video.id);
    formData.append("emotion_name", video.name);
    formData.append("old_path", video.path);

    const uploadBtn = e.target.querySelector('button[type="submit"]');
    uploadBtn.disabled = true;
    uploadBtn.textContent = "⏳ Đang tải lên...";

    try {
      const res = await fetch(`${API_URL}/emotions/upload-video`, {
        method: "POST",
        body: formData,
      });

      let data;

      try {
        data = await res.json();
      } catch (parseError) {
        throw new Error("Lỗi upload video");
      }

      if (!res.ok || data.status !== "success") {
        throw new Error(data.message || "Lỗi upload video");
      }
      // Cập nhật đường dẫn video mới và lưu state
      const newPath = data?.data?.video_path || video.path;
      const newVersion = data?.data?.version;
      updateVideoPath(video.id, newPath, newVersion);

      showNotification(`✅ Đã thay thế video "${video.name}"!`, "success");
      closeModal("video-modal");
      loadEmotionVideos();
    } catch (err) {
      showNotification(
        `❌ ${err?.message || "Có lỗi xảy ra khi thay thế video"}`,
        "error"
      );
    } finally {
      uploadBtn.disabled = false;
      uploadBtn.textContent = "💾 Lưu video";
    }
  });

  $("cancel-video-btn")?.addEventListener("click", () =>
    closeModal("video-modal")
  );
}

window.replaceVideo = function (videoId) {
  editingVideoId = videoId;
  const video = emotionVideos.find((v) => v.id === videoId);
  if (video) {
    $(
      "video-modal-title"
    ).textContent = `🔄 Thay thế Video: ${video.emoji} ${video.name}`;
    $("video-emotion-name").textContent = video.name;
    $("video-current-path").textContent = video.path || "Chưa có video";
    currentVideoFile = null;

    openModal("video-modal");
  }
};

window.deleteVideo = function (videoId) {
  const video = emotionVideos.find((v) => v.id === videoId);
  if (!video.path) {
    showNotification("⚠️ Video đã trống, không thể xóa.", "warning");
    return;
  }

  if (
    !confirm(
      `⚠️ Bạn có chắc chắn muốn xóa video "${video.name}"?\n\nLưu ý: Video sẽ bị xóa khỏi thư mục assets!`
    )
  )
    return;

  fetch(`${API_URL}/emotions/delete-video`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ video_path: video.path }),
  })
    .then(async (res) => {
      let data;

      try {
        data = await res.json();
      } catch (parseError) {
        throw new Error("Lỗi xóa video");
      }

      if (!res.ok || data.status !== "success") {
        throw new Error(data.message || "Lỗi xóa video");
      }
      updateVideoPath(video.id, "");
      showNotification(`✅ Đã xóa video "${video.name}"!`, "success");
      loadEmotionVideos();
    })
    .catch((err) => {
      showNotification(
        `❌ ${err?.message || "Có lỗi xảy ra khi xóa video"}`,
        "error"
      );
    });
};

function restoreVideoState() {
  try {
    const saved = JSON.parse(localStorage.getItem("emotion_videos") || "{}");
    const defaultVersion = getDefaultVersion();

    emotionVideos = DEFAULT_EMOTION_VIDEOS.map((video) => {
      const savedEntry = saved[video.id];
      const hasSavedPath =
        savedEntry && Object.prototype.hasOwnProperty.call(savedEntry, "path");

      if (typeof savedEntry === "string" || hasSavedPath) {
        const savedPath = hasSavedPath ? savedEntry.path : savedEntry;
        const normalizedVersion = savedPath
          ? savedEntry?.version || defaultVersion
          : 0;

        return {
          ...video,
          path: savedPath,
          version: normalizedVersion,
        };
      }

      if (savedEntry && typeof savedEntry === "object") {
        return {
          ...video,
          path: video.path,
          version: savedEntry.version || defaultVersion,
        };
      }

      return {
        ...video,
        version: defaultVersion,
      };
    });
  } catch (error) {
    console.error("Không thể khôi phục trạng thái video:", error);
    const fallbackVersion = getDefaultVersion();
    emotionVideos = DEFAULT_EMOTION_VIDEOS.map((video) => ({
      ...video,
      version: fallbackVersion,
    }));
  }
}

function updateVideoPath(videoId, path, versionOverride) {
  const video = emotionVideos.find((v) => v.id === videoId);
  if (!video) return;

  video.path = path || "";
  video.version = video.path ? versionOverride ?? Date.now() : 0;

  const saved = JSON.parse(localStorage.getItem("emotion_videos") || "{}");
  saved[videoId] = { path: video.path, version: video.version };
  localStorage.setItem("emotion_videos", JSON.stringify(saved));

  if (video.version) {
    localStorage.setItem(DEFAULT_VERSION_KEY, video.version.toString());
  }
}

async function syncEmotionVideosFromServer() {
  try {
    const res = await fetch(`${API_URL}/emotions/videos`, {
      cache: "no-store",
    });
    const data = await res.json();

    if (!res.ok || data.status !== "success") {
      throw new Error(data.message || "Không thể lấy danh sách video cảm xúc");
    }

    const serverVideos = Array.isArray(data?.data?.videos)
      ? data.data.videos
      : [];
    const serverMap = new Map(serverVideos.map((video) => [video.id, video]));
    const saved = JSON.parse(localStorage.getItem("emotion_videos") || "{}");
    const defaultVersion = getDefaultVersion();

    emotionVideos = DEFAULT_EMOTION_VIDEOS.map((defaultVideo) => {
      const serverEntry = serverMap.get(defaultVideo.id);

      if (serverEntry && serverEntry.path) {
        const version = serverEntry.version || Date.now();
        saved[defaultVideo.id] = { path: serverEntry.path, version };
        return { ...defaultVideo, path: serverEntry.path, version };
      }

      const savedEntry = saved[defaultVideo.id];
      const hasSavedPath =
        savedEntry && Object.prototype.hasOwnProperty.call(savedEntry, "path");

      if (typeof savedEntry === "string" || hasSavedPath) {
        const savedPath = hasSavedPath ? savedEntry.path : savedEntry;
        return {
          ...defaultVideo,
          path: savedPath,
          version: savedEntry?.version || defaultVersion,
        };
      }

      return {
        ...defaultVideo,
        version: defaultVersion,
      };
    });

    localStorage.setItem("emotion_videos", JSON.stringify(saved));
    renderVideoGrid();
    updateVideoStats();
  } catch (error) {
    console.error("Không thể đồng bộ video cảm xúc từ server:", error);
  }
}

function updateVideoStats() {
  const totalEl = $("total-videos");
  if (!totalEl) return;

  const availableVideos = emotionVideos.filter((video) => !!video.path).length;
  totalEl.textContent = availableVideos.toString();
}

export { loadEmotionVideos, setupEmotionEvents };
