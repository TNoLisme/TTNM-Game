// fe/src/components/select_game.js

// Ảnh nền cho từng game (dùng sẵn các ảnh ensemble trong assets)
const GAME_THUMBNAILS = {
    'ea2b5c7e-aec8-4f6e-a8bf-99d7b6a05dd8': '/fe/assets/images/recognize_emotion.png',    // Chiếc hộp cảm xúc
    '8573ebd6-23be-4ad9-bd4c-3794b1c4a4fa': '/fe/assets/images/game_click_4.png',    // Thám tử cảm xúc
    'e7b4826b-57ba-4569-953e-723da913d47c': '/fe/assets/images/game_click_3.png', // Cảm xúc đúng chỗ
    'ecefa8d8-b9f5-4d41-abf9-316e6b6cf25b': '/fe/assets/images/game_click_2.png',  // Xưởng lắp ghép cảm xúc
    'bbd1597f-02b1-4e20-b39b-31d27335d385': '/fe/assets/images/game_cv_2.png',     // Thử thách cảm xúc (CV2)
    '9b56e632-dd86-4868-9d74-e0c93125430a': '/fe/assets/images/gameCV.png',       // Câu chuyện trên khuôn mặt
};

function getGameThumbnail(game) {
    const id = (game.game_id || '').toLowerCase();
    if (GAME_THUMBNAILS[id]) return GAME_THUMBNAILS[id];
    // fallback chung
    return '/fe/assets/images/index_image.png';
}

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

document.addEventListener('DOMContentLoaded', async () => {
    const user = JSON.parse(localStorage.getItem('currentUser'));
    if (!user) {
        if (window.egModal && typeof window.egModal.alert === 'function') {
            await window.egModal.alert('Vui lòng đăng nhập!', 'Thông báo');
        } else {
            alert('Vui lòng đăng nhập!');
        }
        window.location.href = '/src/pages/login.html';
        return;
    }

    let games = [];
    try {
        // GỌI ĐÚNG: /api/games (nếu có prefix) HOẶC /games/ (nếu không)
        const res = await fetch('/games', {  // DÙNG /api/games
            headers: { 'Authorization': `Bearer ${user.token}` }
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();
        console.log('Dữ liệu game từ API:', data); // DEBUG

        if (!data) throw new Error(data.message || 'Lỗi dữ liệu');

        games = data || [];
    } catch (err) {
        console.error('Lỗi tải game:', err);
        if (window.egModal && typeof window.egModal.alert === 'function') {
            await window.egModal.alert('Không thể tải danh sách game. Vui lòng thử lại.', 'Lỗi');
        } else {
            alert('Không thể tải danh sách game. Vui lòng thử lại.');
        }
        return;
    }

    const clickList = document.getElementById('game-click-list');
    const cvList = document.getElementById('game-cv-list');

    games.forEach(game => {
        const block = document.createElement('div');
        block.className = 'game-block';
        block.dataset.gameId = game.game_id;

        block.innerHTML = `
            <img src="${getGameThumbnail(game)}" alt="${game.name}" class="game-thumb">
            <h3 class="game-name">${game.name}</h3>
            <p class="game-desc">${game.description || 'Chơi ngay!'}</p>
            <button class="play-btn">Chọn Level</button>
        `;

        const playBtn = block.querySelector('.play-btn');
        playBtn.addEventListener('click', () => {
            window.location.href = `./level_select.html?gameId=${game.game_id}`;
        });

        if (game.game_type === 'GameClick') {
            clickList.appendChild(block);
        } else if (game.game_type === 'GameCV') {
            cvList.appendChild(block);
        }
    });

    document.getElementById('logout-button')?.addEventListener('click', async () => {
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

        const ok = await window.egInlineConfirm(
            'Bạn có chắc chắn muốn đăng xuất không?',
            'Xác nhận đăng xuất',
            'Đăng xuất',
            'Hủy'
        );
        if (!ok) return;
        doLogout();
    });
});