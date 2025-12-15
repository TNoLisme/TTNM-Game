// ==================== CONSTANTS ====================
const API_BASE_URL = "http://localhost:8000";

// Emotion icons mapping
const EMOTION_ICONS = {
    'Vui vẻ': '😊',
    'Buồn bã': '😢',
    'Tức giận': '😠',
    'Sợ hãi': '😨',
    'Ngạc nhiên': '😲',
    'Ghê tởm': '🤢'
};

// Game type mapping
const GAME_TYPE_MAP = {
    'recognize_emotion': { name: 'Chiếc hộp cảm xúc', url: '/src/pages/level_select.html?gameId=ea2b5c7e-aec8-4f6e-a8bf-99d7b6a05dd8' },
    'game_click_2': { name: 'Xưởng lắp ghép cảm xúc', url: '/src/pages/level_select.html?gameId=ecefa8d8-b9f5-4d41-abf9-316e6b6cf25b' },
    'game_click_3': { name: 'Cảm xúc đúng chỗ', url: '/src/pages/level_select.html?gameId=e7b4826b-57ba-4569-953e-723da913d47c' },
    'game_click_4': { name: 'Thám tử cảm xúc', url: '/src/pages/level_select.html?gameId=8573ebd6-23be-4ad9-bd4c-3794b1c4a4fa' },
    'gameCV': { name: 'Game CV', url: '/src/pages/level_select.html?gameId=9b56e632-dd86-4868-9d74-e0c93125430a' },
    'game_cv_2': { name: 'Thử thách cảm xúc', url: '/src/pages/level_select.html?gameId=bbd1597f-02b1-4e20-b39b-31d27335d385' }
};

// Helper function to determine game type from name
function getGameTypeFromName(name) {
    const nameLower = name.toLowerCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '') // Remove accents
        .replace(/đ/g, 'd');
    
    // Thử thách cảm xúc
    if (nameLower.includes('thu thach') && nameLower.includes('cam xuc')) {
        return 'game_cv_2';
    }
    
    // Chiếc hộp cảm xúc
    if (nameLower.includes('chiec hop') && nameLower.includes('cam xuc')) {
        return 'recognize_emotion';
    }
    
    // Xưởng cảm xúc / Xưởng lắp ghép cảm xúc
    if ((nameLower.includes('xuong') && nameLower.includes('cam xuc')) || 
        (nameLower.includes('xuong lap ghep'))) {
        return 'game_click_2';
    }
    
    // Cảm xúc đúng chỗ
    if (nameLower.includes('cam xuc dung cho') ||
        (nameLower.includes('cam xuc') && nameLower.includes('dung cho')) ||
        (nameLower.includes('chon') && nameLower.includes('cam xuc') && nameLower.includes('tinh huong'))) {
        return 'game_click_3';
    }
    
    // Ai là ai
    if (nameLower.includes('ai la ai')) {
        return 'game_click_3';
    }
    
    // Thám tử cảm xúc
    if (nameLower.includes('tham tu') && nameLower.includes('cam xuc')) {
        return 'game_click_4';
    }
    
    // Game CV chuẩn
    if (nameLower.includes('game cv') || nameLower.includes('gamecv')) {
        return 'gameCV';
    }
    
    return null;
}

// ==================== STATE MANAGEMENT ====================
let currentUser = null;
let charts = {
    error: null,
    improvement: null,
    game: null
};

// ==================== UTILITY FUNCTIONS ====================
function getCurrentUserId() {
    const userStr = localStorage.getItem('currentUser');
    console.log('🔍 [getCurrentUserId] userStr:', userStr);
    
    if (!userStr) return null;
    
    try {
        const user = JSON.parse(userStr);
        console.log('✅ [getCurrentUserId] Parsed user:', user);
        const userId = user.user_id || user.id;
        console.log('✅ [getCurrentUserId] userId:', userId);
        return userId;
    } catch (e) {
        console.error('❌ [getCurrentUserId] Error parsing user data:', e);
        return null;
    }
}

function showError(message) {
    if (window.egModal && typeof window.egModal.alert === 'function') {
        window.egModal.alert(message, 'Lỗi');
    } else {
        alert(message);
    }
}

function showLoading(show = true) {
    const loadingElements = document.querySelectorAll('.loading-indicator');
    loadingElements.forEach(el => {
        el.style.display = show ? 'block' : 'none';
    });
}

// ==================== API FUNCTIONS ====================
async function fetchUserProfile(userId) {
    console.log('📡 [fetchUserProfile] Fetching profile for userId:', userId);
    try {
        const url = `${API_BASE_URL}/users/me?user_id=${userId}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch user profile');
        const data = await response.json();
        console.log('✅ [fetchUserProfile] Data:', data);
        return data;
    } catch (error) {
        console.error('❌ [fetchUserProfile] Error:', error);
        return null;
    }
}

async function fetchRecentGames(userId) {
    console.log('📡 [fetchRecentGames] Fetching for userId:', userId);
    try {
        const url = `${API_BASE_URL}/users/stats/recent-games/${userId}?limit=4`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch recent games');
        const data = await response.json();
        console.log('✅ [fetchRecentGames] Data:', data);
        return data.data || [];
    } catch (error) {
        console.error('❌ [fetchRecentGames] Error:', error);
        return [];
    }
}

async function fetchEmotionErrors(userId) {
    console.log('📡 [fetchEmotionErrors] Fetching for userId:', userId);
    try {
        const url = `${API_BASE_URL}/users/stats/emotion-errors/${userId}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch emotion errors');
        const data = await response.json();
        console.log('✅ [fetchEmotionErrors] Data:', data);
        return data.data || {};
    } catch (error) {
        console.error('❌ [fetchEmotionErrors] Error:', error);
        return {};
    }
}

async function fetchEmotionImprovement(userId) {
    console.log('📡 [fetchEmotionImprovement] Fetching for userId:', userId);
    try {
        const url = `${API_BASE_URL}/users/stats/emotion-improvement/${userId}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch emotion improvement');
        const data = await response.json();
        console.log('✅ [fetchEmotionImprovement] Data:', data);
        return data.data || {};
    } catch (error) {
        console.error('❌ [fetchEmotionImprovement] Error:', error);
        return {};
    }
}

async function fetchGamePlayRatio(userId) {
    console.log('📡 [fetchGamePlayRatio] Fetching for userId:', userId);
    try {
        const url = `${API_BASE_URL}/users/stats/game-play-ratio/${userId}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch game play ratio');
        const data = await response.json();
        console.log('✅ [fetchGamePlayRatio] Data:', data);
        return data.data || {};
    } catch (error) {
        console.error('❌ [fetchGamePlayRatio] Error:', error);
        return {};
    }
}

// ==================== EMOTION CARDS ====================
function getEmotionCardClass(errorRate) {
    if (errorRate <= 20) return 'low-error';
    if (errorRate <= 50) return 'medium-error';
    return 'high-error';
}

async function renderEmotionCards(userId) {
    console.log('🎴 [renderEmotionCards] Rendering emotion cards');
    const container = document.getElementById('emotionCardsContainer');
    
    if (!container) {
        console.error('❌ [renderEmotionCards] Container not found');
        return;
    }

    try {
        const errorStats = await fetchEmotionErrors(userId);
        console.log('📊 [renderEmotionCards] Error stats:', errorStats);

        // Convert to array and sort by error rate (low to high)
        const emotionArray = Object.entries(errorStats)
            .map(([name, rate]) => ({ name, rate }))
            .sort((a, b) => a.rate - b.rate);

        console.log('📊 [renderEmotionCards] Sorted emotions:', emotionArray);

        if (emotionArray.length === 0 || emotionArray.every(e => e.rate === 0)) {
            container.innerHTML = `
                <div class="no-data-message">
                    <div class="no-data-icon">📊</div>
                    <p>Chưa có dữ liệu về tỉ lệ sai của các cảm xúc.<br>Hãy chơi game để thu thập dữ liệu nhé!</p>
                </div>
            `;
            return;
        }

        // Render emotion cards
        container.innerHTML = emotionArray.map((emotion, index) => {
            const icon = EMOTION_ICONS[emotion.name] || '😊';
            const cardClass = getEmotionCardClass(emotion.rate);
            const rank = index + 1;

            return `
                <div class="emotion-card ${cardClass}" style="animation-delay: ${index * 0.1}s">
                    <div class="emotion-rank">#${rank}</div>
                    <div class="emotion-icon">${icon}</div>
                    <div class="emotion-name">${emotion.name}</div>
                    <div class="emotion-error-rate">${emotion.rate}%</div>
                    <div class="emotion-label">Tỉ lệ sai</div>
                </div>
            `;
        }).join('');

        // Add animation
        const cards = container.querySelectorAll('.emotion-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                card.style.transition = 'all 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });

        console.log('✅ [renderEmotionCards] Rendered', emotionArray.length, 'cards');

    } catch (error) {
        console.error('❌ [renderEmotionCards] Error:', error);
        container.innerHTML = `
            <div class="no-data-message">
                <div class="no-data-icon">⚠️</div>
                <p>Không thể tải dữ liệu cảm xúc</p>
            </div>
        `;
    }
}

// ==================== RECENT GAMES ====================
function renderRecentGames(games) {
    console.log('🎮 [renderRecentGames] Rendering games:', games);
    const gameList = document.querySelector('.recent-games-section .game-list');
    
    if (!gameList) {
        console.error('❌ [renderRecentGames] Game list container not found');
        return;
    }

    gameList.innerHTML = '';

    if (!games || games.length === 0) {
        console.log('⚠️ [renderRecentGames] No games to display');
        gameList.innerHTML = '<p class="no-games">Chưa có trò chơi nào được chơi gần đây</p>';
        return;
    }

    games.forEach((game, index) => {
        const gameCard = document.createElement('div');
        gameCard.className = 'game-card';
        gameCard.style.cursor = 'pointer';
        gameCard.style.animationDelay = `${index * 0.1}s`;
        
        let gameUrl = '/src/pages/select_game.html';
        let gameImagePath = '/fe/assets/images/default-game.jpg';
        let gameType = null;
        
        // Try to get game type from game.game_type first
        if (game.game_type && GAME_TYPE_MAP[game.game_type]) {
            gameType = game.game_type;
        } else {
            gameType = getGameTypeFromName(game.name);
        }
        
        if (gameType && GAME_TYPE_MAP[gameType]) {
            gameUrl = GAME_TYPE_MAP[gameType].url;
            gameImagePath = `/fe/assets/images/${gameType}.png`;
            console.log(`  📸 Image path: "${gameImagePath}"`);
            console.log(`  🔗 Game URL: "${gameUrl}"`);
        } else {
            console.warn(`  ⚠️ No gameType found! Using defaults`);
            console.log(`  📸 Default image: "${gameImagePath}"`);
            console.log(`  🔗 Default URL: "${gameUrl}"`);
        }

        gameCard.innerHTML = `
            <img src="${gameImagePath}" alt="${game.name}" onerror="this.src='/fe/assets/images/default-game.jpg'">
            <p class="game-name">${game.name}</p>
        `;

        gameCard.addEventListener('click', () => {
            window.location.href = gameUrl;
        });

        gameList.appendChild(gameCard);
    });
    
    console.log('✅ [renderRecentGames] Rendered', games.length, 'games');
}

// ==================== CHARTS ====================
function createBarChart(canvasId, labels, data, title) {
    console.log(`📊 [createBarChart] Creating chart for ${canvasId}`);
    
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`❌ [createBarChart] Canvas #${canvasId} not found!`);
        return null;
    }

    const chartKey = canvasId.replace('Chart', '');
    if (charts[chartKey]) {
        charts[chartKey].destroy();
    }

    if (typeof Chart === 'undefined') {
        console.error('❌ [createBarChart] Chart.js not loaded!');
        return null;
    }

    const colors = [
        'rgba(255, 206, 86, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 99, 132, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(255, 159, 64, 0.8)'
    ];

    try {
        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: title,
                    data: data,
                    backgroundColor: colors.slice(0, data.length),
                    borderColor: colors.slice(0, data.length).map(c => c.replace('0.8', '1')),
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        callbacks: {
                            label: (context) => title + ': ' + context.parsed.y.toFixed(1) + '%'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: (value) => value + '%'
                        }
                    }
                }
            }
        });
        
        console.log(`✅ [createBarChart] Chart created`);
        return chart;
    } catch (error) {
        console.error(`❌ [createBarChart] Error:`, error);
        return null;
    }
}

function createDoughnutChart(canvasId, labels, data, title) {
    console.log(`📊 [createDoughnutChart] Creating chart for ${canvasId}`);
    
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`❌ [createDoughnutChart] Canvas #${canvasId} not found!`);
        return null;
    }

    if (charts.game) {
        charts.game.destroy();
    }

    if (typeof Chart === 'undefined') {
        console.error('❌ [createDoughnutChart] Chart.js not loaded!');
        return null;
    }

    const colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)'
    ];

    try {
        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors.slice(0, data.length),
                    borderColor: '#fff',
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { padding: 15 }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => context.label + ': ' + context.parsed.toFixed(1) + '%'
                        }
                    }
                }
            }
        });
        
        console.log(`✅ [createDoughnutChart] Chart created`);
        return chart;
    } catch (error) {
        console.error(`❌ [createDoughnutChart] Error:`, error);
        return null;
    }
}

async function renderCharts(userId) {
    console.log('📊 [renderCharts] Starting...');
    
    try {
        const [errorStats, improvementStats, gameRatioStats] = await Promise.all([
            fetchEmotionErrors(userId),
            fetchEmotionImprovement(userId),
            fetchGamePlayRatio(userId)
        ]);

        // Chart 1: Error rate
        if (Object.keys(errorStats).length > 0) {
            const errorLabels = Object.keys(errorStats);
            const errorData = Object.values(errorStats);
            charts.error = createBarChart('errorChart', errorLabels, errorData, 'Tỉ lệ sai');
        }

        // Chart 2: Improvement rate
        if (Object.keys(improvementStats).length > 0) {
            const improvementLabels = Object.keys(improvementStats);
            const improvementData = Object.values(improvementStats);
            charts.improvement = createBarChart('improvementChart', improvementLabels, improvementData, 'Cải thiện');
        }

        // Chart 3: Game play ratio
        if (Object.keys(gameRatioStats).length > 0) {
            const gameLabels = Object.keys(gameRatioStats);
            const gameData = Object.values(gameRatioStats);
            charts.game = createDoughnutChart('gameChart', gameLabels, gameData, 'Tỉ lệ chơi');
        }

        console.log('✅ [renderCharts] Completed');

    } catch (error) {
        console.error('❌ [renderCharts] Error:', error);
    }
}

// ==================== NAVIGATION ====================
function initNavigation() {
    console.log('🧭 [initNavigation] Initializing...');
    
    const logoutBtn = document.querySelector('#logout-button');
    const profileButton = document.querySelector('#profile-button');
    const goToGameSelectBtn = document.querySelector('#go-to-game-select');
    const gameNavLink = document.querySelector('#game-nav-link');

    if (!window.egInlineConfirm) {
        window.egEnsureInlineConfirmModal = function () {
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
        };

        window.egInlineConfirm = function (message, title, okText, cancelText) {
            window.egEnsureInlineConfirmModal();

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
        };
    }

    logoutBtn?.addEventListener('click', async () => {
        const doLogout = () => {
            localStorage.removeItem('currentUser');
            window.location.href = '/src/pages/login.html';
        };

        if (window.egModal && typeof window.egModal.confirm === 'function') {
            window.egModal
                .confirm('Bạn có chắc chắn muốn đăng xuất không?', 'Xác nhận đăng xuất', 'Đăng xuất', 'Hủy')
                .then((ok) => { if (ok) doLogout(); });
        } else {
            if (confirm('Bạn có chắc chắn muốn đăng xuất không?')) {
                doLogout();
            }
        }

        const ok = await window.egInlineConfirm(
            'Bạn có chắc chắn muốn đăng xuất không?',
            'Xác nhận đăng xuất',
            'Đăng xuất',
            'Hủy'
        );
        if (!ok) return;
        doLogout();
    });

    profileButton?.addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = '/src/pages/profile.html';
    });

    goToGameSelectBtn?.addEventListener('click', () => {
        window.location.href = '/src/pages/select_game.html';
    });

    gameNavLink?.addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = '/src/pages/select_game.html';
    });
    
    console.log('✅ [initNavigation] Initialized');
}

// ==================== INITIALIZATION ====================
async function initializePage() {
    console.log('🚀 [initializePage] Starting...');
    
    const userId = getCurrentUserId();
    
    if (!userId) {
        console.error('❌ [initializePage] No userId');
        showError('Vui lòng đăng nhập để tiếp tục');
        window.location.href = '/src/pages/login.html';
        return;
    }

    try {
        showLoading(true);

        // Initialize navigation
        initNavigation();

        // Fetch user profile
        currentUser = await fetchUserProfile(userId);

        // Render emotion cards (NEW!)
        await renderEmotionCards(userId);

        // Fetch and render recent games
        const recentGames = await fetchRecentGames(userId);
        renderRecentGames(recentGames);

        // Render charts
        await renderCharts(userId);

        showLoading(false);
        console.log('✅ [initializePage] Completed');

    } catch (error) {
        console.error('❌ [initializePage] Error:', error);
        showError('Có lỗi xảy ra khi tải dữ liệu');
        showLoading(false);
    }
}

// ==================== EVENT LISTENERS ====================
document.addEventListener('DOMContentLoaded', initializePage);

// Cleanup
window.addEventListener('beforeunload', () => {
    Object.values(charts).forEach(chart => {
        if (chart) chart.destroy();
    });
});