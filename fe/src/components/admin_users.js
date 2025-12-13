// users.js - Quản lý Users

import { API_URL, $, fetchAPI, openModal, closeModal, showNotification, calculateAge } from './admin.js';

let currentUsers = [];
let editingUserId = null;

async function loadUsers() {
    try {
        const res = await fetchAPI(`${API_URL}/users?skip=0&limit=100`);

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();
        currentUsers = data.data.users || [];
        
        console.log(`✅ Loaded ${currentUsers.length} users`);
        
        // Áp dụng filters hiện tại
        applyCurrentFilters();
        
        if ($('total-users')) {
            $('total-users').textContent = currentUsers.length;
        }
        
    } catch (err) {
        console.error("❌ Load users error:", err);
        showNotification(`Lỗi tải users: ${err.message}`, 'error');
    }
}

function renderUsersTable(users) {
    const tbody = $('users-tbody');

    if (!tbody) {
        console.error("Không tìm thấy #users-tbody trong DOM!");
        return;
    }

    if (!users || users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align:center; padding: 30px;">
                    <div style="color: #999;">
                        <i class="fas fa-user-slash" style="font-size: 48px; margin-bottom: 10px;"></i>
                        <p>Không tìm thấy user nào</p>
                    </div>
                </td>
            </tr>`;
        return;
    }

    tbody.innerHTML = users.map(user => `
        <tr>
            <td title="${user.user_id}">${user.user_id.substring(0, 8)}...</td>
            <td><strong>${escapeHtml(user.username)}</strong></td>
            <td>${escapeHtml(user.email)}</td>
            <td><span class="badge badge-${user.role}">${user.role}</span></td>
            <td>${user.age || 'N/A'}</td>
            <td>${user.created_at ? new Date(user.created_at).toLocaleDateString('vi-VN') : 'N/A'}</td>
            <td>
                <span class="badge badge-active">Hoạt động</span>
            </td>
            <td class="actions">
                <button class="btn btn-warning" onclick="window.editUser('${user.user_id}')" title="Chỉnh sửa">✏️</button>
                <button class="btn btn-danger" onclick="window.deleteUser('${user.user_id}')" title="Xóa">🗑️</button>
            </td>
        </tr>
    `).join('');
}

function applyCurrentFilters() {
    const searchTerm = $('search-users')?.value?.trim() || '';
    const roleFilter = $('filter-user-role')?.value || '';
    
    console.log('🔍 Applying filters:', { searchTerm, roleFilter });
    
    let filtered = [...currentUsers];
    
    // Apply search
    if (searchTerm) {
        const term = searchTerm.toLowerCase();
        filtered = filtered.filter(user => {
            return (
                user.username?.toLowerCase().includes(term) ||
                user.email?.toLowerCase().includes(term) ||
                user.name?.toLowerCase().includes(term) ||
                user.user_id?.toLowerCase().includes(term) ||
                user.phone_number?.includes(term)
            );
        });
    }
    
    // Apply role filter
    if (roleFilter) {
        filtered = filtered.filter(user => user.role === roleFilter);
    }
    
    console.log(`✅ Filtered: ${filtered.length} / ${currentUsers.length} users`);
    
    renderUsersTable(filtered);
}

function resetFilters() {
    // Clear search input
    const searchInput = $('search-users');
    if (searchInput) searchInput.value = '';
    
    // Clear role filter
    const roleFilter = $('filter-user-role');
    if (roleFilter) roleFilter.value = '';
    
    // Show all users
    renderUsersTable(currentUsers);
    
    showNotification('Đã xóa bộ lọc', 'success');
}

function toggleChildFields(role) {
    const childFieldRows = document.querySelectorAll('.child-fields');
    const isChild = role === 'child';
    
    childFieldRows.forEach(row => {
        if (isChild) {
            row.classList.add('show');
            row.style.display = 'flex';
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

function setupUserEvents() {
    $('add-user-btn')?.addEventListener('click', () => {
        editingUserId = null;
        $('user-modal-title').textContent = '➕ Thêm User Mới';
        $('user-form').reset();
        $('user-password').required = true;
        $('user-password').placeholder = 'Nhập mật khẩu';
        
        toggleChildFields('child');
        
        openModal('user-modal');
    });

    // Search với debounce
    let searchTimeout;
    $('search-users')?.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            applyCurrentFilters();
        }, 300); // Debounce 300ms
    });

    // Role filter
    $('filter-user-role')?.addEventListener('change', () => {
        applyCurrentFilters();
    });

    // Reset filters button
    $('reset-users-filter-btn')?.addEventListener('click', () => {
        resetFilters();
    });

    // Refresh button
    $('refresh-users-btn')?.addEventListener('click', async () => {
        await loadUsers();
        showNotification('Đã làm mới danh sách users', 'success');
    });

    $('user-role')?.addEventListener('change', (e) => {
        toggleChildFields(e.target.value);
    });

    $('user-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();

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
                if (!dateOfBirth) {
                    showNotification("❌ Vui lòng nhập ngày sinh!", "error");
                    return;
                }
                
                const birthDate = new Date(dateOfBirth);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                
                if (birthDate > today) {
                    showNotification("❌ Ngày sinh không thể là tương lai!", "error");
                    return;
                }
                
                if (!gender) {
                    showNotification("❌ Vui lòng chọn giới tính!", "error");
                    return;
                }
                
                if (!phone) {
                    showNotification("❌ Vui lòng nhập số điện thoại!", "error");
                    return;
                }
                
                if (!/^\d{10}$/.test(phone)) {
                    showNotification("❌ Số điện thoại phải là 10 chữ số!", "error");
                    return;
                }
                
                const age = calculateAge(dateOfBirth);
                
                if (age === null || age < 0) {
                    showNotification("❌ Ngày sinh không hợp lệ!", "error");
                    return;
                }
                
                const formattedDate = birthDate.toISOString().split('T')[0];
                
                data.date_of_birth = formattedDate;
                data.gender = gender.toLowerCase();
                data.phone_number = phone;
                data.age = age;
            } else {
                if (gender) {
                    data.gender = gender.toLowerCase();
                }
                
                if (phone) {
                    if (!/^\d{10}$/.test(phone)) {
                        showNotification("❌ Số điện thoại phải là 10 chữ số!", "error");
                        return;
                    }
                    data.phone_number = phone;
                }
                
                if (dateOfBirth) {
                    const birthDate = new Date(dateOfBirth);
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    
                    if (birthDate > today) {
                        showNotification("❌ Ngày sinh không thể là tương lai!", "error");
                        return;
                    }
                    
                    const age = calculateAge(dateOfBirth);
                    if (age === null || age < 0) {
                        showNotification("❌ Ngày sinh không hợp lệ!", "error");
                        return;
                    }
                    
                    data.date_of_birth = birthDate.toISOString().split('T')[0];
                    data.age = age;
                }
            }
        }

        try {
            let res;

            const options = {
                headers: {
                    "Content-Type": "application/json"
                },
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

            showNotification("✔ Thành công!", "success");
            closeModal("user-modal");
            loadUsers();

        } catch (err) {
            console.error("❌ Submit error:", err);
            showNotification("❌ " + err.message, "error");
        }
    });

    $('cancel-user-btn')?.addEventListener('click', () => closeModal('user-modal'));
}

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

window.deleteUser = async (id) => {
    if (!confirm("⚠️ Bạn có chắc chắn muốn xóa user này?")) return;

    try {
        const res = await fetchAPI(`${API_URL}/users/${id}`, {
            method: "DELETE"
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Lỗi xóa user");
        }

        showNotification("✅ Đã xóa user!", "success");
        loadUsers();

    } catch (err) {
        console.error(err);
        showNotification(`❌ ${err.message}`, 'error');
    }
};

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

export { loadUsers, setupUserEvents };