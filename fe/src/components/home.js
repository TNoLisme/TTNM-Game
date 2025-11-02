// Logout & game navigation logic
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.querySelector('#logout-button');
    const button1 = document.querySelector('#button-1');
    const button2 = document.querySelector('#button-2');
    const button3 = document.querySelector('#button-3');
    const profilebutton = document.querySelector('#profile-button');

    logoutBtn?.addEventListener('click', () => {
        localStorage.removeItem('currentUser');
        window.location.href = '/src/pages/login.html';
    });

    button1?.addEventListener('click', () => {
        window.location.href = '/src/pages/learn.html';
    });

    button2?.addEventListener('click', () => {
        window.location.href = '/src/pages/gameClick.html';
    });

    button3?.addEventListener('click', () => {
        window.location.href = '/src/pages/gameCV.html';
    });

    profilebutton?.addEventListener('click', () => {
        window.location.href = '/src/pages/profile.html';
    });

});
