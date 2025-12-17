// gameContents.js - Quản lý Game Contents (THEO PATTERN EMOTION)

import {
    API_URL,
    $,
    fetchAPI,
    openModal,
    closeModal,
    showNotification,
    getEmotionEmoji
} from './admin.js';

let currentGameContents = [];
let editingContentId = null;
let currentMediaFile = null; // File media đang chọn
let gamesList = [];
let currentFilters = {};

// ====================== LOAD GAMES ======================
async function loadGamesList() {
    try {
        const res = await fetchAPI("http://localhost:8000/games/");
        if (!res.ok) throw new Error("Không thể tải danh sách Games");

        const data = await res.json();
        gamesList = data.data || data;
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

// ====================== LOAD & RENDER GAME CONTENTS ======================
async function loadGameContents(filters = {}) {
    try {
        let url = `${API_URL}/game-contents?skip=0&limit=100`;

        if (filters.search) url += `&search=${encodeURIComponent(filters.search)}`;
        if (filters.level) url += `&level=${filters.level}`;
        if (filters.emotion) url += `&emotion=${filters.emotion}`;

        console.log('📡 [DEBUG] Loading game contents from:', url);

        const res = await fetchAPI(url);
        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();
        currentGameContents = data.data?.game_contents || [];
        
        console.log('📦 [DEBUG] Loaded contents:', currentGameContents.length);
        if (currentGameContents.length > 0) {
            console.log('📦 [DEBUG] Sample content:', JSON.stringify(currentGameContents[0], null, 2));
            console.log('📦 [DEBUG] All media_paths:');
            currentGameContents.forEach((c, i) => {
                console.log(`  ${i + 1}. ${c.content_id.substring(0, 8)}... → ${c.media_path || '(no media)'}`);
            });
        }
        
        renderGameContentsTable(currentGameContents);

        if ($('total-game-contents')) {
            $('total-game-contents').textContent = data.data?.total || currentGameContents.length;
        }
    } catch (err) {
        console.error("❌ [DEBUG] Load game contents error:", err);
        showNotification(`❌ ${err.message}`, 'error');
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
            </tr>
        `;
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
            <td>
                ${content.emotion
                    ? getEmotionEmoji(content.emotion) + ' ' + content.emotion
                    : '<span style="color:#999">N/A</span>'
                }
            </td>
            <td>${content.media_path ? '✅' : '❌'}</td>
            <td class="actions">
                <button class="btn btn-warning" onclick="window.editGameContent('${content.content_id}')" title="Chỉnh sửa">✏️</button>
                <button class="btn btn-danger" onclick="window.deleteGameContent('${content.content_id}')" title="Xóa">🗑️</button>
            </td>
        </tr>
    `).join('');
}

function resetFilters() {
    if ($('search-game-contents')) $('search-game-contents').value = '';
    if ($('filter-level')) $('filter-level').value = '';
    if ($('filter-emotion')) $('filter-emotion').value = '';
    currentFilters = {};
    loadGameContents();
}

// ====================== SETUP EVENTS (GIỐNG EMOTION) ======================
function setupGameContentEvents() {
    loadGamesList();

    // ----- Nút thêm mới -----
    $('add-game-content-btn')?.addEventListener('click', () => {
        editingContentId = null;
        $('game-content-modal-title').textContent = '➕ Thêm Nội dung Game';
        $('game-content-form').reset();
        
        // Reset media
        currentMediaFile = null;
        const fileInput = $('gc-media-file');
        if (fileInput) fileInput.value = '';
        
        const previewContainer = $('gc-media-preview');
        if (previewContainer) previewContainer.style.display = 'none';
        
        $('gc-game-id').disabled = false;
        openModal('game-content-modal');
    });

    // ----- Apply filters -----
    $('apply-filters-btn')?.addEventListener('click', () => {
        currentFilters = {
            search: $('search-game-contents')?.value || '',
            level: $('filter-level')?.value || '',
            emotion: $('filter-emotion')?.value || ''
        };
        loadGameContents(currentFilters);
    });

    // ----- Reset filters -----
    $('reset-filters-btn')?.addEventListener('click', resetFilters);

    // ----- Chọn file media (GIỐNG EMOTION LOGIC 100%) -----
    const fileInput = $('gc-media-file');
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];

            if (!file) {
                currentMediaFile = null;
                const previewContainer = $('gc-media-preview');
                if (previewContainer) previewContainer.style.display = 'none';
                return;
            }

            // Validate loại file (support image/video/audio)
            const validTypes = [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp',
                'video/mp4', 'video/webm',
                'audio/mpeg', 'audio/wav', 'audio/ogg'
            ];
            
            if (!validTypes.includes(file.type)) {
                alert('❌ Vui lòng chọn file hợp lệ (image/video/audio)!');
                e.target.value = '';
                currentMediaFile = null;
                const previewContainer = $('gc-media-preview');
                if (previewContainer) previewContainer.style.display = 'none';
                return;
            }

            // Validate kích thước (50MB)
            if (file.size > 50 * 1024 * 1024) {
                alert('❌ File quá lớn! Tối đa 50MB.');
                e.target.value = '';
                currentMediaFile = null;
                const previewContainer = $('gc-media-preview');
                if (previewContainer) previewContainer.style.display = 'none';
                return;
            }

            // Lưu lại file đang chọn
            currentMediaFile = file;

            // Preview media
            const reader = new FileReader();
            reader.onload = (ev) => {
                const previewContent = $('gc-media-preview-content');
                const previewContainer = $('gc-media-preview');
                const fileNameEl = $('gc-file-name');
                const fileSizeEl = $('gc-file-size');

                let html = '';

                if (file.type.startsWith('image/')) {
                    html = `<img src="${ev.target.result}" style="max-width: 300px; border-radius: 8px;">`;
                } else if (file.type.startsWith('video/')) {
                    html = `<video src="${ev.target.result}" controls style="max-width: 300px; border-radius: 8px;"></video>`;
                } else if (file.type.startsWith('audio/')) {
                    html = `<audio src="${ev.target.result}" controls style="width: 100%;"></audio>`;
                }

                if (previewContent) previewContent.innerHTML = html;
                if (previewContainer) previewContainer.style.display = 'block';
                if (fileNameEl) fileNameEl.textContent = file.name;
                if (fileSizeEl) fileSizeEl.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
            };
            reader.readAsDataURL(file);
        });
    }

    // ----- Submit form (GIỐNG EMOTION LOGIC) -----
    const form = $('game-content-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const gameId = $('gc-game-id').value;
            if (!gameId) {
                alert('❌ Vui lòng chọn Game!');
                return;
            }

            if (!currentMediaFile && !editingContentId) {
                alert('❌ Vui lòng chọn media file!');
                return;
            }

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = '⏳ Đang xử lý...';
            }

            try {
                // 🔥 UPLOAD MEDIA TRƯỚC (nếu có file mới) - THEO PATTERN EMOTION
                let mediaPath = '';
                
                if (currentMediaFile) {
                    // Lấy thông tin content hiện tại để có old_path
                    let oldPath = '';
                    if (editingContentId) {
                        const content = currentGameContents.find(c => c.content_id === editingContentId);
                        oldPath = content?.media_path || '';
                        console.log('📝 [DEBUG] Editing content - Old path:', oldPath);
                    }

                    const formData = new FormData();
                    // ✅ GIỐNG EMOTION: media_file (không phải 'file')
                    formData.append('media_file', currentMediaFile);
                    formData.append('content_id', editingContentId || 'new');
                    formData.append('game_id', gameId);
                    formData.append('content_type', $('gc-content-type').value);
                    formData.append('emotion', $('gc-emotion').value || '');
                    formData.append('old_path', oldPath); // ✅ Backend sẽ xóa file cũ

                    console.log('📤 [DEBUG] Upload Request:', {
                        endpoint: `${API_URL}/game-contents/upload-media`,
                        fileName: currentMediaFile.name,
                        fileType: currentMediaFile.type,
                        fileSize: `${(currentMediaFile.size / 1024 / 1024).toFixed(2)} MB`,
                        content_id: editingContentId || 'new',
                        game_id: gameId,
                        content_type: $('gc-content-type').value,
                        emotion: $('gc-emotion').value || '',
                        old_path: oldPath
                    });

                    const uploadRes = await fetch(`${API_URL}/game-contents/upload-media`, {
                        method: 'POST',
                        body: formData
                    });

                    console.log('📥 [DEBUG] Upload Response Status:', uploadRes.status, uploadRes.statusText);

                    const uploadData = await uploadRes.json();
                    console.log('📥 [DEBUG] Upload Response Data:', JSON.stringify(uploadData, null, 2));

                    if (!uploadRes.ok || uploadData.status !== 'success') {
                        console.error('❌ [DEBUG] Upload Failed:', uploadData);
                        throw new Error(uploadData.detail || uploadData.message || 'Lỗi upload media');
                    }

                    mediaPath = uploadData.data.media_path;
                    console.log('✅ [DEBUG] Media uploaded successfully!');
                    console.log('📍 [DEBUG] New media_path:', mediaPath);
                } else if (editingContentId) {
                    // Đang edit nhưng KHÔNG upload file mới → giữ path cũ
                    const content = currentGameContents.find(c => c.content_id === editingContentId);
                    mediaPath = content?.media_path || '';
                    console.log('🔄 [DEBUG] No new file - keeping old path:', mediaPath);
                }

                // 🔥 TẠO/CÂP NHẬT GAME CONTENT
                const emotionVal = $('gc-emotion').value || null;
                const data = {
                    game_id: gameId,
                    level: parseInt($('gc-level').value),
                    content_type: $('gc-content-type').value,
                    question_text: $('gc-question-text').value,
                    correct_answer: emotionVal,
                    emotion: emotionVal,
                    explanation: $('gc-explanation').value || null,
                    media_path: mediaPath
                };

                let res;
                if (editingContentId) {
                    res = await fetchAPI(`${API_URL}/game-contents/${editingContentId}`, {
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

                showNotification(
                    editingContentId 
                        ? "✅ Cập nhật thành công!" 
                        : "✅ Thêm mới thành công!", 
                    "success"
                );
                
                closeModal("game-content-modal");
                currentMediaFile = null;
                await loadGameContents(currentFilters);
                
            } catch (err) {
                console.error('❌ Save error:', err);
                showNotification(`❌ ${err.message}`, "error");
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = '💾 Lưu';
                }
            }
        });
    }

    // ----- Nút Huỷ (GIỐNG EMOTION) -----
    $('cancel-game-content-btn')?.addEventListener('click', () => {
        closeModal('game-content-modal');
        const fileInput = $('gc-media-file');
        if (fileInput) fileInput.value = '';
        currentMediaFile = null;
        const previewContainer = $('gc-media-preview');
        if (previewContainer) previewContainer.style.display = 'none';
    });
}

// ====================== GLOBAL HANDLERS ======================

window.editGameContent = async (content_id) => {
    editingContentId = content_id;

    try {
        console.log('🔍 [DEBUG] Edit Content ID:', content_id);
        
        const res = await fetchAPI(`${API_URL}/game-contents/${content_id}`);
        if (!res.ok) throw new Error('Không tìm thấy nội dung');

        const data = await res.json();
        const content = data.data;

        console.log('📦 [DEBUG] Content Data:', JSON.stringify(content, null, 2));

        $('game-content-modal-title').textContent = '✏️ Chỉnh sửa Nội dung Game';
        $('gc-game-id').value = content.game_id;
        $('gc-game-id').disabled = false;
        $('gc-level').value = content.level;
        $('gc-content-type').value = content.content_type;
        $('gc-emotion').value = content.emotion || '';
        $('gc-question-text').value = content.question_text;
        $('gc-explanation').value = content.explanation || '';

        // Reset trạng thái file (GIỐNG EMOTION)
        currentMediaFile = null;
        const fileInput = $('gc-media-file');
        if (fileInput) fileInput.value = '';

        const previewContainer = $('gc-media-preview');
        const previewContent = $('gc-media-preview-content');
        const fileNameEl = $('gc-file-name');
        const fileSizeEl = $('gc-file-size');

        // Hiển thị media hiện tại (nếu có)
        if (content.media_path) {
            console.log('🖼️ [DEBUG] Original media_path from DB:', content.media_path);
            
            let mediaUrl = content.media_path;
            
            // Xử lý URL (giống logic emotion)
            console.log('🔧 [DEBUG] Processing URL...');
            
            if (!mediaUrl.startsWith('http')) {
                console.log('  ℹ️ Not HTTP URL, processing relative path');
                
                if (mediaUrl.startsWith('../')) {
                    console.log('  ✅ Path starts with ../ - keeping as is');
                    mediaUrl = content.media_path;
                } else if (mediaUrl.startsWith('/uploads/') || mediaUrl.startsWith('uploads/')) {
                    console.log('  ✅ Path is /uploads/ - prepending API_URL');
                    mediaUrl = `${API_URL}${mediaUrl.startsWith('/') ? '' : '/'}${mediaUrl}`;
                } else if (mediaUrl.startsWith('/assets/')) {
                    console.log('  ✅ Path is /fe/ or /assets/ - keeping as is');
                    mediaUrl = content.media_path;
                } else if (mediaUrl.startsWith('/fe/')) {
                    console.log('  ✅ Path is /fe/ strip /fe ');
                    mediaUrl = content.media_path.replace(/^\/fe\//, '/');
                } else {
                    console.log('  ⚠️ Unknown path format, keeping as is');
                }
            } else {
                console.log('  ℹ️ Already HTTP URL');
            }
            
            console.log('🌐 [DEBUG] Final media URL:', mediaUrl);

            let html = '';
            const contentType = content.content_type;

            console.log('🎨 [DEBUG] Rendering preview for type:', contentType);

            if (contentType === 'image' || mediaUrl.match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
                console.log('  📷 Rendering IMAGE');
                html = `<img src="${mediaUrl}" style="max-width: 300px; border-radius: 8px;" onerror="console.error('❌ [DEBUG] Image load failed:', this.src); this.parentElement.innerHTML='<p style=color:red>❌ Không thể tải hình ảnh<br><small>${mediaUrl}</small></p>'" onload="console.log('✅ [DEBUG] Image loaded successfully:', this.src)">`;
            } else if (contentType === 'video' || mediaUrl.match(/\.(mp4|webm)$/i)) {
                console.log('  🎬 Rendering VIDEO');
                html = `<video src="${mediaUrl}" controls style="max-width: 300px; border-radius: 8px;" onerror="console.error('❌ [DEBUG] Video load failed:', this.src); this.parentElement.innerHTML='<p style=color:red>❌ Không thể tải video<br><small>${mediaUrl}</small></p>'" onloadeddata="console.log('✅ [DEBUG] Video loaded successfully:', this.src)"></video>`;
            } else if (contentType === 'audio' || mediaUrl.match(/\.(mp3|wav|ogg)$/i)) {
                console.log('  🔊 Rendering AUDIO');
                html = `<audio src="${mediaUrl}" controls style="width: 100%;" onerror="console.error('❌ [DEBUG] Audio load failed:', this.src); this.parentElement.innerHTML='<p style=color:red>❌ Không thể tải audio<br><small>${mediaUrl}</small></p>'" onloadeddata="console.log('✅ [DEBUG] Audio loaded successfully:', this.src)"></audio>`;
            }

            if (html) {
                console.log('✅ [DEBUG] Preview HTML generated, displaying...');
                if (previewContent) previewContent.innerHTML = html;
                if (previewContainer) previewContainer.style.display = 'block';
                if (fileNameEl) fileNameEl.textContent = content.media_path;
                if (fileSizeEl) fileSizeEl.textContent = '';
            } else {
                console.warn('⚠️ [DEBUG] No HTML generated for preview');
            }
        } else {
            console.log('ℹ️ [DEBUG] No media_path found in content');
            if (previewContainer) previewContainer.style.display = 'none';
        }

        openModal('game-content-modal');
    } catch (err) {
        console.error('❌ [DEBUG] Edit error:', err);
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
        loadGameContents(currentFilters);
    } catch (err) {
        console.error('❌ Delete error:', err);
        showNotification(`❌ ${err.message}`, 'error');
    }
};

// ====================== EXPORT ======================
export {
    loadGameContents,
    setupGameContentEvents,
    resetFilters
};