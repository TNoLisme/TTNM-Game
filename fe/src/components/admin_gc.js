// gameContents.js - Quản lý Game Contents

import { API_URL, $, fetchAPI, openModal, closeModal, showNotification, getEmotionEmoji } from './admin.js';

let currentGameContents = [];
let editingGameContentId = null;
let currentMediaFile = null;
let gamesList = []; // Cache danh sách games

// 🆕 Tải danh sách Game để đưa vào Dropdown
async function loadGamesList() {
    try {
        // Giả định endpoint API lấy tất cả games là /games/
        const res = await fetchAPI("http://localhost:8000/games/");
        if (!res.ok) throw new Error("Không thể tải danh sách Games");

        const data = await res.json();
        gamesList = data.data || data; // Tùy cấu trúc trả về

        populateGameDropdown();

    } catch (err) {
        console.error("❌ Load games error:", err);
    }
}

function populateGameDropdown() {
    const select = $('gc-game-id');
    if (!select) return;

    select.innerHTML = '<option value="">-- Chọn Game --</option>';

    gamesList.forEach(game => {
        const option = document.createElement('option');
        option.value = game.game_id;
        option.textContent = game.name || game.game_id;
        select.appendChild(option);
    });
}

async function loadGameContents(filters = {}) {
    try {
        let url = `${API_URL}/game-contents?skip=0&limit=100`;

        // 🔄 Cập nhật Search: Dùng search=... thay vì game_id
        if (filters.search) url += `&search=${encodeURIComponent(filters.search)}`;
        if (filters.level) url += `&level=${filters.level}`;
        if (filters.emotion) url += `&emotion=${filters.emotion}`;

        console.log('📡 Loading game contents from:', url);

        const res = await fetchAPI(url);

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();

        currentGameContents = data.data?.game_contents || [];

        renderGameContentsTable(currentGameContents);

        if ($('total-game-contents')) {
            $('total-game-contents').textContent = data.data?.total || currentGameContents.length;
        }

    } catch (err) {
        console.error("❌ Load game contents error:", err);
        showNotification(`Lỗi tải nội dung game: ${err.message}`, 'error');
    }
}

function renderGameContentsTable(contents) {
    const tbody = $('game-contents-tbody');

    if (!tbody) {
        console.error("Không tìm thấy #game-contents-tbody trong DOM!");
        return;
    }

    if (!contents || contents.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align:center; padding: 30px;">
                    <div style="color: #999;">
                        <i class="fas fa-inbox" style="font-size: 48px; margin-bottom: 10px;"></i>
                        <p>Chưa có nội dung game nào</p>
                    </div>
                </td>
            </tr>`;
        return;
    }

    tbody.innerHTML = contents.map(content => `
        <tr>
            <td title="${content.content_id}">${content.content_id.substring(0, 8)}...</td>
            <td title="${content.game_id}">${content.game_id.substring(0, 8)}...</td>
            <td><span class="badge badge-info">Level ${content.level}</span></td>
            <td><span class="badge badge-secondary">${content.content_type}</span></td>
            <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis;" title="${content.question_text}">
                ${content.question_text.substring(0, 50)}${content.question_text.length > 50 ? '...' : ''}
            </td>
            <td>${content.emotion ? getEmotionEmoji(content.emotion) + ' ' + content.emotion : '<span style="color:#999">N/A</span>'}</td>
            <td>${content.media_path ? '✅' : '❌'}</td>
            <td class="actions">
                <button class="btn btn-warning" onclick="window.editGameContent('${content.content_id}')" title="Chỉnh sửa">✏️</button>
                <button class="btn btn-danger" onclick="window.deleteGameContent('${content.content_id}')" title="Xóa">🗑️</button>
            </td>
        </tr>
    `).join('');
}

function setupGameContentEvents() {
    // Gọi load games khi khởi tạo
    loadGamesList();

    $('add-game-content-btn')?.addEventListener('click', () => {
        editingGameContentId = null;
        $('game-content-modal-title').textContent = '➕ Thêm Nội dung Game';
        $('game-content-form').reset();
        currentMediaFile = null;
        $('gc-media-preview').style.display = 'none';

        $('gc-game-id').disabled = false;

        openModal('game-content-modal');
    });

    $('apply-filters-btn')?.addEventListener('click', () => {
        const filters = {
            search: $('filter-question').value, // 🆕 Thay đổi ID filter
            level: $('filter-level').value,
            emotion: $('filter-emotion').value
        };

        loadGameContents(filters);
    });

    // Sự kiện chọn file media (Giữ nguyên)
    $('gc-media-file')?.addEventListener('change', (e) => {
        const file = e.target.files[0];

        if (!file) {
            currentMediaFile = null;
            $('gc-media-preview').style.display = 'none';
            return;
        }

        currentMediaFile = file;
        const previewContent = $('gc-media-preview-content');
        const reader = new FileReader();

        reader.onload = (e) => {
            let html = '';
            if (file.type.startsWith('image/')) {
                html = `<img src="${e.target.result}" style="max-width: 300px; border-radius: 8px;">`;
            } else if (file.type.startsWith('video/')) {
                html = `<video src="${e.target.result}" controls style="max-width: 300px; border-radius: 8px;"></video>`;
            } else if (file.type.startsWith('audio/')) {
                html = `<audio src="${e.target.result}" controls style="width: 100%;"></audio>`;
            }
            previewContent.innerHTML = html;
            $('gc-media-preview').style.display = 'block';
        };
        reader.readAsDataURL(file);
    });

    $('game-content-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = e.target.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Đang xử lý...';

        try {
            let mediaPath = null;

            // Logic Upload file (Giữ nguyên)
            if (currentMediaFile) {
                const formData = new FormData();
                formData.append('file', currentMediaFile);
                formData.append('content_type', $('gc-content-type').value);
                // Lấy tên game để tạo folder (nếu có, không thì default)
                const gameSelect = $('gc-game-id');
                const gameName = gameSelect.options[gameSelect.selectedIndex].text || 'emotion_game';
                formData.append('game_name', gameName.replace(/[^a-zA-Z0-9]/g, '')); // Clean name
                formData.append('emotion', $('gc-emotion').value || '');

                const uploadRes = await fetch(`${API_URL}/game-contents/upload-media`, {
                    method: 'POST',
                    body: formData
                });

                const uploadData = await uploadRes.json();
                if (!uploadRes.ok || uploadData.status !== 'success') {
                    throw new Error(uploadData.message || 'Lỗi upload media');
                }
                mediaPath = uploadData.data.media_path;
            }

            // 🆕 Lấy giá trị Emotion làm Correct Answer
            const emotionVal = $('gc-emotion').value || null;

            const data = {
                game_id: $('gc-game-id').value,
                level: parseInt($('gc-level').value),
                content_type: $('gc-content-type').value,
                question_text: $('gc-question-text').value,
                correct_answer: emotionVal, // 👈 Tự động gán
                emotion: emotionVal,
                explanation: $('gc-explanation').value || null,
                media_path: mediaPath
            };

            if (!data.game_id) throw new Error('Vui lòng chọn Game!');

            let res;
            if (editingGameContentId) {
                res = await fetchAPI(`${API_URL}/game-contents/${editingGameContentId}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });
            } else {
                res = await fetchAPI(`${API_URL}/game-contents`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });
            }

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Lỗi API");
            }

            showNotification("✔ Thành công!", "success");
            closeModal("game-content-modal");
            loadGameContents();

        } catch (err) {
            console.error('❌ Save error:', err);
            showNotification("❌ " + err.message, "error");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = '💾 Lưu';
        }
    });

    $('cancel-game-content-btn')?.addEventListener('click', () => closeModal('game-content-modal'));
}

window.editGameContent = async (content_id) => {
    editingGameContentId = content_id;

    try {
        const res = await fetchAPI(`${API_URL}/game-contents/${content_id}`);

        if (!res.ok) {
            throw new Error('Không tìm thấy nội dung');
        }

        const data = await res.json();
        const content = data.data;

        $('game-content-modal-title').textContent = '✏️ Chỉnh sửa Nội dung Game';

        // Populate fields
        $('gc-game-id').value = content.game_id;
        $('gc-game-id').disabled = false; // Có thể disable nếu không muốn cho đổi game

        $('gc-level').value = content.level;
        $('gc-content-type').value = content.content_type;
        $('gc-emotion').value = content.emotion || '';
        $('gc-question-text').value = content.question_text;
        // Bỏ correct_answer field vì nó tự động theo emotion
        $('gc-explanation').value = content.explanation || '';

        openModal('game-content-modal');

    } catch (err) {
        console.error('❌ Edit error:', err);
        showNotification(`❌ ${err.message}`, 'error');
    }
};

window.deleteGameContent = async (content_id) => {
    if (!confirm("⚠️ Bạn có chắc chắn muốn xóa nội dung này?")) return;

    try {
        const res = await fetchAPI(`${API_URL}/game-contents/${content_id}`, {
            method: "DELETE"
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Lỗi xóa nội dung");
        }

        showNotification("✅ Đã xóa nội dung!", "success");
        loadGameContents();

    } catch (err) {
        console.error('❌ Delete error:', err);
        showNotification(`❌ ${err.message}`, 'error');
    }
};

export { loadGameContents, setupGameContentEvents };