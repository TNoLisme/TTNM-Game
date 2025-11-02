function editProfile() {
            alert('Chức năng chỉnh sửa thông tin đang được phát triển!');
        }

        // Xử lý đăng xuất
        document.getElementById('logout-btn').addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('Bạn có chắc muốn đăng xuất?')) {
                // Xóa token và chuyển về trang đăng nhập
                localStorage.removeItem('token');
                window.location.href = 'login.html';
            }
        });

        // Load dữ liệu profile
        window.addEventListener('DOMContentLoaded', function() {
            // Dữ liệu mẫu - sau này sẽ lấy từ API
            setTimeout(() => {
                document.getElementById('user-name').textContent = 'Bé Hùng';
                document.getElementById('username').textContent = 'hungsieunhan';
                document.getElementById('email').textContent = 'hung@gmail.com';
                document.getElementById('join-date').textContent = '01/01/2020';
                document.getElementById('age').textContent = '5 tuổi';
                document.getElementById('games-played').textContent = '12';
                document.getElementById('total-score').textContent = '850';
                document.getElementById('achievements').textContent = '5';
                document.getElementById('play-time').textContent = '4.5h';
            }, 300);
        });

        // Animation cho số liệu
        function animateValue(id, start, end, duration) {
            const obj = document.getElementById(id);
            const range = end - start;
            const increment = end > start ? 1 : -1;
            const stepTime = Math.abs(Math.floor(duration / range));
            let current = start;
            
            const timer = setInterval(function() {
                current += increment;
                obj.textContent = current;
                if (current == end) {
                    clearInterval(timer);
                }
            }, stepTime);
        }