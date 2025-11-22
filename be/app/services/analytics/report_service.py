# be/app/services/reports/report_service.py (INTEGRATED EMAIL)
from uuid import UUID
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.services.analytics.report_generator_service import ReportGeneratorService

load_dotenv()

class ReportService:
    def __init__(
        self,
        user_repo: UsersRepository,
        child_repo: ChildRepository
    ):
        self.user_repo = user_repo
        self.child_repo = child_repo
        self.report_generator = ReportGeneratorService()
        
        # Email config (giống forgot_password)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = os.getenv("EMAIL_USER")
        self.email_pass = os.getenv("EMAIL_PASS")
        
        if not self.email_user or not self.email_pass:
            print("⚠️ Warning: EMAIL_USER và EMAIL_PASS chưa được cấu hình trong .env")
    
    # ==================== MAIN METHOD ====================
    def generate_and_send_report(
        self,
        child_user_id: UUID,
        period: str = "weekly"  # weekly, monthly
    ) -> Dict[str, any]:
        """
        Tạo và gửi báo cáo tiến độ
        
        Args:
            child_user_id: ID của trẻ
            period: Chu kỳ báo cáo (weekly/monthly)
        """
        try:
            # 1. Lấy thông tin trẻ
            child_data = self._get_child_info(child_user_id)
            if not child_data:
                return {
                    "status": "failed",
                    "message": "Không tìm thấy thông tin trẻ"
                }
            
            # 2. Lấy dữ liệu tiến độ
            progress_data = self._get_progress_data(child_user_id, period)
            
            # 3. Tạo PDF
            print(f"📊 Generating PDF report for {child_data['name']}...")
            pdf_buffer = self.report_generator.generate_progress_report(
                child_data,
                progress_data
            )
            print(f"✅ PDF generated successfully")
            
            # 4. Gửi email (✅ LOGIC GIỐNG FORGOT_PASSWORD)
            period_text = "tuần" if period == "weekly" else "tháng"
            email_result = self._send_report_email(
                to_email=child_data['email'],
                child_name=child_data['name'],
                report_pdf=pdf_buffer,
                period=period_text
            )
            
            if email_result['status'] == 'success':
                # Lưu lịch sử gửi report (tùy chọn)
                self._save_report_history(child_user_id, period)
                print(f"✅ Report sent successfully to {child_data['email']}")
            
            return email_result
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "failed",
                "message": f"Lỗi khi tạo báo cáo: {str(e)}"
            }
    
    # ==================== EMAIL LOGIC (GIỐNG FORGOT_PASSWORD) ====================
    def _send_report_email(
        self,
        to_email: str,
        child_name: str,
        report_pdf: BytesIO,
        period: str = "tuần"
    ) -> Dict[str, any]:
        """
        Gửi báo cáo tiến độ qua email
        LOGIC GIỐNG HỆT forgot_password trong users_service
        
        Args:
            to_email: Email người nhận
            child_name: Tên trẻ
            report_pdf: File PDF (BytesIO)
            period: Chu kỳ báo cáo (tuần/tháng)
            
        Returns:
            Dict với status và message
        """
        try:
            # Tạo email message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = f"📊 Báo cáo tiến độ học tập {period} - {child_name}"
            
            # Body HTML
            html_body = self._create_report_email_html(child_name, period)
            
            # Text fallback
            text_body = f"""
Xin chào Quý Phụ huynh,

Chúng tôi rất vui được gửi đến Quý vị báo cáo tiến độ học tập {period} của bé {child_name}.

Vui lòng xem file PDF đính kèm để biết chi tiết.

Trân trọng,
Đội ngũ EmoGarden
            """
            
            # Attach both
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)
            
            # Attach PDF
            report_pdf.seek(0)  # Reset pointer
            attachment = MIMEBase('application', 'pdf')
            attachment.set_payload(report_pdf.read())
            encoders.encode_base64(attachment)
            
            filename = f"BaoCao_{child_name}_{period}.pdf"
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            msg.attach(attachment)
            
            # Gửi email (✅ GIỐNG FORGOT_PASSWORD)
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
            
            print(f"✅ [EMAIL] Report sent to {to_email} successfully")
            return {
                "status": "success",
                "message": f"Đã gửi báo cáo đến {to_email}"
            }
            
        except Exception as e:
            print(f"❌ [EMAIL ERROR] Failed to send report: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "failed",
                "message": f"Lỗi khi gửi email: {str(e)}"
            }
    
    def _create_report_email_html(self, child_name: str, period: str) -> str:
        """Tạo nội dung HTML cho email - GIỐNG STYLE FORGOT_PASSWORD"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .highlight {{
                    background: white;
                    padding: 15px;
                    border-left: 4px solid #667eea;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
                }}
                .emoji {{
                    font-size: 24px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌟 EmoGarden</h1>
                <h2>Báo cáo tiến độ học tập</h2>
            </div>
            
            <div class="content">
                <p>Kính gửi Quý Phụ huynh,</p>
                
                <p>Chúng tôi rất vui được gửi đến Quý vị <strong>báo cáo tiến độ học tập {period}</strong> 
                của bé <strong>{child_name}</strong>.</p>
                
                <div class="highlight">
                    <p class="emoji">📊</p>
                    <p><strong>Nội dung báo cáo bao gồm:</strong></p>
                    <ul>
                        <li>Tổng quan hoạt động học tập</li>
                        <li>Chi tiết từng trò chơi và mức độ hoàn thành</li>
                        <li>Thống kê nhận diện cảm xúc</li>
                        <li>Thành tựu đã đạt được</li>
                        <li>Nhận xét và khuyến nghị từ hệ thống</li>
                    </ul>
                </div>
                
                <p>📎 Vui lòng xem file PDF đính kèm để biết chi tiết.</p>
                
                <div class="highlight">
                    <p class="emoji">💡</p>
                    <p><strong>Lời khuyên:</strong></p>
                    <p>Hãy dành thời gian trò chuyện với bé về những cảm xúc trong ngày. 
                    Việc chia sẻ và lắng nghe sẽ giúp bé phát triển kỹ năng cảm xúc tốt hơn.</p>
                </div>
                
                <p>Nếu Quý vị có bất kỳ thắc mắc nào, vui lòng liên hệ với chúng tôi qua:</p>
                <ul>
                    <li>📧 Email: support@emogarden.com</li>
                    <li>📞 Hotline: 1900-xxxx</li>
                    <li>🌐 Website: www.emogarden.com</li>
                </ul>
                
                <p>Trân trọng,<br>
                <strong>Đội ngũ EmoGarden</strong></p>
            </div>
            
            <div class="footer">
                <p>© 2025 EmoGarden - Nền tảng phát triển kỹ năng cảm xúc cho trẻ em</p>
                <p>Email này được gửi tự động, vui lòng không trả lời trực tiếp.</p>
            </div>
        </body>
        </html>
        """
    
    # ==================== HELPER METHODS ====================
    def _get_child_info(self, user_id: UUID) -> Optional[Dict]:
        """Lấy thông tin trẻ"""
        try:
            user = self.user_repo.get_user_by_id(user_id)
            if not user:
                return None
            
            child = self.child_repo.get_by_user_id(str(user_id))
            
            return {
                'user_id': str(user.user_id),
                'name': user.name,
                'username': user.username,
                'email': user.email,
                'age': child.age if child else None,
                'phone_number': child.phone_number if child else None,
                'gender': child.gender.value if child and child.gender else None
            }
        except Exception as e:
            print(f"Error getting child info: {e}")
            return None
    
    def _get_progress_data(self, user_id: UUID, period: str) -> Dict:
        """
        Lấy dữ liệu tiến độ từ database
        
        TODO: Implement logic lấy data thực từ sessions, game_history, child_progress
        Hiện tại dùng demo data
        """
        # Tính ngày bắt đầu và kết thúc
        end_date = datetime.now()
        if period == "weekly":
            start_date = end_date - timedelta(days=7)
        else:  # monthly
            start_date = end_date - timedelta(days=30)
        
        # DEMO DATA - Thay thế bằng query thực
        return {
            'period': period,
            'start_date': start_date.strftime('%d/%m/%Y'),
            'end_date': end_date.strftime('%d/%m/%Y'),
            'total_sessions': 15,
            'total_playtime': 240,
            'avg_score': 7.5,
            'games_stats': [
                {
                    'game_name': 'Nhận diện cảm xúc',
                    'sessions': 8,
                    'avg_score': 8.2,
                    'level': 3
                },
                {
                    'game_name': 'Xây dựng khuôn mặt',
                    'sessions': 5,
                    'avg_score': 7.0,
                    'level': 2
                },
                {
                    'game_name': 'Thể hiện cảm xúc',
                    'sessions': 2,
                    'avg_score': 6.5,
                    'level': 1
                }
            ],
            'emotion_stats': {
                'vui': {'correct': 45, 'incorrect': 5, 'accuracy': 90.0},
                'buồn': {'correct': 38, 'incorrect': 12, 'accuracy': 76.0},
                'giận': {'correct': 30, 'incorrect': 10, 'accuracy': 75.0},
                'sợ': {'correct': 25, 'incorrect': 15, 'accuracy': 62.5},
                'ngạc nhiên': {'correct': 35, 'incorrect': 8, 'accuracy': 81.4}
            },
            'achievements': [
                'Hoàn thành 15 phiên học tập',
                'Đạt level 3 trong game "Nhận diện cảm xúc"',
                'Nhận diện cảm xúc "vui" với độ chính xác 90%',
                'Chơi liên tục 5 ngày'
            ]
        }
    
    def _save_report_history(self, user_id: UUID, period: str):
        """Lưu lịch sử gửi báo cáo (tùy chọn)"""
        # TODO: Implement nếu cần track history
        pass
    
    # ==================== TEST METHOD ====================
    def send_test_email(self, to_email: str) -> Dict[str, any]:
        """Test cấu hình email - GIỐNG FORGOT_PASSWORD"""
        try:
            msg = MIMEText("Đây là email test từ EmoGarden Report System. Email hoạt động bình thường.")
            msg['Subject'] = "Test Email - EmoGarden Reports"
            msg['From'] = self.email_user
            msg['To'] = to_email
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
            
            print(f"✅ Test email sent to {to_email}")
            return {"status": "success", "message": "Email test đã được gửi"}
            
        except Exception as e:
            print(f"❌ Test email failed: {e}")
            return {"status": "failed", "message": str(e)}