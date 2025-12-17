from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from datetime import datetime
from io import BytesIO
from typing import Dict, List
import os

class ReportGeneratorService:
    def __init__(self):
        self.main_font = 'Times-Roman'
        self.bold_font = 'Times-Bold'
        self.italic_font = 'Times-Italic'
        self.bold_italic_font = 'Times-BoldItalic'
        
        # Margins chuẩn
        self.page_width = 7 * inch  # A4 width - margins
        self.left_margin = 0.5 * inch
        self.right_margin = 0.5 * inch
        
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            fonts_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..', 'fe', 'assets', 'fonts'))

            regular_path = os.path.join(fonts_dir, 'DejaVuSans.ttf')
            bold_path = os.path.join(fonts_dir, 'DejaVuSans-Bold.ttf')
            italic_path = os.path.join(fonts_dir, 'DejaVuSansCondensed.ttf')
            bold_italic_path = os.path.join(fonts_dir, 'DejaVuSans-BoldOblique.ttf')

            if os.path.exists(regular_path) and os.path.exists(bold_path) and os.path.exists(bold_italic_path):
                pdfmetrics.registerFont(TTFont('DejaVu', regular_path))
                pdfmetrics.registerFont(TTFont('DejaVu-Bold', bold_path))
                if os.path.exists(italic_path):
                    pdfmetrics.registerFont(TTFont('DejaVu-Italic', italic_path))
                else:
                    pdfmetrics.registerFont(TTFont('DejaVu-Italic', regular_path))
                pdfmetrics.registerFont(TTFont('DejaVu-BoldItalic', bold_italic_path))

                self.main_font = 'DejaVu'
                self.bold_font = 'DejaVu-Bold'
                self.italic_font = 'DejaVu-Italic'
                self.bold_italic_font = 'DejaVu-BoldItalic'

                print("✅ Vietnamese font loaded successfully")
            else:
                print(f"⚠️ Vietnamese font not found at: {fonts_dir}")
        except Exception as e:
            print(f"⚠️ Warning: Could not load Vietnamese font: {e}")
    
    def _create_header_box(self, text: str, color: str = "#71b7f8") -> Drawing:
        """Header box với màu chuyên nghiệp hơn"""
        d = Drawing(self.page_width + 0.2*inch, 0.4*inch)
        rect = Rect(0, 0, self.page_width + 0.2*inch, 0.4*inch)
        rect.fillColor = colors.HexColor(color)
        rect.strokeColor = None
        d.add(rect)
        
        label = String(0.3*inch, 0.12*inch, text)
        label.fontName = self.bold_font
        label.fontSize = 12
        label.fillColor = colors.white
        d.add(label)
        return d
    
    def _create_stat_card(self, label: str, value: str) -> Drawing:
        """Stat card với thiết kế tối giản - width cố định"""
        card_width = 3.6 * inch
        d = Drawing(card_width, 0.9*inch)
        
        # Border only
        rect = Rect(0, 0, card_width, 0.9*inch)
        rect.fillColor = colors.white
        rect.strokeColor = colors.HexColor('#d1d5db')
        rect.strokeWidth = 1
        d.add(rect)
        
        # Value
        value_text = String(0.3*inch, 0.45*inch, value)
        value_text.fontName = self.bold_font
        value_text.fontSize = 16
        value_text.fillColor = colors.HexColor('#1f2937')
        d.add(value_text)
        
        # Label
        label_text = String(0.3*inch, 0.2*inch, label)
        label_text.fontName = self.main_font
        label_text.fontSize = 9
        label_text.fillColor = colors.HexColor('#6b7280')
        d.add(label_text)
        
        return d
    
    def _create_progress_bar(self, percentage: float, width: float = 3*inch) -> Drawing:
        """Progress bar đơn giản"""
        d = Drawing(width, 0.25*inch)
        
        # Background
        bg_rect = Rect(0, 0, width, 0.25*inch)
        bg_rect.fillColor = colors.HexColor('#e5e7eb')
        bg_rect.strokeColor = None
        d.add(bg_rect)
        
        # Progress
        progress_width = width * (percentage / 100)
        progress_rect = Rect(0, 0, progress_width, 0.25*inch)
        
        if percentage >= 80:
            progress_rect.fillColor = colors.HexColor('#10b981')
        elif percentage >= 60:
            progress_rect.fillColor = colors.HexColor('#3b82f6')
        elif percentage >= 40:
            progress_rect.fillColor = colors.HexColor('#f59e0b')
        else:
            progress_rect.fillColor = colors.HexColor('#ef4444')
        progress_rect.strokeColor = None
        d.add(progress_rect)
        
        # Percentage text
        text = String(width/2, 0.06*inch, f"{percentage:.0f}%")
        text.fontName = self.bold_font
        text.fontSize = 9
        text.fillColor = colors.white if percentage > 30 else colors.HexColor('#1f2937')
        text.textAnchor = 'middle'
        d.add(text)
        
        return d
    
    def _create_daily_sessions_chart(self, daily_sessions: Dict) -> Drawing:
        """Biểu đồ cột cho số phiên theo ngày - căn giữa"""
        d = Drawing(self.page_width, 2.5*inch)
        
        if not daily_sessions:
            return d
        
        chart = VerticalBarChart()
        # Căn giữa chart trong drawing
        chart_width = int(self.page_width) - 100
        chart.x = (int(self.page_width) - chart_width) / 2
        chart.y = 30
        chart.height = 150
        chart.width = chart_width
        
        days = list(daily_sessions.keys())
        sessions = list(daily_sessions.values())
        
        chart.data = [sessions]
        chart.categoryAxis.categoryNames = days
        chart.categoryAxis.labels.angle = 0
        chart.categoryAxis.labels.fontSize = 9
        chart.categoryAxis.labels.boxAnchor = 'n'
        chart.categoryAxis.labels.fontName = self.main_font
        
        chart.valueAxis.valueMin = 0
        max_sessions = max(sessions) if sessions else 10
        chart.valueAxis.valueMax = max_sessions + 2
        chart.valueAxis.valueStep = max(1, max_sessions // 5)
        chart.valueAxis.labels.fontSize = 9
        chart.valueAxis.labels.fontName = self.main_font
        
        # Màu xanh dương chuyên nghiệp
        for i in range(len(days)):
            chart.bars[i].fillColor = colors.HexColor('#3b82f6')
        
        chart.bars.strokeColor = None
        
        d.add(chart)
        return d
    
    def _create_emotion_chart(self, emotion_stats: Dict) -> Drawing:
        """Biểu đồ cột cho cảm xúc - 6 cảm xúc - căn giữa"""
        d = Drawing(self.page_width, 2.5*inch)
        
        if not emotion_stats:
            return d
        
        chart = VerticalBarChart()
        # Căn giữa chart trong drawing
        chart_width = int(self.page_width) - 100
        chart.x = (int(self.page_width) - chart_width) / 2
        chart.y = 30
        chart.height = 130
        chart.width = chart_width
        
        professional_colors = [
        '#3b82f6',  # Blue
        '#10b981',  # Green
        '#f59e0b',  # Amber
        '#ef4444',  # Red
        '#8b5cf6',  # Purple
        '#06b6d4',  # Cyan
        ]
        # Đảm bảo có đủ 6 cảm xúc
        all_emotions = ['vui vẻ', 'buồn bã', 'tức giận', 'sợ hãi', 'ngạc nhiên', 'ghê tởm']
        emotions = []
        accuracies = []
        
        for emotion in all_emotions:
            emotions.append(emotion.capitalize())
            if emotion in emotion_stats:
                accuracies.append(emotion_stats[emotion].get('accuracy', 0))
            else:
                accuracies.append(0)
        
        chart.data = [accuracies]
        chart.categoryAxis.categoryNames = emotions
        chart.categoryAxis.labels.angle = 0
        chart.categoryAxis.labels.fontSize = 9
        chart.categoryAxis.labels.boxAnchor = 'n'
        chart.categoryAxis.labels.fontName = self.main_font
        
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 100
        chart.valueAxis.valueStep = 20
        chart.valueAxis.labels.fontSize = 9
        chart.valueAxis.labels.fontName = self.main_font
        
        # Màu xanh lá chuyên nghiệp
        for i in range(6):
            chart.bars[i].fillColor = colors.HexColor(professional_colors[i])
        chart.bars.strokeColor = colors.white
        
        d.add(chart)
        return d
    
    def _create_games_pie_chart(self, games_stats: List[Dict]) -> Drawing:
        """Biểu đồ tròn - 6 games - căn giữa trong khung"""
        chart_width = self.page_width
        d = Drawing(chart_width, 3.5*inch)
        
        if not games_stats:
            return d
        
        pie = Pie()
        # Căn giữa pie chart
        pie.x = chart_width / 2 - 90
        pie.y = 50
        pie.width = 180
        pie.height = 180
        
        professional_colors = [
        '#3b82f6',  # Blue
        '#10b981',  # Green
        '#f59e0b',  # Amber
        '#ef4444',  # Red
        '#8b5cf6',  # Purple
        '#06b6d4',  # Cyan
        ]
        # Đảm bảo có đủ 6 games
        games_to_show = games_stats[:6] if len(games_stats) >= 6 else games_stats
        while len(games_to_show) < 6:
            games_to_show.append({'game_name': 'Câu chuyện trên khuôn mặt', 'sessions': 0})
        
        pie.data = [game.get('sessions', 0) for game in games_to_show]
        pie.labels = [game.get('game_name', 'Câu chuyện trên khuôn mặt') for game in games_to_show]
        
        pie.slices.strokeColor = colors.white
        pie.slices.strokeWidth = 2
        
        for i in range(6):
            pie.slices[i].fillColor = colors.HexColor(professional_colors[i])
        
        pie.slices.fontSize = 8
        pie.slices.fontColor = colors.black
        pie.slices.fontName = self.main_font
        
        d.add(pie)
        return d
    
    def _create_score_trend_chart(self, games_stats: List[Dict]) -> Drawing:
        """Biểu đồ xu hướng điểm"""
        d = Drawing(3.5*inch, 2.5*inch)
        
        if not games_stats:
            return d
        
        chart = HorizontalLineChart()
        chart.x = 50
        chart.y = 40
        chart.height = 140
        chart.width = 200
        
        scores = [game.get('avg_score', 0) for game in games_stats[:7]]
        chart.data = [scores]
        
        chart.categoryAxis.categoryNames = [f"G{i+1}" for i in range(len(scores))]
        chart.categoryAxis.labels.fontSize = 8
        chart.categoryAxis.labels.fontName = self.main_font
        
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 10
        chart.valueAxis.valueStep = 2
        chart.valueAxis.labels.fontSize = 9
        chart.valueAxis.labels.fontName = self.main_font
        
        chart.lines[0].strokeColor = colors.HexColor('#3b82f6')
        chart.lines[0].strokeWidth = 2
        chart.lines[0].symbol = None
        
        d.add(chart)
        return d
    
    def _create_summary_box(self, title: str, content: str, color: str = '#3b82f6') -> Table:
        """Box tổng quan"""
        data = [
            [Paragraph(f"<b>{title}</b>", ParagraphStyle(
                'BoxTitle',
                fontName=self.bold_font,
                fontSize=10,
                textColor=colors.white
            ))],
            [Paragraph(content, ParagraphStyle(
                'BoxContent',
                fontName=self.main_font,
                fontSize=9,
                textColor=colors.HexColor('#1f2937'),
                leading=13
            ))]
        ]
        
        table = Table(data, colWidths=[self.page_width])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(color)),
            ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#f9fafb')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (0, 0), 8),
            ('BOTTOMPADDING', (0, 0), (0, 0), 8),
            ('TOPPADDING', (0, 1), (0, 1), 10),
            ('BOTTOMPADDING', (0, 1), (0, 1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ]))
        return table
    
    def generate_progress_report(self, child_data: Dict, progress_data: Dict) -> BytesIO:
        """Generate PDF report - Return BytesIO only"""
        buffer = BytesIO()
        
        period = progress_data.get('period', 'weekly')
        child_name = child_data.get('name', 'Student').replace(' ', '_')
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"Report_{period}_{child_name}_{date_str}.pdf"
        
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=0.5*inch, 
            leftMargin=0.5*inch,
            topMargin=0.5*inch, 
            bottomMargin=0.5*inch,
            title=filename
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=8,
            alignment=1,
            fontName=self.bold_font
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=20,
            alignment=1,
            fontName=self.main_font
        )
        
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=8,
            spaceBefore=4,
            fontName=self.main_font
        )
        
        # ==================== HEADER ====================
        header_line = Drawing(self.page_width, 3)
        line1 = Line(0, 0, self.page_width, 0)
        line1.strokeColor = colors.HexColor("#7eadfa")
        line1.strokeWidth = 3
        header_line.add(line1)
        elements.append(header_line)
        elements.append(Spacer(1, 20))
        
        title = Paragraph("BÁO CÁO TIẾN ĐỘ HỌC TẬP", title_style)
        elements.append(title)
        
        period_text = "TUẦN" if progress_data.get("period") == "weekly" else "THÁNG"
        subtitle = Paragraph(
            f"{period_text}: {progress_data.get('start_date')} đến {progress_data.get('end_date')}",
            subtitle_style
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 8))
        
        # ==================== THÔNG TIN HỌC VIÊN ====================
        elements.append(self._create_header_box("THÔNG TIN HỌC VIÊN"))
        elements.append(Spacer(1, 18))
        
        child_info = [
            ['Họ và tên:', child_data.get('name', 'N/A')],
            ['Tuổi:', str(child_data.get('age', 'N/A')) + ' tuổi'],
            ['Mã học viên:', child_data.get('user_id', 'N/A')],
            ['Email:', child_data.get('email', 'N/A')],
        ]
        
        child_table = Table(child_info, colWidths=[2*inch, 5*inch])
        child_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f9fafb')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), self.bold_font),
            ('FONTNAME', (1, 0), (1, -1), self.main_font),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#e5e7eb')),
        ]))
        elements.append(child_table)
        elements.append(Spacer(1, 18))
        
        # ==================== TỔNG QUAN - CARDS ====================
        elements.append(self._create_header_box("TỔNG QUAN HOẠT ĐỘNG"))
        elements.append(Spacer(1, 18))
        
        # Cards với khoảng cách đều
        card_spacing = 0.15 * inch
        stats_row1 = [
            [self._create_stat_card("Tổng số phiên", str(progress_data.get('total_sessions', 0))),
             self._create_stat_card("Thời gian chơi", f"{progress_data.get('total_playtime', 0)} phút")]
        ]
        stats_row2 = [
            [self._create_stat_card("Điểm trung bình", f"{progress_data.get('avg_score', 0):.1f}/100"),
             self._create_stat_card("Số trò chơi đã chơi trong tuần", str(len(progress_data.get('games_stats', []))))]
        ]
        
        stats_table1 = Table(stats_row1, colWidths=[3.3*inch, 3.3*inch], spaceBefore=0, spaceAfter=0)
        stats_table1.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), card_spacing),
            ('RIGHTPADDING', (0, 0), (-1, -1), card_spacing),
        ]))
        elements.append(stats_table1)
        elements.append(Spacer(1, 12))
        
        stats_table2 = Table(stats_row2, colWidths=[3.3*inch, 3.3*inch], spaceBefore=0, spaceAfter=0)
        stats_table2.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), card_spacing),
            ('RIGHTPADDING', (0, 0), (-1, -1), card_spacing),
        ]))
        elements.append(stats_table2)
        elements.append(Spacer(1, 18))
        
        
        # ==================== BIỂU ĐỒ PHIÊN HỌC THEO NGÀY ====================
        daily_sessions = progress_data.get('daily_sessions', {})
        if daily_sessions:
            elements.append(self._create_header_box("SỐ PHIÊN HỌC THEO NGÀY"))
            elements.append(Spacer(1, 18))
            elements.append(self._create_daily_sessions_chart(daily_sessions))
            elements.append(Spacer(1, 20))
        
        elements.append(PageBreak())

        # ==================== BIỂU ĐỒ TRÒ CHƠI ====================
        games_stats = progress_data.get('games_stats', [])
        if games_stats:
            elements.append(self._create_header_box("PHÂN TÍCH TRÒ CHƠI"))
            
            # Pie chart căn giữa
            elements.append(self._create_games_pie_chart(games_stats))
            elements.append(Spacer(1, 4))
            
            # Games detail table
            games_data = [['Tên trò chơi', 'Phiên', 'Điểm TB', 'Level', 'Tiến độ']]
            
            for game in games_stats[:6]:
                progress_pct = game.get('level', 0) / 8 * 100
                games_data.append([
                    game.get('game_name', 'N/A'),
                    str(game.get('sessions', 0)),
                    f"{game.get('avg_score', 0):.1f}",
                    str(game.get('level', 1)),
                    self._create_progress_bar(progress_pct, 2*inch)
                ])
            
            games_table = Table(games_data, colWidths=[2*inch, 0.9*inch, 0.9*inch, 0.8*inch, 2.4*inch])
            games_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#71a6fa")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), self.bold_font),
                ('FONTNAME', (0, 1), (-1, -1), self.main_font),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#e5e7eb')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ]))
            elements.append(games_table)
        elements.append(Spacer(1, 18))
        
        # ==================== THỐNG KÊ CẢM XÚC ====================
        emotion_stats = progress_data.get('emotion_stats', {})
        elements.append(self._create_header_box("THỐNG KÊ NHẬN DIỆN CẢM XÚC"))
        elements.append(Spacer(1, 18))
        
        elements.append(self._create_emotion_chart(emotion_stats))
        elements.append(PageBreak())
        
        # Emotion detail table
        all_emotions = ['vui vẻ', 'buồn bã', 'tức giận', 'sợ hãi', 'ngạc nhiên', 'ghê tởm']
        emotion_data = [['Cảm xúc', 'Đúng', 'Sai', 'Tổng', 'Độ chính xác']]
        
        for emotion in all_emotions:
            if emotion in emotion_stats:
                stats = emotion_stats[emotion]
                correct = stats.get('correct', 0)
                incorrect = stats.get('incorrect', 0)
                total = correct + incorrect
                accuracy = stats.get('accuracy', 0)
            else:
                correct = incorrect = total = accuracy = 0
            
            emotion_data.append([
                emotion.capitalize(),
                str(correct),
                str(incorrect),
                str(total),
                self._create_progress_bar(accuracy, 2*inch)
            ])
        
        emotion_table = Table(emotion_data, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 2.8*inch])
        emotion_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#71b7f8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), self.bold_font),
            ('FONTNAME', (0, 1), (-1, -1), self.main_font),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        elements.append(emotion_table)
        elements.append(Spacer(1, 18))
        
        # ==================== THÀNH TỰU ====================
        elements.append(self._create_header_box("THÀNH TỰU ĐẠT ĐƯỢC"))
        elements.append(Spacer(1, 18))
        
        achievements = progress_data.get('achievements', [])
        if achievements:
            achievement_data = [[f"✓ {ach}"] for ach in achievements]
            achievement_table = Table(achievement_data, colWidths=[self.page_width])
            achievement_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdf4')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.main_font),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#86efac')),
            ]))
            elements.append(achievement_table)
        else:
            no_achievement = Paragraph("Chưa có thành tựu nào. Hãy tiếp tục cố gắng!", section_style)
            elements.append(no_achievement)
        
        elements.append(Spacer(1, 18))
        
        # ==================== NHẬN XÉT ====================
        elements.append(self._create_header_box("NHẬN XÉT VÀ KHUYẾN NGHỊ"))
        elements.append(Spacer(1, 18))
        
        comments = self._generate_comments(progress_data)
        if not comments:
            comment_text = "• Chưa có nhận xét cho giai đoạn này."
        else:
            comment_text = "<br/>".join(f"• {c}" for c in comments)

        comment_para = Paragraph(comment_text, ParagraphStyle(
            'CommentStyle',
            fontName=self.main_font,
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#1f2937')
        ))
        
        comment_table = Table([[comment_para]], colWidths=[self.page_width])
        comment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fffbeb')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#fde68a')),
        ]))
        elements.append(comment_table)
        elements.append(Spacer(1, 18))
        
        # ==================== FOOTER ====================
        footer_line = Drawing(self.page_width, 1)
        line2 = Line(0, 0, self.page_width, 0)
        line2.strokeColor = colors.HexColor('#d1d5db')
        line2.strokeWidth = 1
        footer_line.add(line2)
        elements.append(footer_line)
        elements.append(Spacer(1, 8))
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor('#6b7280'),
            alignment=1,
            fontName=self.italic_font
        )
        
        footer_text = f"""
        Báo cáo được tạo tự động bởi hệ thống EmoGarden<br/>
        Ngày tạo: {datetime.now().strftime('%d/%m/%Y lúc %H:%M')}<br/>
        Email: support@emogarden.com | Web: www.emogarden.com
        """
        footer = Paragraph(footer_text, footer_style)
        elements.append(footer)
        
        doc.build(elements)
        buffer.seek(0)
        
        return buffer
    
    def _generate_overview_text(self, progress_data: Dict) -> str:
        """Tạo đoạn tổng quan"""
        total_sessions = progress_data.get('total_sessions', 0)
        avg_score = progress_data.get('avg_score', 0)
        
        if avg_score >= 8:
            level = "xuất sắc"
        elif avg_score >= 7:
            level = "tốt"
        elif avg_score >= 6:
            level = "khá"
        else:
            level = "cần cố gắng"
        
        return f"Bé đã hoàn thành {total_sessions} phiên học tập với điểm trung bình {avg_score:.1f}/10 - mức độ {level}. Bé thể hiện sự tiến bộ rõ rệt trong quá trình học tập và rèn luyện kỹ năng nhận diện cảm xúc."
    
    def _generate_comments(self, progress_data: Dict) -> List[str]:
        comments = []
        
        total_sessions = progress_data.get('total_sessions', 1)
        avg_score = progress_data.get('avg_score', 1)
        
        if total_sessions >= 20:
            comments.append("Bé rất chăm chỉ và đều đặn trong việc học tập. Đây là một thói quen tuyệt vời!")
        elif total_sessions >= 10:
            comments.append("Bé có tần suất học tập tốt. Hãy tiếp tục duy trì và cố gắng tăng thêm nhé!")
        else:
            comments.append("Khuyến khích bé dành nhiều thời gian hơn để học tập và rèn luyện kỹ năng.")
        
        if avg_score >= 8:
            comments.append("Kết quả học tập xuất sắc! Bé đang tiến bộ rất tốt và nắm vững kiến thức.")
        elif avg_score >= 6:
            comments.append("Kết quả khá tốt. Bé đang trên đà phát triển và cải thiện từng ngày.")
        elif avg_score >= 4:
            comments.append("Bé đang làm quen với các bài học. Cần thêm thời gian để nắm vững kiến thức.")
        else:
            comments.append("Bé cần được hỗ trợ và khuyến khích nhiều hơn trong quá trình học tập.")
        
        emotion_stats = progress_data.get('emotion_stats', {})
        if emotion_stats:
            avg_emotion_accuracy = sum(s.get('accuracy', 0) for s in emotion_stats.values()) / len(emotion_stats)
            
            if avg_emotion_accuracy >= 80:
                comments.append("Bé đã nắm vững việc nhận diện và hiểu các cảm xúc cơ bản rất tốt.")
            elif avg_emotion_accuracy >= 60:
                comments.append("Bé đang tiến bộ trong việc nhận diện cảm xúc. Tiếp tục rèn luyện thêm nhé!")
            
            weak_emotions = [e for e, s in emotion_stats.items() if s.get('accuracy', 0) < 60]
            if weak_emotions:
                emotions_str = ', '.join([e.capitalize() for e in weak_emotions])
                comments.append(f"Nên tập trung hơn vào việc nhận diện các cảm xúc: {emotions_str}.")
        
        comments.append("Phụ huynh nên dành 15-20 phút mỗi ngày để trò chuyện với bé về cảm xúc.")
        
        return comments