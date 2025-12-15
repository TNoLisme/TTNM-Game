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
from typing import Dict, List, Tuple
import os

class ReportGeneratorService:
    def __init__(self):
        self.main_font = 'Times-Roman'
        self.bold_font = 'Times-Bold'
        self.italic_font = 'Times-Italic'
        self.bold_italic_font = 'Times-BoldItalic'
        
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(current_dir, '..', '..', 'fe', 'assets', 'fonts', 'DejaVuSans.ttf')
            
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('DejaVu', font_path))
                print("✅ Vietnamese font loaded successfully")
            else:
                print(f"⚠️ Vietnamese font not found at: {font_path}")
        except Exception as e:
            print(f"⚠️ Warning: Could not load Vietnamese font: {e}")
    
    def _create_header_box(self, text: str, color: str = '#667eea') -> Drawing:
        d = Drawing(6.5*inch, 0.5*inch)
        rect = Rect(0, 0, 6.5*inch, 0.5*inch)
        rect.fillColor = colors.HexColor(color)
        rect.strokeColor = None
        d.add(rect)
        
        label = String(0.2*inch, 0.18*inch, text)
        label.fontName = self.bold_font
        label.fontSize = 14
        label.fillColor = colors.white
        d.add(label)
        return d
    
    def _create_stat_card(self, label: str, value: str, icon: str = "") -> Drawing:
        d = Drawing(3*inch, 1*inch)
        
        rect = Rect(0, 0, 3*inch, 1*inch)
        rect.fillColor = colors.HexColor('#f8f9fa')
        rect.strokeColor = colors.HexColor('#e9ecef')
        rect.strokeWidth = 1
        d.add(rect)
        
        value_text = String(0.2*inch, 0.5*inch, value)
        value_text.fontName = self.bold_font
        value_text.fontSize = 18
        value_text.fillColor = colors.HexColor('#667eea')
        d.add(value_text)
        
        label_text = String(0.2*inch, 0.25*inch, label)
        label_text.fontName = self.main_font
        label_text.fontSize = 10
        label_text.fillColor = colors.HexColor('#6c757d')
        d.add(label_text)
        
        return d
    
    def _create_progress_bar(self, percentage: float, width: float = 4*inch) -> Drawing:
        d = Drawing(width, 0.3*inch)
        
        bg_rect = Rect(0, 0, width, 0.3*inch)
        bg_rect.fillColor = colors.HexColor('#e9ecef')
        bg_rect.strokeColor = None
        d.add(bg_rect)
        
        progress_width = width * (percentage / 100)
        progress_rect = Rect(0, 0, progress_width, 0.3*inch)
        
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
        
        text = String(width/2, 0.08*inch, f"{percentage:.0f}%")
        text.fontName = self.bold_font
        text.fontSize = 10
        text.fillColor = colors.white if percentage > 30 else colors.black
        text.textAnchor = 'middle'
        d.add(text)
        
        return d
    
    def _create_emotion_chart(self, emotion_stats: Dict) -> Drawing:
        """Biểu đồ cột cho cảm xúc - Tăng kích thước"""
        d = Drawing(6.5*inch, 3*inch)
        
        if not emotion_stats:
            return d
        
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 30
        chart.height = 200
        chart.width = 420
        
        emotions = list(emotion_stats.keys())
        accuracies = [stats.get('accuracy', 0) for stats in emotion_stats.values()]
        
        chart.data = [accuracies]
        chart.categoryAxis.categoryNames = emotions
        chart.categoryAxis.labels.angle = 0
        chart.categoryAxis.labels.fontSize = 10
        chart.categoryAxis.labels.boxAnchor = 'n'
        chart.categoryAxis.labels.fontName = self.main_font
        
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 100
        chart.valueAxis.valueStep = 20
        chart.valueAxis.labels.fontSize = 10
        chart.valueAxis.labels.fontName = self.main_font
        
        colors_list = [
            colors.HexColor('#667eea'),
            colors.HexColor('#764ba2'),
            colors.HexColor('#f093fb'),
            colors.HexColor('#4facfe'),
            colors.HexColor('#43e97b')
        ]
        
        for i in range(len(emotions)):
            chart.bars[i].fillColor = colors_list[i % len(colors_list)]
        
        chart.bars.strokeColor = None
        
        d.add(chart)
        return d
    
    def _create_games_pie_chart(self, games_stats: List[Dict]) -> Drawing:
        """Biểu đồ tròn - Tăng kích thước"""
        d = Drawing(3.2*inch, 3*inch)
        
        if not games_stats:
            return d
        
        pie = Pie()
        pie.x = 80
        pie.y = 40
        pie.width = 160
        pie.height = 160
        
        pie.data = [game.get('sessions', 0) for game in games_stats[:5]]
        pie.labels = [game.get('game_name', 'N/A')[:15] for game in games_stats[:5]]
        
        pie.slices.strokeColor = colors.white
        pie.slices.strokeWidth = 2
        pie.slices[0].fillColor = colors.HexColor('#667eea')
        pie.slices[1].fillColor = colors.HexColor('#764ba2')
        pie.slices[2].fillColor = colors.HexColor('#f093fb')
        pie.slices[3].fillColor = colors.HexColor('#4facfe')
        pie.slices[4].fillColor = colors.HexColor('#43e97b')
        
        pie.slices.fontSize = 9
        pie.slices.fontColor = colors.black
        pie.slices.fontName = self.main_font
        
        d.add(pie)
        return d
    
    def _create_score_trend_chart(self, games_stats: List[Dict]) -> Drawing:
        """Biểu đồ xu hướng điểm - Tăng kích thước"""
        d = Drawing(3.2*inch, 3*inch)
        
        if not games_stats:
            return d
        
        chart = HorizontalLineChart()
        chart.x = 40
        chart.y = 40
        chart.height = 180
        chart.width = 220
        
        scores = [game.get('avg_score', 0) for game in games_stats[:7]]
        chart.data = [scores]
        
        chart.categoryAxis.categoryNames = [f"G{i+1}" for i in range(len(scores))]
        chart.categoryAxis.labels.fontSize = 9
        chart.categoryAxis.labels.fontName = self.main_font
        
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 10
        chart.valueAxis.valueStep = 2
        chart.valueAxis.labels.fontSize = 10
        chart.valueAxis.labels.fontName = self.main_font
        
        chart.lines[0].strokeColor = colors.HexColor('#667eea')
        chart.lines[0].strokeWidth = 3
        chart.lines[0].symbol = None
        
        d.add(chart)
        return d
    
    def _create_summary_box(self, title: str, content: str, color: str = '#667eea') -> Table:
        """Tạo box tổng quan"""
        data = [
            [Paragraph(f"<b>{title}</b>", ParagraphStyle(
                'BoxTitle',
                fontName=self.bold_font,
                fontSize=11,
                textColor=colors.white
            ))],
            [Paragraph(content, ParagraphStyle(
                'BoxContent',
                fontName=self.main_font,
                fontSize=9,
                textColor=colors.HexColor('#212529'),
                leading=14
            ))]
        ]
        
        table = Table(data, colWidths=[6.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(color)),
            ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#f8f9fa')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (0, 0), 10),
            ('BOTTOMPADDING', (0, 0), (0, 0), 10),
            ('TOPPADDING', (0, 1), (0, 1), 12),
            ('BOTTOMPADDING', (0, 1), (0, 1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
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
            rightMargin=40, 
            leftMargin=40,
            topMargin=40, 
            bottomMargin=40,
            title=filename
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=26,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=10,
            alignment=1,
            fontName=self.bold_font
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#6c757d'),
            spaceAfter=30,
            alignment=1,
            fontName=self.italic_font
        )
        
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            spaceBefore=5,
            fontName=self.main_font
        )
        
        # ==================== HEADER ====================
        header_line = Drawing(6.5*inch, 0.1*inch)
        line1 = Line(0, 0, 6.5*inch, 0)
        line1.strokeColor = colors.HexColor('#667eea')
        line1.strokeWidth = 3
        header_line.add(line1)
        elements.append(header_line)
        elements.append(Spacer(1, 20))
        
        try:
            logo_path = os.path.join(os.path.dirname(__file__), '../../static/logo.png')
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=1.2*inch, height=1.2*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 15))
        except:
            pass
        
        title = Paragraph("BAO CAO TIEN DO HOC TAP", title_style)
        elements.append(title)
        
        period_text = "TUAN" if progress_data.get("period") == "weekly" else "THANG"
        subtitle = Paragraph(
            f"{period_text}: {progress_data.get('start_date')} den {progress_data.get('end_date')}",
            subtitle_style
        )
        elements.append(subtitle)
        
        # ==================== THÔNG TIN HỌC VIÊN ====================
        elements.append(self._create_header_box("THONG TIN HOC VIEN"))
        elements.append(Spacer(1, 15))
        
        child_info = [
            ['Ho va ten:', child_data.get('name', 'N/A')],
            ['Tuoi:', str(child_data.get('age', 'N/A')) + ' tuoi'],
            ['Ma hoc vien:', child_data.get('user_id', 'N/A')[:12] + '...'],
            ['Email:', child_data.get('email', 'N/A')],
        ]
        
        child_table = Table(child_info, colWidths=[2*inch, 4.5*inch])
        child_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#212529')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), self.bold_font),
            ('FONTNAME', (1, 0), (1, -1), self.main_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ]))
        elements.append(child_table)
        elements.append(Spacer(1, 20))
        
        # ==================== TỔNG QUAN - CARDS ====================
        elements.append(self._create_header_box("TONG QUAN HOAT DONG", '#764ba2'))
        elements.append(Spacer(1, 15))
        
        stats_row1 = [
            [self._create_stat_card("Tong so phien", str(progress_data.get('total_sessions', 0))),
             self._create_stat_card("Thoi gian choi", f"{progress_data.get('total_playtime', 0)}p")]
        ]
        stats_row2 = [
            [self._create_stat_card("Diem trung binh", f"{progress_data.get('avg_score', 0):.1f}/10"),
             self._create_stat_card("So tro choi", str(len(progress_data.get('games_stats', []))))]
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
        elements.append(Spacer(1, 15))
        
        # Tổng quan text
        summary_text = self._generate_overview_text(progress_data)
        summary_box = self._create_summary_box("TONG KET", summary_text, '#764ba2')
        elements.append(summary_box)
        elements.append(Spacer(1, 20))
        
        # ==================== BIỂU ĐỒ SONG SONG ====================
        games_stats = progress_data.get('games_stats', [])
        if games_stats:
            elements.append(self._create_header_box("PHAN TICH TRO CHOI", '#f093fb'))
            elements.append(Spacer(1, 15))
            
            # Đặt 2 charts cạnh nhau
            charts_row = [
                [self._create_games_pie_chart(games_stats), self._create_score_trend_chart(games_stats)]
            ]
            charts_table = Table(charts_row, colWidths=[3.25*inch, 3.25*inch])
            charts_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(charts_table)
            elements.append(Spacer(1, 15))
            
            # Games detail table
            games_data = [['Ten tro choi', 'Phien', 'Diem TB', 'Level', 'Tien do']]
            
            for game in games_stats[:5]:
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
                ('FONTNAME', (0, 0), (-1, 0), self.bold_font),
                ('FONTNAME', (0, 1), (-1, -1), self.main_font),
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
        
        # ==================== PAGE BREAK ====================
        elements.append(PageBreak())
        
        # ==================== THỐNG KÊ CẢM XÚC ====================
        emotion_stats = progress_data.get('emotion_stats', {})
        if emotion_stats:
            elements.append(self._create_header_box("THONG KE NHAN DIEN CAM XUC", '#4facfe'))
            elements.append(Spacer(1, 15))
            
            elements.append(self._create_emotion_chart(emotion_stats))
            elements.append(Spacer(1, 15))
            
            emotion_data = [['Cam xuc', 'Dung', 'Sai', 'Tong', 'Do chinh xac']]
            
            for emotion, stats in emotion_stats.items():
                correct = stats.get('correct', 0)
                incorrect = stats.get('incorrect', 0)
                total = correct + incorrect
                accuracy = stats.get('accuracy', 0)
                
                emotion_data.append([
                    emotion.capitalize(),
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
                ('FONTNAME', (0, 0), (-1, 0), self.bold_font),
                ('FONTNAME', (0, 1), (-1, -1), self.main_font),
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
            elements.append(Spacer(1, 20))
        
        # ==================== THÀNH TỰU ====================
        elements.append(self._create_header_box("THANH TUU DAT DUOC", '#43e97b'))
        elements.append(Spacer(1, 15))
        
        achievements = progress_data.get('achievements', [])
        if achievements:
            achievement_data = [[f"+ {ach}"] for ach in achievements]
            achievement_table = Table(achievement_data, colWidths=[6.5*inch])
            achievement_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdf4')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#212529')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.main_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#86efac')),
            ]))
            elements.append(achievement_table)
        else:
            no_achievement = Paragraph("Chua co thanh tuu nao. Hay tiep tuc co gang!", section_style)
            elements.append(no_achievement)
        
        elements.append(Spacer(1, 20))
        
        # ==================== NHẬN XÉT ====================
        elements.append(self._create_header_box("NHAN XET VA KHUYEN NGHI", '#f59e0b'))
        elements.append(Spacer(1, 15))
        
        comments = self._generate_comments(progress_data)
        if not comments:
            comment_text = "• Chưa có nhận xét cho giai đoạn này."
        else:
            comment_text = "<br/>".join(f"• {c}" for c in comments)

        comment_para = Paragraph(comment_text, ParagraphStyle(
            'CommentStyle',
            fontName=self.main_font,
            fontSize=9,
            leading=14,
            textColor=colors.HexColor('#212529')
        ))
        
        comment_table = Table([[comment_para]], colWidths=[6.5*inch])
        comment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fffbeb')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fde68a')),
        ]))
        elements.append(comment_table)
        elements.append(Spacer(1, 30))
        
        # ==================== FOOTER ====================
        footer_line = Drawing(6.5*inch, 0.1*inch)
        line2 = Line(0, 0, 6.5*inch, 0)
        line2.strokeColor = colors.HexColor('#dee2e6')
        line2.strokeWidth = 1
        footer_line.add(line2)
        elements.append(footer_line)
        elements.append(Spacer(1, 10))
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#6c757d'),
            alignment=1,
            fontName=self.italic_font
        )
        
        footer_text = f"""
        Bao cao duoc tao tu dong boi he thong EmoGarden<br/>
        Ngay tao: {datetime.now().strftime('%d/%m/%Y luc %H:%M')}<br/>
        Email: support@emogarden.com | Hotline: 1900-xxxx | Web: www.emogarden.com
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
            level = "xuat sac"
        elif avg_score >= 7:
            level = "tot"
        elif avg_score >= 6:
            level = "kha"
        else:
            level = "can co gang"
        
        return f"Be da hoan thanh {total_sessions} phien hoc tap voi diem trung binh {avg_score:.1f}/10 - muc do {level}. Be the hien su tien bo ro ret trong qua trinh hoc tap va ren luyen ky nang nhan dien cam xuc."
    
    def _generate_comments(self, progress_data: Dict) -> List[str]:
        comments = []
        
        total_sessions = progress_data.get('total_sessions', 1)
        avg_score = progress_data.get('avg_score', 1)
        
        # Nhận xét về tần suất chơi
        if total_sessions >= 20:
            comments.append("Be rat cham chi va deu dan trong viec hoc tap. Day la mot thoi quen tuyet voi!")
        elif total_sessions >= 10:
            comments.append("Be co tan suat hoc tap tot. Hay tiep tuc duy tri va co gang tang them nhe!")
        else:
            comments.append("Khuyen khich be danh nhieu thoi gian hon de hoc tap va ren luyen ky nang.")
        
        # Nhận xét về điểm số
        if avg_score >= 8:
            comments.append("Ket qua hoc tap xuat sac! Be dang tien bo rat tot va nam vung kien thuc.")
        elif avg_score >= 6:
            comments.append("Ket qua kha tot. Be dang tren da phat trien va cai thien tung ngay.")
        elif avg_score >= 4:
            comments.append("Be dang lam quen voi cac bai hoc. Can them thoi gian de nam vung kien thuc.")
        else:
            comments.append("Be can duoc ho tro va khuyen khich nhieu hon trong qua trinh hoc tap.")
        
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