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
        alert("Mật khẩu mới và mật khẩu xác nhận không khớp!");
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
        password: newPassword || undefined  // Chỉ gửi nếu có nhập
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

        alert("Thông tin cá nhân đã được cập nhật thành công!");
        closeModal();
        loadProfile();
    } catch (err) {
        alert("Lỗi: " + err.message);
    }
}

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
    $("edit-password").value = ""; // Luôn để trống
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

document.addEventListener("DOMContentLoaded", () => {
    console.log("%cPROFILE.JS 100% SỐNG!", "color: gold; font-size: 20px;");
    loadProfile();

    const editBtn = document.getElementById("edit-btn");
    const form = document.getElementById("edit-form");
    const closeBtn = document.querySelector(".modal-close");
    const logout = document.getElementById("logout-btn");

    if (editBtn) editBtn.onclick = openEditModal;
    if (form) form.onsubmit = saveProfile;
    if (closeBtn) closeBtn.onclick = closeModal;
    if (logout) logout.onclick = () => confirm("Đăng xuất?") && (localStorage.clear(), location.href = "/src/pages/login.html");

    document.addEventListener("keydown", e => {
        const modal = document.getElementById("edit-modal");
        if (e.key === "Escape" && modal && modal.getAttribute("aria-hidden") === "false") {
            closeModal();
        }
    });
});

window.closeModal = closeModal;