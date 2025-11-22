const API_URL = "http://localhost:8000";

const $ = id => document.getElementById(id);

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
        animate("achievements", data.achievements ?? 8);
        $("play-time").textContent = (data.play_time ?? "6.2") + "h";

        window.currentProfile = data;
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
    const token = localStorage.getItem("token");
    
    console.log("%c=== REQUEST REPORT DEBUG ===", "color: yellow; font-size: 14px;");
    console.log("Token exists:", !!token);
    console.log("Token preview:", token ? token.substring(0, 20) + "..." : "NULL");
    console.log("Period:", period);
    console.log("Current profile:", window.currentProfile);
    
    if (!token) {
        showToast("Vui lòng đăng nhập để nhận báo cáo!", "error");
        console.error("❌ No token found in localStorage");
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

    if (!confirm(`Gửi báo cáo ${periodText} này qua email?\n\nBáo cáo sẽ được gửi đến: ${userEmail}`)) {
        return;
    }

    showToast(`Đang tạo báo cáo ${periodText}... Vui lòng đợi`, "info");

    try {
        console.log(`🚀 Calling API: POST ${API_URL}/reports/request-report?period=${period}`);
        
        const res = await fetch(`${API_URL}/reports/request-report?period=${period}`, {
            method: "POST",
            headers: { 
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        console.log("📥 Response status:", res.status);
        
        const data = await res.json();
        console.log("📦 Response data:", data);

        if (!res.ok) {
            if (res.status === 401) {
                console.error("❌ 401 Unauthorized - Token invalid/expired");
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
    console.log("%c🚀 PROFILE.JS LOADED WITH DEBUG", "color: gold; font-size: 16px;");
    console.log("Token in localStorage:", localStorage.getItem("token") ? "EXISTS" : "NULL");
    
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
    if (logout) logout.onclick = () => confirm("Đăng xuất?") && (localStorage.clear(), location.href = "/src/pages/login.html");

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