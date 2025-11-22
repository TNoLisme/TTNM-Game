from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
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
        # Register Vietnamese font (cần download font)
        try:
            font_path = os.path.join(os.path.dirname(__file__), r'D:\TTNM\TTNM-Game\fe\assets\fonts\DejaVuSans.ttf')

            pdfmetrics.registerFont(TTFont('DejaVu', font_path))
        except:
            print("⚠️ Warning: Vietnamese font not found, using default")
    
    def _create_header_box(self, text: str, color: str = '#667eea') -> Drawing:
        """Tạo header box đẹp cho section"""
        d = Drawing(6.5*inch, 0.5*inch)
        rect = Rect(0, 0, 6.5*inch, 0.5*inch)
        rect.fillColor = colors.HexColor(color)
        rect.strokeColor = None
        d.add(rect)
        
        label = String(0.2*inch, 0.18*inch, text)
        label.fontName = 'Helvetica-Bold'
        label.fontSize = 14
        label.fillColor = colors.white
        d.add(label)
        return d
    
    def _create_stat_card(self, label: str, value: str, icon: str = "📊") -> Drawing:
        """Tạo card thống kê đẹp"""
        d = Drawing(3*inch, 1*inch)
        
        # Background
        rect = Rect(0, 0, 3*inch, 1*inch)
        rect.fillColor = colors.HexColor('#f8f9fa')
        rect.strokeColor = colors.HexColor('#e9ecef')
        rect.strokeWidth = 1
        d.add(rect)
        
        # Icon
        icon_text = String(0.2*inch, 0.6*inch, icon)
        icon_text.fontSize = 20
        d.add(icon_text)
        
        # Value
        value_text = String(0.2*inch, 0.35*inch, value)
        value_text.fontName = 'Helvetica-Bold'
        value_text.fontSize = 16
        value_text.fillColor = colors.HexColor('#667eea')
        d.add(value_text)
        
        # Label
        label_text = String(0.2*inch, 0.15*inch, label)
        label_text.fontName = 'Helvetica'
        label_text.fontSize = 9
        label_text.fillColor = colors.HexColor('#6c757d')
        d.add(label_text)
        
        return d
    
    def _create_progress_bar(self, percentage: float, width: float = 4*inch) -> Drawing:
        """Tạo thanh tiến độ"""
        d = Drawing(width, 0.3*inch)
        
        # Background bar
        bg_rect = Rect(0, 0, width, 0.3*inch)
        bg_rect.fillColor = colors.HexColor('#e9ecef')
        bg_rect.strokeColor = None
        d.add(bg_rect)
        
        # Progress bar
        progress_width = width * (percentage / 100)
        progress_rect = Rect(0, 0, progress_width, 0.3*inch)
        
        # Gradient color based on percentage
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
        text = String(width/2, 0.08*inch, f"{percentage:.0f}%")
        text.fontName = 'Helvetica-Bold'
        text.fontSize = 10
        text.fillColor = colors.white if percentage > 30 else colors.black
        text.textAnchor = 'middle'
        d.add(text)
        
        return d
    
    def _create_emotion_chart(self, emotion_stats: Dict) -> Drawing:
        """Tạo biểu đồ cột cho thống kê cảm xúc"""
        d = Drawing(400, 200)
        
        if not emotion_stats:
            return d
        
        chart = VerticalBarChart()
        chart.x = 30
        chart.y = 30
        chart.height = 150
        chart.width = 350
        
        emotions = list(emotion_stats.keys())
        accuracies = [stats.get('accuracy', 0) for stats in emotion_stats.values()]
        
        chart.data = [accuracies]
        chart.categoryAxis.categoryNames = emotions
        chart.categoryAxis.labels.angle = 0
        chart.categoryAxis.labels.fontSize = 9
        chart.categoryAxis.labels.boxAnchor = 'n'
        
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 100
        chart.valueAxis.valueStep = 20
        chart.valueAxis.labels.fontSize = 9
        
        # Gradient colors for bars
        colors_list = [
            colors.HexColor('#667eea'),
            colors.HexColor('#764ba2'),
            colors.HexColor('#f093fb'),
            colors.HexColor('#4facfe'),
            colors.HexColor('#43e97b')
        ]
        
        for i in range(len(emotions)):
            chart.bars[0].fillColor = colors_list[i % len(colors_list)]
        
        chart.bars.strokeColor = None
        
        d.add(chart)
        return d
    
    def _create_games_pie_chart(self, games_stats: List[Dict]) -> Drawing:
        """Tạo biểu đồ tròn cho thời gian chơi các trò chơi"""
        d = Drawing(300, 200)
        
        if not games_stats:
            return d
        
        pie = Pie()
        pie.x = 80
        pie.y = 30
        pie.width = 140
        pie.height = 140
        
        pie.data = [game.get('sessions', 0) for game in games_stats[:5]]  # Top 5 games
        pie.labels = [game.get('game_name', 'N/A')[:15] for game in games_stats[:5]]
        
        # Beautiful color scheme
        pie.slices.strokeColor = colors.white
        pie.slices.strokeWidth = 2
        pie.slices[0].fillColor = colors.HexColor('#667eea')
        pie.slices[1].fillColor = colors.HexColor('#764ba2')
        pie.slices[2].fillColor = colors.HexColor('#f093fb')
        pie.slices[3].fillColor = colors.HexColor('#4facfe')
        pie.slices[4].fillColor = colors.HexColor('#43e97b')
        
        pie.slices.fontSize = 8
        pie.slices.fontColor = colors.black
        
        d.add(pie)
        return d
    
    def _create_score_trend_chart(self, games_stats: List[Dict]) -> Drawing:
        """Tạo biểu đồ xu hướng điểm số"""
        d = Drawing(400, 200)
        
        if not games_stats:
            return d
        
        chart = HorizontalLineChart()
        chart.x = 40
        chart.y = 30
        chart.height = 150
        chart.width = 340
        
        scores = [game.get('avg_score', 0) for game in games_stats[:10]]
        chart.data = [scores]
        
        chart.categoryAxis.categoryNames = [f"G{i+1}" for i in range(len(scores))]
        chart.categoryAxis.labels.fontSize = 8
        
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 10
        chart.valueAxis.valueStep = 2
        chart.valueAxis.labels.fontSize = 9
        
        chart.lines[0].strokeColor = colors.HexColor('#667eea')
        chart.lines[0].strokeWidth = 2
        chart.lines[0].symbol = None
        
        d.add(chart)
        return d
    
    def generate_progress_report(self, child_data: Dict, progress_data: Dict) -> BytesIO:
        """
        Tạo báo cáo tiến độ PDF
        
        Args:
            child_data: {user_id, name, age, email, phone_number}
            progress_data: {
                period: "weekly/monthly",
                start_date, end_date,
                total_sessions, total_playtime,
                games_stats: [{game_name, sessions, avg_score, level}],
                emotion_stats: {emotion: {correct, incorrect, accuracy}},
                achievements: [...]
            }
        
        Returns:
            BytesIO: PDF file in memory
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=40, leftMargin=40,
                              topMargin=40, bottomMargin=40)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=26,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=10,
            alignment=1,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#6c757d'),
            spaceAfter=30,
            alignment=1,
            fontName='Helvetica-Oblique'
        )
        
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            spaceBefore=5
        )
        
        # ==================== HEADER ====================
        # Decorative header line
        header_line = Drawing(6.5*inch, 0.1*inch)
        line1 = Line(0, 0, 6.5*inch, 0)
        line1.strokeColor = colors.HexColor('#667eea')
        line1.strokeWidth = 3
        header_line.add(line1)
        elements.append(header_line)
        elements.append(Spacer(1, 20))
        
        # Logo
        try:
            logo_path = os.path.join(os.path.dirname(__file__), '../../static/logo.png')
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=1.2*inch, height=1.2*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 15))
        except:
            pass
        
        # Title
        title = Paragraph("BÁO CÁO TIẾN ĐỘ HỌC TẬP", title_style)
        elements.append(title)
        
        # Subtitle
        period_text = "TUẦN" if progress_data.get("period") == "weekly" else "THÁNG"
        subtitle = Paragraph(
            f"{period_text}: {progress_data.get('start_date')} đến {progress_data.get('end_date')}",
            subtitle_style
        )
        elements.append(subtitle)
        
        # ==================== THÔNG TIN HỌC VIÊN ====================
        elements.append(self._create_header_box("👤 THÔNG TIN HỌC VIÊN"))
        elements.append(Spacer(1, 15))
        
        child_info = [
            ['Họ và tên:', child_data.get('name', 'N/A')],
            ['Tuổi:', str(child_data.get('age', 'N/A')) + ' tuổi'],
            ['Mã học viên:', child_data.get('user_id', 'N/A')[:12] + '...'],
            ['Email:', child_data.get('email', 'N/A')],
        ]
        
        child_table = Table(child_info, colWidths=[2*inch, 4.5*inch])
        child_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#212529')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ]))
        elements.append(child_table)
        elements.append(Spacer(1, 25))
        
        # ==================== TỔNG QUAN - CARDS ====================
        elements.append(self._create_header_box("📊 TỔNG QUAN HOẠT ĐỘNG", '#764ba2'))
        elements.append(Spacer(1, 15))
        
        # Stats cards in table layout
        stats_row1 = [
            [self._create_stat_card("Tổng số phiên", str(progress_data.get('total_sessions', 0)), "🎮"),
             self._create_stat_card("Thời gian chơi", f"{progress_data.get('total_playtime', 0)}p", "⏱️")]
        ]
        stats_row2 = [
            [self._create_stat_card("Điểm trung bình", f"{progress_data.get('avg_score', 0):.1f}/10", "⭐"),
             self._create_stat_card("Số trò chơi", str(len(progress_data.get('games_stats', []))), "🎯")]
        ]
        
        stats_table1 = Table(stats_row1, colWidths=[3.25*inch, 3.25*inch])
        stats_table1.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(stats_table1)
        elements.append(Spacer(1, 10))
        
        stats_table2 = Table(stats_row2, colWidths=[3.25*inch, 3.25*inch])
        stats_table2.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(stats_table2)
        elements.append(Spacer(1, 25))
        
        # ==================== BIỂU ĐỒ TRÒ CHƠI ====================
        games_stats = progress_data.get('games_stats', [])
        if games_stats:
            elements.append(self._create_header_box("🎮 PHÂN BỐ THỜI GIAN CHƠI", '#f093fb'))
            elements.append(Spacer(1, 15))
            elements.append(self._create_games_pie_chart(games_stats))
            elements.append(Spacer(1, 20))
            
            # Games detail table
            games_data = [['Tên trò chơi', 'Phiên', 'Điểm TB', 'Level', 'Tiến độ']]
            
            for game in games_stats[:5]:  # Top 5 games
                progress_pct = min(game.get('avg_score', 0) * 10, 100)
                games_data.append([
                    game.get('game_name', 'N/A')[:20],
                    str(game.get('sessions', 0)),
                    f"{game.get('avg_score', 0):.1f}",
                    str(game.get('level', 1)),
                    self._create_progress_bar(progress_pct, 1.5*inch)
                ])
            
            games_table = Table(games_data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 0.7*inch, 2.2*inch])
            games_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
            ]))
            elements.append(games_table)
            elements.append(Spacer(1, 25))
        
        # ==================== PAGE BREAK ====================
        elements.append(PageBreak())
        
        # ==================== THỐNG KÊ CẢM XÚC ====================
        emotion_stats = progress_data.get('emotion_stats', {})
        if emotion_stats:
            elements.append(self._create_header_box("😊 THỐNG KÊ NHẬN DIỆN CẢM XÚC", '#4facfe'))
            elements.append(Spacer(1, 15))
            
            # Emotion chart
            elements.append(self._create_emotion_chart(emotion_stats))
            elements.append(Spacer(1, 20))
            
            # Emotion detail table
            emotion_data = [['Cảm xúc', 'Đúng', 'Sai', 'Tổng', 'Độ chính xác']]
            
            emotion_icons = {
                'vui': '😊',
                'buồn': '😢',
                'giận': '😠',
                'sợ': '😨',
                'ngạc nhiên': '😲'
            }
            
            for emotion, stats in emotion_stats.items():
                correct = stats.get('correct', 0)
                incorrect = stats.get('incorrect', 0)
                total = correct + incorrect
                accuracy = stats.get('accuracy', 0)
                icon = emotion_icons.get(emotion.lower(), '😐')
                
                emotion_data.append([
                    f"{icon} {emotion.capitalize()}",
                    str(correct),
                    str(incorrect),
                    str(total),
                    self._create_progress_bar(accuracy, 1.5*inch)
                ])
            
            emotion_table = Table(emotion_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 2*inch])
            emotion_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
            ]))
            elements.append(emotion_table)
            elements.append(Spacer(1, 25))
        
        # ==================== THÀNH TỰU ====================
        elements.append(self._create_header_box("🏆 THÀNH TỰU ĐẠT ĐƯỢC", '#43e97b'))
        elements.append(Spacer(1, 15))
        
        achievements = progress_data.get('achievements', [])
        if achievements:
            achievement_data = [[f"🏆 {ach}"] for ach in achievements]
            achievement_table = Table(achievement_data, colWidths=[6.5*inch])
            achievement_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#212529')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ]))
            elements.append(achievement_table)
        else:
            no_achievement = Paragraph("Chưa có thành tựu nào. Hãy tiếp tục cố gắng! 💪", section_style)
            elements.append(no_achievement)
        
        elements.append(Spacer(1, 25))
        
        # ==================== NHẬN XÉT ====================
        elements.append(self._create_header_box("💬 NHẬN XÉT VÀ KHUYẾN NGHỊ", '#f59e0b'))
        elements.append(Spacer(1, 15))
        
        comments = self._generate_comments(progress_data) or []
        comment_data = [[f"• {comment}"] for comment in comments]
        
        if comment_data:
            comment_table = Table(comment_data, colWidths=[6.5*inch])
            comment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fffbeb')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#212529')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ]))
            elements.append(comment_table)
        else:
            elements.append(Paragraph("Chưa có nhận xét nào.", styles['Normal']))
        
        elements.append(Spacer(1, 30))
        
        # ==================== FOOTER ====================
        footer_line = Drawing(6.5*inch, 0.1*inch)
        line2 = Line(0, 0, 6.5*inch, 0)
        line2.strokeColor = colors.HexColor('#dee2e6')
        line2.strokeWidth = 1
        footer_line.add(line2)
        elements.append(footer_line)
        elements.append(Spacer(1, 10))
        
        footer_text = f"""
        <para align=center fontSize=8 textColor=#6c757d>
        <i>Báo cáo được tạo tự động bởi hệ thống EmoGarden</i><br/>
        <i>Ngày tạo: {datetime.now().strftime('%d/%m/%Y lúc %H:%M')}</i><br/>
        <i>📧 support@emogarden.com | 📞 Hotline: 1900-xxxx | 🌐 www.emogarden.com</i>
        </para>
        """
        footer = Paragraph(footer_text, styles['Normal'])
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _generate_comments(self, progress_data: Dict) -> List[str]:
        """Tạo nhận xét tự động dựa trên dữ liệu"""
        comments = []
        
        total_sessions = progress_data.get('total_sessions', 0)
        avg_score = progress_data.get('avg_score', 0)
        
        # Nhận xét về tần suất chơi
        if total_sessions >= 20:
            comments.append("Bé rất chăm chỉ và đều đặn trong việc học tập. Đây là một thói quen tuyệt vời! 👏")
        elif total_sessions >= 10:
            comments.append("Bé có tần suất học tập tốt. Hãy tiếp tục duy trì và cố gắng tăng thêm nhé!")
        else:
            comments.append("Khuyến khích bé dành nhiều thời gian hơn để học tập và rèn luyện kỹ năng.")
        
        # Nhận xét về điểm số
        if avg_score >= 8:
            comments.append("Kết quả học tập xuất sắc! Bé đang tiến bộ rất tốt và nắm vững kiến thức. 🌟")
        elif avg_score >= 6:
            comments.append("Kết quả khá tốt. Bé đang trên đà phát triển và cải thiện từng ngày.")
        elif avg_score >= 4:
            comments.append("Bé đang làm quen với các bài học. Cần thêm thời gian để nắm vững kiến thức.")
        else:
            comments.append("Bé cần được hỗ trợ và khuyến khích nhiều hơn trong quá trình học tập.")
        
        # Nhận xét về cảm xúc
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
        
        # Khuyến nghị cho phụ huynh
        comments.append("Phụ huynh nên dành 15-20 phút mỗi ngày để trò chuyện với bé về cảm xúc");