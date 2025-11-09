const API_URL = "http://localhost:8000";

// Game state
let gameState = {
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
    successThreshold: 2000, // 2 seconds holding correct emotion
    maxAttemptTime: 30000, // 30 seconds max
    speechSynthesis: null
};

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

// Helper functions
const $ = (id) => document.getElementById(id);
const $$ = (selector) => document.querySelector(selector);

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
            alert('Không tìm thấy thông tin người dùng. Vui lòng đăng nhập lại.');
            console.log('Redirecting to login after alert...');
            window.location.href = '/src/pages/login.html';
        }, 3000);
        return;
    }
    
    console.log('✅ User found:', userId);

    // Get level from query params
    const urlParams = new URLSearchParams(window.location.search);
    const selectedLevel = parseInt(urlParams.get('level')) || 1;
    gameState.selectedLevel = selectedLevel;
    console.log('Selected level:', selectedLevel);

    // Load face-api.js models
    await loadFaceApiModels();
    
    // Load scenarios from backend
    await loadScenarios();
    
    // Filter scenarios by level
    const originalCount = gameState.scenarios.length;
    gameState.scenarios = gameState.scenarios.filter(scenario => {
        const scenarioLevel = scenario.level || 1;
        return scenarioLevel === selectedLevel;
    });
    
    console.log(`Filtered scenarios: ${originalCount} total -> ${gameState.scenarios.length} for level ${selectedLevel}`);
    
    if (gameState.scenarios.length === 0) {
        showError(`Không có màn nào ở level ${selectedLevel}. Vui lòng chọn level khác.`);
        setTimeout(() => {
            window.location.href = '/src/pages/select_game.html';
        }, 3000);
        return;
    }
    
    // Setup event listeners
    setupEventListeners();
    
    // Start first scenario
    if (gameState.scenarios.length > 0) {
        startScenario(0);
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
async function loadScenarios() {
    try {
        const response = await fetch(`${API_URL}/games/cv/scenarios`);
        if (!response.ok) throw new Error('Failed to load scenarios');
        const data = await response.json();
        gameState.scenarios = data.scenarios || [];
        console.log('Scenarios loaded:', gameState.scenarios);
    } catch (error) {
        console.error('Error loading scenarios:', error);
        showError('Không thể tải tình huống. Vui lòng thử lại.');
    }
}

// Setup event listeners
function setupEventListeners() {
    $('hint-btn')?.addEventListener('click', showHint);
    $('start-btn')?.addEventListener('click', startDetection);
    $('back-button')?.addEventListener('click', () => window.history.back());
    $('logout-button')?.addEventListener('click', handleLogout);
}

// Start a scenario
function startScenario(index) {
    if (index >= gameState.scenarios.length) {
        endGame();
        return;
    }

    gameState.currentScenarioIndex = index;
    gameState.currentScenario = gameState.scenarios[index];
    gameState.targetEmotion = gameState.currentScenario.target_emotion;
    gameState.isDetecting = false;
    gameState.currentEmotion = null;
    gameState.detectionStartTime = null;

    // Update UI
    updateScenarioUI();
    
    // Read scenario description
    speakText(`Con nghe tình huống nhé. ${gameState.currentScenario.description}`);
    
    // Start countdown
    startCountdown();
}

// Update scenario UI
function updateScenarioUI() {
    $('scenario-title').textContent = gameState.currentScenario.title;
    $('scenario-description').textContent = gameState.currentScenario.description;
    $('target-emotion').textContent = `Cảm xúc: ${gameState.currentScenario.target_emotion}`;
    
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
    countdownEl.style.display = 'block';
    
    const interval = setInterval(() => {
        count--;
        if (count > 0) {
            countdownEl.textContent = `${count}...`;
        } else {
            countdownEl.textContent = 'Chuẩn bị nào...';
            clearInterval(interval);
            setTimeout(() => {
                countdownEl.style.display = 'none';
            }, 1000);
        }
    }, 1000);
}

// Show hint animation
function showHint() {
    if (!gameState.currentScenario) return;
    
    const hintContainer = $('hint-animation');
    const emotion = gameState.targetEmotion;
    const hintText = gameState.currentHint || `Hãy thể hiện cảm xúc ${emotion}!`;
    
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
                facingMode: 'user',
                width: { ideal: 640 },
                height: { ideal: 480 }
            } 
        });
        gameState.videoStream = stream;
        
        const video = $('camera-video');
        video.srcObject = stream;
        
        // Wait for video to be ready
        await new Promise((resolve, reject) => {
            video.onloadedmetadata = () => {
                video.play().then(resolve).catch(reject);
            };
            video.onerror = reject;
            setTimeout(() => reject(new Error('Video load timeout')), 5000);
        });
        
        gameState.isDetecting = true;
        gameState.detectionStartTime = Date.now();
        
        // Disable start button
        $('start-btn').disabled = true;
        $('start-btn').textContent = 'Đang nhận diện...';
        
        // Start session
        await startSession();
        
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
        
        // Re-enable button
        $('start-btn').disabled = false;
        $('start-btn').textContent = '▶️ Bắt đầu';
    }
}

// Start session
async function startSession() {
    try {
        const user = JSON.parse(localStorage.getItem('currentUser') || '{}');
        const userId = user.user_id || user.userId || user.id || user.user?.user_id;
        
        if (!userId) {
            console.error('Cannot start session: no user_id found');
            return;
        }
        
        const response = await fetch(`${API_URL}/games/cv/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                game_type: 'GameCV'
            })
        });
        const data = await response.json();
        gameState.sessionId = data.session_id;
    } catch (error) {
        console.error('Error starting session:', error);
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
                
                // Update UI
                updateDetectionUI(gameEmotion, confidence);
                
                // Check if correct emotion
                if (gameEmotion === gameState.targetEmotion && confidence > 0.7) {
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
    
    const emotionIcon = $('detected-emotion-icon');
    const emotionPercent = $('detected-emotion-percent');
    
    if (emotion) {
        emotionIcon.textContent = EMOTION_ICONS[emotion] || '😐';
        emotionPercent.textContent = `${Math.round(confidence * 100)}%`;
    } else {
        emotionIcon.textContent = '👤';
        emotionPercent.textContent = '0%';
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
    
    gameState.isDetecting = false;
    if (gameState.detectionInterval) {
        clearInterval(gameState.detectionInterval);
        gameState.detectionInterval = null;
    }
    
    // Stop camera
    if (gameState.videoStream) {
        gameState.videoStream.getTracks().forEach(track => track.stop());
        gameState.videoStream = null;
    }
    
    // Re-enable start button
    $('start-btn').disabled = false;
    $('start-btn').textContent = '▶️ Bắt đầu';
    
    // Show success animation
    showSuccessAnimation();
    
    // Speak success message
    speakText(`Quá tuyệt! Con làm rất tốt.`);
    
    // Save result
    await saveResult(true);
    
    // Move to next scenario after delay
    setTimeout(() => {
        startScenario(gameState.currentScenarioIndex + 1);
    }, 3000);
}

// Handle timeout
async function handleTimeout() {
    if (!gameState.isDetecting) return; // Prevent multiple calls
    
    gameState.isDetecting = false;
    if (gameState.detectionInterval) {
        clearInterval(gameState.detectionInterval);
        gameState.detectionInterval = null;
    }
    
    // Stop camera
    if (gameState.videoStream) {
        gameState.videoStream.getTracks().forEach(track => track.stop());
        gameState.videoStream = null;
    }
    
    // Re-enable start button
    $('start-btn').disabled = false;
    $('start-btn').textContent = '▶️ Bắt đầu';
    
    speakText('Chúng ta thử lại thêm lần nữa nhé! Câu sau mình sẽ làm tốt hơn!');
    
    // Save result
    await saveResult(false);
    
    // Move to next scenario
    setTimeout(() => {
        startScenario(gameState.currentScenarioIndex + 1);
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
async function saveResult(success) {
    try {
        await fetch(`${API_URL}/games/cv/result`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: gameState.sessionId,
                scenario_id: gameState.currentScenario.id,
                target_emotion: gameState.targetEmotion,
                detected_emotion: gameState.currentEmotion,
                success: success,
                time_taken: Date.now() - gameState.detectionStartTime
            })
        });
    } catch (error) {
        console.error('Error saving result:', error);
    }
}

// Cache for Vietnamese voice availability
let hasVietnameseVoice = null;
let vietnameseVoiceCache = null;

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
async function speakWithFPTAI(text) {
    try {
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
            // FPT AI returns async URL, try to poll for result
            audioUrl = await pollForAudioUrl(data.async);
            // If polling fails, try using async URL directly (might be direct audio URL)
            if (!audioUrl) {
                audioUrl = data.async;
            }
        } else if (data.url) {
            // Direct audio URL
            audioUrl = data.url;
        }
        
        if (audioUrl) {
            const audio = new Audio(audioUrl);
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

// Poll for audio URL from FPT AI async endpoint
async function pollForAudioUrl(asyncUrl, maxAttempts = 10) {
    for (let i = 0; i < maxAttempts; i++) {
        try {
            const response = await fetch(asyncUrl);
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
    // Cancel any ongoing speech
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    
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
                    // Fallback to FPT AI on error
                    speakWithFPTAI(text);
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
                return; // Successfully using browser voice
            } else {
                // No Vietnamese voice found, use FPT AI
                speakWithFPTAI(text);
                return;
            }
        } else {
            // Wait for voices to load
            window.speechSynthesis.onvoiceschanged = () => {
                if (!getVoices()) {
                    // No Vietnamese voice, use FPT AI
                    speakWithFPTAI(text);
                }
            };
            // Fallback after delay
            setTimeout(() => {
                if (!getVoices()) {
                    speakWithFPTAI(text);
                }
            }, 500);
            return;
        }
    }
    
    // If speech synthesis not supported, use FPT AI TTS
    speakWithFPTAI(text);
}

// End game
function endGame() {
    gameState.isDetecting = false;
    if (gameState.detectionInterval) {
        clearInterval(gameState.detectionInterval);
    }
    
    if (gameState.videoStream) {
        gameState.videoStream.getTracks().forEach(track => track.stop());
    }
    
    // Stop any ongoing speech
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    
    // Show summary
    showSummary();
}

// Show summary
function showSummary() {
    const summaryText = 'Hôm nay con đã thể hiện cảm xúc rất tốt! Cảm xúc con làm giỏi nhất là ' + 
        (gameState.targetEmotion || 'tất cả') + '. Lần sau mình luyện thêm nhé!';
    speakText(summaryText);
    
    // Show summary UI (simple alert for now, can be enhanced)
    setTimeout(() => {
        if (confirm('Game đã hoàn thành! Con muốn chơi tiếp hay nghỉ một lát?')) {
            // Restart game
            location.reload();
        } else {
            // Go back to home
            window.location.href = '/src/pages/home.html';
        }
    }, 3000);
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

// Logout
function handleLogout() {
    if (confirm('Bạn có muốn đăng xuất không?')) {
        localStorage.removeItem('currentUser');
        window.location.href = '/src/pages/login.html';
    }
}

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

