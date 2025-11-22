"""seed game cv scenarios

Revision ID: seed_cv_scenarios
Revises: ac7ec224898e
Create Date: 2025-01-XX XX:XX:XX
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mssql import NVARCHAR, UNIQUEIDENTIFIER as mssqlUUID

# revision identifiers, used by Alembic.
revision: str = 'seed_cv_scenarios'
down_revision: Union[str, Sequence[str], None] = 'ac7ec224898e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Seed 6 scenarios for Game CV."""
    # Lấy game_id của GameCV (hoặc tạo mới nếu chưa có)
    connection = op.get_bind()
    
    # Kiểm tra xem GameCV đã tồn tại chưa
    result = connection.execute(sa.text("""
        SELECT game_id FROM games WHERE game_type = 'GameCV'
    """))
    game_row = result.fetchone()
    
    if game_row:
        game_id = str(game_row[0])
    else:
        # Tạo GameCV nếu chưa có
        connection.execute(sa.text("""
            INSERT INTO games (game_id, game_type, name, level, difficulty_level, max_errors, level_threshold, time_limit)
            VALUES (NEWID(), 'GameCV', 'Game CV - Nhận diện cảm xúc', 1, 1, 3, 5, 300)
        """))
        result = connection.execute(sa.text("""
            SELECT game_id FROM games WHERE game_type = 'GameCV'
        """))
        game_id = str(result.fetchone()[0])
    
    # 6 Tình huống với đầy đủ thông tin
    scenarios = [
        {
            'title': 'Quà bất ngờ',
            'description': 'Con mở hộp quà bất ngờ và thấy món con thích.',
            'target_emotion': 'vui',
            'instruction': 'Con thử cười tự nhiên nhé.',
            'hint': 'Hãy tưởng tượng con vừa nhận được món quà yêu thích!',
            'image_path': '/assets/images/happy/situation_happy.png',
            'explanation': 'Khi nhận được quà bất ngờ, chúng ta thường cảm thấy vui vẻ và hạnh phúc.'
        },
        {
            'title': 'Bất ngờ lớn',
            'description': 'Một quả bóng bỗng nổ to bên cạnh con.',
            'target_emotion': 'ngạc nhiên',
            'instruction': 'Mắt mở to, miệng hé nhẹ.',
            'hint': 'Hãy tưởng tượng một điều gì đó bất ngờ xảy ra!',
            'image_path': '/assets/images/surprise/situation_surprise.png',
            'explanation': 'Khi gặp điều bất ngờ, chúng ta thường mở to mắt và há miệng.'
        },
        {
            'title': 'Món đồ yêu thích bị vỡ',
            'description': 'Đồ chơi con thích bị rơi và vỡ.',
            'target_emotion': 'buồn',
            'instruction': 'Mắt rũ xuống, môi dưới hơi trễ.',
            'hint': 'Hãy tưởng tượng món đồ yêu thích của con bị hỏng.',
            'image_path': '/assets/images/sad/situation_sad.png',
            'explanation': 'Khi mất mát thứ gì đó quan trọng, chúng ta cảm thấy buồn.'
        },
        {
            'title': 'Bạn lấy đồ',
            'description': 'Bạn cầm mất món đồ con đang chơi.',
            'target_emotion': 'tức giận',
            'instruction': 'Lông mày hạ xuống, ánh mắt nghiêm.',
            'hint': 'Hãy tưởng tượng ai đó lấy mất đồ của con mà không hỏi.',
            'image_path': '/assets/images/angry/situation_angry.png',
            'explanation': 'Khi bị đối xử không công bằng, chúng ta có thể cảm thấy tức giận.'
        },
        {
            'title': 'Tiếng sấm đêm',
            'description': 'Tiếng sấm rất to lúc trời tối.',
            'target_emotion': 'sợ hãi',
            'instruction': 'Mắt mở to, hơi khép vai.',
            'hint': 'Hãy tưởng tượng một âm thanh lớn và đáng sợ.',
            'image_path': '/assets/images/fear/situation_fear.png',
            'explanation': 'Khi gặp điều đáng sợ, chúng ta thường cảm thấy lo lắng và sợ hãi.'
        },
        {
            'title': 'Món ăn hư',
            'description': 'Con ngửi thấy món ăn đã bị hư.',
            'target_emotion': 'ghê tởm',
            'instruction': 'Mũi nhăn, miệng hơi mở, lông mày cau lại.',
            'hint': 'Hãy tưởng tượng mùi hôi khó chịu.',
            'image_path': '/assets/images/disgust/situation_disgust.png',
            'explanation': 'Khi gặp thứ gì đó khó chịu, chúng ta thường nhăn mặt và cảm thấy ghê tởm.'
        }
    ]
    
    # Insert scenarios vào game_content
    # Format: question_text = title, explanation = description, media_path = image
    for scenario in scenarios:
        # Lưu description vào explanation, hint có thể lưu thêm vào explanation với format đặc biệt
        # Hoặc đơn giản: explanation = description, hint lưu riêng trong code
        connection.execute(sa.text("""
            INSERT INTO game_content (content_id, game_id, level, content_type, media_path, question_text, correct_answer, emotion, explanation)
            VALUES (NEWID(), :game_id, 1, 'image', :image_path, :title, :target_emotion, :target_emotion, :description)
        """), {
            'game_id': game_id,
            'image_path': scenario['image_path'],
            'title': scenario['title'],
            'target_emotion': scenario['target_emotion'],
            'description': scenario['description']
        })
    
    # Lưu hint vào một bảng riêng hoặc dùng explanation (tạm thời dùng explanation để chứa hint)
    # Hoặc có thể thêm cột hint vào game_content nếu cần

def downgrade() -> None:
    """Remove seeded scenarios."""
    connection = op.get_bind()
    
    # Xóa các scenarios của GameCV
    connection.execute(sa.text("""
        DELETE FROM game_content 
        WHERE game_id IN (SELECT game_id FROM games WHERE game_type = 'GameCV')
    """))

