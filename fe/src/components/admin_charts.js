// Thêm vào file admin.js hoặc tạo file mới admin_dashboard.js

import { API_URL, $, fetchAPI } from './admin.js';

// ==========================================
// LOAD TOTAL STATS
// ==========================================
// ==========================================
// LOAD GAME PLAY STATISTICS (PIE CHART)
// ==========================================
async function loadGamePlayStats() {
    try {
        console.log('📊 Loading game play statistics...');
        
        const response = await fetch('http://localhost:8000/admin/stats/all-users-game-play-ratio');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('📦 Received data:', result);
        
        if (result.status === 'success' && result.data) {
            const { game_stats, total_sessions } = result.data;
            
            // Update total sessions if element exists
            const totalSessionsEl = document.getElementById('total-game-sessions');
            if (totalSessionsEl) {
                totalSessionsEl.textContent = total_sessions || 0;
            }
            
            // Render pie chart
            renderGameStatsChart(game_stats);
        } else {
            console.warn('⚠️ No game stats data available');
            renderEmptyChart();
        }
        
    } catch (error) {
        console.error('❌ Error loading game play stats:', error);
        renderEmptyChart();
    }
}

// ==========================================
// RENDER PIE CHART
// ==========================================
function renderGameStatsChart(gameStats) {
    const chartContainer = $('users-chart');
    
    if (!chartContainer) {
        console.error('❌ Chart container not found!');
        return;
    }
    
    if (!gameStats || gameStats.length === 0) {
        renderEmptyChart();
        return;
    }
    
    // Clear previous content
    chartContainer.innerHTML = '';
    
    // Create SVG pie chart
    const size = 260;
    const center = size / 2;
    const radius = size / 2 - 20;
    
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', size);
    svg.setAttribute('height', size);
    svg.setAttribute('viewBox', `0 0 ${size} ${size}`);
    svg.style.maxWidth = '100%';
    svg.style.height = 'auto';
    
    let currentAngle = -90; // Start from top
    
    gameStats.forEach((game, index) => {
        const percentage = game.percentage;
        const angle = (percentage / 100) * 360;
        
        // Calculate path for pie slice
        const startAngle = currentAngle * Math.PI / 180;
        const endAngle = (currentAngle + angle) * Math.PI / 180;
        
        const x1 = center + radius * Math.cos(startAngle);
        const y1 = center + radius * Math.sin(startAngle);
        const x2 = center + radius * Math.cos(endAngle);
        const y2 = center + radius * Math.sin(endAngle);
        
        const largeArc = angle > 180 ? 1 : 0;
        
        const pathData = [
            `M ${center} ${center}`,
            `L ${x1} ${y1}`,
            `A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`,
            'Z'
        ].join(' ');
        
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', pathData);
        path.setAttribute('fill', game.color);
        path.setAttribute('stroke', 'white');
        path.setAttribute('stroke-width', '2');
        path.style.cursor = 'pointer';
        path.style.transition = 'opacity 0.3s';
        
        // Add hover effect
        path.addEventListener('mouseenter', () => {
            path.style.opacity = '0.8';
        });
        path.addEventListener('mouseleave', () => {
            path.style.opacity = '1';
        });
        
        // Add tooltip
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = `${game.game_name}: ${game.play_count} lượt (${game.percentage}%)`;
        path.appendChild(title);
        
        svg.appendChild(path);
        
        currentAngle += angle;
    });
    
    // Create chart wrapper (left side)
    const chartWrapper = document.createElement('div');
    chartWrapper.style.cssText = `
        flex: 0 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px;
    `;
    chartWrapper.appendChild(svg);
    
    // Create legend (right side)
    const legendDiv = document.createElement('div');
    legendDiv.style.cssText = `
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 10px;
        padding: 10px;
    `;
    
    gameStats.forEach((game) => {
        const legendItem = document.createElement('div');
        legendItem.style.cssText = `
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 7px;
            background: linear-gradient(135deg, ${game.color}15, ${game.color}08);
            border-left: 4px solid ${game.color};
            border-radius: 4px;
            font-size: 15px;
            transition: all 0.3s;
            cursor: pointer;
        `;
        
        // Hover effect
        legendItem.addEventListener('mouseenter', () => {
            legendItem.style.transform = 'translateX(5px)';
            legendItem.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
        });
        legendItem.addEventListener('mouseleave', () => {
            legendItem.style.transform = 'translateX(0)';
            legendItem.style.boxShadow = 'none';
        });
        
        const colorBox = document.createElement('div');
        colorBox.style.cssText = `
            width: 10px;
            height: 10px;
            background: ${game.color};
            border-radius: 4px;
            flex-shrink: 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        `;
        
        const textContainer = document.createElement('div');
        textContainer.style.cssText = `
            flex: 1;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        `;
        
        const label = document.createElement('span');
        label.style.cssText = `
            font-weight: 500;
            color: #2c3e50;
        `;
        label.textContent = game.game_name;
        
        const statsContainer = document.createElement('div');
        statsContainer.style.cssText = `
            display: flex;
            align-items: center;
            gap: 4px;
        `;
        
        const playCount = document.createElement('span');
        playCount.style.cssText = `
            font-size: 10px;
            color: #7f8c8d;
        `;
        playCount.textContent = `${game.play_count} lượt`;
        
        const percentage = document.createElement('strong');
        percentage.style.cssText = `
            font-size: 13px;
            color: ${game.color};
            font-weight: 700;
        `;
        percentage.textContent = `${game.percentage}%`;
        
        statsContainer.appendChild(playCount);
        statsContainer.appendChild(percentage);
        
        textContainer.appendChild(label);
        textContainer.appendChild(statsContainer);
        
        legendItem.appendChild(colorBox);
        legendItem.appendChild(textContainer);
        legendDiv.appendChild(legendItem);
    });
    
    // Create main container (horizontal layout)
    const container = document.createElement('div');
    container.style.cssText = `
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 20px;
        min-height: 320px;
    `;
    
    container.appendChild(chartWrapper);
    container.appendChild(legendDiv);
    chartContainer.appendChild(container);
    
    console.log('✅ Chart rendered successfully');
}


// ==========================================
// RENDER EMPTY CHART
// ==========================================
function renderEmptyChart() {
    const chartContainer = $('users-chart');
    if (!chartContainer) return;
    
    chartContainer.innerHTML = `
        <div style="
            text-align: center;
            padding: 30px 10px;
            color: #95a5a6;
        ">
            <div style="font-size: 24px; margin-bottom: 8px;">📊</div>
            <p style="font-size: 8px; font-weight: 500;">Chưa có dữ liệu chơi game</p>
            <p style="font-size: 7px; margin-top: 3px;">Dữ liệu sẽ hiển thị khi có người dùng chơi game</p>
        </div>
    `;
}

// Export function to be used in main admin.js
export { loadGamePlayStats };