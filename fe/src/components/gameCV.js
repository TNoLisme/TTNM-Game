const API_URL = "http://localhost:8000";

const CV_GAME_CONFIG = {
    GV1: {
        id: "GV1",
        documentTitle: "Câu chuyện trên khuôn mặt",
        navTitle: "Câu chuyện trên khuôn mặt",
        endpoint: "/games/cv/scenarios",
        emptyLevelMessage: (level) => `Không có tình huống nào ở level ${level}. Vui lòng chọn level khác.`,
        introBuilder: (scenario) => `Con nghe tình huống nhé. ${scenario.description}`,
        summaryBuilder: (emotion) =>
            `Hôm nay con đã thể hiện cảm xúc rất tốt! Cảm xúc con làm giỏi nhất là ${emotion || "tất cả"}. Lần sau mình luyện thêm nhé!`,
    },
    GV2: {
        id: "GV2",
        documentTitle: "Thử thách cảm xúc",
        navTitle: "Thử thách cảm xúc",
        endpoint: "/games/cv/requests",
        requiresEmotion: true,
        emptyEmotionMessage: (emotion) => `Hiện chưa có bài luyện cho cảm xúc "${emotion}". Vui lòng quay lại chọn cảm xúc khác.`,
        emptyLevelMessage: (level) => `Không có yêu cầu nào ở level ${level}. Vui lòng chọn level khác.`,
        introBuilder: (scenario) =>
            `Hãy thể hiện khuôn mặt ${scenario.target_emotion} nhé. ${scenario.description}`,
        summaryBuilder: (emotion) =>
            `Con đã luyện tập các biểu cảm ${emotion || "đa dạng"} rất tốt hôm nay! Nhớ giữ phong độ nhé!`,
    },
};

// Map game_id từ database sang key nội bộ GV1/GV2
const DB_GAME_CV_SCENARIO_ID = "e05909f3-3dee-42a6-9a75-fd985b1bdf47".toLowerCase(); // Câu chuyện trên khuôn mặt (GV1)
const DB_GAME_CV_REQUEST_ID = "61f5e09e-eefa-44c1-86e1-87dfceac3b8e".toLowerCase(); // Thử thách cảm xúc (GV2)

// Game state
let gameState = {
    gameId: "GV1",
    config: CV_GAME_CONFIG.GV1,
    selectedEmotion: null,
    currentScenario: null,
    currentScenarioIndex: 0,
    scenarios: [],
    selectedLevel: 1, // Level được chọn từ level_select
    sessionId: null,
    isDetecting: false,
    detectionInterval: null,
    videoStream: null,
    faceApiModels: null,
    currentEmotion: null,
    targetEmotion: null,
    detectionStartTime: null,
    successThreshold: 500, // 0.5 seconds holding correct emotion (60% confidence)
    maxAttemptTime: 30000, // 30 seconds max (more time)
    roundTimerInterval: null,
    roundTimerEndAt: null,
    speechSynthesis: null,
    currentConfidence: 0.0, // Confidence score hiện tại từ face-api.js (0-1)
    bestConfidence: 0.0 // Confidence score cao nhất trong màn chơi này
};

const ROUND_TIMER_WARNING_MS = 5000;

const CV_MAX_SCENARIOS_PER_LEVEL = 5;

// Emotion mapping from face-api.js to game emotions
const EMOTION_MAP = {
    'happy': 'vui',
    'sad': 'buồn',
    'angry': 'tức giận',
    'fearful': 'sợ hãi',
    'surprised': 'ngạc nhiên',
    'disgusted': 'ghê tởm',
    'neutral': null
};

// Emotion icons
const EMOTION_ICONS = {
    'vui': '😊',
    'buồn': '😢',
    'tức giận': '😠',
    'sợ hãi': '😨',
    'ngạc nhiên': '😲',
    'ghê tởm': '🤢'
};

// Local tracking of how many times each emotion has been failed in this session
const CV_MAX_INCORRECT_BEFORE_LEARN = 3;
const cvEmotionErrorCounts = {};
const cvLearnedEmotions = new Set();

// Simple learning cards for each basic emotion (texts reused từ trang Học)
const CV_LEARNING_CARDS = {
    'vui': {
        title: 'Vui',
        description: 'Lan được tặng một món quà bất ngờ nên Lan rất vui và mỉm cười.'
    },
    'buồn': {
        title: 'Buồn',
        description: 'An đánh rơi kem rồi, nên An buồn và khóc.'
    },
    'tức giận': {
        title: 'Tức giận',
        description: 'Nam bị bạn giật đồ chơi mà không xin phép nên Nam tức giận.'
    },
    'sợ hãi': {
        title: 'Sợ hãi',
        description: 'Bé Mai đi lạc mẹ trong siêu thị nên cảm thấy rất sợ hãi.'
    },
    'ngạc nhiên': {
        title: 'Ngạc nhiên',
        description: 'Huy mở hộp quà ra và thấy món đồ chơi mình rất thích nên rất ngạc nhiên.'
    },
    'ghê tởm': {
        title: 'Ghê tởm',
        description: 'Minh ngửi thấy mùi rác thối nên cảm thấy rất ghê tởm.'
    }
};

// Helper functions
const $ = (id) => document.getElementById(id);
const $$ = (selector) => document.querySelector(selector);

function setCameraPlaceholderVisible(visible) {
    const el = $('camera-placeholder');
    if (!el) return;
    el.style.display = visible ? 'flex' : 'none';
}

function setDetectionUIVisible(visible) {
    const info = $('detection-info');
    if (!info) return;
    info.classList.toggle('is-visible', !!visible);
}

function resetDetectionUI() {
    const icon = $('detected-emotion-icon');
    const bar = $('detected-progress-bar');
    const pctEl = $('detected-emotion-percent');
    if (icon) icon.textContent = '';
    if (bar) {
        bar.style.width = '0%';
        bar.classList.remove('level-low', 'level-mid', 'level-high');
    }
    if (pctEl) pctEl.textContent = '';
    setDetectionUIVisible(false);
}

function setRoundTimerVisible(visible) {
    const timerEl = $('round-timer');
    if (!timerEl) return;
    timerEl.classList.toggle('is-visible', !!visible);
    if (!visible) {
        timerEl.classList.remove('is-warning');
        timerEl.textContent = '';
    }
}

function stopRoundTimer() {
    if (gameState.roundTimerInterval) {
        clearInterval(gameState.roundTimerInterval);
        gameState.roundTimerInterval = null;
    }
    gameState.roundTimerEndAt = null;
    setRoundTimerVisible(false);
}

function formatRemainingTime(ms) {
    const totalSeconds = Math.max(0, Math.ceil(ms / 1000));
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const mm = String(minutes).padStart(2, '0');
    const ss = String(seconds).padStart(2, '0');
    return `${mm}:${ss}`;
}

function startRoundTimer() {
    const timerEl = $('round-timer');
    if (!timerEl) return;

    stopRoundTimer();

    const endAt = Date.now() + (gameState.maxAttemptTime || 0);
    gameState.roundTimerEndAt = endAt;
    setRoundTimerVisible(true);

    const tick = () => {
        if (!gameState.roundTimerEndAt) return;
        const remainingMs = gameState.roundTimerEndAt - Date.now();
        timerEl.textContent = `⏱ ${formatRemainingTime(remainingMs)}`;
        timerEl.classList.toggle('is-warning', remainingMs <= ROUND_TIMER_WARNING_MS);
    };

    tick();
    gameState.roundTimerInterval = setInterval(tick, 200);
}

function applyGameConfig() {
    const config = gameState.config || CV_GAME_CONFIG.GV1;
    try {
        document.title = config.documentTitle;
    } catch (error) {
        console.warn("Unable to set document title:", error);
    }

    const navTitleEl = $$(".navbar-title");
    if (navTitleEl) {
        navTitleEl.textContent = config.navTitle;
    }
}

// Initialize game
async function initGame() {
    console.log('Initializing Game CV...');
    console.log('Current URL:', window.location.href);
    
    // Wait a bit to ensure localStorage is ready
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Check for user - check multiple possible user_id fields
    const userStr = localStorage.getItem('currentUser');
    console.log('Raw user from localStorage:', userStr);
    console.log('All localStorage keys:', Object.keys(localStorage));
    
    if (!userStr) {
        console.error('No currentUser found in localStorage');
        console.error('All localStorage items:', { ...localStorage });
        showError('Vui lòng đăng nhập để chơi game');
        setTimeout(() => {
            console.log('Redirecting to login...');
            window.location.href = '/src/pages/login.html';
        }, 2000);
        return;
    }
    
    let user;
    try {
        user = JSON.parse(userStr);
        console.log('Parsed user object:', user);
    } catch (e) {
        console.error('Error parsing user from localStorage:', e);
        showError('Lỗi đọc thông tin người dùng. Vui lòng đăng nhập lại.');
        setTimeout(() => window.location.href = '/src/pages/login.html', 2000);
        return;
    }
    
    const userId = user.user_id || user.userId || user.id || user.user?.user_id;
    console.log('Extracted userId:', userId);
    console.log('Full user object keys:', Object.keys(user));
    console.log('user.user_id:', user.user_id);
    console.log('user.userId:', user.userId);
    console.log('user.id:', user.id);
    console.log('user.user?.user_id:', user.user?.user_id);
    
    if (!userId) {
        console.error('No user_id found in user object:', user);
        console.error('Available keys in user:', Object.keys(user));
        console.error('Full user object:', JSON.stringify(user, null, 2));
        
        // Show error but don't redirect immediately - let user see the error
        showError('Vui lòng đăng nhập để chơi game. Đang chuyển về trang đăng nhập...');
        
        // Wait a bit longer and show alert before redirecting
        setTimeout(() => {
            if (window.egModal && typeof window.egModal.alert === 'function') {
                window.egModal.alert('Không tìm thấy thông tin người dùng. Vui lòng đăng nhập lại.', 'Thông báo').then(() => {
                    console.log('Redirecting to login after alert...');
                    window.location.href = '/src/pages/login.html';
                });
            } else {
                alert('Không tìm thấy thông tin người dùng. Vui lòng đăng nhập lại.');
                console.log('Redirecting to login after alert...');
                window.location.href = '/src/pages/login.html';
            }
        }, 3000);
        return;
    }
    
    console.log('✅ User found:', userId);

    // Get level & game from query params
    const urlParams = new URLSearchParams(window.location.search);
    const rawGameId = urlParams.get('gameId');

    // Mặc định: GV1 (biểu cảm theo tình huống)
    let gameKey = "GV1";

    if (rawGameId) {
        const lowerId = rawGameId.toLowerCase();
        if (lowerId === DB_GAME_CV_REQUEST_ID) {
            // Thử thách cảm xúc (game_cv_2)
            gameKey = "GV2";
        } else if (lowerId === DB_GAME_CV_SCENARIO_ID) {
            // Câu chuyện trên khuôn mặt / game CV tình huống
            gameKey = "GV1";
        }
    }

    gameState.gameId = gameKey;
    gameState.config = CV_GAME_CONFIG[gameKey] || CV_GAME_CONFIG.GV1;
    applyGameConfig();
    console.log('Selected game:', gameKey, 'rawGameId:', rawGameId);

    // Initial UI state for HCI (ẩn camera đen và 0%)
    setCameraPlaceholderVisible(true);
    resetDetectionUI();

    const selectedLevel = parseInt(urlParams.get('level')) || 1;
    const selectedEmotion = urlParams.get('emotion');

    if (gameState.config?.requiresEmotion) {
        if (!selectedEmotion) {
            showError('Vui lòng chọn cảm xúc trước khi chơi game nhé!');
            setTimeout(() => {
                window.location.href = '/src/pages/level_select.html?gameId=GV2';
            }, 2500);
            return;
        }
        gameState.selectedEmotion = decodeURIComponent(selectedEmotion).toLowerCase();
        console.log('Selected emotion:', gameState.selectedEmotion);
        // Với game theo yêu cầu, mặc định level = 1 để tương thích backend
        gameState.selectedLevel = 1;
    } else {
        gameState.selectedLevel = selectedLevel;
        console.log('Selected level:', selectedLevel);
    }

    // Load face-api.js models
    await loadFaceApiModels();
    
    // Load scenarios from backend with level parameter
    // For GV1 (biểu cảm theo tình huống), backend will filter and random 10 scenarios
    // For GV2 (biểu cảm theo yêu cầu), still filter by emotion on frontend
    await loadScenarios(gameState.selectedLevel);
    
    // Filter scenarios by emotion for GV2 (game theo yêu cầu)
    if (gameState.config?.requiresEmotion && gameState.selectedEmotion) {
        const originalCount = gameState.scenarios.length;
        const emotionKey = gameState.selectedEmotion;
        gameState.scenarios = gameState.scenarios.filter(scenario =>
            (scenario.target_emotion || '').toLowerCase() === emotionKey
        );
        console.log(`Filtered scenarios: ${originalCount} total -> ${gameState.scenarios.length} cho cảm xúc ${emotionKey}`);
    }
    // For GV1, scenarios are already filtered and randomized by backend, no need to filter again

    if (gameState.scenarios.length > CV_MAX_SCENARIOS_PER_LEVEL) {
        gameState.scenarios = gameState.scenarios.slice(0, CV_MAX_SCENARIOS_PER_LEVEL);
        console.log(`Limited scenarios to ${CV_MAX_SCENARIOS_PER_LEVEL} per level`);
    }

    if (gameState.scenarios.length === 0) {
        let emptyMessage = `Không có màn nào ở level ${gameState.selectedLevel}. Vui lòng chọn level khác.`;
        if (gameState.config?.requiresEmotion && gameState.selectedEmotion) {
            emptyMessage = typeof gameState.config?.emptyEmotionMessage === 'function'
                ? gameState.config.emptyEmotionMessage(gameState.selectedEmotion)
                : `Không tìm thấy bài luyện cho cảm xúc ${gameState.selectedEmotion}.`;
        } else if (typeof gameState.config?.emptyLevelMessage === 'function') {
            emptyMessage = gameState.config.emptyLevelMessage(gameState.selectedLevel);
        }
        showError(emptyMessage);
        setTimeout(() => {
            window.location.href = '/src/pages/select_game.html';
        }, 3000);
        return;
    }
    
    // Setup event listeners
    setupEventListeners();
    
    // Load saved progress and decide if we need a new session
    // This will either:
    // - Reload: use old session without asking
    // - Fresh visit with progress: ask popup, then use old or create new
    // - No progress: create new session
    const needNewSession = await loadGameProgress();
    
    // Only create new session if needed (no old session or user chose restart)
    if (needNewSession) {
        await startSession();
    }
    
    // Start first scenario (or continue from saved progress)
    // At this point, currentScenarioIndex and sessionId are already set
    if (gameState.scenarios.length > 0) {
        if (gameState.currentScenarioIndex >= gameState.scenarios.length) {
            gameState.currentScenarioIndex = 0;
        }
        const savedIndex = gameState.currentScenarioIndex || 0;
        startScenario(savedIndex);
    }
}

// Load face-api.js models
async function loadFaceApiModels() {
    try {
        console.log('Loading face-api.js models...');
        // Try local models first (if placed in /models directory)
        const LOCAL_MODEL_URL = '/models';
        const CDN_MODEL_URL = 'https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights';
        
        try {
            // Try local models first
            await Promise.all([
                faceapi.nets.tinyFaceDetector.loadFromUri(LOCAL_MODEL_URL),
                faceapi.nets.faceLandmark68Net.loadFromUri(LOCAL_MODEL_URL),
                faceapi.nets.faceRecognitionNet.loadFromUri(LOCAL_MODEL_URL),
                faceapi.nets.faceExpressionNet.loadFromUri(LOCAL_MODEL_URL)
            ]);
            gameState.faceApiModels = true;
            console.log('Face-api.js models loaded from local directory');
        } catch (localError) {
            console.log('Local models not found, trying CDN...');
            // Fallback to CDN
            await Promise.all([
                faceapi.nets.tinyFaceDetector.loadFromUri(CDN_MODEL_URL),
                faceapi.nets.faceLandmark68Net.loadFromUri(CDN_MODEL_URL),
                faceapi.nets.faceRecognitionNet.loadFromUri(CDN_MODEL_URL),
                faceapi.nets.faceExpressionNet.loadFromUri(CDN_MODEL_URL)
            ]);
            gameState.faceApiModels = true;
            console.log('Face-api.js models loaded from CDN');
        }
    } catch (error) {
        console.error('Error loading face-api.js models:', error);
        showError('Không thể tải mô hình nhận diện. Vui lòng tải models từ https://github.com/justadudewhohacks/face-api.js/tree/master/weights và đặt vào thư mục /models');
    }
}

// Load scenarios from backend
async function loadScenarios(level = 1) {
    try {
        const endpoint = gameState.config?.endpoint || "/games/cv/scenarios";
        // Add level parameter for game "biểu cảm theo tình huống" (GV1)
        const url = gameState.gameId === 'GV1' 
            ? `${API_URL}${endpoint}?level=${level}`
            : `${API_URL}${endpoint}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to load scenarios');
        const data = await response.json();
        gameState.scenarios = data.scenarios || [];
        console.log(`Scenarios loaded for level ${level}:`, gameState.scenarios.length, 'scenarios');
    } catch (error) {
        console.error('Error loading scenarios:', error);
        showError('Không thể tải tình huống. Vui lòng thử lại.');
    }
}

// Setup event listeners
function setupEventListeners() {
    $('hint-btn')?.addEventListener('click', showHint);
    $('start-btn')?.addEventListener('click', startDetection);
    $('back-button')?.addEventListener('click', () => {
        // Clear sessionStorage so next visit will ask popup (not auto continue)
        sessionStorage.removeItem('gameCV_active_session');
        console.log('🔙 Back button clicked - cleared session marker');
        window.history.back();
    });
    $('logout-button')?.addEventListener('click', handleLogout);
}

// Start a scenario
function startScenario(index) {
    console.log(`Starting scenario ${index} of ${gameState.scenarios.length}`);
    if (index >= gameState.scenarios.length) {
        console.log('All scenarios completed, ending game...');
        endGame();
        return;
    }

    gameState.currentScenarioIndex = index;
    gameState.currentScenario = gameState.scenarios[index];
    gameState.targetEmotion = gameState.currentScenario.target_emotion;
    gameState.isDetecting = false;

    stopRoundTimer();
    gameState.currentEmotion = null;
    gameState.detectionStartTime = null;
    gameState.bestConfidence = 0.0; // Reset confidence score cao nhất cho màn chơi mới
    gameState.usedHint = false; // Reset hint flag cho màn mới

    // Save progress to localStorage
    saveGameProgress();

    // Update UI
    updateScenarioUI();

    // Khi sang màn mới (chưa bấm bắt đầu), giữ UI ở trạng thái chờ
    setCameraPlaceholderVisible(true);
    resetDetectionUI();
    
    // Read scenario description
    const introSpeech = typeof gameState.config?.introBuilder === 'function'
        ? gameState.config.introBuilder(gameState.currentScenario)
        : `Con nghe tình huống nhé. ${gameState.currentScenario.description}`;
    speakText(introSpeech);
    
    // Start countdown
    startCountdown();
}

// Update scenario UI
function updateScenarioUI() {
    $('scenario-title').textContent = gameState.currentScenario.title;
    $('scenario-description').textContent = gameState.currentScenario.description;
    const targetEmotionEl = $('target-emotion');
    if (targetEmotionEl) {
        if (gameState.gameId === 'GV1') {
            // Ở chế độ Câu chuyện trên khuôn mặt, không hiển thị trước cảm xúc mục tiêu để tránh lộ đáp án
            targetEmotionEl.style.display = 'none';
            targetEmotionEl.textContent = '';
        } else {
            // Ở chế độ yêu cầu (GV2) có thể hiển thị cảm xúc đã chọn
            targetEmotionEl.style.display = '';
            targetEmotionEl.textContent = `Cảm xúc: ${gameState.currentScenario.target_emotion}`;
        }
    }
    
    // Update progress indicator (Màn X/10)
    const progressIndicator = document.getElementById('progress-indicator');
    if (progressIndicator) {
        const currentScenario = gameState.currentScenarioIndex + 1;
        const totalScenarios = gameState.scenarios.length;
        progressIndicator.textContent = gameState.gameId === 'GV1'
            ? `Màn ${currentScenario}/${totalScenarios}`
            : `Lượt ${currentScenario}/${totalScenarios}`;
    }

    // Update progress bar
    const progressBarFill = document.getElementById('cv-level-progress-fill');
    if (progressBarFill) {
        const currentScenario = gameState.currentScenarioIndex + 1;
        const totalScenarios = gameState.scenarios.length;
        const percentage = (currentScenario / totalScenarios) * 100;
        
        progressBarFill.style.width = `${percentage}%`;
    }
    
    // Hiển thị ảnh minh họa nếu có
    const scenarioImage = $('scenario-image');
    const imageContainer = document.querySelector('.scenario-image-container');
    if (scenarioImage && gameState.currentScenario.image_path) {
        scenarioImage.src = gameState.currentScenario.image_path;
        scenarioImage.style.display = 'block';
        if (imageContainer) {
            imageContainer.style.display = 'flex';
            imageContainer.style.background = 'transparent';
        }
        scenarioImage.onerror = () => {
            // Nếu ảnh không tải được, hiển thị placeholder
            scenarioImage.style.display = 'none';
            if (imageContainer) {
                imageContainer.style.background = 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)';
                imageContainer.innerHTML = `<div style="color: #666; font-size: 1.2rem; text-align: center; padding: 20px;">${EMOTION_ICONS[gameState.targetEmotion] || '📷'}<br><span style="font-size: 0.9rem;">${gameState.currentScenario.title}</span></div>`;
            }
        };
        scenarioImage.onload = () => {
            // Ảnh tải thành công
            if (imageContainer) {
                imageContainer.style.background = 'transparent';
            }
        };
    } else {
        // Không có ảnh, ẩn container
        if (imageContainer) {
            imageContainer.style.display = 'none';
        }
    }
    
    // Lưu hint vào state để dùng khi bấm "Gợi ý"
    gameState.currentHint = gameState.currentScenario.hint || "";
}

// Start countdown
function startCountdown() {
    let count = 5;
    const countdownEl = $('countdown');
    countdownEl.textContent = `${count}...`;
    countdownEl.classList.add('is-visible');
    
    const interval = setInterval(() => {
        count--;
        if (count > 0) {
            countdownEl.textContent = `${count}...`;
        } else {
            countdownEl.textContent = 'Chuẩn bị nào...';
            clearInterval(interval);
            setTimeout(() => {
                countdownEl.classList.remove('is-visible');
            }, 1000);
        }
    }, 1000);
}

// Show hint animation
function showHint() {
    if (!gameState.currentScenario) return;
    
    // Track that user used hint for this scenario
    gameState.usedHint = true;
    console.log('💡 Hint used - will be saved in session_questions');
    
    const hintContainer = $('hint-animation');
    const emotion = gameState.targetEmotion;
    const hintText = gameState.currentHint || `Hãy thể hiện cảm xúc ${emotion}!`;
    speakText(hintText);
    
    // Show animation placeholder with emotion-specific animation và hint text
    hintContainer.innerHTML = `
        <div class="hint-content">
            <div class="emotion-animation ${emotion}">${EMOTION_ICONS[emotion] || '😐'}</div>
            <div class="hint-text">${hintText}</div>
        </div>
    `;
    hintContainer.style.display = 'flex';
    
    // Hide after animation completes
    setTimeout(() => {
        hintContainer.style.display = 'none';
    }, 3000);
}

// Start detection
async function startDetection() {
    if (gameState.isDetecting) return;
    
    // Check if face-api models are loaded
    if (!gameState.faceApiModels) {
        showError('Mô hình nhận diện chưa sẵn sàng. Vui lòng đợi...');
        return;
    }
    
    // Request camera access
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            } 
        });
        
        const video = $('camera-video');
        gameState.videoStream = stream;
        video.srcObject = stream;

        // Hide placeholder as soon as the video actually starts rendering frames
        // (some browsers can behave differently with onloadedmetadata timing)
        const hidePlaceholderOnce = () => {
            setCameraPlaceholderVisible(false);
            video.removeEventListener('playing', hidePlaceholderOnce);
            video.removeEventListener('loadeddata', hidePlaceholderOnce);
        };
        video.addEventListener('playing', hidePlaceholderOnce);
        video.addEventListener('loadeddata', hidePlaceholderOnce);
        
        // Wait for video to be ready (avoid missing event if metadata is already available)
        await new Promise((resolve, reject) => {
            let settled = false;

            const cleanup = () => {
                video.removeEventListener('loadedmetadata', onMeta);
                video.removeEventListener('error', onErr);
            };

            const onMeta = () => {
                if (settled) return;
                video.play().then(() => {
                    // Chắc chắn ẩn placeholder khi video đã play thành công
                    setCameraPlaceholderVisible(false);
                    settled = true;
                    cleanup();
                    resolve();
                }).catch((e) => {
                    settled = true;
                    cleanup();
                    reject(e);
                });
            };

            const onErr = (e) => {
                if (settled) return;
                settled = true;
                cleanup();
                reject(e);
            };

            video.addEventListener('loadedmetadata', onMeta);
            video.addEventListener('error', onErr);

            if (video.readyState >= 1) {
                onMeta();
            }

            setTimeout(() => {
                if (!settled) {
                    settled = true;
                    cleanup();
                    reject(new Error('Video load timeout'));
                }
            }, 5000);
        });
        
        gameState.isDetecting = true;
        gameState.detectionStartTime = Date.now();

        startRoundTimer();

        // Khi bắt đầu detect: hiển thị thanh tiến độ (không hiển thị 0% bằng số)
        setDetectionUIVisible(true);
        
        // Disable start button
        $('start-btn').disabled = true;
        $('start-btn').textContent = 'Đang nhận diện...';
        
        // Ensure session exists (should already be created in initGame, but check just in case)
        if (!gameState.sessionId) {
            await startSession();
        }
        
        // Start emotion detection loop
        startEmotionDetection();
        
        // Speak instruction
        const instruction = gameState.currentScenario.instruction || 
            `Giờ con thể hiện khuôn mặt ${gameState.targetEmotion} nhé.`;
        speakText(instruction);
        
    } catch (error) {
        console.error('Error accessing camera:', error);
        let errorMessage = 'Không thể truy cập camera. ';
        
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            errorMessage += 'Vui lòng cho phép quyền truy cập camera trong cài đặt trình duyệt.';
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
            errorMessage += 'Không tìm thấy camera. Vui lòng kiểm tra thiết bị.';
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
            errorMessage += 'Camera đang được sử dụng bởi ứng dụng khác.';
        } else {
            errorMessage += 'Vui lòng thử lại.';
        }
        
        showError(errorMessage);

        stopRoundTimer();

        // Nếu không bật được camera, quay về trạng thái chờ
        setCameraPlaceholderVisible(true);
        resetDetectionUI();
        
        // Re-enable button
        $('start-btn').disabled = false;
        $('start-btn').textContent = '▶️ Bắt đầu';
    }
}

// Start session
async function startSession() {
    try {
        // Always get fresh user from localStorage to ensure we have the latest user_id
        const userStr = localStorage.getItem('currentUser');
        if (!userStr) {
            console.error('Cannot start session: no currentUser in localStorage');
            showError('Vui lòng đăng nhập để chơi game');
            return;
        }
        
        const user = JSON.parse(userStr);
        const userId = user.user_id || user.userId || user.id || user.user?.user_id;
        
        console.log('🔄 Starting session with user_id:', userId);
        console.log('   Full user object:', user);
        
        if (!userId) {
            console.error('Cannot start session: no user_id found in user object');
            console.error('User object:', user);
            return;
        }
        
        const gameType = gameState.gameId === 'GV2' ? 'GameCVRequest' : 'GameCV';

        console.log(`📤 Sending start_session request: user_id=${userId}, game_type=${gameType}`);

        const response = await fetch(`${API_URL}/games/cv/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                game_type: gameType
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            console.error('Error starting session:', response.status, errorData);
            showError('Không thể khởi tạo session. Vui lòng thử lại.');
            return;
        }
        
        const data = await response.json();
        gameState.sessionId = data.session_id;
        console.log('Session started successfully:', data.session_id);
    } catch (error) {
        console.error('Error starting session:', error);
        showError('Lỗi khi khởi tạo session: ' + error.message);
    }
}

// Start emotion detection loop
function startEmotionDetection() {
    const video = $('camera-video');
    if (!video || !video.videoWidth) {
        console.error('Video not ready');
        return;
    }
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    gameState.detectionInterval = setInterval(async () => {
        if (!gameState.isDetecting || !gameState.faceApiModels) return;
        
        // Check timeout
        if (Date.now() - gameState.detectionStartTime > gameState.maxAttemptTime) {
            handleTimeout();
            return;
        }
        
        // Check if video is ready
        if (video.readyState !== video.HAVE_ENOUGH_DATA) {
            return;
        }
        
        // Draw video frame to canvas
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        try {
            // Detect emotions
            const detections = await faceapi
                .detectAllFaces(canvas, new faceapi.TinyFaceDetectorOptions())
                .withFaceLandmarks()
                .withFaceExpressions();
            
            if (detections.length > 0) {
                const detection = detections[0];
                const expressions = detection.expressions;
                
                // Get dominant emotion
                const dominantEmotion = Object.keys(expressions).reduce((a, b) => 
                    expressions[a] > expressions[b] ? a : b
                );
                
                // Map to game emotion
                const gameEmotion = EMOTION_MAP[dominantEmotion];
                const confidence = expressions[dominantEmotion];
                
                // Lưu confidence score hiện tại
                gameState.currentConfidence = confidence;
                
                // Update UI
                updateDetectionUI(gameEmotion, confidence);
                
                // Check if correct emotion (giữ trên 60% trong 0.5s)
                if (gameEmotion === gameState.targetEmotion && confidence >= 0.6) {
                    // Chỉ lưu bestConfidence khi đúng cảm xúc VÀ >= 60% (điều kiện để success)
                    if (confidence > gameState.bestConfidence) {
                        gameState.bestConfidence = confidence;
                        console.log(`🎯 New best confidence for ${gameEmotion}: ${(confidence * 100).toFixed(1)}% (>= 60%)`);
                    }
                    handleCorrectEmotion();
                } else {
                    handleIncorrectEmotion(gameEmotion, confidence);
                }
            } else {
                // No face detected
                updateDetectionUI(null, 0);
                updateTrafficLight('red');
                correctEmotionStartTime = null;
            }
        } catch (error) {
            console.error('Error in emotion detection:', error);
        }
    }, 200); // Check every 200ms for better performance
}

// Update detection UI
function updateDetectionUI(emotion, confidence) {
    gameState.currentEmotion = emotion;
    
    // Trước khi bấm bắt đầu: không hiển thị chỉ số nào để tránh cảm giác thất bại
    if (!gameState.isDetecting) {
        resetDetectionUI();
        return;
    }

    const iconEl = $('detected-emotion-icon');
    const percentEl = $('detected-emotion-percent');

    // Đang detect: hiển thị thanh tiến độ
    setDetectionUIVisible(true);

    const conf = confidence || 0;
    if (conf <= 0) {
        if (iconEl) iconEl.textContent = '';
        if (percentEl) percentEl.textContent = '';
        return;
    }

    if (iconEl) {
        // Nếu không map được emotion (vd. neutral), vẫn hiển thị icon trung tính
        iconEl.textContent = emotion ? (EMOTION_ICONS[emotion] || '😐') : '😐';
    }

    if (percentEl) {
        const pct = Math.max(0, Math.min(100, Math.round(conf * 100)));
        percentEl.textContent = `${pct}%`;
    }
}

// Handle correct emotion
let correctEmotionStartTime = null;

function handleCorrectEmotion() {
    if (!correctEmotionStartTime) {
        correctEmotionStartTime = Date.now();
    }
    
    const holdTime = Date.now() - correctEmotionStartTime;
    updateTrafficLight('green');
    
    if (holdTime >= gameState.successThreshold) {
        // Success!
        correctEmotionStartTime = null; // Reset
        handleSuccess();
    }
}

// Handle incorrect emotion
function handleIncorrectEmotion(emotion, confidence) {
    // Reset timer if emotion is wrong
    if (gameState.currentEmotion !== gameState.targetEmotion) {
        correctEmotionStartTime = null;
    }
    
    if (confidence < 0.5) {
        updateTrafficLight('red');
    } else {
        updateTrafficLight('yellow');
    }
}

// Normalize game emotion name to a stable key
function normalizeGameEmotionKey(rawEmotion) {
    if (!rawEmotion) return '';
    return String(rawEmotion).toLowerCase().trim();
}

// Map game emotion key (vui, buồn, ...) sang key dùng trên trang Học
function mapGameEmotionToLearnKey(gameEmotion) {
    const map = {
        'vui': 'happy',
        'buồn': 'sad',
        'tức giận': 'angry',
        'sợ hãi': 'fear',
        'ngạc nhiên': 'surprise',
        'ghê tởm': 'disgust'
    };
    return map[gameEmotion] || 'happy';
}

// Ghi nhận một lần thất bại cho cảm xúc hiện tại, nếu vượt ngưỡng thì mở thẻ học
function registerCvIncorrectAndMaybeShowLearn() {
    const key = normalizeGameEmotionKey(gameState.targetEmotion);
    if (!key) return false;

    cvEmotionErrorCounts[key] = (cvEmotionErrorCounts[key] || 0) + 1;
    console.log('📊 CV emotion incorrect count', key, cvEmotionErrorCounts[key]);

    if (cvEmotionErrorCounts[key] >= CV_MAX_INCORRECT_BEFORE_LEARN && !cvLearnedEmotions.has(key)) {
        cvLearnedEmotions.add(key);
        showCvLearningCard(key);
        return true;
    }
    return false;
}

// Hiển thị popup thẻ học cảm xúc cho game CV
function showCvLearningCard(emotionKey) {
    const modal = document.getElementById('cv-learning-modal');
    const titleEl = document.getElementById('cv-learning-emotion-title');
    const descEl = document.getElementById('cv-learning-description');
    const learnBtn = document.getElementById('cv-learning-open-learn');
    const closeBtn = document.getElementById('cv-learning-close-btn');

    if (!modal || !titleEl || !descEl || !closeBtn) {
        console.warn('CV learning modal elements not found');
        return;
    }

    const card = CV_LEARNING_CARDS[emotionKey] || { title: emotionKey, description: '' };
    const icon = EMOTION_ICONS[emotionKey] || '🙂';

    titleEl.textContent = `${icon} ${card.title}`;
    descEl.textContent = card.description || '';
    modal.style.display = 'flex';

    if (learnBtn) {
        const learnEmotion = mapGameEmotionToLearnKey(emotionKey);
        learnBtn.onclick = () => {
            window.location.href = `/src/pages/learn.html?emotion=${encodeURIComponent(learnEmotion)}`;
        };
    }

    closeBtn.onclick = () => {
        modal.style.display = 'none';
        const nextIndex = gameState.currentScenarioIndex + 1;
        startScenario(nextIndex);
    };
}

// Update traffic light
function updateTrafficLight(color) {
    const red = $('traffic-red');
    const yellow = $('traffic-yellow');
    const green = $('traffic-green');
    
    // Reset all
    red.classList.remove('active');
    yellow.classList.remove('active');
    green.classList.remove('active');
    
    // Activate current
    if (color === 'red') {
        red.classList.add('active');
        $('feedback-text').textContent = 'Chưa giống lắm, mình thử lại nhé.';
    } else if (color === 'yellow') {
        yellow.classList.add('active');
        $('feedback-text').textContent = 'Sắp đúng rồi, cố giữ thêm.';
    } else if (color === 'green') {
        green.classList.add('active');
        $('feedback-text').textContent = 'Đúng rồi! Giữ nguyên như thế!';
    }
}

// Handle success
async function handleSuccess() {
    if (!gameState.isDetecting) return; // Prevent multiple calls
    
    console.log('✅ Success! Saving result...');
    
    gameState.isDetecting = false;

    stopRoundTimer();
    if (gameState.detectionInterval) {
        clearInterval(gameState.detectionInterval);
        gameState.detectionInterval = null;
    }
    
    // Stop camera
    if (gameState.videoStream) {
        gameState.videoStream.getTracks().forEach(track => track.stop());
        gameState.videoStream = null;
    }

    // Về trạng thái chờ (ẩn chỉ số, hiện placeholder)
    setCameraPlaceholderVisible(true);
    resetDetectionUI();
    
    // Re-enable start button
    $('start-btn').disabled = false;
    $('start-btn').textContent = '▶️ Bắt đầu';
    
    // Show success animation
    showSuccessAnimation();
    
    // Speak success message
    speakText(`Quá tuyệt! Con làm rất tốt.`);
    
    // Save result với confidence score cao nhất (convert sang 0-100)
    const bestConfidencePercent = gameState.bestConfidence * 100; // Convert từ 0-1 sang 0-100
    console.log(`💾 Saving success with best confidence: ${gameState.bestConfidence} (${bestConfidencePercent}%)`);
    await saveResult(true, bestConfidencePercent);
    
    // Move to next scenario after delay
    const nextIndex = gameState.currentScenarioIndex + 1;
    console.log(`Moving to next scenario: ${nextIndex} (total: ${gameState.scenarios.length})`);
    setTimeout(() => {
        startScenario(nextIndex);
    }, 3000);
}

// Handle timeout
async function handleTimeout() {
    if (!gameState.isDetecting) return; // Prevent multiple calls
    
    console.log('⏱️ Timeout! Saving result...');
    
    gameState.isDetecting = false;

    stopRoundTimer();
    if (gameState.detectionInterval) {
        clearInterval(gameState.detectionInterval);
        gameState.detectionInterval = null;
    }
    
    // Stop camera
    if (gameState.videoStream) {
        gameState.videoStream.getTracks().forEach(track => track.stop());
        gameState.videoStream = null;
    }

    // Về trạng thái chờ (ẩn chỉ số, hiện placeholder)
    setCameraPlaceholderVisible(true);
    resetDetectionUI();
    
    // Re-enable start button
    $('start-btn').disabled = false;
    $('start-btn').textContent = '▶️ Bắt đầu';

    const nextIndex = gameState.currentScenarioIndex + 1;
    const isLastTurn = nextIndex >= (gameState.scenarios ? gameState.scenarios.length : 0);
    if (!(gameState.gameId !== 'GV1' && isLastTurn)) {
        speakText('Chúng ta thử lại thêm lần nữa nhé! Lần sau mình sẽ làm tốt hơn!');
    }
    
    // Timeout = thất bại, không lưu bestConfidence (chỉ lưu khi success)
    console.log(`💾 Saving timeout (failure) - no confidence score saved`);
    await saveResult(false, 0); // Lưu 0 vì không đạt được success
    
    // Đếm số lần thất bại cho cảm xúc hiện tại, nếu vượt ngưỡng thì mở thẻ học
    const shouldShowLearn = registerCvIncorrectAndMaybeShowLearn();
    if (shouldShowLearn) {
        // Khi đóng thẻ học sẽ tự nhảy sang màn tiếp theo
        return;
    }
    
    // Nếu chưa cần học lại, chuyển sang màn tiếp theo như cũ
    console.log(`Moving to next scenario: ${nextIndex} (total: ${gameState.scenarios.length})`);
    setTimeout(() => {
        startScenario(nextIndex);
    }, 3000);
}

// Show success animation
function showSuccessAnimation() {
    const successEl = $('success-animation');
    successEl.style.display = 'flex';
    successEl.innerHTML = `
        <div class="success-content">
            <div class="success-icon">🎉</div>
            <div class="success-text">Xuất sắc!</div>
            <div class="success-message">Con đã thể hiện ${gameState.targetEmotion} rất tốt!</div>
            <div class="success-sticker">${EMOTION_ICONS[gameState.targetEmotion] || '⭐'}</div>
        </div>
    `;
    
    setTimeout(() => {
        successEl.style.display = 'none';
    }, 2500);
}

// Save result
async function saveResult(success, confidenceScore = 0.0) {
    try {
        if (!gameState.sessionId) {
            console.error('Cannot save result: no session_id found');
            return;
        }
        
        if (!gameState.currentScenario || !gameState.currentScenario.id) {
            console.error('Cannot save result: no scenario_id found');
            return;
        }
        
        // confidenceScore đã được convert sang 0-100 rồi (từ bestConfidencePercent)
        console.log(`💾 Saving result: success=${success}, confidence_score=${confidenceScore}% (thang 100)`);
        
        const response = await fetch(`${API_URL}/games/cv/result`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: gameState.sessionId,
                scenario_id: gameState.currentScenario.id,
                target_emotion: gameState.targetEmotion,
                detected_emotion: gameState.currentEmotion,
                success: success,
                time_taken: Date.now() - gameState.detectionStartTime,
                confidence_score: confidenceScore // Confidence score (0-100), đã được convert rồi
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            console.error('Error saving result:', response.status, errorData);
            return;
        }
        
        const data = await response.json();
        console.log('Result saved successfully:', data);
    } catch (error) {
        console.error('Error saving result:', error);
    }
}

// End session
async function endSession() {
    try {
        if (!gameState.sessionId) {
            console.error('Cannot end session: no session_id found');
            return;
        }

        console.log('Ending session:', gameState.sessionId);
        
        const response = await fetch(`${API_URL}/games/cv/end`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: gameState.sessionId
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            console.error('Error ending session:', response.status, errorData);
            return;
        }

        const data = await response.json();
        console.log('✅ Session ended successfully:', data);
        console.log('Final score:', data.score);
        console.log('Emotion errors:', data.emotion_errors);
        
        // Lưu kết quả cuối cùng vào localStorage để có thể xem sau
        gameState.finalScore = data.score;
        gameState.finalEmotionErrors = data.emotion_errors;
        gameState.finalBestEmotion = null;
        
        // Tính điểm theo thang 100 từ best_confidence
        let bestConfidenceScore = 0;
        if (data.emotion_errors) {
            try {
                const emotionErrors = typeof data.emotion_errors === 'string' 
                    ? JSON.parse(data.emotion_errors) 
                    : data.emotion_errors;
                
                if (gameState.gameId === 'GV2') {
                    // GV2: lấy đúng theo cảm xúc mục tiêu đang luyện
                    const targetEmotion = gameState.targetEmotion || '';
                    const targetEmotionLower = targetEmotion.toLowerCase().trim();

                    // Thử tìm với nhiều cách: exact match, với encoding sai
                    let emotionKey = targetEmotion;
                    if (emotionErrors[targetEmotion] && emotionErrors[targetEmotion].best_confidence) {
                        emotionKey = targetEmotion;
                    } else if (emotionErrors[targetEmotionLower] && emotionErrors[targetEmotionLower].best_confidence) {
                        emotionKey = targetEmotionLower;
                    } else {
                        const possibleKeys = Object.keys(emotionErrors);
                        for (const key of possibleKeys) {
                            const keyLower = key.toLowerCase().trim();
                            const targetWords = targetEmotionLower.split(/\s+/);
                            const keyWords = keyLower.split(/\s+/);
                            if (targetWords.some(word => keyWords.includes(word)) ||
                                keyWords.some(word => targetWords.includes(word))) {
                                emotionKey = key;
                                break;
                            }
                        }
                    }

                    if (emotionErrors[emotionKey] && emotionErrors[emotionKey].best_confidence) {
                        bestConfidenceScore = Math.round(emotionErrors[emotionKey].best_confidence);
                        gameState.finalBestEmotion = emotionKey;
                    }
                    console.log(`📊 Best confidence score for ${targetEmotion} (found as "${emotionKey}"): ${bestConfidenceScore}%`);
                } else {
                    // GV1: lấy cảm xúc có best_confidence cao nhất trong toàn session
                    let bestKey = null;
                    let bestVal = 0;
                    for (const [key, value] of Object.entries(emotionErrors || {})) {
                        if (!value || typeof value !== 'object') continue;
                        const bc = Number(value.best_confidence || 0);
                        if (bc > bestVal) {
                            bestVal = bc;
                            bestKey = key;
                        }
                    }
                    bestConfidenceScore = Math.round(bestVal || 0);
                    gameState.finalBestEmotion = bestKey;
                    console.log(`📊 Best emotion overall: ${bestKey || 'N/A'} (${bestConfidenceScore}%)`);
                }
            } catch (e) {
                console.warn('Error parsing emotion_errors:', e);
            }
        }
        gameState.finalBestConfidenceScore = bestConfidenceScore;
        
        // Lưu vào localStorage
        try {
            const sessionData = {
                session_id: gameState.sessionId,
                score: data.score,
                emotion_errors: data.emotion_errors,
                ended_at: new Date().toISOString()
            };
            const existingSessions = JSON.parse(localStorage.getItem('gameCV_sessions') || '[]');
            existingSessions.push(sessionData);
            localStorage.setItem('gameCV_sessions', JSON.stringify(existingSessions));
            console.log('Session data saved to localStorage');
        } catch (e) {
            console.warn('Could not save to localStorage:', e);
        }
    } catch (error) {
        console.error('Error ending session:', error);
    }
}

// Cache for Vietnamese voice availability
let hasVietnameseVoice = null;
let vietnameseVoiceCache = null;

let ttsRequestId = 0;
let ttsFallbackTimer = null;
let currentFptAudio = null;

function stopFptAudio() {
    if (!currentFptAudio) return;
    try {
        currentFptAudio.pause();
        currentFptAudio.currentTime = 0;
    } catch (e) {
        // ignore
    }
    currentFptAudio = null;
}

// Check if Vietnamese voice is available
function checkVietnameseVoice() {
    if (hasVietnameseVoice !== null) {
        return hasVietnameseVoice;
    }
    
    const voices = window.speechSynthesis.getVoices();
    const vietnameseVoice = voices.find(voice => {
        const lang = voice.lang.toLowerCase();
        const name = voice.name.toLowerCase();
        return lang === 'vi-vn' || 
               lang === 'vi' || 
               lang.includes('vietnam') ||
               name.includes('vietnamese') ||
               name.includes('việt') ||
               name.includes('viet');
    });
    
    if (vietnameseVoice) {
        vietnameseVoiceCache = vietnameseVoice;
        hasVietnameseVoice = true;
        return true;
    }
    
    hasVietnameseVoice = false;
    return false;
}

// Use FPT AI TTS API for Vietnamese text-to-speech
async function speakWithFPTAI(text, requestId) {
    try {
        if (typeof requestId === 'number' && requestId !== ttsRequestId) {
            return false;
        }
        const response = await fetch("https://api.fpt.ai/hmi/tts/v5", {
            method: "POST",
            headers: {
                "api-key": "OXvPopJqIJgON0AglCE0KPkBvOovWSoy",
                "speed": "0.8", // Slightly slower
                "voice": "banmai", // Vietnamese voice
            },
            body: text, // Send text directly, not JSON
        });

        if (!response.ok) {
            throw new Error('FPT AI TTS API error');
        }

        const data = await response.json();
        
        let audioUrl = null;
        
        if (data.async) {
            // FPT AI v5 returns async URL which is usually the direct audio URL
            // Check if it's already an audio file URL
            if (data.async.includes('.mp3') || data.async.includes('file01.fpt.ai')) {
                // It's already an audio URL, use it directly
                audioUrl = data.async;
            } else {
                // It might be a JSON endpoint, try to poll for result
                // But based on FPT AI v5 docs, async URL is usually the audio URL directly
                audioUrl = data.async; // Try using it directly first
            }
        } else if (data.url) {
            // Direct audio URL
            audioUrl = data.url;
        }
        
        if (audioUrl) {
            // Always use proxy endpoint to avoid CORS issues with FPT AI
            const proxyUrl = `${API_URL}/games/cv/audio-proxy?url=${encodeURIComponent(audioUrl)}`;
            if (typeof requestId === 'number' && requestId !== ttsRequestId) {
                return false;
            }

            stopFptAudio();

            const audio = new Audio(proxyUrl);
            currentFptAudio = audio;

            audio.play().catch(err => {
                console.error('Error playing audio:', err);
            });
            return true;
        }
        
        return false;
    } catch (error) {
        console.error('FPT AI TTS error:', error);
        return false;
    }
}

// Poll for audio URL from FPT AI async endpoint via backend proxy
async function pollForAudioUrl(asyncUrl, maxAttempts = 10) {
    // Use backend proxy to avoid CORS issues when polling JSON endpoint
    const proxyUrl = `${API_URL}/games/cv/audio-proxy?url=${encodeURIComponent(asyncUrl)}`;
    
    for (let i = 0; i < maxAttempts; i++) {
        try {
            const response = await fetch(proxyUrl);
            const data = await response.json();
            
            if (data.url) {
                return data.url;
            }
            
            // Wait before next poll
            await new Promise(resolve => setTimeout(resolve, 500));
        } catch (error) {
            console.error('Error polling audio URL:', error);
            break;
        }
    }
    return null;
}

// Text-to-Speech with fallback to FPT AI
async function speakText(text) {
    const requestId = ++ttsRequestId;

    if (ttsFallbackTimer) {
        clearTimeout(ttsFallbackTimer);
        ttsFallbackTimer = null;
    }

    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = null;
        window.speechSynthesis.cancel();
    }

    stopFptAudio();
    
    // First, try to use browser's speech synthesis with Vietnamese voice
    if ('speechSynthesis' in window) {
        const getVoices = () => {
            if (checkVietnameseVoice() && vietnameseVoiceCache) {
                // Use Vietnamese voice from browser
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.voice = vietnameseVoiceCache;
                utterance.lang = 'vi-VN';
                utterance.rate = 0.85;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                
                utterance.onerror = (event) => {
                    console.error('Speech synthesis error:', event);
                    if (requestId === ttsRequestId) {
                        speakWithFPTAI(text, requestId);
                    }
                };
                
                window.speechSynthesis.speak(utterance);
                return true;
            }
            return false;
        };
        
        // Check voices immediately
        const voices = window.speechSynthesis.getVoices();
        if (voices.length > 0) {
            if (getVoices()) {
                if (ttsFallbackTimer) {
                    clearTimeout(ttsFallbackTimer);
                    ttsFallbackTimer = null;
                }
                window.speechSynthesis.onvoiceschanged = null;
                return; // Successfully using browser voice
            } else {
                // No Vietnamese voice found, use FPT AI
                speakWithFPTAI(text, requestId);
                return;
            }
        } else {
            // Wait for voices to load
            window.speechSynthesis.onvoiceschanged = () => {
                if (requestId !== ttsRequestId) return;
                window.speechSynthesis.onvoiceschanged = null;
                if (getVoices()) {
                    if (ttsFallbackTimer) {
                        clearTimeout(ttsFallbackTimer);
                        ttsFallbackTimer = null;
                    }
                    return;
                }
                speakWithFPTAI(text, requestId);
            };
            // Fallback after delay
            ttsFallbackTimer = setTimeout(() => {
                if (requestId !== ttsRequestId) return;
                window.speechSynthesis.onvoiceschanged = null;
                if (!getVoices()) {
                    speakWithFPTAI(text, requestId);
                }
            }, 500);
            return;
        }
    }
    
    // If speech synthesis not supported, use FPT AI TTS
    speakWithFPTAI(text, requestId);
}

// End game
async function endGame() {
    console.log('🎮 Ending game...');
    
    gameState.isDetecting = false;

    stopRoundTimer();
    if (gameState.detectionInterval) {
        clearInterval(gameState.detectionInterval);
        gameState.detectionInterval = null;
    }

    if (gameState.videoStream) {
        gameState.videoStream.getTracks().forEach(track => track.stop());
        gameState.videoStream = null;
    }

    // Về trạng thái chờ (ẩn chỉ số, hiện placeholder)
    setCameraPlaceholderVisible(true);
    resetDetectionUI();

    // Stop any ongoing speech
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }

    // Invalidate any in-flight async TTS (especially FPT audio fetch) to avoid voice being "chèn"
    ttsRequestId++;
    if (ttsFallbackTimer) {
        clearTimeout(ttsFallbackTimer);
        ttsFallbackTimer = null;
    }

    stopFptAudio();

    // Clear saved progress since level is completed
    clearGameProgress();

    // End session in backend
    console.log('Calling endSession()...');
    await endSession();

    // Show summary
    showSummary();
}

// Show summary
function showSummary() {
    const bestEmotion = gameState.finalBestEmotion || gameState.targetEmotion;
    const summaryText = typeof gameState.config?.summaryBuilder === 'function'
        ? gameState.config.summaryBuilder(bestEmotion)
        : 'Hôm nay con đã thể hiện cảm xúc rất tốt! Cảm xúc con làm giỏi nhất là ' +
            (bestEmotion || 'tất cả') + '. Lần sau mình luyện thêm nhé!';
    speakText(summaryText);
    
    // Show modal UI thay vì alert
    setTimeout(() => {
        showGameCompleteModal();
    }, 2000);
}

// Show game complete modal
function showGameCompleteModal() {
    const modal = document.getElementById('game-complete-modal');
    const completionMessage = document.getElementById('completion-message');
    const scoreDisplay = document.getElementById('score-display');
    const playAgainBtn = document.getElementById('play-again-btn');
    const exitBtn = document.getElementById('exit-btn');
    
    if (!modal) {
        // Fallback nếu không có modal
        const handleChoice = (ok) => {
            if (ok) {
                location.reload();
            } else {
                window.location.href = '/src/pages/home.html';
            }
        };

        if (window.egModal && typeof window.egModal.confirm === 'function') {
            window.egModal
                .confirm('Game đã hoàn thành! Con muốn chơi tiếp hay nghỉ một lát?', 'Hoàn thành', 'Chơi tiếp', 'Về trang chủ')
                .then(handleChoice);
        } else {
            handleChoice(confirm('Game đã hoàn thành! Con muốn chơi tiếp hay nghỉ một lát?'));
        }
        return;
    }
    
    // Set message - khác nhau cho GV1 và GV2
    if (completionMessage) {
        if (gameState.gameId === 'GV1') {
            completionMessage.textContent = 'Con đã hoàn thành level! Làm tốt lắm!';
        } else {
            completionMessage.textContent = 'Con đã hoàn thành thử thách! Làm tốt lắm!';
        }
    }
    
    // Set score - GV1: số màn pass; GV2: % tốt nhất
    if (scoreDisplay) {
        if (gameState.gameId === 'GV1') {
            const passed = Number(gameState.finalScore || 0);
            const total = Number((gameState.scenarios && gameState.scenarios.length) || 0);
            scoreDisplay.innerHTML = `
                <div class="score-value">Hoàn thành: <span class="score-number">${passed}</span>/${total} màn</div>
            `;
        } else {
            const score = Number(gameState.finalBestConfidenceScore || 0);
            scoreDisplay.innerHTML = `
                <div class="score-value">Điểm tốt nhất trong lần này: <span class="score-number">${score}</span>%</div>
            `;
        }
    }
    
    // Show modal
    modal.style.display = 'flex';
    
    // Play again button
    if (playAgainBtn) {
        playAgainBtn.onclick = () => {
            modal.style.display = 'none';
            // Quay về trang chọn level/cảm xúc để chơi lại
            const urlParams = new URLSearchParams(window.location.search);
            const gameId = urlParams.get('gameId') || gameState.gameId || 'GV1';
            window.location.href = `/src/pages/level_select.html?gameId=${gameId}`;
        };
    }
    
    // Exit button - quay về trang chọn level/cảm xúc
    if (exitBtn) {
        exitBtn.onclick = () => {
            modal.style.display = 'none';
            // Quay về trang chọn level/cảm xúc
            const urlParams = new URLSearchParams(window.location.search);
            const gameId = urlParams.get('gameId') || gameState.gameId || 'GV1';
            window.location.href = `/src/pages/level_select.html?gameId=${gameId}`;
        };
    }
}

// Error handling
function showError(message) {
    const errorEl = $('error-message');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
    console.error(message);
}

// Save game progress to localStorage
function saveGameProgress() {
    try {
        const progressKey = `gameCV_progress_${gameState.gameId}_${gameState.selectedLevel || 1}`;
        const progress = {
            gameId: gameState.gameId,
            selectedLevel: gameState.selectedLevel,
            selectedEmotion: gameState.selectedEmotion,
            currentScenarioIndex: gameState.currentScenarioIndex,
            sessionId: gameState.sessionId,
            scenarios: gameState.scenarios.map(s => ({ id: s.id, title: s.title })), // Only save IDs and titles
            timestamp: Date.now()
        };
        localStorage.setItem(progressKey, JSON.stringify(progress));
        console.log(`💾 Saved game progress: scenario ${gameState.currentScenarioIndex + 1}/${gameState.scenarios.length}`);
    } catch (e) {
        console.warn('Could not save game progress:', e);
    }
}

// Show continue game modal and return when user chooses
function showContinueGameModal(progress, progressKey) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.id = 'continue-game-modal';
        modal.className = 'game-complete-modal';
        modal.style.display = 'flex';

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>🎮 Tiếp tục chơi?</h2>
                </div>
                <div class="modal-body">
                    <p>
                        Bạn đang chơi dở level <strong class="cv-modal-highlight">${gameState.selectedLevel}</strong>.<br>
                        Tiếp tục từ màn <strong class="cv-modal-highlight">${progress.currentScenarioIndex + 1}</strong> nhé?
                    </p>
                </div>
                <div class="modal-actions">
                    <button id="continue-yes-btn" class="modal-btn play-again-btn">✅ Tiếp tục</button>
                    <button id="continue-no-btn" class="modal-btn exit-btn">🔄 Chơi lại từ đầu</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        const cleanup = () => {
            if (modal.parentNode) document.body.removeChild(modal);
        };

        // Tiếp tục chơi
        document.getElementById('continue-yes-btn').onclick = () => {
            cleanup();
            gameState.sessionId = progress.sessionId;
            gameState.currentScenarioIndex = progress.currentScenarioIndex || 0;
            console.log(`✅ Continuing from saved progress: scenario ${gameState.currentScenarioIndex + 1}, session ${gameState.sessionId}`);
            resolve();
        };

        // Chơi lại từ đầu
        document.getElementById('continue-no-btn').onclick = () => {
            cleanup();
            console.log(`🔄 User chose to start from beginning - ending old session ${progress.sessionId}`);
            try {
                const blob = new Blob([JSON.stringify({ session_id: progress.sessionId })], {
                    type: 'application/json'
                });
                navigator.sendBeacon(`${API_URL}/games/cv/end`, blob);
            } catch (e) {
                console.warn('⚠️ Error ending old session:', e);
            }
            gameState.currentScenarioIndex = 0;
            localStorage.removeItem(progressKey);
            console.log(`🔄 Using NEW session ${gameState.sessionId}`);
            resolve();
        };
    });
}

// Load game progress from localStorage
// Returns true if need to create new session, false if using old session
async function loadGameProgress() {
    try {
        const progressKey = `gameCV_progress_${gameState.gameId}_${gameState.selectedLevel || 1}`;
        const savedProgress = localStorage.getItem(progressKey);
        
        if (savedProgress) {
            const progress = JSON.parse(savedProgress);
            // Check if progress is recent (within 1 hour) and for same game/level
            const oneHour = 60 * 60 * 1000;
            const isRecent = (Date.now() - progress.timestamp) < oneHour;
            
            if (isRecent && 
                progress.gameId === gameState.gameId && 
                progress.selectedLevel === gameState.selectedLevel &&
                progress.sessionId) {
                console.log(`📂 Found saved progress: scenario ${progress.currentScenarioIndex + 1}, session ${progress.sessionId}`);
                
                // Check if this is a reload (F5) or a fresh visit (closed tab then reopened)
                const isReload = sessionStorage.getItem('gameCV_active_session');
                
                if (isReload) {
                    // RELOAD case - always use old session, regardless of progress
                    console.log('🔄 Reload detected - auto continuing from saved progress');
                    gameState.sessionId = progress.sessionId;
                    gameState.currentScenarioIndex = progress.currentScenarioIndex || 0;
                    sessionStorage.setItem('gameCV_active_session', 'true');
                    return false; // Use old session, DON'T create new
                }
                
                // FRESH VISIT (from menu/home/new tab)
                if (progress.currentScenarioIndex > 0) {
                    // Has progress - ask user
                    console.log('🆕 Fresh visit detected - asking user');
                    await showContinueGameModal(progress, progressKey);
                    sessionStorage.setItem('gameCV_active_session', 'true');
                    
                    // Check if user chose continue (sessionId set) or restart (null)
                    if (gameState.sessionId) {
                        return false; // User chose continue, use old session
                    } else {
                        return true; // User chose restart, create new session
                    }
                } else {
                    // No real progress yet (just started), treat as new game
                    localStorage.removeItem(progressKey);
                    console.log('🆕 Fresh visit with no progress, creating new session');
                    sessionStorage.setItem('gameCV_active_session', 'true');
                    return true;
                }
            } else {
                // Progress is old or doesn't match, create new session
                localStorage.removeItem(progressKey);
                console.log('🔄 Cleared old/invalid progress, creating new session');
                sessionStorage.setItem('gameCV_active_session', 'true');
                return true;
            }
        }
        
        // No saved progress, create new session
        console.log('🆕 No saved progress, creating new session');
        sessionStorage.setItem('gameCV_active_session', 'true');
        return true;
    } catch (e) {
        console.warn('Could not load game progress:', e);
        sessionStorage.setItem('gameCV_active_session', 'true');
        return true;
    }
}

// Clear game progress (when level is completed)
function clearGameProgress() {
    try {
        const progressKey = `gameCV_progress_${gameState.gameId}_${gameState.selectedLevel || 1}`;
        localStorage.removeItem(progressKey);
        console.log('🗑️ Cleared game progress');
    } catch (e) {
        console.warn('Could not clear game progress:', e);
    }
}

// Logout
function handleLogout() {
    const doLogout = () => {
        localStorage.removeItem('currentUser');
        window.location.href = '/src/pages/login.html';
    };

    if (window.egModal && typeof window.egModal.confirm === 'function') {
        window.egModal
            .confirm('Bạn có chắc chắn muốn đăng xuất không?', 'Xác nhận đăng xuất', 'Đăng xuất', 'Hủy')
            .then((ok) => {
                if (!ok) return;
                doLogout();
            });
        return;
    }

    if (confirm('Bạn có muốn đăng xuất không?')) {
        doLogout();
    }
}

// REMOVED beforeunload: It was ending session on reload (F5) too
// Session should only end when:
// 1. User clicks back/home button (handled below)
// 2. User finishes all scenarios (endGame)
// 3. User chooses "Chơi lại" in popup (handled in modal)

// COMMENTED OUT: This was causing premature session end when switching tabs
// The beforeunload event handler above is sufficient for cleanup
// document.addEventListener('visibilitychange', async () => {
//     if (document.hidden && gameState.sessionId && !gameState.isDetecting) {
//         // Page is hidden and not actively playing, end session
//         await endSession();
//     }
// });

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - Game CV');
    
    try {
        // Load voices for speech synthesis (needed for Vietnamese TTS)
        if ('speechSynthesis' in window) {
            // Trigger voice loading
            window.speechSynthesis.getVoices();
            // Some browsers need this event
            window.speechSynthesis.onvoiceschanged = () => {
                // Check and cache Vietnamese voice
                checkVietnameseVoice();
                const voices = window.speechSynthesis.getVoices();
                const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
                if (isDevelopment) {
                    console.log('Available voices:', voices.length);
                }
                if (hasVietnameseVoice) {
                    if (isDevelopment) {
                        console.log('Vietnamese voice found:', vietnameseVoiceCache?.name);
                    }
                } else {
                    if (isDevelopment) {
                        console.log('No Vietnamese voice found, will use FPT AI TTS for Vietnamese');
                    }
                }
            };
        }
        
        // Wait for face-api.js to load
        const checkFaceApi = setInterval(() => {
            if (typeof faceapi !== 'undefined') {
                clearInterval(checkFaceApi);
                console.log('Face-api.js loaded, initializing game...');
                initGame().catch(error => {
                    console.error('Error in initGame:', error);
                    showError('Lỗi khởi tạo game: ' + error.message);
                });
            }
        }, 100);
        
        // Timeout after 5 seconds
        setTimeout(() => {
            clearInterval(checkFaceApi);
            if (typeof faceapi === 'undefined') {
                console.error('Face-api.js not loaded after 5 seconds');
                showError('Không thể tải thư viện nhận diện. Vui lòng tải lại trang.');
            }
        }, 5000);
    } catch (error) {
        console.error('Error in DOMContentLoaded:', error);
        showError('Lỗi khởi tạo: ' + error.message);
    }
});

