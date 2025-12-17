from fastapi import APIRouter, Depends, HTTPException, Body, Query
from app.services.users.users_service import UsersService
from app.schemas.users.user_schema import UserSchema
from app.repository.users_repo import UsersRepository
from app.repository.child_repo import ChildRepository
from app.database import get_db
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Any
from app.current_user import logout
from sqlalchemy import text
import json

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register")
async def register(user: UserSchema.ChildRequest, db=Depends(get_db)):
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    result = service.create_child(user.dict())
    if result.get("status") != "success":
        raise HTTPException(400, detail=result.get("message", "Đăng ký thất bại"))

    return {"status": "success", "message": "Đăng ký thành công", "data": {"user_id": result.get("user_id")}}


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(request: LoginRequest, db=Depends(get_db)):
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    result = service.login(request.username, request.password)
    if not result["success"]:
        raise HTTPException(400, detail=result["message"])

    return result


@router.post("/verify-otp")
async def verify_otp(request: UserSchema.VerifyOtpRequest, db=Depends(get_db)):
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    result = service.verify_otp(request.dict())
    if result.get("status") != "success":
        raise HTTPException(400, detail=result.get("message"))

    return result


@router.post("/logout")
async def api_logout():
    logout()
    return {"success": True, "message": "Đăng xuất thành công"}


@router.post("/forgot-password")
async def forgot_password(request: UserSchema.ForgotPasswordRequest, db=Depends(get_db)):
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    result = service.forgot_password(request.dict())
    if result.get("status") != "success":
        raise HTTPException(400, detail=result.get("message"))

    return result


@router.post("/reset-password")
async def reset_password(request: UserSchema.ResetPasswordRequest, db=Depends(get_db)):
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    result = service.reset_password(request.dict())
    if result.get("status") != "success":
        raise HTTPException(400, detail=result.get("message"))

    return result


@router.get("/me")
async def get_profile(user_id: UUID = Query(...), db=Depends(get_db)):
    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)
    service = UsersService(user_repo, child_repo)

    profile = service.get_current_user_info(user_id)
    if not profile:
        raise HTTPException(404, detail="User not found")

    return profile


@router.put("/me")
async def update_all_in_one(payload: dict = Body(...), db=Depends(get_db)):
    user_id_str = payload.get("user_id")
    update = payload.get("update", {})

    if not user_id_str:
        raise HTTPException(400, "Thiếu user_id")

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(400, "user_id sai định dạng")

    user_repo = UsersRepository(db)
    child_repo = ChildRepository(db)

    user = user_repo.get_by_id(user_id)
    child = child_repo.get_by_user_id(user_id)
    if not user or not child:
        raise HTTPException(404, "Không tìm thấy người dùng")

    # Cập nhật bảng users
    for field in ["name", "username", "email"]:
        if field in update and update[field] not in ["", None]:
            setattr(user, field, str(update[field]))

    # Cập nhật password (nếu có)
    if "password" in update and update["password"]:
        user.password = update["password"]

    # Cập nhật bảng children
    if "age" in update and update["age"] not in ["", None]:
        child.age = int(update["age"])
    if "gender" in update and update["gender"] in ["male", "female"]:
        child.gender = update["gender"]
    if "date_of_birth" in update and update["date_of_birth"]:
        child.date_of_birth = update["date_of_birth"]
    if "phone_number" in update and update["phone_number"]:
        child.phone_number = update["phone_number"].strip()

    user_repo.save(user)
    child_repo.save(child)
    db.commit()

    service = UsersService(user_repo, child_repo)
    return service.get_current_user_info(user_id)

@router.get("/stats/recent-games/{user_id}")
async def get_recent_games(user_id: UUID, limit: int = 4, db=Depends(get_db)):
    """Lấy danh sách game đã chơi gần đây"""
    try:
        query = text("""
            SELECT TOP(:limit)
                g.game_id,
                g.name,
                g.game_type,
                MAX(s.start_time) as last_played
            FROM sessions s
            JOIN games g ON s.game_id = g.game_id
            WHERE s.user_id = :user_id
            GROUP BY g.game_id, g.name, g.game_type
            ORDER BY last_played DESC
        """)
        
        result = db.execute(query, {"user_id": str(user_id), "limit": limit})
        games = []
        for row in result:
            games.append({
                "game_id": str(row.game_id),
                "name": row.name,
                "game_type": row.game_type,
                "last_played": row.last_played.isoformat() if row.last_played else None
            })
        
        return {"status": "success", "data": games}
    except Exception as e:
        print(f"Error in get_recent_games: {str(e)}")
        raise HTTPException(500, detail=f"Lỗi truy vấn dữ liệu: {str(e)}")
        
# Mapping cảm xúc Tiếng Việt <-> Tiếng Anh
EMOTION_MAP = {
    'happy': 'Vui vẻ',
    'sad': 'Buồn bã',
    'angry': 'Tức giận',
    'fear': 'Sợ hãi',
    'surprise': 'Ngạc nhiên',
    'disgust': 'Ghê tởm'
}

# Reverse map và variations (để handle các trường hợp viết khác nhau)
EMOTION_VARIATIONS = {
    'happy': ['happy', 'vui vẻ', 'vui ve', 'vui v?', 'vui'],
    'sad': ['sad', 'buồn bã', 'buon ba', 'bu?n bã', 'buon', 'buồn'],
    'angry': ['angry', 'tức giận', 'tuc gian', 't?c gi?n', 'tức', 'giận'],
    'fear': ['fear', 'sợ hãi', 'so hai', 's? hãi', 'sợ'],
    'surprise': ['surprise', 'ngạc nhiên', 'ngac nhien', 'ng?c nhiên', 'ngạc'],
    'disgust': ['disgust', 'ghê tởm', 'ghe tom', 'ghê t?m', 'ghê']
}

def normalize_emotion(emotion_str):
    """Chuẩn hóa tên cảm xúc về key tiếng Anh"""
    if not emotion_str:
        return None
    
    emotion_lower = emotion_str.lower().strip()
    
    # Kiểm tra từng variation
    for key, variations in EMOTION_VARIATIONS.items():
        for var in variations:
            if var.lower() in emotion_lower:
                return key
    
    return None


@router.get("/stats/emotion-accuracy/{user_id}")
async def get_emotion_accuracy_stats(user_id: UUID, db=Depends(get_db)):
    """Lấy thống kê tỉ lệ đúng của 6 cảm xúc - trả về correct/incorrect/accuracy"""
    try:
        print(f"\n=== DEBUG emotion-errors for user {user_id} ===")
        
        # Query theo cách mới - lấy correct và incorrect từ session_questions
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
            AND gc.emotion IS NOT NULL
            GROUP BY gc.emotion
        """)
        
        emotion_results = db.execute(
            emotion_query,
            {"user_id": str(user_id)}
        ).fetchall()
        
        emotion_stats = {}
        for row in emotion_results:
            total = row.correct + row.incorrect
            accuracy = (row.correct / total * 100) if total > 0 else 0
            
            # Chuẩn hóa tên emotion
            normalized = normalize_emotion(row.emotion)
            if normalized and normalized in EMOTION_MAP:
                display_name = EMOTION_MAP[normalized]
                emotion_stats[display_name] = {
                    "correct": int(row.correct),
                    "incorrect": int(row.incorrect),
                    "accuracy": round(accuracy, 1)
                }
                print(f"{display_name}: {row.correct}/{total} = {accuracy:.1f}%")
        
        # Đảm bảo có đầy đủ 6 cảm xúc
        for key, display_name in EMOTION_MAP.items():
            if display_name not in emotion_stats:
                emotion_stats[display_name] = {
                    "correct": 0,
                    "incorrect": 0,
                    "accuracy": 0.0
                }
        
        print(f"✅ Emotions query executed: {len(emotion_stats)} emotions tracked")
        print(f"Final stats: {emotion_stats}")
        
        return {"status": "success", "data": emotion_stats}
        
    except Exception as e:
        print(f"Error in get_emotion_accuracy_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return empty stats với đúng format
        empty_stats = {
            v: {"correct": 0, "incorrect": 0, "accuracy": 0.0} 
            for v in EMOTION_MAP.values()
        }
        return {"status": "success", "data": empty_stats}

@router.get("/stats/emotion-improvement/{user_id}")
async def get_emotion_improvement_stats(user_id: UUID, db=Depends(get_db)):
    """Lấy thống kê cải thiện từ child_progress"""
    try:
        print(f"\n=== DEBUG emotion-improvement for user {user_id} ===")
        
        # Query chính
        query = text("""
            SELECT 
                cp.review_emotions,
                cp.accuracy,
                cp.last_played
            FROM child_progress cp
            WHERE cp.child_id = :user_id
            AND cp.review_emotions IS NOT NULL
            AND cp.review_emotions != ''
            AND cp.review_emotions != '[]'
            AND cp.last_played >= DATEADD(day, -60, GETDATE())
            ORDER BY cp.last_played ASC
        """)
        
        result = db.execute(query, {"user_id": str(user_id)})
        
        # Thu thập accuracy theo thời gian
        emotion_timeline = {key: [] for key in EMOTION_MAP.keys()}
        
        rows_processed = 0
        for row in result:
            rows_processed += 1
            if row.review_emotions and row.accuracy is not None:
                try:
                    emotions = json.loads(row.review_emotions) if isinstance(row.review_emotions, str) else row.review_emotions
                    
                    if isinstance(emotions, list) and len(emotions) > 0:
                        if rows_processed <= 3:
                            print(f"Row {rows_processed}: accuracy={row.accuracy}, emotions={emotions}")
                        
                        for emotion_str in emotions:
                            normalized = normalize_emotion(emotion_str)
                            if normalized:
                                emotion_timeline[normalized].append(row.accuracy)
                                if rows_processed <= 3:
                                    print(f"  {emotion_str} -> {normalized}: accuracy {row.accuracy}")
                except Exception as e:
                    print(f"Error parsing row {rows_processed}: {e}")
                    continue
        
        print(f"\nProcessed {rows_processed} rows")
        print("Emotion timelines (count):")
        for key in EMOTION_MAP.keys():
            print(f"  {key}: {len(emotion_timeline[key])} records")
        
        # Tính improvement
        stats = {}
        for key, display_name in EMOTION_MAP.items():
            accuracies = emotion_timeline[key]
            
            if len(accuracies) >= 2:
                # So sánh nửa đầu (cũ) vs nửa sau (mới)
                mid = len(accuracies) // 2
                old_half = accuracies[:mid]
                new_half = accuracies[mid:]
                
                old_avg = sum(old_half) / len(old_half)
                new_avg = sum(new_half) / len(new_half)
                improvement = new_avg - old_avg
                
                stats[display_name] = round(improvement, 1)
                print(f"{display_name}: old={old_avg:.1f}%, new={new_avg:.1f}%, improvement={improvement:+.1f}%")
            else:
                stats[display_name] = 0
        
        print(f"Final stats: {stats}")
        return {"status": "success", "data": stats}
        
    except Exception as e:
        print(f"Error in get_emotion_improvement_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "success", "data": {v: 0 for v in EMOTION_MAP.values()}}


@router.get("/stats/game-play-ratio/{user_id}")
async def get_game_play_ratio(user_id: UUID, db=Depends(get_db)):
    """Lấy thống kê tỉ lệ chơi của các trò chơi"""
    try:
        print(f"\n=== DEBUG game-play-ratio for user {user_id} ===")
        
        query = text("""
            SELECT 
                g.name,
                COUNT(*) as play_count
            FROM sessions s
            JOIN games g ON s.game_id = g.game_id
            WHERE s.user_id = :user_id
            GROUP BY g.name
        """)
        
        result = db.execute(query, {"user_id": str(user_id)})
        total = 0
        game_counts = {}
        
        for row in result:
            game_counts[row.name] = row.play_count
            total += row.play_count
        
        stats = {}
        if total > 0:
            for game_name, count in game_counts.items():
                ratio = (count / total * 100)
                stats[game_name] = round(ratio, 1)
        
        print(f"Final stats: {stats}")
        return {"status": "success", "data": stats}
        
    except Exception as e:
        print(f"Error in get_game_play_ratio: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, detail=f"Lỗi truy vấn dữ liệu: {str(e)}")


@router.get("/stats/weak-emotions/{user_id}")
async def get_weak_emotions(user_id: UUID, limit: int = 3, db=Depends(get_db)):
    """Lấy top 3 cảm xúc cần rèn luyện"""
    try:
        print(f"\n=== DEBUG weak-emotions for user {user_id} ===")
        
        query = text("""
            SELECT 
                cp.review_emotions,
                cp.accuracy
            FROM child_progress cp
            WHERE cp.child_id = :user_id
            AND cp.review_emotions IS NOT NULL
            AND cp.review_emotions != ''
            AND cp.review_emotions != '[]'
            ORDER BY cp.last_played DESC
        """)
        
        result = db.execute(query, {"user_id": str(user_id)})
        
        emotion_stats = {key: {'total': 0, 'sum_accuracy': 0} for key in EMOTION_MAP.keys()}
        
        rows_processed = 0
        for row in result:
            rows_processed += 1
            if row.review_emotions:
                try:
                    emotions = json.loads(row.review_emotions) if isinstance(row.review_emotions, str) else row.review_emotions
                    
                    if isinstance(emotions, list) and len(emotions) > 0:
                        for emotion_str in emotions:
                            normalized = normalize_emotion(emotion_str)
                            if normalized:
                                emotion_stats[normalized]['total'] += 1
                                emotion_stats[normalized]['sum_accuracy'] += row.accuracy
                                if rows_processed <= 3:
                                    print(f"  {emotion_str} -> {normalized}: accuracy {row.accuracy}")
                except:
                    continue
        
        print(f"Processed {rows_processed} rows")
        
        weak_list = []
        for key, stats_data in emotion_stats.items():
            if stats_data['total'] > 0:
                avg_accuracy = stats_data['sum_accuracy'] / stats_data['total']
                error_rate = 100 - avg_accuracy
                
                # Chỉ coi là yếu nếu accuracy < 80
                if avg_accuracy < 80:
                    weak_list.append({
                        'emotion': EMOTION_MAP[key],
                        'error_rate': round(error_rate, 1),
                        'avg_accuracy': round(avg_accuracy, 1)
                    })
                    print(f"  {EMOTION_MAP[key]}: avg={avg_accuracy:.1f}%, error={error_rate:.1f}%")
        
        # Sắp xếp theo error_rate giảm dần
        weak_list.sort(key=lambda x: x['error_rate'], reverse=True)
        
        emotions = [{"emotion": item['emotion'], "error_rate": item['error_rate']} 
                   for item in weak_list[:limit]]
        
        print(f"Final weak emotions: {emotions}")
        return {"status": "success", "data": emotions}
        
    except Exception as e:
        print(f"Error in get_weak_emotions: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "success", "data": []}