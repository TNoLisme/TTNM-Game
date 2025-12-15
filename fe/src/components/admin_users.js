// users.js - Quản lý Users

import { API_URL, $, fetchAPI, openModal, closeModal, showNotification, calculateAge } from './admin.js';

let currentUsers = [];
let editingUserId = null;
let deleteUserId = null; // Lưu ID user cần xóa
// let searchTimeout = null; // Đã loại bỏ Debounce

// ==========================================
// LOAD & FILTER USERS
// ==========================================
async function loadUsers() {
    // 1. Lấy giá trị từ UI
    const searchTerm = $('search-users') ? $('search-users').value.trim() : '';
    const roleFilter = $('filter-role') ? $('filter-role').value : '';

    try {
        let url;

        // 2. Chọn API dựa trên việc có từ khóa tìm kiếm hay không
        if (searchTerm) {
            // Dùng API Search theo tên
            url = `${API_URL}/users/search?name=${encodeURIComponent(searchTerm)}&skip=0&limit=100`;
        } else {
            // Dùng API List mặc định
            url = `${API_URL}/users?skip=0&limit=100`;
        }

        // 3. Thực thi fetch API
        const res = await fetchAPI(url);

        if (!res.ok) {
            const errData = await res.json();
            // Lỗi MSSQL (400) sẽ được hiển thị ở đây
            throw new Error(errData.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();
        let users = data.data.users || [];

        // 4. Xử lý bộ lọc Role (Client-side filtering)
        if (roleFilter) {
            users = users.filter(u => u.role.toLowerCase() === roleFilter.toLowerCase());
        }

        currentUsers = users;
        renderUsersTable(currentUsers);

        if ($('total-users')) {
            $('total-users').textContent = users.length;
        }

    } catch (err) {
        console.error("❌ Load users error:", err);
        showNotification(`Lỗi tải users: ${err.message}`, 'error');
    }
}

function renderUsersTable(users) {
    const tbody = $('users-tbody');

    if (!tbody) return;

    // Colspan = 9
    if (!users.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align:center; padding: 30px; color: #999;">
                    <i class="fas fa-search" style="font-size: 24px; margin-bottom: 10px; display:block"></i>
                    Không tìm thấy user nào phù hợp
                </td>
            </tr>`;
        return;
    }

    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.user_id.substring(0, 8)}...</td>
            <td><strong>${user.username}</strong></td>
            <td>${user.name || 'N/A'}</td> 
            <td>${user.email}</td>
            <td><span class="badge badge-${user.role.toLowerCase()}">${user.role}</span></td>
            <td>${user.age || 'N/A'}</td>
            <td>${user.created_at ? new Date(user.created_at).toLocaleDateString('vi-VN') : 'N/A'}</td>
            <td>
                <span class="badge badge-active">Hoạt động</span>
            </td>
            <td class="actions">
                <button class="btn btn-warning" onclick="window.editUser('${user.user_id}')" title="Sửa">✏️</button>
                <button class="btn btn-danger" onclick="window.openDeleteUserModal('${user.user_id}')" title="Xóa">🗑️</button>
            </td>
        </tr>
    `).join('');
}

// ==========================================
// SETUP EVENTS
// ==========================================
function setupUserEvents() {
    // 1. Sự kiện Tìm kiếm (CHỈ khi bấm nút Tìm kiếm)
    $('search-users-btn')?.addEventListener('click', () => {
        // clearTimeout(searchTimeout); // Không cần debounce nữa
        loadUsers();
    });

    // 2. Sự kiện Lọc Role
    $('filter-role')?.addEventListener('change', () => {
        loadUsers();
    });

    // 3. Sự kiện mở Modal Thêm User
    $('add-user-btn')?.addEventListener('click', () => {
        editingUserId = null;
        $('user-modal-title').textContent = '➕ Thêm User Mới';
        $('user-form').reset();
        $('user-password').required = true;
        $('user-password').placeholder = 'Nhập mật khẩu';

        toggleChildFields('child');

        openModal('user-modal');
    });

    $('user-role')?.addEventListener('change', (e) => {
        toggleChildFields(e.target.value);
    });

    // 4. Submit Form Thêm/Sửa User
    $('user-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleSaveUser();
    });

    $('cancel-user-btn')?.addEventListener('click', () => closeModal('user-modal'));

    // 5. Sự kiện cho Modal Xóa (Confirm Delete)
    $('confirm-delete-btn')?.addEventListener('click', async () => {
        if (deleteUserId) {
            await executeDeleteUser(deleteUserId);
        }
    });

    $('cancel-delete-btn')?.addEventListener('click', () => closeModal('confirm-delete-modal'));
    $('close-confirm-modal')?.addEventListener('click', () => closeModal('confirm-delete-modal'));

    // Tải lần đầu tiên
    // loadUsers();
}

// Helper: Ẩn hiện các trường thông tin trẻ em
function toggleChildFields(role) {
    const childFieldRows = document.querySelectorAll('.child-fields');
    const isChild = role === 'child';

    childFieldRows.forEach(row => {
        if (isChild) {
            row.classList.add('show');
            row.style.display = 'grid';
        } else {
            row.classList.remove('show');
            row.style.display = 'none';
        }
    });

    const childInputs = ['user-date-of-birth', 'user-gender', 'user-phone'];
    childInputs.forEach(id => {
        const input = $(id);
        if (input) {
            input.required = isChild;
        }
    });
}

// ==========================================
// HANDLE SAVE/EDIT
// ==========================================

async function handleSaveUser() {
    const role = $('user-role').value;

    const data = {
        username: $('user-username').value.trim(),
        name: $('user-name').value.trim(),
        email: $('user-email').value.trim(),
        role: role.toLowerCase()
    };

    const passwordValue = $('user-password').value;
    if (passwordValue) {
        data.password = passwordValue;
    } else if (!editingUserId) {
        showNotification("❌ Mật khẩu là bắt buộc khi tạo user mới!", "error");
        return;
    }

    if (role === 'child') {
        const dateOfBirthInput = $('user-date-of-birth');
        const genderInput = $('user-gender');
        const phoneInput = $('user-phone');

        const dateOfBirth = dateOfBirthInput?.value;
        const gender = genderInput?.value;
        const phone = phoneInput?.value.trim();

        if (!editingUserId) {
            if (!dateOfBirth || !gender || !phone) {
                showNotification("❌ Vui lòng nhập đủ thông tin trẻ!", "error");
                return;
            }
            if (new Date(dateOfBirth) > new Date()) {
                showNotification("❌ Ngày sinh không hợp lệ!", "error");
                return;
            }
            if (!/^\d{10}$/.test(phone)) {
                showNotification("❌ Số điện thoại phải là 10 số!", "error");
                return;
            }

            data.date_of_birth = dateOfBirth;
            data.gender = gender.toLowerCase();
            data.phone_number = phone;
            data.age = calculateAge(dateOfBirth);
        } else {
            if (gender) data.gender = gender.toLowerCase();
            if (phone) data.phone_number = phone;
            if (dateOfBirth) {
                data.date_of_birth = dateOfBirth;
                data.age = calculateAge(dateOfBirth);
            }
        }
    }

    try {
        let res;
        const options = {
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        };

        if (editingUserId) {
            res = await fetchAPI(`${API_URL}/users/${editingUserId}`, {
                method: "PUT",
                ...options
            });
        } else {
            res = await fetchAPI(`${API_URL}/users`, {
                method: "POST",
                ...options
            });
        }

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || err.message || "Lỗi API");
        }

        showNotification("✔ Lưu thành công!", "success");
        closeModal("user-modal");
        loadUsers();

    } catch (err) {
        console.error("❌ Save error:", err);
        showNotification("❌ " + err.message, "error");
    }
}

// Window functions để gọi từ HTML onclick
window.editUser = (id) => {
    editingUserId = id;
    const user = currentUsers.find(u => u.user_id === id);
    if (!user) return;

    $('user-modal-title').textContent = '✏️ Chỉnh sửa User';

    $('user-username').value = user.username;
    $('user-email').value = user.email;
    $('user-name').value = user.name || '';
    $('user-role').value = user.role;

    toggleChildFields(user.role);

    if (user.role === 'child') {
        $('user-gender').value = user.gender || 'male';
        $('user-phone').value = user.phone_number || '';
        $('user-date-of-birth').value = '';

        $('user-date-of-birth').required = false;
        $('user-phone').required = false;
    } else {
        $('user-gender').value = 'male';
        $('user-phone').value = '';
        $('user-date-of-birth').value = '';
    }


    $('user-password').required = false;
    $('user-password').placeholder = 'Để trống nếu không đổi';

    openModal('user-modal');
};

// Mở Modal Xóa (Thay thế confirm popup cũ)
window.openDeleteUserModal = (id) => {
    deleteUserId = id;
    openModal('confirm-delete-modal');
}

async function executeDeleteUser(id) {
    const confirmBtn = $('confirm-delete-btn');
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = '⏳ Đang xóa...';

    try {
        const res = await fetchAPI(`${API_URL}/users/${id}`, {
            method: "DELETE"
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Lỗi xóa user");
        }

        showNotification("✅ Đã xóa user!", "success");
        closeModal('confirm-delete-modal');
        loadUsers();

    } catch (err) {
        console.error(err);
        showNotification(`❌ ${err.message}`, 'error');
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = '🗑️ Xóa ngay';
        deleteUserId = null;
    }
};

export { loadUsers, setupUserEvents };