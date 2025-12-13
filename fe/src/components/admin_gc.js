import { API_URL, $, fetchAPI, openModal, closeModal, showNotification, getEmotionEmoji } from './admin.js';

let currentGameContents = [];
let editingGameContentId = null;
let currentMediaFile = null;
let availableGames = []; // Lưu danh sách games từ API

// Load danh sách games từ API
async function loadAvailableGames() {
    try {
        console.log('📡 Loading available games...');
        const res = await fetchAPI(`${API_URL}/games?skip=0&limit=100`);
        
        if (!res.ok) {
            throw new Error('Không thể tải danh sách games');
        }
        
        const data = await res.json();
        availableGames = data.data?.games || [];
        
        console.log(`✅ Loaded ${availableGames.length} games:`, availableGames);
        
        // Populate game select dropdown trong filter
        populateGameFilterSelect();
        
    } catch (err) {
        console.error("❌ Load games error:", err);
        showNotification(`Lỗi tải danh sách games: ${err.message}`, 'error');
    }
}

// Populate game select dropdown cho FILTER
function populateGameFilterSelect() {
    const filterSelect = $('filter-game-id');
    if (filterSelect) {
        filterSelect.innerHTML = '<option value="">-- Tất cả games --</option>';
        
        availableGames.forEach(game => {
            const option = document.createElement('option');
            option.value = game.game_id;
            option.textContent = `${game.name} (Level ${game.level})`;
            filterSelect.appendChild(option);
        });
    }
}

// Populate game select dropdown cho MODAL (thêm/sửa)
function populateGameModalSelect() {
    const selectElement = $('gc-game-select');
    if (!selectElement) return;
    
    selectElement.innerHTML = '<option value="">-- Chọn game --</option>';
    
    availableGames.forEach(game => {
        const option = document.createElement('option');
        option.value = game.game_id;
        option.textContent = `${game.name} (Level ${game.level})`;
        option.dataset.gameType = game.game_type;
        selectElement.appendChild(option);
    });
}

async function loadGameContents() {
    try {
        // Build URL với tất cả filters hiện tại
        let url = `${API_URL}/game-contents?skip=0&limit=100`;
        
        const gameIdFilter = $('filter-game-id')?.value?.trim();
        const levelFilter = $('filter-level')?.value;
        const emotionFilter = $('filter-emotion')?.value;
        
        if (gameIdFilter) url += `&game_id=${encodeURIComponent(gameIdFilter)}`;
        if (levelFilter) url += `&level=${encodeURIComponent(levelFilter)}`;
        if (emotionFilter) url += `&emotion=${encodeURIComponent(emotionFilter)}`;
        
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
        
        // Áp dụng search filter nếu có
        applyCurrentFilters();
        
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

    tbody.innerHTML = contents.map(content => {
        // Tìm tên game từ game_id
        const game = availableGames.find(g => g.game_id === content.game_id);
        const gameName = game ? game.name : content.game_id.substring(0, 8) + '...';
        
        return `
        <tr>
            <td title="${content.content_id}">${content.content_id.substring(0, 8)}...</td>
            <td title="${content.game_id}">
                <span class="badge badge-primary">${gameName}</span>
            </td>
            <td><span class="badge badge-info">Level ${content.level}</span></td>
            <td><span class="badge badge-secondary">${content.content_type}</span></td>
            <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis;" title="${escapeHtml(content.question_text)}">
                ${escapeHtml(content.question_text.substring(0, 50))}${content.question_text.length > 50 ? '...' : ''}
            </td>
            <td>${content.emotion ? getEmotionEmoji(content.emotion) + ' ' + content.emotion : '<span style="color:#999">N/A</span>'}</td>
            <td>${content.media_path ? '✅' : '❌'}</td>
            <td class="actions">
                <button class="btn btn-warning" onclick="window.editGameContent('${content.content_id}')" title="Chỉnh sửa">✏️</button>
                <button class="btn btn-danger" onclick="window.deleteGameContent('${content.content_id}')" title="Xóa">🗑️</button>
            </td>
        </tr>
        `;
    }).join('');
}

function applyCurrentFilters() {
    const searchTerm = $('search-game-contents')?.value?.trim() || '';
    
    console.log('🔍 Applying search filter:', searchTerm);
    
    let filtered = [...currentGameContents];
    
    // Apply search
    if (searchTerm) {
        const term = searchTerm.toLowerCase();
        filtered = filtered.filter(content => {
            return (
                content.content_id?.toLowerCase().includes(term) ||
                content.game_id?.toLowerCase().includes(term) ||
                content.question_text?.toLowerCase().includes(term) ||
                content.emotion?.toLowerCase().includes(term) ||
                content.content_type?.toLowerCase().includes(term) ||
                content.correct_answer?.toLowerCase().includes(term) ||
                content.explanation?.toLowerCase().includes(term)
            );
        });
    }
    
    console.log(`✅ Filtered: ${filtered.length} / ${currentGameContents.length} game contents`);
    
    renderGameContentsTable(filtered);
    
    // Update total count
    if ($('total-game-contents')) {
        $('total-game-contents').textContent = filtered.length;
    }
}

function resetFilters() {
    // Clear all filters
    if ($('filter-game-id')) $('filter-game-id').value = '';
    if ($('filter-level')) $('filter-level').value = '';
    if ($('filter-emotion')) $('filter-emotion').value = '';
    if ($('search-game-contents')) $('search-game-contents').value = '';
    
    // Reload data
    loadGameContents();
    
    showNotification('Đã xóa bộ lọc', 'success');
}

function setupGameContentEvents() {
    // Load games khi khởi tạo
    loadAvailableGames();
    
    $('add-game-content-btn')?.addEventListener('click', () => {
        editingGameContentId = null;
        $('game-content-modal-title').textContent = '➕ Thêm Nội dung Game';
        $('game-content-form').reset();
        currentMediaFile = null;
        $('gc-media-preview').style.display = 'none';
        
        // Populate modal select
        populateGameModalSelect();
        
        // Reset game select
        if ($('gc-game-select')) {
            $('gc-game-select').value = '';
            $('gc-game-select').disabled = false;
        }
        
        // Ẩn game_id input (sẽ được set tự động khi chọn game)
        if ($('gc-game-id')) {
            $('gc-game-id').value = '';
        }
        
        openModal('game-content-modal');
    });

    // Khi chọn game trong modal, set game_id tương ứng
    $('gc-game-select')?.addEventListener('change', (e) => {
        const selectedGameId = e.target.value;
        if ($('gc-game-id')) {
            $('gc-game-id').value = selectedGameId;
        }
        
        console.log('✅ Selected game:', selectedGameId);
        const selectedGame = availableGames.find(g => g.game_id === selectedGameId);
        if (selectedGame) {
            console.log('📝 Game details:', selectedGame);
        }
    });

    // ✅ Auto-apply filters khi chọn game
    $('filter-game-id')?.addEventListener('change', () => {
        console.log('🔄 Game filter changed, reloading...');
        loadGameContents();
    });

    // ✅ Auto-apply filters khi chọn level
    $('filter-level')?.addEventListener('change', () => {
        console.log('🔄 Level filter changed, reloading...');
        loadGameContents();
    });

    // ✅ Auto-apply filters khi chọn emotion
    $('filter-emotion')?.addEventListener('change', () => {
        console.log('🔄 Emotion filter changed, reloading...');
        loadGameContents();
    });

    // Reset filters button
    $('reset-filters-btn')?.addEventListener('click', () => {
        resetFilters();
    });

    // Search input với debounce
    let searchTimeout;
    $('search-game-contents')?.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            applyCurrentFilters();
        }, 300); // Debounce 300ms
    });

    // Refresh button
    $('refresh-game-contents-btn')?.addEventListener('click', async () => {
        await loadGameContents();
        showNotification('Đã làm mới danh sách game contents', 'success');
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
            // Validate game selection
            const gameId = $('gc-game-id')?.value?.trim();
            if (!gameId) {
                throw new Error('Vui lòng chọn game trước khi lưu!');
            }
            
            // Validate UUID format
            const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
            if (!uuidRegex.test(gameId)) {
                throw new Error('Game ID không hợp lệ. Vui lòng chọn lại game.');
            }
            
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
                game_id: gameId,
                level: parseInt($('gc-level').value),
                content_type: $('gc-content-type').value,
                question_text: $('gc-question-text').value,
                correct_answer: $('gc-emotion').value,
                emotion: $('gc-emotion').value || null,
                explanation: $('gc-explanation').value || null,
                media_path: mediaPath
            };
            
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
        
        // Populate modal select
        populateGameModalSelect();
        
        // Set game select và disable (không cho đổi game khi edit)
        if ($('gc-game-select')) {
            $('gc-game-select').value = content.game_id;
            $('gc-game-select').disabled = true; // Không cho chỉnh sửa game
        }
        
        // Set game_id
        $('gc-game-id').value = content.game_id;
        
        $('gc-level').value = content.level;
        $('gc-content-type').value = content.content_type;
        $('gc-emotion').value = content.emotion || '';
        $('gc-question-text').value = content.question_text;
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

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

export { loadGameContents, setupGameContentEvents };