// admin_reports.js - FIXED VERSION
import { API_URL, $, fetchAPI, showNotification } from './admin.js';

let reportsData = {
    weekly_reports: [],
    monthly_reports: [],
    weekly_trend: 0,
    monthly_trend: 0,
    total_count: 0
};

// ==========================================
// LOAD REPORTS DATA
// ==========================================
export async function loadReports() {
    try {
        console.log('📊 Loading reports...');
        
        const response = await fetchAPI(`${API_URL}/reports/statistics`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        
        // ✅ Validate data structure
        if (!data || typeof data !== 'object') {
            throw new Error('Invalid data format');
        }
        
        // ✅ Set default values nếu thiếu
        reportsData = {
            weekly_reports: data.weekly_reports || [],
            monthly_reports: data.monthly_reports || [],
            weekly_trend: data.weekly_trend || 0,
            monthly_trend: data.monthly_trend || 0,
            total_count: data.total_count || 0
        };
        
        console.log('✅ Reports loaded:', reportsData);
        
        renderReportsStatistics(reportsData);
        renderReportsTable(reportsData);
        
    } catch (error) {
        console.error('❌ Error loading reports:', error);
        showNotification('Không thể tải dữ liệu báo cáo: ' + error.message, 'error');
        
        // ✅ Render empty state
        renderEmptyState();
    }
}

// ==========================================
// RENDER EMPTY STATE
// ==========================================
function renderEmptyState() {
    // Reset statistics
    const stats = {
        weekly_reports: [],
        monthly_reports: [],
        weekly_trend: 0,
        monthly_trend: 0,
        total_count: 0
    };
    
    renderReportsStatistics(stats);
    renderReportsTable(stats);
}

// ==========================================
// RENDER STATISTICS CARDS
// ==========================================
function renderReportsStatistics(data) {
    const weeklyCount = data.weekly_reports?.length || 0;
    const monthlyCount = data.monthly_reports?.length || 0;
    const totalCount = data.total_count || (weeklyCount + monthlyCount);
    
    // ✅ Update dashboard stats (nếu tồn tại)
    const totalReportsEl = $('total-reports');
    if (totalReportsEl) {
        totalReportsEl.textContent = totalCount;
    }
    
    // ✅ Update reports section stats với null checking
    const weeklyEl = $('weekly-reports-count');
    const monthlyEl = $('monthly-reports-count');
    const totalEl = $('total-reports-count');
    
    if (weeklyEl) weeklyEl.textContent = weeklyCount;
    if (monthlyEl) monthlyEl.textContent = monthlyCount;
    if (totalEl) totalEl.textContent = totalCount;
    
    // ✅ Update trend indicators
    updateTrendIndicator('weekly-trend', data.weekly_trend || 0);
    updateTrendIndicator('monthly-trend', data.monthly_trend || 0);
}

function updateTrendIndicator(elementId, trend) {
    const el = $(elementId);
    if (!el) return;
    
    const trendValue = parseFloat(trend) || 0;
    
    if (trendValue > 0) {
        el.textContent = `↗️ +${trendValue.toFixed(1)}%`;
        el.style.color = '#2ecc71';
    } else if (trendValue < 0) {
        el.textContent = `↘️ ${trendValue.toFixed(1)}%`;
        el.style.color = '#e74c3c';
    } else {
        el.textContent = '➡️ 0%';
        el.style.color = '#95a5a6';
    }
}

// ==========================================
// RENDER REPORTS TABLE
// ==========================================
function renderReportsTable(data) {
    const tbody = $('reports-tbody');
    if (!tbody) return;
    
    const allReports = [
        ...(data.weekly_reports || []).map(r => ({...r, period: 'weekly'})),
        ...(data.monthly_reports || []).map(r => ({...r, period: 'monthly'}))
    ];
    
    if (allReports.length === 0) {
        tbody.innerHTML = `
            <tr class="no-data">
                <td colspan="7">
                    <span class="no-data-icon">📭</span>
                    <div class="no-data-text">Chưa có báo cáo nào được gửi</div>
                </td>
            </tr>
        `;
        return;
    }
    
    // Sort by date desc
    allReports.sort((a, b) => new Date(b.sent_at) - new Date(a.sent_at));
    
    tbody.innerHTML = allReports.map(report => {
        const childInitial = report.child_name ? report.child_name.charAt(0).toUpperCase() : '?';
        
        return `
        <tr>
            <td>
                <code style="font-size: 11px; background: #ecf0f1; padding: 4px 8px; border-radius: 4px; display: block; overflow: hidden; text-overflow: ellipsis;">
                    ${report.report_id.substring(0, 8)}...
                </code>
            </td>
            <td>
                <div class="child-info-cell">
                    <div class="child-avatar">${childInitial}</div>
                    <div class="child-details">
                        <span class="child-name" title="${report.child_name || 'N/A'}">${report.child_name || 'N/A'}</span>
                        <span class="child-email" title="${report.child_email || ''}">${report.child_email || ''}</span>
                    </div>
                </div>
            </td>
            <td>
                <span class="period-badge ${report.period}">
                    ${report.period === 'weekly' ? '📅 Tuần' : '📆 Tháng'}
                </span>
            </td>
            <td>
                <div class="report-summary-cell" title="${report.summary || 'Chưa có tóm tắt'}">
                    ${report.summary || 'Chưa có tóm tắt'}
                </div>
            </td>
            <td>
                <div class="mini-stats">
                    <div class="stat-item">
                        <span class="stat-icon">📊</span>
                        <span class="stat-value">${report.stats?.total_sessions || 0}</span> phiên
                    </div>
                    <div class="stat-item">
                        <span class="stat-icon">⏱️</span>
                        <span class="stat-value">${report.stats?.total_playtime || 0}</span> phút
                    </div>
                    <div class="stat-item">
                        <span class="stat-icon">⭐</span>
                        <span class="stat-value">${report.stats?.avg_score || 0}</span> điểm
                    </div>
                </div>
            </td>
            <td>${formatDateTime(report.sent_at)}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn-action btn-view" onclick="viewReportDetails('${report.report_id}')" title="Xem chi tiết">
                        👁️ Xem
                    </button>
                    <button class="btn-action btn-resend" onclick="resendReport('${report.report_id}')" title="Gửi lại">
                        🔄 Gửi lại
                    </button>
                </div>
            </td>
        </tr>
    `}).join('');
}

// ==========================================
// FILTER & SEARCH
// ==========================================
export function setupReportEvents() {
    // Search input
    const searchInput = $('search-reports');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            filterReports(e.target.value);
        });
    }
    
    // Period filter
    const periodFilter = $('filter-report-period');
    if (periodFilter) {
        periodFilter.addEventListener('change', () => {
            const searchTerm = $('search-reports')?.value || '';
            filterReports(searchTerm);
        });
    }
    
    // Status filter
    const statusFilter = $('filter-report-status');
    if (statusFilter) {
        statusFilter.addEventListener('change', () => {
            const searchTerm = $('search-reports')?.value || '';
            filterReports(searchTerm);
        });
    }
    
    // Refresh button
    const refreshBtn = $('refresh-reports-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async () => {
            await loadReports();
            showNotification('Đã làm mới dữ liệu báo cáo', 'success');
        });
    }
}

function filterReports(searchTerm = '') {
    const periodFilter = $('filter-report-period')?.value || '';
    const statusFilter = $('filter-report-status')?.value || '';
    
    const allReports = [
        ...(reportsData.weekly_reports || []),
        ...(reportsData.monthly_reports || [])
    ];
    
    const filtered = allReports.filter(report => {
        const matchesSearch = !searchTerm || 
            report.child_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            report.child_email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            report.summary?.toLowerCase().includes(searchTerm.toLowerCase());
            
        const matchesPeriod = !periodFilter || report.report_type === periodFilter;
        const matchesStatus = !statusFilter || report.status === statusFilter;
        
        return matchesSearch && matchesPeriod && matchesStatus;
    });
    
    renderFilteredReports(filtered);
}

function renderFilteredReports(reports) {
    const tbody = $('reports-tbody');
    if (!tbody) return;
    
    if (reports.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 30px; color: #7f8c8d;">
                    🔍 Không tìm thấy báo cáo phù hợp
                </td>
            </tr>
        `;
        return;
    }
    
    // Sort by generated_at desc
    reports.sort((a, b) => {
        const dateA = new Date(a.generated_at || a.sent_at || 0);
        const dateB = new Date(b.generated_at || b.sent_at || 0);
        return dateB - dateA;
    });
    
    tbody.innerHTML = reports.map(report => renderReportRow(report)).join('');
}

// ==========================================
// HELPER FUNCTIONS
// ==========================================
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'N/A';
        
        return date.toLocaleString('vi-VN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        return 'N/A';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==========================================
// GLOBAL ACTIONS
// ==========================================
window.viewReportDetails = async function(reportId) {
    if (!reportId) {
        showNotification('Report ID không hợp lệ', 'error');
        return;
    }
    
    try {
        console.log('👁️ Viewing report:', reportId);
        
        const response = await fetchAPI(`${API_URL}/reports/${reportId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const report = await response.json();
        
        // ✅ Parse data field
        let parsedData = {};
        try {
            parsedData = typeof report.data === 'string' ? JSON.parse(report.data) : report.data || {};
        } catch (e) {
            console.warn('Cannot parse data:', e);
        }
        
        // ✅ Display modal with database fields
        const details = `
📊 CHI TIẾT BÁO CÁO

━━━━━━━━━━━━━━━━━━━━━━━━
📋 THÔNG TIN CƠ BẢN
━━━━━━━━━━━━━━━━━━━━━━━━
• ID: ${report.report_id}
• Trẻ: ${report.child_name}
• Email: ${report.child_email}
• Loại: ${report.report_type === 'weekly' ? 'Báo cáo tuần' : 'Báo cáo tháng'}
• Ngày tạo: ${formatDateTime(report.generated_at)}

━━━━━━━━━━━━━━━━━━━━━━━━
📝 TÓM TẮT
━━━━━━━━━━━━━━━━━━━━━━━━
${report.summary || 'Chưa có tóm tắt'}

━━━━━━━━━━━━━━━━━━━━━━━━
📊 DỮ LIỆU CHI TIẾT
━━━━━━━━━━━━━━━━━━━━━━━━
• Tổng số: ${parsedData.total || 0}
• Số đúng: ${parsedData.correct || 0}
• Điểm trung bình: ${parsedData.avg_score || 0}
        `.trim();
        
        alert(details);
        
    } catch (error) {
        console.error('❌ Error viewing report:', error);
        showNotification('Không thể tải chi tiết báo cáo', 'error');
    }
};

window.resendReport = async function(reportId) {
    if (!reportId) {
        showNotification('Report ID không hợp lệ', 'error');
        return;
    }
    
    if (!confirm('Bạn có chắc muốn gửi lại báo cáo này?')) {
        return;
    }
    
    try {
        console.log('🔄 Resending report:', reportId);
        
        const response = await fetchAPI(`${API_URL}/reports/${reportId}/resend`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        showNotification('Đã gửi lại báo cáo thành công', 'success');
        await loadReports(); // Refresh data
        
    } catch (error) {
        console.error('❌ Error resending report:', error);
        showNotification('Không thể gửi lại báo cáo: ' + error.message, 'error');
    }
};
