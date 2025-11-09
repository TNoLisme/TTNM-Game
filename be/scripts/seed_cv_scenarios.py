"""
Script để seed 6 tình huống Game CV vào database
Chạy: python scripts/seed_cv_scenarios.py
"""

import sys
import os
from pathlib import Path

# Thêm thư mục be vào path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL_SQLSERVER")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL_SQLSERVER not found in .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

try:
    # Kiểm tra xem GameCV đã tồn tại chưa
    result = db.execute(text("SELECT game_id FROM games WHERE game_type = 'GameCV'"))
    game_row = result.fetchone()
    
    if game_row:
        game_id = str(game_row[0])
        print(f"Found existing GameCV with ID: {game_id}")
    else:
        # Tạo GameCV nếu chưa có
        new_game_id = str(uuid4())
        db.execute(text("""
            INSERT INTO games (game_id, game_type, name, level, difficulty_level, max_errors, level_threshold, time_limit)
            VALUES (:game_id, 'GameCV', 'Game CV - Nhận diện cảm xúc', 1, 1, 3, 5, 300)
        """), {"game_id": new_game_id})
        db.commit()
        game_id = new_game_id
        print(f"Created new GameCV with ID: {game_id}")
    
    # Xóa scenarios cũ nếu có (để tránh duplicate)
    db.execute(text("""
        DELETE FROM game_content 
        WHERE game_id = :game_id
    """), {"game_id": game_id})
    db.commit()
    print("Cleared old scenarios")
    
    # 6 Tình huống với đầy đủ thông tin - sử dụng ảnh có sẵn
    scenarios = [
        {
            'title': 'Quà bất ngờ',
            'description': 'Con mở hộp quà bất ngờ và thấy món con thích.',
            'target_emotion': 'vui',
            'image_path': '/assets/images/happy/situation_happy.png'
        },
        {
            'title': 'Bất ngờ lớn',
            'description': 'Một quả bóng bỗng nổ to bên cạnh con.',
            'target_emotion': 'ngạc nhiên',
            'image_path': '/assets/images/surprise/situation_surprise.png'
        },
        {
            'title': 'Món đồ yêu thích bị vỡ',
            'description': 'Đồ chơi con thích bị rơi và vỡ.',
            'target_emotion': 'buồn',
            'image_path': '/assets/images/sad/situation_sad.png'
        },
        {
            'title': 'Bạn lấy đồ',
            'description': 'Bạn cầm mất món đồ con đang chơi.',
            'target_emotion': 'tức giận',
            'image_path': '/assets/images/angry/situation_angry.png'
        },
        {
            'title': 'Tiếng sấm đêm',
            'description': 'Tiếng sấm rất to lúc trời tối.',
            'target_emotion': 'sợ hãi',
            'image_path': '/assets/images/fear/situation_fear.png'
        },
        {
            'title': 'Món ăn hư',
            'description': 'Con ngửi thấy món ăn đã bị hư.',
            'target_emotion': 'ghê tởm',
            'image_path': '/assets/images/disgust/situation_disgust.png'
        }
    ]
    
    # Insert scenarios vào game_content
    for scenario in scenarios:
        content_id = str(uuid4())
        db.execute(text("""
            INSERT INTO game_content (content_id, game_id, level, content_type, media_path, question_text, correct_answer, emotion, explanation)
            VALUES (:content_id, :game_id, 1, 'image', :image_path, :title, :target_emotion, :target_emotion, :description)
        """), {
            'content_id': content_id,
            'game_id': game_id,
            'image_path': scenario['image_path'],
            'title': scenario['title'],
            'target_emotion': scenario['target_emotion'],
            'description': scenario['description']
        })
        print(f"✓ Inserted scenario: {scenario['title']} ({scenario['target_emotion']})")
    
    db.commit()
    print(f"\n✅ Successfully seeded {len(scenarios)} scenarios for Game CV!")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

