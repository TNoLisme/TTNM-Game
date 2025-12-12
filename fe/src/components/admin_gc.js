// gameContents.js - Quản lý Game Contents

import { API_URL, $, fetchAPI, openModal, closeModal, showNotification, getEmotionEmoji } from './admin.js';

let currentGameContents = [];
let editingGameContentId = null;
let currentMediaFile = null;

async function loadGameContents(filters = {}) {
    try {
        let url = `${API_URL}/game-contents?skip=0&limit=100`;
        
        if (filters.game_id) url += `&game_id=${filters.game_id}`;
        if (filters.level) url += `&level=${filters.level}`;
        if (filters.emotion) url += `&emotion=${filters.emotion}`;
        
        console.log('📡 Loading game contents from:', url);
        
        const res = await fetchAPI(url);

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();
        console.log('📦 Received data:', data);
        
        currentGameContents = data.data?.game_contents || [];
        
        console.log(`✅ Loaded ${currentGameContents.length} game contents`);
        
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
    $('add-game-content-btn')?.addEventListener('click', () => {
        editingGameContentId = null;
        $('game-content-modal-title').textContent = '➕ Thêm Nội dung Game';
        $('game-content-form').reset();
        currentMediaFile = null;
        $('gc-media-preview').style.display = 'none';
        
        $('gc-game-id').disabled = false;
        $('gc-game-id').value = '';
        
        openModal('game-content-modal');
    });

    $('apply-filters-btn')?.addEventListener('click', () => {
        const filters = {
            game_id: $('filter-game-id').value,
            level: $('filter-level').value,
            emotion: $('filter-emotion').value
        };
        
        console.log('🔍 Applying filters:', filters);
        loadGameContents(filters);
    });

    $('gc-media-file')?.addEventListener('change', (e) => {
        const file = e.target.files[0];
        
        if (!file) {
            currentMediaFile = null;
            $('gc-media-preview').style.display = 'none';
            return;
        }
        
        currentMediaFile = file;
        const previewContent = $('gc-media-preview-content');
        
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewContent.innerHTML = `<img src="${e.target.result}" style="max-width: 300px; border-radius: 8px;">`;
                $('gc-media-preview').style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else if (file.type.startsWith('video/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewContent.innerHTML = `<video src="${e.target.result}" controls style="max-width: 300px; border-radius: 8px;"></video>`;
                $('gc-media-preview').style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else if (file.type.startsWith('audio/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewContent.innerHTML = `<audio src="${e.target.result}" controls style="width: 100%;"></audio>`;
                $('gc-media-preview').style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });

    $('game-content-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = e.target.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Đang xử lý...';
        
        try {
            let mediaPath = null;
            
            if (currentMediaFile) {
                const formData = new FormData();
                formData.append('file', currentMediaFile);
                formData.append('content_type', $('gc-content-type').value);
                formData.append('game_name', 'emotion_game');
                formData.append('emotion', $('gc-emotion').value || '');
                
                console.log('📤 Uploading media...');
                
                const uploadRes = await fetch(`${API_URL}/game-contents/upload-media`, {
                    method: 'POST',
                    body: formData
                });
                
                const uploadData = await uploadRes.json();
                
                if (!uploadRes.ok || uploadData.status !== 'success') {
                    throw new Error(uploadData.message || 'Lỗi upload media');
                }
                
                mediaPath = uploadData.data.media_path;
                console.log('✅ Media uploaded:', mediaPath);
            }
            
            const data = {
                game_id: $('gc-game-id').value.trim(),
                level: parseInt($('gc-level').value),
                content_type: $('gc-content-type').value,
                question_text: $('gc-question-text').value,
                correct_answer: $('gc-correct-answer').value || null,
                emotion: $('gc-emotion').value || null,
                explanation: $('gc-explanation').value || null,
                media_path: mediaPath
            };
            
            const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
            if (!uuidRegex.test(data.game_id)) {
                throw new Error('Game ID phải là UUID hợp lệ (VD: 550e8400-e29b-41d4-a716-446655440000)');
            }
            
            console.log('💾 Saving game content:', data);
            
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
        
        console.log('📝 Editing content:', content);
        
        $('game-content-modal-title').textContent = '✏️ Chỉnh sửa Nội dung Game';
        
        $('gc-game-id').value = content.game_id;
        $('gc-game-id').disabled = false;
        
        $('gc-level').value = content.level;
        $('gc-content-type').value = content.content_type;
        $('gc-emotion').value = content.emotion || '';
        $('gc-question-text').value = content.question_text;
        $('gc-correct-answer').value = content.correct_answer || '';
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