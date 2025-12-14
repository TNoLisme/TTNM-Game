(function () {
  const API_URL = 'http://localhost:8000/assistant/chat';
  const GAME_ID = getGameIdFromLocation();
  const BACKEND_BASE = API_URL.replace('/assistant/chat', '');
  let allowTts = false;

  let hasVietnameseVoice = null;
  let vietnameseVoiceCache = null;

  function getGameIdFromLocation() {
    try {
      const path = window.location.pathname || '';
      const file = path.split('/').pop() || '';
      const base = file.replace(/\.html$/i, '');
      const map = {
        game_click_2: 'game_click_2',
        game_click_3: 'game_click_3',
        game_click_4: 'game_click_4',
        gameCV: 'gameCV',
        game_cv_2: 'gameCV',
        recognize_emotion: 'recognize_emotion',
        level_select: 'level_select',
        select_game: 'select_game',
        home: 'home',
        learn: 'learn',
        profile: 'profile',
        login: 'login',
        register: 'register',
        admin: 'admin',
        test_email: 'test_email',
      };
      return map[base] || base || 'global';
    } catch (e) {
      return 'global';
    }
  }

  function getLevelFromUrl() {
    try {
      const params = new URLSearchParams(window.location.search);
      const raw = params.get('level');
      const n = raw ? Number(raw) : NaN;
      return Number.isNaN(n) ? null : n;
    } catch (e) {
      return null;
    }
  }

  function createMessageElement(text, role) {
    const el = document.createElement('div');
    el.className = `eg-chatbot-message eg-chatbot-message-${role}`;
    el.textContent = text;
    return el;
  }

  function checkVietnameseVoice() {
    if (hasVietnameseVoice !== null) {
      return hasVietnameseVoice;
    }

    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      hasVietnameseVoice = false;
      return false;
    }

    const voices = window.speechSynthesis.getVoices() || [];
    const vietnameseVoice = voices.find((voice) => {
      const lang = (voice.lang || '').toLowerCase();
      const name = (voice.name || '').toLowerCase();
      return (
        lang === 'vi-vn' ||
        lang === 'vi' ||
        lang.includes('vietnam') ||
        name.includes('vietnamese') ||
        name.includes('việt') ||
        name.includes('viet')
      );
    });

    if (vietnameseVoice) {
      vietnameseVoiceCache = vietnameseVoice;
      hasVietnameseVoice = true;
      return true;
    }

    hasVietnameseVoice = false;
    return false;
  }

  // Đọc tiếng Việt bằng speechSynthesis của trình duyệt, ưu tiên voice tiếng Việt nếu có
  async function speakWithFPTAI(text) {
    try {
      if (!text) return;

      const response = await fetch('https://api.fpt.ai/hmi/tts/v5', {
        method: 'POST',
        headers: {
          'api-key': 'OXvPopJqIJgON0AglCE0KPkBvOovWSoy',
          speed: '0.8',
          voice: 'banmai',
        },
        body: text,
      });

      if (!response.ok) {
        throw new Error('FPT AI TTS API error');
      }

      const data = await response.json();

      let audioUrl = null;
      if (data.async) {
        // Nếu async đã là link .mp3 hoặc file01.fpt.ai thì dùng luôn
        if (data.async.includes('.mp3') || data.async.includes('file01.fpt.ai')) {
          audioUrl = data.async;
        } else {
          // Ngược lại, đây thường là endpoint JSON -> dùng proxy để poll lấy url thật
          audioUrl = await resolveFptAsyncUrl(data.async);
        }
      } else if (data.url) {
        audioUrl = data.url;
      }

      if (audioUrl) {
        try {
          console.log('[Chatbot TTS] FPT final audioUrl:', audioUrl);
        } catch (_) {}

        // Ưu tiên phát trực tiếp file mp3 từ FPT (thường không bị CORS khi chỉ phát audio)
        if (audioUrl.includes('.mp3') || audioUrl.includes('file01.fpt.ai')) {
          const directAudio = new Audio(audioUrl);
          directAudio.play().catch((err) => {
            console.warn('[Chatbot TTS] Không phát được audio FPT trực tiếp, thử qua proxy. Chi tiết:', err);
            const proxyUrl = `${BACKEND_BASE}/games/cv/audio-proxy?url=${encodeURIComponent(audioUrl)}`;
            try {
              console.log('[Chatbot TTS] proxy audio URL:', proxyUrl);
            } catch (_) {}
            const proxiedAudio = new Audio(proxyUrl);
            proxiedAudio.play().catch((err2) => {
              console.warn('[Chatbot TTS] Không phát được audio FPT qua proxy. Chi tiết:', err2);
            });
          });
        } else {
          // Trường hợp audioUrl không phải mp3 rõ ràng, vẫn dùng proxy
          const proxyUrl = `${BACKEND_BASE}/games/cv/audio-proxy?url=${encodeURIComponent(audioUrl)}`;
          try {
            console.log('[Chatbot TTS] proxy audio URL:', proxyUrl);
          } catch (_) {}
          const proxiedAudio = new Audio(proxyUrl);
          proxiedAudio.play().catch((err2) => {
            console.warn('[Chatbot TTS] Không phát được audio FPT qua proxy. Chi tiết:', err2);
          });
        }
      } else {
        console.warn('[Chatbot TTS] Không tìm được URL audio hợp lệ từ FPT AI.');
      }
    } catch (error) {
      console.warn('FPT AI TTS error (không nghiêm trọng, chỉ là không phát được tiếng):', error);
    }
  }

  async function resolveFptAsyncUrl(asyncUrl) {
    try {
      const proxyUrl = `${BACKEND_BASE}/games/cv/audio-proxy?url=${encodeURIComponent(asyncUrl)}`;
      // Thử poll nhiều lần giống game CV
      for (let i = 0; i < 6; i++) {
        try {
          const res = await fetch(proxyUrl);
          if (!res.ok) continue;
          const data = await res.json().catch(() => null);
          if (data && data.url) {
            return data.url;
          }
        } catch (e) {
          // bỏ qua và thử lại lần sau
        }
        await new Promise((resolve) => setTimeout(resolve, 500));
      }
    } catch (e) {
      console.warn('[Chatbot TTS] Lỗi khi resolve async URL FPT:', e);
    }
    return null;
  }

  function speakTextVi(text) {
    try {
      if (!text || typeof window === 'undefined') return;

      try {
        console.log('[Chatbot TTS] speakTextVi called with text:', String(text).slice(0, 80));
      } catch (_) {}

      const hasSpeechSynthesis = 'speechSynthesis' in window && typeof SpeechSynthesisUtterance !== 'undefined';

      if (hasSpeechSynthesis) {
        // Hủy câu đang đọc, nếu có
        window.speechSynthesis.cancel();
      }

      const tryBrowserVietnamese = () => {
        if (!hasSpeechSynthesis) return false;
        const voices = window.speechSynthesis.getVoices() || [];
        try {
          console.log('[Chatbot TTS] available voices:', voices.map((v) => `${v.name} (${v.lang})`));
        } catch (_) {}

        if (!voices.length) return false;

        if (checkVietnameseVoice() && vietnameseVoiceCache) {
          try {
            console.log('[Chatbot TTS] using VI voice:', vietnameseVoiceCache.name, vietnameseVoiceCache.lang);
          } catch (_) {}
          const utter = new SpeechSynthesisUtterance(text);
          utter.voice = vietnameseVoiceCache;
          utter.lang = 'vi-VN';
          utter.rate = 0.85;
          utter.pitch = 1.0;
          utter.volume = 1.0;
          window.speechSynthesis.speak(utter);
          return true;
        }
        return false;
      };

      if (hasSpeechSynthesis) {
        const voices = window.speechSynthesis.getVoices() || [];
        if (voices.length > 0) {
          if (!tryBrowserVietnamese()) {
            // Không có voice tiếng Việt: fallback sang FPT AI
            speakWithFPTAI(text);
          }
        } else {
          window.speechSynthesis.onvoiceschanged = () => {
            if (!tryBrowserVietnamese()) {
              speakWithFPTAI(text);
            }
          };
          setTimeout(() => {
            if (!tryBrowserVietnamese()) {
              speakWithFPTAI(text);
            }
          }, 500);
        }
      } else {
        // Trình duyệt không hỗ trợ speechSynthesis, dùng FPT AI
        speakWithFPTAI(text);
      }
    } catch (e) {
      // ignore
    }
  }

  function initChatbotWidget() {
    if (document.querySelector('.eg-chatbot-container')) return;

    const container = document.createElement('div');
    container.className = 'eg-chatbot-container';

    container.innerHTML = `
      <button class="eg-chatbot-toggle" aria-label="Mở trợ lý EmoGarden">
        💬
      </button>
      <div class="eg-chatbot-panel" aria-label="Trợ lý EmoGarden" role="dialog">
        <div class="eg-chatbot-header">
          <div class="eg-chatbot-title">Trợ lý EmoGarden</div>
          <button class="eg-chatbot-close" aria-label="Đóng">×</button>
        </div>
        <div class="eg-chatbot-messages" id="eg-chatbot-messages"></div>
        <form class="eg-chatbot-input-row">
          <input type="text" class="eg-chatbot-input" placeholder="Hỏi cách chơi game này..." autocomplete="off" />
          <button type="button" class="eg-chatbot-mic" aria-label="Nói để hỏi">🎤</button>
          <button type="submit" class="eg-chatbot-send">Gửi</button>
          <div class="eg-chatbot-voice-bar" aria-hidden="true">
            <div class="eg-chatbot-voice-wave">
              <span></span>
              <span></span>
              <span></span>
              <span></span>
              <span></span>
            </div>
            <div class="eg-chatbot-voice-text">Đang nghe...</div>
            <div class="eg-chatbot-voice-actions">
              <button type="button" class="eg-chatbot-voice-cancel" aria-label="Hủy ghi âm">✕</button>
              <button type="button" class="eg-chatbot-voice-confirm" aria-label="Gửi câu hỏi vừa nói">✓</button>
            </div>
          </div>
        </form>
      </div>
    `;

    document.body.appendChild(container);

    const toggleBtn = container.querySelector('.eg-chatbot-toggle');
    const panel = container.querySelector('.eg-chatbot-panel');
    const closeBtn = container.querySelector('.eg-chatbot-close');
    const messagesEl = container.querySelector('.eg-chatbot-messages');
    const form = container.querySelector('.eg-chatbot-input-row');
    const input = container.querySelector('.eg-chatbot-input');
    const micBtn = container.querySelector('.eg-chatbot-mic');
    const sendBtn = container.querySelector('.eg-chatbot-send');
    const voiceBar = container.querySelector('.eg-chatbot-voice-bar');
    const voiceText = container.querySelector('.eg-chatbot-voice-text');
    const voiceCancelBtn = container.querySelector('.eg-chatbot-voice-cancel');
    const voiceConfirmBtn = container.querySelector('.eg-chatbot-voice-confirm');

    const SpeechRecognition =
      (typeof window !== 'undefined' && (window.SpeechRecognition || window.webkitSpeechRecognition)) ||
      null;
    let recognition = null;
    let recognizing = false;
    let pendingTranscript = '';

    function openVoiceBar() {
      if (!voiceBar || !voiceText) return;
      if (form) {
        form.classList.add('eg-chatbot-input-row-recording');
      }
      voiceBar.classList.add('eg-chatbot-voice-bar-open');
      voiceBar.setAttribute('aria-hidden', 'false');
      pendingTranscript = '';
      voiceText.textContent = 'Đang nghe...';
    }

    function closeVoiceBar() {
      if (!voiceBar || !voiceText) return;
      if (form) {
        form.classList.remove('eg-chatbot-input-row-recording');
      }
      voiceBar.classList.remove('eg-chatbot-voice-bar-open');
      voiceBar.setAttribute('aria-hidden', 'true');
      pendingTranscript = '';
    }

    if (SpeechRecognition && micBtn) {
      recognition = new SpeechRecognition();
      recognition.lang = 'vi-VN';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {
        recognizing = true;
        micBtn.classList.add('eg-chatbot-mic-active');
        openVoiceBar();
      };

      recognition.onend = () => {
        recognizing = false;
        micBtn.classList.remove('eg-chatbot-mic-active');
      };

      recognition.onresult = (event) => {
        try {
          const result = event.results && event.results[0] && event.results[0][0];
          const transcript = result && result.transcript;
          if (transcript && voiceText) {
            pendingTranscript = transcript.trim();
            voiceText.textContent = pendingTranscript || 'Mình chưa nghe rõ, thử nói lại nhé.';
          }
        } catch (e) {}
      };

      recognition.onerror = () => {
        if (voiceText) {
          voiceText.textContent = 'Mình chưa nghe rõ, thử nói lại nhé.';
        }
      };

      micBtn.addEventListener('click', () => {
        try {
          if (!recognition) {
            addMessage('Trình duyệt chưa hỗ trợ nói để hỏi. Con gõ chữ giúp mình nhé.', 'assistant');
            return;
          }
          if (recognizing) {
            recognition.stop();
            closeVoiceBar();
          } else {
            openVoiceBar();
            recognition.start();
          }
        } catch (e) {
          addMessage('Không mở được micro. Con kiểm tra lại quyền truy cập micro giúp nhé.', 'assistant');
        }
      });

      if (voiceCancelBtn) {
        voiceCancelBtn.addEventListener('click', () => {
          pendingTranscript = '';
          if (recognition && recognizing) {
            try {
              recognition.stop();
            } catch (e) {}
          }
          closeVoiceBar();
        });
      }

      if (voiceConfirmBtn) {
        voiceConfirmBtn.addEventListener('click', () => {
          if (!pendingTranscript) {
            if (voiceText) {
              voiceText.textContent = 'Mình chưa nghe rõ, thử nói lại nhé.';
            }
            return;
          }
          input.value = pendingTranscript;
          pendingTranscript = '';
          closeVoiceBar();
          if (input.value) {
            form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
          }
        });
      }
    } else if (micBtn) {
      micBtn.addEventListener('click', () => {
        addMessage('Trình duyệt này chưa hỗ trợ micro cho trò chơi. Con tạm thời gõ chữ nhé.', 'assistant');
      });
    }

    function openPanel() {
      panel.classList.add('eg-chatbot-panel-open');
      allowTts = true;
      input.focus();
    }

    function closePanel() {
      panel.classList.remove('eg-chatbot-panel-open');
    }

    function addMessage(text, role) {
      const el = createMessageElement(text, role);
      messagesEl.appendChild(el);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      if (role === 'assistant' && allowTts) {
        speakTextVi(text);
      }
    }

    toggleBtn.addEventListener('click', () => {
      if (panel.classList.contains('eg-chatbot-panel-open')) {
        closePanel();
      } else {
        openPanel();
      }
    });

    closeBtn.addEventListener('click', () => {
      closePanel();
    });

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const text = (input.value || '').trim();
      if (!text) return;

      addMessage(text, 'user');
      input.value = '';

      const level = getLevelFromUrl();
      const payload = {
        game_id: GAME_ID,
        level: level,
        message: text,
      };

      addMessage('Đang nghĩ câu trả lời...', 'assistant system');

      try {
        const res = await fetch(API_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        // Xóa message "đang nghĩ" cuối cùng
        const pending = messagesEl.querySelector('.eg-chatbot-message-assistant.system:last-child');
        if (pending) pending.remove();

        if (!res.ok) {
          let msg = 'Có lỗi khi gọi trợ lý. Bạn thử lại sau nhé.';
          try {
            const data = await res.json();
            if (data && data.detail) msg = data.detail;
          } catch (_) {
            // bỏ qua
          }
          addMessage(msg, 'assistant');
          return;
        }

        const data = await res.json();
        const reply = (data && data.reply) || 'Trợ lý chưa trả lời được câu này, bạn thử hỏi cách khác nhé.';
        addMessage(reply, 'assistant');
      } catch (err) {
        addMessage('Không kết nối được tới trợ lý. Kiểm tra lại backend hoặc mạng nhé.', 'assistant');
      }
    });

    // Lời chào ban đầu
    addMessage('Chào bé! Mình là trợ lý EmoGarden, có thể giúp bé hiểu cách chơi game này.', 'assistant');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatbotWidget);
  } else {
    initChatbotWidget();
  }
})();
