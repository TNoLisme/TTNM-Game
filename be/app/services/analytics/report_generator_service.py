from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, Image, PageBreak, KeepTogether, Frame
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Optional
import os


class FontManager:
    """Quản lý font cho PDF - hỗ trợ tiếng Việt và Emoji"""
    
    FONTS = {
        'regular': 'VNFont',
        'bold': 'VNFont-Bold',
        'italic': 'VNFont-Italic'
    }
    
    @classmethod
    def initialize(cls) -> bool:
        """Khởi tạo font - tự động tìm và load font hỗ trợ Unicode"""
        try:
            # Danh sách font hỗ trợ Unicode/Emoji tốt
            possible_paths = [
                # Windows - Segoe UI Emoji + Arial Unicode
                (r'C:\Windows\Fonts\seguiemj.ttf', r'C:\Windows\Fonts\arialbd.ttf', r'C:\Windows\Fonts\ariali.ttf'),
                (r'C:\Windows\Fonts\arial.ttf', r'C:\Windows\Fonts\arialbd.ttf', r'C:\Windows\Fonts\ariali.ttf'),
                # Linux - DejaVu hỗ trợ Unicode tốt
                ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 
                 '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                 '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'),
                # macOS
                ('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
                 '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
                 '/System/Library/Fonts/Supplemental/Arial.ttf'),
            ]
            
            # Tìm bộ font có sẵn
            regular_font = None
            bold_font = None
            italic_font = None
            
            for regular, bold, italic in possible_paths:
                if os.path.exists(regular):
                    regular_font = regular
                    bold_font = bold if os.path.exists(bold) else regular
                    italic_font = italic if os.path.exists(italic) else regular
                    break
            
            # Nếu không tìm thấy, dùng font mặc định
            if not regular_font:
                print("⚠️ Using default fonts (limited emoji support)")
                cls.FONTS = {
                    'regular': 'Helvetica',
                    'bold': 'Helvetica-Bold',
                    'italic': 'Helvetica-Oblique'
                }
                return False
            
            # Đăng ký font
            pdfmetrics.registerFont(TTFont(cls.FONTS['regular'], regular_font))
            pdfmetrics.registerFont(TTFont(cls.FONTS['bold'], bold_font))
            pdfmetrics.registerFont(TTFont(cls.FONTS['italic'], italic_font))
            
            print(f"✅ Fonts loaded: {regular_font}")
            return True
            
        except Exception as e:
            print(f"⚠️ Font loading error: {e}")
            cls.FONTS = {
                'regular': 'Helvetica',
                'bold': 'Helvetica-Bold',
                'italic': 'Helvetica-Oblique'
            }
            return False


class ColorPalette:
    """Bảng màu hiện đại cho report"""
    PRIMARY = colors.HexColor('#6366f1')      # Indigo
    SECONDARY = colors.HexColor('#8b5cf6')    # Purple
    SUCCESS = colors.HexColor('#10b981')      # Green
    WARNING = colors.HexColor('#f59e0b')      # Orange
    DANGER = colors.HexColor('#ef4444')       # Red
    INFO = colors.HexColor('#3b82f6')         # Blue
    
    GRAY_50 = colors.HexColor('#f9fafb')
    GRAY_100 = colors.HexColor('#f3f4f6')
    GRAY_200 = colors.HexColor('#e5e7eb')
    GRAY_300 = colors.HexColor('#d1d5db')
    GRAY_600 = colors.HexColor('#4b5563')
    GRAY_900 = colors.HexColor('#111827')


class ReportGeneratorService:
    """Service tạo báo cáo PDF hiện đại cho EmoGarden"""
    
    def __init__(self):
        """Khởi tạo service"""
        self.font_available = FontManager.initialize()
        self.fonts = FontManager.FONTS
        self.colors = ColorPalette
        self.styles = self._create_styles()
    
    def _create_styles(self) -> Dict:
        """Tạo các style cho document"""
        base_styles = getSampleStyleSheet()
        
        custom_styles = {
            'Title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Heading1'],
                fontName=self.fonts['bold'],
                fontSize=28,
                textColor=self.colors.PRIMARY,
                alignment=TA_CENTER,
                spaceAfter=8,
                spaceBefore=0
            ),
            
            'Subtitle': ParagraphStyle(
                'CustomSubtitle',
                parent=base_styles['Normal'],
                fontName=self.fonts['italic'],
                fontSize=13,
                textColor=self.colors.GRAY_600,
                alignment=TA_CENTER,
                spaceAfter=20
            ),
            
            'SectionHeader': ParagraphStyle(
                'SectionHeader',
                parent=base_styles['Heading2'],
                fontName=self.fonts['bold'],
                fontSize=18,
                textColor=colors.white,
                alignment=TA_LEFT,
                leftIndent=10,
                spaceAfter=0,
                spaceBefore=0
            ),
            
            'Normal': ParagraphStyle(
                'CustomNormal',
                parent=base_styles['Normal'],
                fontName=self.fonts['regular'],
                fontSize=11,
                textColor=self.colors.GRAY_900,
                alignment=TA_LEFT
            ),
            
            'TableHeader': ParagraphStyle(
                'TableHeader',
                parent=base_styles['Normal'],
                fontName=self.fonts['bold'],
                fontSize=13,
                textColor=colors.white,
                alignment=TA_CENTER
            ),
            
            'TableCell': ParagraphStyle(
                'TableCell',
                parent=base_styles['Normal'],
                fontName=self.fonts['regular'],
                fontSize=11,
                textColor=self.colors.GRAY_900,
                alignment=TA_CENTER
            ),
            
            'Footer': ParagraphStyle(
                'Footer',
                parent=base_styles['Normal'],
                fontName=self.fonts['italic'],
                fontSize=8,
                textColor=self.colors.GRAY_600,
                alignment=TA_CENTER
            )
        }
        
        return custom_styles
    
    def _create_section_header(self, text: str, icon: str = "", bg_color=None) -> Table:
        if bg_color is None:
            bg_color = self.colors.PRIMARY
        
        full_text = f"{icon} {text}" if icon else text
        header_para = Paragraph(full_text, self.styles['SectionHeader'])
        
        table = Table([[header_para]], colWidths=[7*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table
    
    def _create_info_card(self, label: str, value: str, icon: str = "•") -> List:
        """Tạo card thông tin đẹp"""
        data = [
            [Paragraph(f"<b>{icon} {label}</b>", self.styles['Normal'])],
            [Paragraph(f"<font size=14 color='#6366f1'><b>{value}</b></font>", self.styles['Normal'])]
        ]
        
        table = Table(data, colWidths=[3.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.colors.GRAY_50),
            ('BOX', (0, 0), (-1, -1), 1, self.colors.GRAY_200),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        return table
    
    def _create_progress_indicator(self, percentage: float) -> str:
        """Tạo thanh tiến độ bằng text"""
        filled = int(percentage / 10)
        empty = 10 - filled
        
        if percentage >= 80:
            color = '#10b981'  # Green
        elif percentage >= 60:
            color = '#3b82f6'  # Blue
        elif percentage >= 40:
            color = '#f59e0b'  # Orange
        else:
            color = '#ef4444'  # Red
        
        bar = '█' * filled + '░' * empty
        return f"<font color='{color}'>{bar}</font> {percentage:.0f}%"
    
    def _create_emotion_bar_chart(self, emotion_stats: Dict) -> Drawing:
        d = Drawing(350, 180)  

        if not emotion_stats:
            return d

        chart = VerticalBarChart()
        chart.x = 40     
        chart.y = 25
        chart.width = 260  
        chart.height = 130

        emotions = list(emotion_stats.keys())
        accuracies = [stats.get('accuracy', 0) for stats in emotion_stats.values()]

        chart.data = [accuracies]

        chart.categoryAxis.categoryNames = [e.capitalize() for e in emotions]
        chart.categoryAxis.labels.angle = 0
        chart.categoryAxis.labels.fontSize = 10
        chart.categoryAxis.labels.dy = -5

        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 100
        chart.valueAxis.valueStep = 20
        chart.valueAxis.labels.fontSize = 10

        chart.bars[0].fillColor = self.colors.PRIMARY
        chart.bars.strokeColor = None

        d.add(chart)
        return d

    
    def _create_games_pie_chart(self, games_stats: List[Dict]) -> Drawing:
        d = Drawing(380, 240)  

        if not games_stats:
            return d

        pie = Pie()
        pie.x = 110
        pie.y = 40
        pie.width = 150
        pie.height = 150

        top_games = games_stats[:5]
        pie.data = [game.get('sessions', 0) for game in top_games]
        pie.labels = [game.get('game_name', 'N/A')[:25] for game in top_games]

        color_scheme = [
            self.colors.PRIMARY,
            self.colors.SECONDARY,
            self.colors.INFO,
            self.colors.SUCCESS,
            self.colors.WARNING
        ]

        pie.slices.strokeColor = colors.white
        pie.slices.strokeWidth = 1.5

        for i, color in enumerate(color_scheme):
            if i < len(top_games):
                pie.slices[i].fillColor = color

        pie.slices.fontSize = 10       
        pie.slices.fontName = self.fonts['regular']
        pie.slices.popout = 3         

        d.add(pie)
        return d

    
    def _create_score_trend_drawing(self, games_stats: List[Dict]) -> Drawing:
        d = Drawing(380, 160)

        if not games_stats:
            return d

        max_games = min(len(games_stats), 10)
        bar_width = 30
        spacing = 12
        start_x = 25

        for i, game in enumerate(games_stats[:max_games]):
            score = game.get('avg_score', 0)
            bar_height = (score / 10) * 110

            if score >= 8:
                bar_color = self.colors.SUCCESS
            elif score >= 6:
                bar_color = self.colors.INFO
            elif score >= 4:
                bar_color = self.colors.WARNING
            else:
                bar_color = self.colors.DANGER

            rect = Rect(start_x + (i * (bar_width + spacing)), 30, bar_width, bar_height)
            rect.fillColor = bar_color
            rect.strokeColor = None
            d.add(rect)

            label = String(
                start_x + (i * (bar_width + spacing)) + bar_width/2,
                bar_height + 35,
                f"{score:.1f}"
            )
            label.fontSize = 10 
            label.textAnchor = 'middle'
            label.fontName = self.fonts['bold']
            d.add(label)

        return d

    
    def _create_stat_summary_table(self, stats: Dict) -> Table:
        data = [
            [
                self._create_info_card("Tổng số phiên", str(stats.get('total_sessions', 0)), "🎮"),
                self._create_info_card("Thời gian chơi", f"{stats.get('total_playtime', 0)}p", "⏱️")
            ],
            [
                self._create_info_card("Điểm trung bình", f"{stats.get('avg_score', 0):.1f}/10", "⭐"),
                self._create_info_card("Số trò chơi", str(len(stats.get('games_stats', []))), "🎯")
            ]
        ]
        
        table = Table(data, colWidths=[3.5*inch, 3.5*inch], rowHeights=[1.2*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        return table
    
    def generate_progress_report(self, child_data: Dict, progress_data: Dict) -> BytesIO:
        """
        Tạo báo cáo tiến độ PDF hiện đại
        
        Args:
            child_data: {
                'user_id': str,
                'name': str,
                'age': int,
                'email': str,
                'phone_number': str (optional)
            }
            progress_data: {
                'period': 'weekly' | 'monthly',
                'start_date': str,
                'end_date': str,
                'total_sessions': int,
                'total_playtime': int (minutes),
                'avg_score': float,
                'games_stats': [
                    {
                        'game_name': str,
                        'sessions': int,
                        'avg_score': float,
                        'level': int
                    }
                ],
                'emotion_stats': {
                    'emotion_name': {
                        'correct': int,
                        'incorrect': int,
                        'accuracy': float
                    }
                },
                'achievements': [str]
            }
        
        Returns:
            BytesIO: PDF file buffer
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        
        # ==================== HEADER ====================
        # Decorative line
        line_table = Table([['']], colWidths=[7*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 4, self.colors.PRIMARY),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Title
        title = Paragraph("BÁO CÁO TIẾN ĐỘ HỌC TẬP", self.styles['Title'])
        elements.append(title)
        
        # Subtitle
        period_text = "TUẦN" if progress_data.get("period") == "weekly" else "THÁNG"
        subtitle_text = f"{period_text}: {progress_data.get('start_date')} đến {progress_data.get('end_date')}"
        subtitle = Paragraph(subtitle_text, self.styles['Subtitle'])
        elements.append(subtitle)
        
        elements.append(Spacer(1, 0.2*inch))
        
        # ==================== THÔNG TIN HỌC VIÊN ====================
        elements.append(self._create_section_header("THÔNG TIN HỌC VIÊN", "👤"))
        elements.append(Spacer(1, 0.15*inch))
        
        child_info_data = [
            [
                Paragraph("<b>Họ và tên:</b>", self.styles['Normal']),
                Paragraph(child_data.get('name', 'N/A'), self.styles['Normal'])
            ],
            [
                Paragraph("<b>Tuổi:</b>", self.styles['Normal']),
                Paragraph(f"{child_data.get('age', 'N/A')} tuổi", self.styles['Normal'])
            ],
            [
                Paragraph("<b>Mã học viên:</b>", self.styles['Normal']),
                Paragraph(child_data.get('user_id', 'N/A')[:15] + '...', self.styles['Normal'])
            ],
            [
                Paragraph("<b>Email:</b>", self.styles['Normal']),
                Paragraph(child_data.get('email', 'N/A'), self.styles['Normal'])
            ]
        ]
        
        child_info_table = Table(child_info_data, colWidths=[2.2*inch, 4.8*inch])
        child_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.colors.GRAY_50),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors.GRAY_200),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(child_info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # ==================== TỔNG QUAN ====================
        elements.append(self._create_section_header("TỔNG QUAN HOẠT ĐỘNG", "📊", self.colors.SECONDARY))
        elements.append(Spacer(1, 0.15*inch))
        
        stats_table = self._create_stat_summary_table(progress_data)
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # ==================== CHI TIẾT TRÒ CHƠI ====================
        games_stats = progress_data.get('games_stats', [])
        if games_stats:
            elements.append(self._create_section_header("CHI TIẾT TRÒ CHƠI", "🎮", self.colors.INFO))
            elements.append(Spacer(1, 0.15*inch))
            
            # Thêm biểu đồ tròn phân bố
            pie_chart = self._create_games_pie_chart(games_stats)
            pie_table = Table([[pie_chart]], colWidths=[7*inch])
            pie_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(pie_table)
            elements.append(Spacer(1, 0.1*inch))
            
            # Bảng chi tiết
            game_header = [
                Paragraph("<b>Tên trò chơi</b>", self.styles['TableHeader']),
                Paragraph("<b>Phiên</b>", self.styles['TableHeader']),
                Paragraph("<b>Điểm TB</b>", self.styles['TableHeader']),
                Paragraph("<b>Level</b>", self.styles['TableHeader']),
                Paragraph("<b>Tiến độ</b>", self.styles['TableHeader'])
            ]
            
            game_data = [game_header]
            
            for game in games_stats[:10]:  # Top 10 games
                progress_pct = min(game.get('avg_score', 0) * 10, 100)
                progress_bar = self._create_progress_indicator(progress_pct)
                
                game_data.append([
                    Paragraph(game.get('game_name', 'N/A'), self.styles['TableCell']),
                    Paragraph(str(game.get('sessions', 0)), self.styles['TableCell']),
                    Paragraph(f"{game.get('avg_score', 0):.1f}", self.styles['TableCell']),
                    Paragraph(str(game.get('level', 1)), self.styles['TableCell']),
                    Paragraph(progress_bar, self.styles['TableCell'])
                ])
            
            game_table = Table(game_data, colWidths=[2.2*inch, 0.8*inch, 0.9*inch, 0.8*inch, 2.3*inch])
            game_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors.INFO),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors.GRAY_200),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors.GRAY_50]),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(game_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # ==================== PAGE BREAK ====================
        elements.append(PageBreak())
        
        # ==================== THỐNG KÊ CẢM XÚC ====================
        emotion_stats = progress_data.get('emotion_stats', {})
        if emotion_stats:
            elements.append(self._create_section_header("THỐNG KÊ NHẬN DIỆN CẢM XÚC", "😊", self.colors.SUCCESS))
            elements.append(Spacer(1, 0.15*inch))
            
            # Biểu đồ cột
            bar_chart = self._create_emotion_bar_chart(emotion_stats)
            chart_table = Table([[bar_chart]], colWidths=[7*inch])
            chart_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(chart_table)
            elements.append(Spacer(1, 0.15*inch))
            
            # Bảng chi tiết
            emotion_icons = {
                'vui': '😊',
                'buon': '😢',
                'gian': '😠',
                'so': '😨',
                'ngac nhien': '😲'
            }
            
            emotion_header = [
                Paragraph("<b>Cảm xúc</b>", self.styles['TableHeader']),
                Paragraph("<b>Đúng</b>", self.styles['TableHeader']),
                Paragraph("<b>Sai</b>", self.styles['TableHeader']),
                Paragraph("<b>Tổng</b>", self.styles['TableHeader']),
                Paragraph("<b>Độ chính xác</b>", self.styles['TableHeader'])
            ]
            
            emotion_data = [emotion_header]
            
            for emotion, stats in emotion_stats.items():
                correct = stats.get('correct', 0)
                incorrect = stats.get('incorrect', 0)
                total = correct + incorrect
                accuracy = stats.get('accuracy', 0)
                
                # Tìm icon phù hợp
                icon = '😐'
                emotion_lower = emotion.lower().replace(' ', '')
                for key, emoji in emotion_icons.items():
                    if key in emotion_lower:
                        icon = emoji
                        break
                
                progress_bar = self._create_progress_indicator(accuracy)
                
                emotion_data.append([
                    Paragraph(f"{icon} {emotion.capitalize()}", self.styles['TableCell']),
                    Paragraph(str(correct), self.styles['TableCell']),
                    Paragraph(str(incorrect), self.styles['TableCell']),
                    Paragraph(str(total), self.styles['TableCell']),
                    Paragraph(progress_bar, self.styles['TableCell'])
                ])
            
            emotion_table = Table(emotion_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 2.5*inch])
            emotion_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors.SUCCESS),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors.GRAY_200),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors.GRAY_50]),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(emotion_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # ==================== THÀNH TỰU ====================
        elements.append(self._create_section_header("THÀNH TỰU ĐẠT ĐƯỢC", "🏆", self.colors.WARNING))
        elements.append(Spacer(1, 0.15*inch))
        
        achievements = progress_data.get('achievements', [])
        if achievements:
            achievement_data = []
            for ach in achievements:
                achievement_data.append([Paragraph(f"🏆 {ach}", self.styles['Normal'])])
            
            achievement_table = Table(achievement_data, colWidths=[7*inch])
            achievement_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.colors.GRAY_50),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors.GRAY_200),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(achievement_table)
        else:
            no_ach = Paragraph(
                "Chưa có thành tựu nào. Hãy tiếp tục cố gắng! 💪",
                self.styles['Normal']
            )
            elements.append(no_ach)
        
        elements.append(Spacer(1, 0.3*inch))
        
        # ==================== NHẬN XÉT ====================
        elements.append(self._create_section_header("NHẬN XÉT VÀ KHUYẾN NGHỊ", "💬", self.colors.SECONDARY))
        elements.append(Spacer(1, 0.15*inch))
        
        comments = self._generate_auto_comments(progress_data)
        
        if comments:
            comment_data = []
            for i, comment in enumerate(comments, 1):
                comment_data.append([Paragraph(f"{i}. {comment}", self.styles['Normal'])])
            
            comment_table = Table(comment_data, colWidths=[7*inch])
            comment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fffbeb')),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(comment_table)
        
        elements.append(Spacer(1, 0.4*inch))
        
        # ==================== FOOTER ====================
        footer_line = Table([['']], colWidths=[7*inch])
        footer_line.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 1, self.colors.GRAY_200),
        ]))
        elements.append(footer_line)
        elements.append(Spacer(1, 0.15*inch))
        
        footer_text = f"""
        <para align=center>
        <i>Báo cáo được tạo tự động bởi hệ thống EmoGarden</i><br/>
        <i>Ngày tạo: {datetime.now().strftime('%d/%m/%Y lúc %H:%M')}</i><br/>
        <i>📧 support@emogarden.com | 📞 Hotline: 1900-xxxx | 🌐 www.emogarden.com</i>
        </para>
        """
        footer = Paragraph(footer_text, self.styles['Footer'])
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _generate_auto_comments(self, progress_data: Dict) -> List[str]:
        """Tạo nhận xét tự động dựa trên dữ liệu"""
        comments = []
        
        total_sessions = progress_data.get('total_sessions', 0)
        avg_score = progress_data.get('avg_score', 0)
        
        # Nhận xét về tần suất
        if total_sessions >= 20:
            comments.append(
                "Bé rất chăm chỉ và đều đặn trong việc học tập. "
                "Đây là một thói quen tuyệt vời cần duy trì!"
            )
        elif total_sessions >= 10:
            comments.append(
                "Bé có tần suất học tập tốt. "
                "Hãy tiếp tục duy trì và cố gắng tăng thêm nhé!"
            )
        else:
            comments.append(
                "Khuyến khích bé dành nhiều thời gian hơn để học tập "
                "và rèn luyện kỹ năng mỗi ngày."
            )
        
        # Nhận xét về điểm số
        if avg_score >= 8:
            comments.append(
                "Kết quả học tập xuất sắc! Bé đang tiến bộ rất tốt "
                "và nắm vững kiến thức."
            )
        elif avg_score >= 6:
            comments.append(
                "Kết quả khá tốt. Bé đang trên đà phát triển "
                "và cải thiện từng ngày."
            )
        elif avg_score >= 4:
            comments.append(
                "Bé đang làm quen với các bài học. "
                "Cần thêm thời gian để nắm vững kiến thức."
            )
        else:
            comments.append(
                "Bé cần được hỗ trợ và khuyến khích nhiều hơn trong quá trình học tập.")
        
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