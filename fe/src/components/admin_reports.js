import { API_URL, $, fetchAPI, showNotification } from './admin.js';

let reportsData = {
    weekly_reports: [],
    monthly_reports: [],
    weekly_trend: 0,
    monthly_trend: 0,
    total_count: 0
};

let allUniqueReports = [];

// 🔥 FIX: Sử dụng đúng endpoint
const REPORTS_API_URL = "http://localhost:8000/reports";  // ← Không dùng /admin prefix

// ==========================================
// LOAD REPORTS DATA
// ==========================================
export async function loadReports() {
    try {
        console.log('📊 Loading reports from:', `${REPORTS_API_URL}/statistics`);
        
        // 🔥 FIX: Gọi đúng endpoint
        const response = await fetchAPI(`${REPORTS_API_URL}/statistics`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        
        console.log('📦 Raw response:', data);
        
        if (!data || typeof data !== 'object') {
            throw new Error('Invalid data format');
        }
        
        reportsData = {
            weekly_reports: data.weekly_reports || [],
            monthly_reports: data.monthly_reports || [],
            weekly_trend: data.weekly_trend || 0,
            monthly_trend: data.monthly_trend || 0,
            total_count: data.total_count || 0
        };
        
        // Combine và deduplicate reports
        const allReports = [
            ...(reportsData.weekly_reports || []),
            ...(reportsData.monthly_reports || [])
        ];
        
        allUniqueReports = Array.from(
            new Map(allReports.map(r => [r.report_id, r])).values()
        );
        
        console.log('✅ Reports loaded:', {
            weekly: reportsData.weekly_reports.length,
            monthly: reportsData.monthly_reports.length,
            unique: allUniqueReports.length
        });
        
        // 🔍 DEBUG: Log first report để check structure
        if (allUniqueReports.length > 0) {
            console.log('🔍 First report structure:', allUniqueReports[0]);
            console.log('🔍 Has report_type?', 'report_type' in allUniqueReports[0]);
            console.log('🔍 report_type value:', allUniqueReports[0].report_type);
        }
        
        renderReportsStatistics(reportsData);
        
        // Áp dụng filters hiện tại (nếu có) hoặc hiển thị tất cả
        const searchTerm = $('search-reports')?.value?.trim() || '';
        const periodFilter = $('filter-report-period')?.value || '';
        
        if (searchTerm || periodFilter) {
            applyCurrentFilters();
        } else {
            renderReportsTable(allUniqueReports);
        }
        
    } catch (error) {
        console.error('❌ Error loading reports:', error);
        showNotification('Không thể tải dữ liệu báo cáo: ' + error.message, 'error');
        renderEmptyState();
    }
}

// ==========================================
// RENDER EMPTY STATE
// ==========================================
function renderEmptyState() {
    const stats = {
        weekly_reports: [],
        monthly_reports: [],
        weekly_trend: 0,
        monthly_trend: 0,
        total_count: 0
    };
    
    allUniqueReports = [];
    
    renderReportsStatistics(stats);
    renderReportsTable([]);
}

// ==========================================
// RENDER STATISTICS CARDS
// ==========================================
function renderReportsStatistics(data) {
    const weeklyCount = data.weekly_reports?.length || 0;
    const monthlyCount = data.monthly_reports?.length || 0;
    const totalCount = data.total_count || allUniqueReports.length;
    
    const totalReportsEl = $('total-reports');
    if (totalReportsEl) {
        totalReportsEl.textContent = totalCount;
    }
    
    const weeklyEl = $('weekly-reports-count');
    const monthlyEl = $('monthly-reports-count');
    const totalEl = $('total-reports-count');
    
    if (weeklyEl) weeklyEl.textContent = weeklyCount;
    if (monthlyEl) monthlyEl.textContent = monthlyCount;
    if (totalEl) totalEl.textContent = totalCount;
    
    updateTrendIndicator('weekly-trend', data.weekly_trend || 0);
    updateTrendIndicator('monthly-trend', data.monthly_trend || 0);
}

function updateTrendIndicator(elementId, trend) {
    const el = $(elementId);
    if (!el) return;
    
    const trendValue = parseFloat(trend) || 0;
    
    if (trendValue > 0) {
        el.innerHTML = '<span class="trend-icon">↗️</span> +' + trendValue.toFixed(1) + '%';
        el.style.color = '#2ecc71';
    } else if (trendValue < 0) {
        el.innerHTML = '<span class="trend-icon">↘️</span> ' + trendValue.toFixed(1) + '%';
        el.style.color = '#e74c3c';
    } else {
        el.innerHTML = '<span class="trend-icon">➡️</span> 0%';
        el.style.color = '#95a5a6';
    }
}

// ==========================================
// RENDER REPORTS TABLE
// ==========================================
function renderReportsTable(reports) {
    const tbody = $('reports-tbody');
    if (!tbody) {
        console.error('❌ Element #reports-tbody not found!');
        return;
    }
    
    console.log(`📋 Rendering ${reports?.length || 0} reports`);
    
    if (!reports || reports.length === 0) {
        tbody.innerHTML = `
            <tr class="no-data">
                <td colspan="7">
                    <span class="no-data-icon">📭</span>
                    <div class="no-data-text">Không tìm thấy báo cáo nào</div>
                </td>
            </tr>
        `;
        return;
    }
    
    // Sort by generated_at desc
    const sortedReports = [...reports].sort((a, b) => {
        const dateA = new Date(a.generated_at || 0);
        const dateB = new Date(b.generated_at || 0);
        return dateB - dateA;
    });
    
    tbody.innerHTML = sortedReports.map(report => {
        const childInitial = report.child_name ? report.child_name.charAt(0).toUpperCase() : '?';
        const reportType = report.report_type || 'weekly';
        const periodBadge = reportType === 'weekly' ? '📅 Tuần' : '📆 Tháng';
        
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
                        <span class="child-name" title="${escapeHtml(report.child_name || 'N/A')}">${escapeHtml(report.child_name || 'N/A')}</span>
                        <span class="child-email" title="${escapeHtml(report.child_email || '')}">${escapeHtml(report.child_email || '')}</span>
                    </div>
                </div>
            </td>
            <td>
                <span class="period-badge ${reportType}">
                    ${periodBadge}
                </span>
            </td>
            <td>
                <div class="report-summary-cell" title="${escapeHtml(report.summary || 'Chưa có tóm tắt')}">
                    ${escapeHtml(report.summary || 'Chưa có tóm tắt')}
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
            <td>${formatDateTime(report.generated_at)}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn-action btn-view" onclick="window.viewReportDetails('${report.report_id}')" title="Xem chi tiết">
                        👁️ Xem
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
    // Search input với debounce
    let searchTimeout;
    const searchInput = $('search-reports');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                applyCurrentFilters();
            }, 300); // Debounce 300ms
        });
    }
    
    // Period filter
    const periodFilter = $('filter-report-period');
    if (periodFilter) {
        periodFilter.addEventListener('change', () => {
            applyCurrentFilters();
        });
    }
    
    // Reset filters button
    const resetFiltersBtn = $('reset-reports-filter-btn');
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', () => {
            resetFilters();
        });
    }
    
    // Refresh button
    const refreshBtn = $('refresh-reports-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', async () => {
            // Clear filters trước khi refresh
            const searchInput = $('search-reports');
            const periodFilter = $('filter-report-period');
            if (searchInput) searchInput.value = '';
            if (periodFilter) periodFilter.value = '';
            
            await loadReports();
            showNotification('Đã làm mới dữ liệu báo cáo', 'success');
        });
    }
    
    // Modal close buttons
    const closeModalBtn = $('close-report-modal');
    const closeDetailBtn = $('close-report-detail-btn');
    const modal = $('report-modal');
    
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            if (modal) modal.style.display = 'none';
        });
    }
    
    if (closeDetailBtn) {
        closeDetailBtn.addEventListener('click', () => {
            if (modal) modal.style.display = 'none';
        });
    }
    
    // Click outside modal to close
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
    
    // Resend button trong modal
    const resendBtn = $('resend-report-btn');
    if (resendBtn) {
        resendBtn.addEventListener('click', async () => {
            const reportId = resendBtn.getAttribute('data-report-id');
            if (reportId) {
                await window.resendReport(reportId);
                if (modal) modal.style.display = 'none';
            }
        });
    }
}

function applyCurrentFilters() {
    // Safety check: Nếu chưa có data, không làm gì cả
    if (!allUniqueReports || allUniqueReports.length === 0) {
        console.log('⚠️ No reports data available yet');
        renderReportsTable([]);
        return;
    }
    
    const searchTerm = $('search-reports')?.value?.trim() || '';
    const periodFilter = $('filter-report-period')?.value || '';
    
    console.log('🔍 Applying filters:', { searchTerm, periodFilter });
    
    let filtered = [...allUniqueReports];
    
    // Apply search
    if (searchTerm) {
        const term = searchTerm.toLowerCase();
        filtered = filtered.filter(report => {
            return (
                report.child_name?.toLowerCase().includes(term) ||
                report.child_email?.toLowerCase().includes(term) ||
                report.summary?.toLowerCase().includes(term) ||
                report.report_id?.toLowerCase().includes(term)
            );
        });
    }
    
    // Apply period filter
    if (periodFilter) {
        filtered = filtered.filter(report => report.report_type === periodFilter);
    }
    
    renderReportsTable(filtered);
}

function resetFilters() {
    // Clear search input
    const searchInput = $('search-reports');
    if (searchInput) searchInput.value = '';
    
    // Clear period filter
    const periodFilter = $('filter-report-period');
    if (periodFilter) periodFilter.value = '';
    
    // Safety check trước khi render
    if (allUniqueReports && allUniqueReports.length > 0) {
        renderReportsTable(allUniqueReports);
        showNotification('Đã xóa bộ lọc', 'success');
    } else {
        console.log('⚠️ No reports to show');
        renderReportsTable([]);
    }
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
    if (!text) return '';
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
        
        // 🔥 FIX: Đúng endpoint
        const response = await fetchAPI(`${REPORTS_API_URL}/${reportId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        const report = data.status === 'success' ? data : data;
        
        console.log('📦 Report detail:', report);
        
        // Parse data field
        let parsedData = {};
        try {
            parsedData = typeof report.data === 'string' ? JSON.parse(report.data) : report.data || {};
        } catch (e) {
            console.warn('Cannot parse data:', e);
        }
        
        // Populate modal
        const modal = $('report-modal');
        
        if ($('report-detail-child-name')) {
            $('report-detail-child-name').textContent = report.child_name || 'N/A';
        }
        
        if ($('report-detail-child-email')) {
            $('report-detail-child-email').textContent = report.child_email || 'N/A';
        }
        
        if ($('report-detail-period')) {
            const periodText = report.report_type === 'weekly' ? '📅 Báo cáo tuần' : '📆 Báo cáo tháng';
            $('report-detail-period').textContent = periodText;
        }
        
        if ($('report-detail-sent-at')) {
            $('report-detail-sent-at').textContent = formatDateTime(report.generated_at);
        }
        
        if ($('report-detail-summary')) {
            $('report-detail-summary').textContent = report.summary || 'Chưa có tóm tắt';
        }
        
        if ($('report-detail-sessions')) {
            $('report-detail-sessions').textContent = parsedData.total_sessions || 0;
        }
        
        if ($('report-detail-playtime')) {
            $('report-detail-playtime').textContent = parsedData.total_playtime || 0;
        }
        
        if ($('report-detail-score')) {
            $('report-detail-score').textContent = parsedData.avg_score || 0;
        }
        
        // Set report_id cho resend button
        const resendBtn = $('resend-report-btn');
        if (resendBtn) {
            resendBtn.setAttribute('data-report-id', report.report_id);
        }
        
        // Show modal
        if (modal) {
            modal.style.display = 'block';
        }
        
    } catch (error) {
        console.error('❌ Error viewing report:', error);
        showNotification('Không thể tải chi tiết báo cáo: ' + error.message, 'error');
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
        
        // 🔥 FIX: Đúng endpoint
        const response = await fetchAPI(`${REPORTS_API_URL}/${reportId}/resend`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        
        showNotification(result.message || 'Đã gửi lại báo cáo thành công', 'success');
        await loadReports();
        
    } catch (error) {
        console.error('❌ Error resending report:', error);
        showNotification('Không thể gửi lại báo cáo: ' + error.message, 'error');
    }
};

// Export thêm REPORTS_API_URL nếu cần dùng ở file khác
export { REPORTS_API_URL };