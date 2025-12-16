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
import re
import unicodedata
from urllib.parse import quote
from dotenv import load_dotenv
from sqlalchemy import text

from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.repository.report_repo import ReportRepository
from app.domain.analytics.report import Report, ReportTypeEnum
from app.services.analytics.report_generator_service import ReportGeneratorService
from app.database import get_db

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
    
    def generate_and_send_report(
        self,
        child_user_id: UUID,
        period: str = "weekly"
    ) -> Dict[str, any]:
        """Generate and send AI-powered report"""
        try:
            print(f"\n{'='*60}")
            print(f"📊 GENERATING AI-POWERED REPORT")
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
            
            # 2. Lấy dữ liệu tiến độ từ DATABASE
            progress_data = self._get_progress_data_from_db(child_user_id, period)
            print(f"✅ Progress data loaded: {progress_data['total_sessions']} sessions")
            
            # 3. Tạo summary text
            summary = self._generate_summary(progress_data)
            print(f"✅ Summary generated")
            
            # 4. Lưu vào database
            report_entity = None
            if self.report_repo:
                try:
                    report_entity = self._save_report_to_db(
                        child_user_id=child_user_id,
                        report_type=period,
                        summary=summary,
                        data=progress_data
                    )
                    print(f"✅ Report saved to database: {report_entity.report_id}")
                except Exception as db_error:
                    print(f"❌ Database save failed: {db_error}")
            
            # 5. Tạo PDF
            print(f"🤖 Generating AI-powered PDF...")
            pdf_buffer = self.report_generator.generate_progress_report(
                child_data,
                progress_data
            )
            
            # 6. Gửi email
            period_text = "tuần" if period == "weekly" else "tháng"
            print(f"📧 Sending email to {child_data['email']}...")
            email_result = self._send_report_email(
                to_email=child_data['email'],
                child_name=child_data['name'],
                report_pdf=pdf_buffer,
                period=period_text
            )
            
            # 7. Return kết quả
            if email_result['status'] == 'success':
                return {
                    "status": "success",
                    "message": f"Đã gửi báo cáo đến {child_data['email']}",
                    "report_id": str(report_entity.report_id) if report_entity else None,
                    "saved_to_db": report_entity is not None
                }
            else:
                return email_result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "failed",
                "message": f"Lỗi: {str(e)}"
            }
    
    def _get_progress_data_from_db(self, user_id: UUID, period: str) -> Dict:
        try:
            db = next(get_db())
            
            # Xác định time range
            end_date = datetime.now()
            if period == "weekly":
                start_date = end_date - timedelta(days=7)
            elif period == "monthly":
                start_date = end_date - timedelta(days=30)
            else:  # daily
                start_date = end_date - timedelta(days=1)
            
            print(f"\n📅 Date Range: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
            print(f"🔍 Querying for user_id: {str(user_id)}")
            
            overview_query = text("""
                SELECT 
                    COUNT(DISTINCT s.session_id) as total_sessions,
                    COALESCE(SUM(DATEDIFF(SECOND, s.start_time, s.end_time) / 60.0), 0) as total_playtime,
                    COALESCE(AVG(CAST(s.score AS FLOAT)), 0) as avg_score,
                    COUNT(DISTINCT s.game_id) as total_games
                FROM sessions s
                WHERE s.user_id = :user_id
                AND s.start_time >= :start_date
                AND s.end_time IS NOT NULL
            """)
            
            overview_result = db.execute(
                overview_query,
                {"user_id": str(user_id), "start_date": start_date}
            ).fetchone()
            
            print(f"✅ Overview query executed successfully")
            print(f"   Total sessions: {overview_result.total_sessions}")
            print(f"   Total playtime: {overview_result.total_playtime:.1f} mins")
            print(f"   Avg score: {overview_result.avg_score:.2f}")
            
            games_query = text("""
                SELECT 
                    g.name as game_name,
                    COUNT(DISTINCT s.session_id) as sessions,
                    COALESCE(AVG(CAST(s.score AS FLOAT)), 0) as avg_score,
                    MAX(s.level) as max_level,
                    COALESCE(MAX(cp.accuracy), 0) as accuracy
                FROM sessions s
                JOIN games g ON s.game_id = g.game_id
                LEFT JOIN child_progress cp ON cp.child_id = s.user_id 
                    AND cp.game_id = s.game_id
                WHERE s.user_id = :user_id
                AND s.start_time >= :start_date
                AND s.end_time IS NOT NULL
                GROUP BY g.game_id, g.name
                ORDER BY sessions DESC, avg_score DESC
            """)
            
            games_results = db.execute(
                games_query,
                {"user_id": str(user_id), "start_date": start_date}
            ).fetchall()
            
            games_stats = [
                {
                    "game_name": row.game_name,
                    "sessions": row.sessions,
                    "avg_score": round(float(row.avg_score), 2),
                    "level": row.max_level,
                    "accuracy": round(float(row.accuracy or 0), 2)
                }
                for row in games_results
            ]
            
            print(f"✅ Games query executed: {len(games_stats)} games found")
            if games_stats:
                print(f"   Top game: {games_stats[0]['game_name']} ({games_stats[0]['sessions']} sessions)")
            
            emotion_query = text("""
                SELECT 
                    gc.emotion,
                    SUM(CASE WHEN sq.is_correct = 1 THEN 1 ELSE 0 END) as correct,
                    SUM(CASE WHEN sq.is_correct = 0 THEN 1 ELSE 0 END) as incorrect
                FROM session_questions sq
                JOIN questions q ON sq.question_id = q.question_id
                JOIN game_content gc ON q.content_id = gc.content_id
                JOIN sessions s ON sq.session_id = s.session_id
                WHERE s.user_id = :user_id
                AND sq.timestamp >= :start_date
                AND gc.emotion IS NOT NULL
                GROUP BY gc.emotion
            """)
            
            emotion_results = db.execute(
                emotion_query,
                {"user_id": str(user_id), "start_date": start_date}
            ).fetchall()
            
            emotion_stats = {}
            for row in emotion_results:
                total = row.correct + row.incorrect
                accuracy = (row.correct / total * 100) if total > 0 else 0
                emotion_stats[row.emotion] = {
                    "correct": row.correct,
                    "incorrect": row.incorrect,
                    "accuracy": round(accuracy, 2)
                }
            
            print(f"✅ Emotions query executed: {len(emotion_stats)} emotions tracked")
            
            achievements = []
            
            if overview_result.total_sessions >= 20:
                achievements.append(f"Hoàn thành {overview_result.total_sessions} phiên học tập")
            elif overview_result.total_sessions >= 10:
                achievements.append(f"Hoàn thành {overview_result.total_sessions} phiên học tập")
            elif overview_result.total_sessions >= 5:
                achievements.append(f"Hoàn thành {overview_result.total_sessions} phiên học tập")
            
            if overview_result.avg_score >= 8:
                achievements.append("Đạt điểm trung bình xuất sắc (≥8/10)")
            elif overview_result.avg_score >= 7:
                achievements.append("Đạt điểm trung bình tốt (≥7/10)")
            elif overview_result.avg_score >= 6:
                achievements.append("Đạt điểm trung bình khá (≥6/10)")
            
            if games_stats:
                if games_stats[0]['sessions'] >= 10:
                    achievements.append(f"Chơi game \"{games_stats[0]['game_name']}\" {games_stats[0]['sessions']} lần")
                elif games_stats[0]['sessions'] >= 5:
                    achievements.append(f"Chơi game \"{games_stats[0]['game_name']}\" {games_stats[0]['sessions']} lần")
            
            if emotion_stats:
                high_accuracy_emotions = [
                    e for e, s in emotion_stats.items() 
                    if s['accuracy'] >= 85
                ]
                if high_accuracy_emotions:
                    achievements.append(f"Nhận diện chính xác cảm xúc {', '.join(high_accuracy_emotions)}")
                
                medium_accuracy_emotions = [
                    e for e, s in emotion_stats.items() 
                    if 70 <= s['accuracy'] < 85
                ]
                if medium_accuracy_emotions:
                    achievements.append(f"Đang tiến bộ trong nhận diện {', '.join(medium_accuracy_emotions)}")
            
            if overview_result.total_playtime >= 120:  # 2 hours
                achievements.append(f"Dành {int(overview_result.total_playtime)} phút học tập")
            
            if not achievements:
                achievements.append("Bắt đầu hành trình học tập với EmoGarden")
            
            print(f"✅ Achievements generated: {len(achievements)} items")
            
            # ==================== BUILD RESULT ====================
            result = {
                'period': period,
                'start_date': start_date.strftime('%d/%m/%Y'),
                'end_date': end_date.strftime('%d/%m/%Y'),
                'total_sessions': overview_result.total_sessions or 0,
                'total_playtime': int(overview_result.total_playtime or 0),
                'avg_score': round(float(overview_result.avg_score or 0), 2),
                'total_games': overview_result.total_games or 0,
                'games_stats': games_stats,
                'emotion_stats': emotion_stats,
                'achievements': achievements
            }
            
            print(f"\n✅ Final data prepared successfully")
            print(f"📊 Summary: {result['total_sessions']} sessions, {result['total_games']} games, {len(emotion_stats)} emotions")
            
            return result
            
        except Exception as e:
            print(f"❌ Error querying database: {e}")
            import traceback
            traceback.print_exc()
            
            # Return empty data nếu query fail
            return {
                'period': period,
                'start_date': (datetime.now() - timedelta(days=7 if period == 'weekly' else 30)).strftime('%d/%m/%Y'),
                'end_date': datetime.now().strftime('%d/%m/%Y'),
                'total_sessions': 0,
                'total_playtime': 0,
                'avg_score': 0,
                'total_games': 0,
                'games_stats': [],
                'emotion_stats': {},
                'achievements': ["Chưa có dữ liệu cho kỳ báo cáo này"]
            }
        finally:
            db.close()
    
    def _save_report_to_db(
        self,
        child_user_id: UUID,
        report_type: str,
        summary: str,
        data: Dict
    ) -> Report:
        """Save report to database"""
        if not self.report_repo:
            raise Exception("ReportRepository not initialized")
        
        try:
            report_type_enum = ReportTypeEnum[report_type]
        except KeyError:
            raise ValueError(f"Invalid report_type: {report_type}")
        
        report = Report(
            report_id=uuid4(),
            child_id=child_user_id,
            report_type=report_type_enum,
            generated_at=datetime.now(),
            summary=summary,
            data=json.dumps(data, ensure_ascii=False)
        )
        
        saved_report = self.report_repo.save(report)
        return saved_report
    
    def _generate_summary(self, progress_data: Dict) -> str:
        """Generate summary text"""
        total_sessions = progress_data.get('total_sessions', 0)
        avg_score = progress_data.get('avg_score', 0)
        achievements_count = len(progress_data.get('achievements', []))
        
        if total_sessions == 0:
            return "Bé chưa có hoạt động nào trong kỳ này."
        
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
    def _sanitize_filename(self, filename: str) -> str:
        name = (filename or '').strip()
        name = unicodedata.normalize('NFKD', name)
        name = ''.join(ch for ch in name if not unicodedata.combining(ch))
        name = re.sub(r'[^A-Za-z0-9._-]+', '_', name)
        name = re.sub(r'_+', '_', name).strip('_')
        return name or 'BaoCao'

    def _send_report_email(
        self,
        to_email: str,
        child_name: str,
        report_pdf: BytesIO,
        period: str = "tuần"
    ) -> Dict[str, any]:
        """Send email with generated PDF"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = f"🤖 Báo cáo tiến độ học tập {period} - {child_name}"
            
            html_body = self._create_report_email_html(child_name, period)
            text_body = f"""
Xin chào Quý Phụ huynh,

Chúng tôi rất vui được gửi đến Quý vị báo cáo tiến độ học tập {period} của bé {child_name}.

Báo cáo này được tạo tự động bởi với thiết kế đẹp mắt và phân tích chi tiết.

Vui lòng xem file PDF đính kèm.

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
            
            filename_utf8 = f"BaoCao_{child_name}_{period}.pdf"
            filename_ascii = self._sanitize_filename(filename_utf8)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename="{filename_ascii}"; filename*=UTF-8\'\'{quote(filename_utf8)}'
            )
            msg.attach(attachment)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}")
            return {
                "status": "success",
                "message": f"Đã gửi báo cáo đến {to_email}"
            }
            
        except Exception as e:
            print(f"❌ Email error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "failed",
                "message": f"Lỗi gửi email: {str(e)}"
            }
    
    def _create_report_email_html(self, child_name: str, period: str) -> str:
        """Create email HTML"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
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
                .badge {{
                    background: #10b981;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 12px;
                    display: inline-block;
                }}
                .highlight {{
                    background: white;
                    padding: 15px;
                    border-left: 4px solid #667eea;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <span class="badge">🤖 AI-Powered</span>
                <h1>🌟 EmoGarden</h1>
                <h2>Báo cáo tiến độ học tập</h2>
            </div>
            <div class="content">
                <p>Kính gửi Quý Phụ huynh,</p>
                <p>Chúng tôi rất vui được gửi đến Quý vị báo cáo tiến độ học tập {period} của bé <strong>{child_name}</strong>.</p>
                <div class="highlight">
                    <p>🤖 Báo cáo này được tạo tự động bởi <strong>AI</strong> với:</p>
                    <ul>
                        <li>✅ Thiết kế chuyên nghiệp</li>
                        <li>📊 Biểu đồ trực quan</li>
                        <li>📈 Phân tích chi tiết</li>
                        <li>💡 Khuyến nghị cá nhân hóa</li>
                    </ul>
                </div>
                <p>📎 Vui lòng xem file PDF đính kèm để biết chi tiết.</p>
                <p>Trân trọng,<br><strong>Đội ngũ EmoGarden</strong></p>
            </div>
        </body>
        </html>
        """
    
    def _get_child_info(self, user_id: UUID) -> Optional[Dict]:
        """Get child information"""
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
    
    def send_test_email(self, email: str) -> Dict:
        """Test email configuration"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = email
            msg['Subject'] = "Test Email - EmoGarden Report System"
            
            body = "This is a test email from EmoGarden Report System. If you receive this, the email configuration is working correctly."
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
            
            return {
                "status": "success",
                "message": f"Test email sent successfully to {email}"
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Email test failed: {str(e)}"
            }