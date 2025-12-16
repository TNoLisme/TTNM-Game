const API_URL = "http://localhost:8000";

const $ = id => document.getElementById(id);

const GAME_BADGES = [
    {
        gameId: '3bcb2108-721c-4a15-a585-31f3084ed000',
        name: 'Chiếc hộp cảm xúc',
        icon: '📦',
        totalLevels: 8,
        type: 'levels'
    },
    {
        gameId: 'aacaf79e-e15e-42a9-a3d1-a522720d919b',
        name: 'Thám tử cảm xúc',
        icon: '🕵️',
        totalLevels: 8,
        type: 'levels'
    },
    {
        gameId: '08bbffbf-d147-4556-bccb-b7621cafbf15',
        name: 'Cảm xúc đúng chỗ',
        icon: '🎯',
        totalLevels: 8,
        type: 'levels'
    },
    {
        gameId: '33ecafaa-ec7e-40d2-9c67-ed0a29ac0051',
        name: 'Xưởng lắp ghép cảm xúc',
        icon: '🧩',
        totalLevels: 8,
        type: 'levels'
    },
    {
        gameId: 'e05909f3-3dee-42a6-9a75-fd985b1bdf47',
        name: 'Câu chuyện trên khuôn mặt',
        icon: '🎭',
        totalLevels: 8,
        type: 'levels'
    },
    {
        gameId: '61f5e09e-eefa-44c1-86e1-87dfceac3b8e',
        name: 'Thử thách cảm xúc',
        icon: '📷',
        type: 'emotions'
    }
];

async function loadGameProgress(userId, gameId) {
    const url = `${API_URL}/games/progress/${gameId}?user_id=${encodeURIComponent(userId)}`;
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

async function loadEmotionScores(userId) {
    const url = `${API_URL}/games/cv/emotion-scores?user_id=${encodeURIComponent(userId)}`;
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

function setBadgesLoading() {
    const container = document.getElementById('badges-container');
    if (!container) return;
    container.innerHTML = '';
    for (let i = 0; i < GAME_BADGES.length; i++) {
        const el = document.createElement('div');
        el.className = 'badge locked';
        el.title = 'Đang tải huy hiệu...';
        el.textContent = '🔒';
        container.appendChild(el);
    }
}

async function renderGameBadges(userId) {
    const container = document.getElementById('badges-container');
    if (!container) return;

    setBadgesLoading();

    let emotionScores = null;
    try {
        emotionScores = await loadEmotionScores(userId);
    } catch (e) {
        emotionScores = null;
    }

    const progressResults = await Promise.all(
        GAME_BADGES.map(async (b) => {
            if (b.type !== 'levels') return { ok: true, progress: null };
            try {
                const progress = await loadGameProgress(userId, b.gameId);
                return { ok: true, progress };
            } catch (e) {
                return { ok: false, progress: null };
            }
        })
    );

    container.innerHTML = '';
    let unlockedCount = 0;
    const unlockedNow = [];

    GAME_BADGES.forEach((b, idx) => {
        let unlocked = false;
        if (b.type === 'levels') {
            const { progress } = progressResults[idx] || {};
            const level = progress && typeof progress.level === 'number' ? progress.level : 1;
            unlocked = level >= (b.totalLevels + 1);
        } else {
            const scores = emotionScores && emotionScores.scores ? emotionScores.scores : {};
            const keys = ['vui', 'buồn', 'ngạc nhiên', 'tức giận', 'sợ hãi', 'ghê tởm'];
            unlocked = keys.every((k) => {
                const v = scores[k];
                return typeof v === 'number' && v >= 100;
            });
        }

        const el = document.createElement('div');
        el.className = unlocked ? 'badge' : 'badge locked';
        if (unlocked) {
            el.title = b.name;
            el.textContent = b.icon;
            unlockedCount += 1;
            unlockedNow.push(b.gameId);
        } else {
            el.title = `Hoàn thành tất cả màn của "${b.name}" để mở khóa`;
            el.textContent = '🔒';
        }
        container.appendChild(el);
    });

    const achievementsEl = document.getElementById('achievements');
    if (achievementsEl) {
        animate('achievements', unlockedCount);
    }

    let unlockedPrev = [];
    try {
        unlockedPrev = JSON.parse(localStorage.getItem('egUnlockedBadges') || '[]');
        if (!Array.isArray(unlockedPrev)) unlockedPrev = [];
    } catch (e) {
        unlockedPrev = [];
    }

    const newlyUnlocked = unlockedNow.filter((id) => !unlockedPrev.includes(id));
    if (newlyUnlocked.length > 0) {
        const id = newlyUnlocked[0];
        const badge = GAME_BADGES.find((b) => b.gameId === id);
        if (badge) {
            await inlineAlert(
                `Chúc mừng! Bé đã hoàn thành "${badge.name}" và nhận được huy hiệu ${badge.icon}`,
                'Chúc mừng nhận huy hiệu',
                'Tuyệt vời!'
            );
        }
    }

    localStorage.setItem('egUnlockedBadges', JSON.stringify(unlockedNow));
}

function ensureInlineConfirmModal() {
    if (document.getElementById('eg-confirm-overlay')) return;

    if (!document.getElementById('eg-confirm-style')) {
        const style = document.createElement('style');
        style.id = 'eg-confirm-style';
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

    const overlay = document.createElement('div');
    overlay.id = 'eg-confirm-overlay';
    overlay.className = 'eg-confirm-overlay';
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
}

function inlineConfirm(message, title, okText, cancelText) {
    ensureInlineConfirmModal();

    const overlay = document.getElementById('eg-confirm-overlay');
    const titleEl = document.getElementById('eg-confirm-title');
    const msgEl = document.getElementById('eg-confirm-message');
    const okBtn = document.getElementById('eg-confirm-ok');
    const cancelBtn = document.getElementById('eg-confirm-cancel');

    if (!overlay || !titleEl || !msgEl || !okBtn || !cancelBtn) {
        return Promise.resolve(confirm(message));
    }

    titleEl.textContent = title || 'Xác nhận';
    msgEl.textContent = message || '';
    okBtn.textContent = okText || 'OK';
    cancelBtn.textContent = cancelText || 'Hủy';

    return new Promise((resolve) => {
        const close = (result) => {
            overlay.classList.remove('is-open');
            okBtn.onclick = null;
            cancelBtn.onclick = null;
            overlay.onclick = null;
            document.removeEventListener('keydown', onKeyDown);
            resolve(result);
        };

        const onKeyDown = (e) => {
            if (e.key === 'Escape') close(false);
        };

        okBtn.onclick = () => close(true);
        cancelBtn.onclick = () => close(false);
        overlay.onclick = (e) => {
            if (e.target === overlay) close(false);
        };
        document.addEventListener('keydown', onKeyDown);

        overlay.classList.add('is-open');
        cancelBtn.focus();
    });
}

function inlineAlert(message, title, okText) {
    ensureInlineConfirmModal();

    const overlay = document.getElementById('eg-confirm-overlay');
    const titleEl = document.getElementById('eg-confirm-title');
    const msgEl = document.getElementById('eg-confirm-message');
    const okBtn = document.getElementById('eg-confirm-ok');
    const cancelBtn = document.getElementById('eg-confirm-cancel');

    if (!overlay || !titleEl || !msgEl || !okBtn || !cancelBtn) {
        alert(message);
        return Promise.resolve();
    }

    const prevCancelDisplay = cancelBtn.style.display;
    cancelBtn.style.display = 'none';

    titleEl.textContent = title || 'Thông báo';
    msgEl.textContent = message || '';
    okBtn.textContent = okText || 'OK';

    return new Promise((resolve) => {
        const close = () => {
            overlay.classList.remove('is-open');
            okBtn.onclick = null;
            cancelBtn.onclick = null;
            overlay.onclick = null;
            document.removeEventListener('keydown', onKeyDown);
            cancelBtn.style.display = prevCancelDisplay;
            resolve();
        };

        const onKeyDown = (e) => {
            if (e.key === 'Escape') close();
        };

        okBtn.onclick = () => close();
        cancelBtn.onclick = () => close();
        overlay.onclick = (e) => {
            if (e.target === overlay) close();
        };
        document.addEventListener('keydown', onKeyDown);

        overlay.classList.add('is-open');
        okBtn.focus();
    });
}

function getUserId() {
    const user = JSON.parse(localStorage.getItem("currentUser") || "{}");
    const id = user.user_id || user.userId || user.id;
    if (!id || typeof id !== "string") return null;
    console.log("%cUSER_ID:", "color: cyan;", id);
    return id.trim();
}

async function loadProfile() {
    const userId = getUserId();
    if (!userId) return showError("Chưa đăng nhập bro ơi!");

    const url = `${API_URL}/users/me?user_id=${userId}&t=${Date.now()}`;

    try {
        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) throw new Error(`API lỗi ${res.status}`);
        const data = await res.json();

        $("user-name").textContent   = data.name  ?? "Bé Vui Vẻ";
        $("username").textContent    = data.username ?? "---";
        $("email").textContent       = data.email ?? "---";
        $("age").textContent         = (data.age ?? 0) + " tuổi";
        $("join-date").textContent   = new Date(data.created_at ?? Date.now())
                                        .toLocaleDateString("vi-VN");

        animate("games-played", data.games_played ?? 15);
        animate("total-score",  data.total_score  ?? 1200);
        $("play-time").textContent = (data.play_time ?? "6.2") + "h";

        window.currentProfile = data;

        renderGameBadges(userId);
    } catch (e) {
        showError("Load lỗi: " + e.message);
        console.error(e);
    }
}

async function saveProfile(e) {
    e.preventDefault();
    const userId = getUserId();
    if (!userId) return alert("Chưa đăng nhập bro!");

    const newPassword = $("edit-password").value;
    const confirmPassword = $("edit-password-confirm").value;

    if (newPassword && newPassword !== confirmPassword) {
        showToast("Mật khẩu mới và mật khẩu xác nhận không khớp!", "error");
        $("edit-password-confirm").focus();
        return;
    }

    const update = {
        name: $("edit-name").value.trim(),
        username: $("edit-username").value.trim(),
        email: $("edit-email").value.trim(),
        age: $("edit-age").value ? parseInt($("edit-age").value) : null,
        phone_number: $("edit-phone").value.trim(),
        gender: $("edit-gender").value,
        date_of_birth: $("edit-dob").value,
        password: newPassword || undefined
    };

    Object.keys(update).forEach(key => {
        if (update[key] === "" || update[key] === null || update[key] === undefined) {
            delete update[key];
        }
    });

    try {
        const res = await fetch(`${API_URL}/users/me?user_id=${userId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: userId,
                update: update
            })
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Lỗi server");
        }

        showToast("Thông tin cá nhân đã được cập nhật thành công!", "success");
        closeModal();
        loadProfile();
    } catch (err) {
        showToast("Lỗi: " + err.message, "error");
    }
}

// ==================== REPORT FUNCTIONS ====================

async function requestReport(period) {
    const userId = getUserId();
    
    console.log("%c=== REQUEST REPORT DEBUG ===", "color: yellow; font-size: 14px;");
    console.log("Period:", period);
    console.log("User ID:", userId);
    console.log("Current profile:", window.currentProfile);
    
    if (!userId) {
        showToast("Vui lòng đăng nhập để nhận báo cáo!", "error");
        console.error("❌ No user_id found");
        return;
    }

    if (!window.currentProfile) {
        showToast("Đang tải thông tin người dùng...", "info");
        await loadProfile();
        if (!window.currentProfile) {
            showToast("Không thể tải thông tin người dùng", "error");
            return;
        }
    }

    const periodText = period === "weekly" ? "tuần" : "tháng";
    const userEmail = window.currentProfile?.email || 'email của bạn';

    let ok = false;
    if (window.egModal && typeof window.egModal.confirm === 'function') {
        ok = await window.egModal.confirm(
            `Bạn có chắc chắn muốn tạo báo cáo ${periodText} và gửi qua email không?\n\nBáo cáo sẽ được gửi đến: ${userEmail}`,
            'Xác nhận tạo báo cáo',
            'Tạo báo cáo',
            'Hủy'
        );
    } else {
        ok = await inlineConfirm(
            `Bạn có chắc chắn muốn tạo báo cáo ${periodText} và gửi qua email không?\n\nBáo cáo sẽ được gửi đến: ${userEmail}`,
            'Xác nhận tạo báo cáo',
            'Tạo báo cáo',
            'Hủy'
        );
    }

    if (!ok) return;

    showToast(`Đang tạo báo cáo ${periodText}... Vui lòng đợi`, "info");

    try {
        // ✅ Gọi đúng endpoint với user_id trong query
        const url = `${API_URL}/reports/request-report?period=${period}&user_id=${userId}`;
        console.log(`🚀 Calling API: POST ${url}`);
        
        const res = await fetch(url, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json"
            }
        });

        console.log("📥 Response status:", res.status);
        
        const data = await res.json();
        console.log("📦 Response data:", data);

        if (!res.ok) {
            if (res.status === 401) {
                console.error("❌ 401 Unauthorized");
                showToast("Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại!", "error");
                setTimeout(() => {
                    localStorage.clear();
                    location.href = "/src/pages/login.html";
                }, 2000);
                return;
            }
            throw new Error(data.detail || data.message || "Lỗi khi tạo báo cáo");
        }

        showToast(`✅ Báo cáo ${periodText} đang được gửi đến email của bạn!`, "success");
        console.log("✅ Report requested successfully:", data);

    } catch (err) {
        console.error("❌ Report error:", err);
        showToast(`❌ Lỗi: ${err.message}`, "error");
    }
}

// ==================== EXISTING FUNCTIONS ====================

function showError(msg) {
    const el = document.getElementById("error-message");
    if (!el) return;
    el.textContent = msg;
    el.style.display = "block";
    setTimeout(() => el.style.display = "none", 5000);
}

function openEditModal() {
    if (!window.currentProfile) return alert("Tải profile trước!");
    const d = window.currentProfile;

    const modal = document.getElementById("edit-modal");
    if (!modal) return;
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("modal-open");

    $("edit-username").value = d.username || "";
    $("edit-name").value = d.name || "";
    $("edit-email").value = d.email || "";
    $("edit-age").value = d.age || "";
    $("edit-gender").value = d.gender || "male";
    $("edit-dob").value = d.date_of_birth || "";
    $("edit-phone").value = d.phone_number || "";
    $("edit-password").value = "";
    $("edit-password-confirm").value = "";

    const firstField = $("edit-name");
    if (firstField) {
        requestAnimationFrame(() => firstField.focus());
    }
}

function closeModal() {
    const modal = document.getElementById("edit-modal");
    if (!modal) return;
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("modal-open");
}

function animate(id, end) {
    const el = document.getElementById(id);
    if (!el) return;
    let cur = 0;
    const timer = setInterval(() => {
        cur += Math.ceil((end - cur) / 10);
        el.textContent = cur;
        if (cur >= end) { el.textContent = end; clearInterval(timer); }
    }, 60);
}

function showToast(message, type = "success") {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-icon">${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</div>
        <div class="toast-message">${message}</div>
    `;
    container.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==================== EVENT LISTENERS ====================

document.addEventListener("DOMContentLoaded", () => {
    console.log("%c🚀 PROFILE.JS LOADED", "color: gold; font-size: 16px;");
    console.log("User ID:", getUserId() ? "EXISTS" : "NULL");
    
    loadProfile();

    const editBtn = document.getElementById("edit-btn");
    const form = document.getElementById("edit-form");
    const closeBtn = document.querySelector(".modal-close");
    const logout = document.getElementById("logout-btn");

    const weeklyReportBtn = document.getElementById("request-weekly-report");
    const monthlyReportBtn = document.getElementById("request-monthly-report");

    if (editBtn) editBtn.onclick = openEditModal;
    if (form) form.onsubmit = saveProfile;
    if (closeBtn) closeBtn.onclick = closeModal;
    if (logout) logout.onclick = async () => {
        const ok = await inlineConfirm(
            'Bạn có chắc chắn muốn đăng xuất không?',
            'Xác nhận đăng xuất',
            'Đăng xuất',
            'Hủy'
        );
        if (!ok) return;
        localStorage.clear();
        location.href = "/src/pages/login.html";
    };

    if (weeklyReportBtn) {
        weeklyReportBtn.onclick = () => requestReport("weekly");
    }
    if (monthlyReportBtn) {
        monthlyReportBtn.onclick = () => requestReport("monthly");
    }

    document.addEventListener("keydown", e => {
        const modal = document.getElementById("edit-modal");
        if (e.key === "Escape" && modal && modal.getAttribute("aria-hidden") === "false") {
            closeModal();
        }
    });
});

window.closeModal = closeModal;
