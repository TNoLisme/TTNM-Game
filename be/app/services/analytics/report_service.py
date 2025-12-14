from uuid import UUID, uuid4
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import json
from dotenv import load_dotenv

from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.repository.report_repo import ReportRepository
from app.domain.analytics.report import Report, ReportTypeEnum  # ← IMPORT ReportTypeEnum
from app.services.analytics.report_generator_service import ReportGeneratorService

load_dotenv()

class ReportService:
    def __init__(
        self,
        user_repo: UsersRepository,
        child_repo: ChildRepository,
        report_repo: ReportRepository
    ):
        self.user_repo = user_repo
        self.child_repo = child_repo
        self.report_repo = report_repo 
        self.report_generator = ReportGeneratorService()
        
        # Email config
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = os.getenv("EMAIL_USER")
        self.email_pass = os.getenv("EMAIL_PASS")
        
        if not self.email_user or not self.email_pass:
            print("⚠️ Warning: EMAIL_USER và EMAIL_PASS chưa được cấu hình trong .env")
    
    # ==================== MAIN METHOD (UPDATED) ====================
    # Thay thế method generate_and_send_report trong report_service.py

    def generate_and_send_report(
        self,
        child_user_id: UUID,
        period: str = "weekly"
    ) -> Dict[str, any]:
        try:
            print(f"\n{'='*60}")
            print(f"📊 GENERATING REPORT")
            print(f"   Child User ID: {child_user_id}")
            print(f"   Period: {period}")
            print(f"{'='*60}\n")
            
            # 1. Lấy thông tin trẻ
            child_data = self._get_child_info(child_user_id)
            if not child_data:
                return {
                    "status": "failed",
                    "message": "Không tìm thấy thông tin trẻ"
                }
            
            print(f"✅ Child info loaded: {child_data['name']} ({child_data['email']})")
            
            # 2. Lấy dữ liệu tiến độ
            progress_data = self._get_progress_data(child_user_id, period)
            print(f"✅ Progress data loaded: {progress_data['total_sessions']} sessions")
            
            # 3. Tạo summary text
            summary = self._generate_summary(progress_data)
            print(f"✅ Summary generated: {summary}")
            
            # 4. Lưu vào database
            report_entity = None
            if self.report_repo:
                try:
                    print(f"💾 Saving report to database...")
                    report_entity = self._save_report_to_db(
                        child_user_id=child_user_id,
                        report_type=period,
                        summary=summary,
                        data=progress_data
                    )
                    print(f"✅ REPORT SAVED TO DATABASE!")
                    print(f"   Report ID: {report_entity.report_id}")
                    print(f"   Report Type: {report_entity.report_type}")
                except Exception as db_error:
                    print(f"❌ DATABASE SAVE FAILED: {db_error}")
                    import traceback
                    traceback.print_exc()
            
            # 5. Tạo PDF - 🔥 HANDLE TUPLE RETURN
            print(f"📄 Generating PDF report...")
            pdf_result = self.report_generator.generate_progress_report(
                child_data,
                progress_data
            )
            
            # 🔥 FIX: Unpack tuple
            if isinstance(pdf_result, tuple):
                pdf_buffer, pdf_filename = pdf_result
                print(f"✅ PDF generated: {pdf_filename}")
            else:
                # Fallback nếu chỉ return BytesIO
                pdf_buffer = pdf_result
                pdf_filename = f"Report_{period}_{child_data['name']}.pdf"
                print(f"✅ PDF generated (legacy format)")
            
            # 6. Gửi email
            period_text = "tuần" if period == "weekly" else "tháng"
            print(f"📧 Sending email to {child_data['email']}...")
            email_result = self._send_report_email(
                to_email=child_data['email'],
                child_name=child_data['name'],
                report_pdf=pdf_buffer,  # ✅ Đã là BytesIO
                period=period_text
            )
            
            # 7. Return kết quả
            if email_result['status'] == 'success':
                print(f"✅ Report sent successfully to {child_data['email']}")
                return {
                    "status": "success",
                    "message": f"Đã gửi báo cáo đến {child_data['email']}",
                    "report_id": str(report_entity.report_id) if report_entity else None,
                    "saved_to_db": report_entity is not None
                }
            else:
                return email_result
            
        except Exception as e:
            print(f"❌ ERROR generating report: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "failed",
                "message": f"Lỗi khi tạo báo cáo: {str(e)}"
            }
    
    # ✅ FIXED METHOD: CONVERT STRING → ENUM
    def _save_report_to_db(
        self,
        child_user_id: UUID,
        report_type: str,  # ← Nhận string "weekly" hoặc "monthly"
        summary: str,
        data: Dict
    ) -> Report:
        if not self.report_repo:
            raise Exception("ReportRepository not initialized - cannot save to database")
        
        try:
            report_type_enum = ReportTypeEnum[report_type]  # "weekly" → ReportTypeEnum.weekly
        except KeyError:
            raise ValueError(f"Invalid report_type: {report_type}. Must be 'daily', 'weekly', or 'monthly'")
        
        # Tạo Report domain entity
        report = Report(
            report_id=uuid4(),
            child_id=child_user_id,
            report_type=report_type_enum,  # ← Truyền Enum thay vì string
            generated_at=datetime.now(),
            summary=summary,
            data=json.dumps(data, ensure_ascii=False)  # Convert dict → JSON string
        )
        
        print(f"📝 Creating report entity:")
        print(f"   - report_id: {report.report_id}")
        print(f"   - child_id: {report.child_id}")
        print(f"   - report_type: {report.report_type} (Enum)")
        print(f"   - summary: {report.summary}")
        
        # Lưu vào database qua repository
        saved_report = self.report_repo.save(report)
        
        print(f"💾 Report saved to database successfully!")
        print(f"   - Saved report_id: {saved_report.report_id}")
        
        return saved_report
    
    # ✅ NEW METHOD: TẠO SUMMARY TEXT
    def _generate_summary(self, progress_data: Dict) -> str:
        """Tạo summary text từ progress data"""
        total_sessions = progress_data.get('total_sessions', 0)
        avg_score = progress_data.get('avg_score', 0)
        achievements_count = len(progress_data.get('achievements', []))
        
        if total_sessions == 0:
            return "Bé chưa có hoạt động nào trong kỳ này."
        
        # Logic tạo summary dựa trên data
        if avg_score >= 8:
            progress_text = "tiến bộ xuất sắc"
        elif avg_score >= 7:
            progress_text = "tiến bộ tốt"
        elif avg_score >= 6:
            progress_text = "tiến bộ khá"
        else:
            progress_text = "cần cố gắng thêm"
        
        summary = f"Bé đã hoàn thành {total_sessions} phiên học, {progress_text}!"
        
        if achievements_count > 0:
            summary += f" Đạt được {achievements_count} thành tựu mới."
        
        return summary
    
    # ==================== EMAIL LOGIC ====================
    def _send_report_email(
        self,
        to_email: str,
        child_name: str,
        report_pdf: BytesIO,
        period: str = "tuần"
    ) -> Dict[str, any]:
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = f"📊 Báo cáo tiến độ học tập {period} - {child_name}"
            
            html_body = self._create_report_email_html(child_name, period)
            text_body = f"""
Xin chào Quý Phụ huynh,

Chúng tôi rất vui được gửi đến Quý vị báo cáo tiến độ học tập {period} của bé {child_name}.

Vui lòng xem file PDF đính kèm để biết chi tiết.

Trân trọng,
Đội ngũ EmoGarden
            """
            
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)
            
            # Attach PDF
            report_pdf.seek(0)
            attachment = MIMEBase('application', 'pdf')
            attachment.set_payload(report_pdf.read())
            encoders.encode_base64(attachment)
            
            filename = f"BaoCao_{child_name}_{period}.pdf"
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            msg.attach(attachment)
            
            # Gửi email
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
        """Tạo HTML email"""
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
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
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
                <p>Chúng tôi rất vui được gửi đến Quý vị báo cáo tiến độ học tập {period} của bé <strong>{child_name}</strong>.</p>
                <div class="highlight">
                    <p>📎 Vui lòng xem file PDF đính kèm để biết chi tiết.</p>
                </div>
                <p>Trân trọng,<br><strong>Đội ngũ EmoGarden</strong></p>
            </div>
            <div class="footer">
                <p>© 2025 EmoGarden</p>
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
        """Lấy dữ liệu tiến độ - DEMO DATA"""
        end_date = datetime.now()
        if period == "weekly":
            start_date = end_date - timedelta(days=7)
        else:
            start_date = end_date - timedelta(days=30)
        
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
                }
            ],
            'emotion_stats': {
                'vui': {'correct': 45, 'incorrect': 5, 'accuracy': 90.0}
            },
            'achievements': [
                'Hoàn thành 15 phiên học tập',
                'Đạt level 3 trong game "Nhận diện cảm xúc"'
            ]
        }
    
    # ==================== TEST METHOD ====================
    def send_test_email(self, to_email: str) -> Dict[str, any]:
        """Test email"""
        try:
            msg = MIMEText("Test email từ EmoGarden")
            msg['Subject'] = "Test Email - EmoGarden Reports"
            msg['From'] = self.email_user
            msg['To'] = to_email
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
            
            return {"status": "success", "message": "Email test đã được gửi"}
        except Exception as e:
            return {"status": "failed", "message": str(e)}