# Hướng dẫn Seed Data cho Game CV

## Cách 1: Dùng Script Python (Khuyến nghị)

```bash
cd be
python scripts/seed_cv_scenarios.py
```

Script này sẽ:
- Tạo GameCV nếu chưa có
- Xóa scenarios cũ (nếu có)
- Insert 6 tình huống mới với đầy đủ thông tin

## Cách 2: Dùng Migration Alembic

```bash
cd be
alembic upgrade head
```

Migration `seed_game_cv_scenarios.py` sẽ tự động chạy khi upgrade.

## Cách 3: Insert thủ công vào Database

Nếu muốn insert thủ công, chạy SQL sau:

```sql
-- 1. Tạo GameCV nếu chưa có
IF NOT EXISTS (SELECT 1 FROM games WHERE game_type = 'GameCV')
BEGIN
    INSERT INTO games (game_id, game_type, name, level, difficulty_level, max_errors, level_threshold, time_limit)
    VALUES (NEWID(), 'GameCV', 'Game CV - Nhận diện cảm xúc', 1, 1, 3, 5, 300)
END

-- 2. Lấy game_id
DECLARE @game_id UNIQUEIDENTIFIER = (SELECT game_id FROM games WHERE game_type = 'GameCV')

-- 3. Xóa scenarios cũ
DELETE FROM game_content WHERE game_id = @game_id

-- 4. Insert 6 scenarios
INSERT INTO game_content (content_id, game_id, level, content_type, media_path, question_text, correct_answer, emotion, explanation)
VALUES
    (NEWID(), @game_id, 1, 'image', '/assets/images/scenarios/gift.jpg', 'Quà bất ngờ', 'vui', 'vui', 'Con mở hộp quà bất ngờ và thấy món con thích.'),
    (NEWID(), @game_id, 1, 'image', '/assets/images/scenarios/surprise.jpg', 'Bất ngờ lớn', 'ngạc nhiên', 'ngạc nhiên', 'Một quả bóng bỗng nổ to bên cạnh con.'),
    (NEWID(), @game_id, 1, 'image', '/assets/images/scenarios/broken_toy.jpg', 'Món đồ yêu thích bị vỡ', 'buồn', 'buồn', 'Đồ chơi con thích bị rơi và vỡ.'),
    (NEWID(), @game_id, 1, 'image', '/assets/images/scenarios/angry.jpg', 'Bạn lấy đồ', 'tức giận', 'tức giận', 'Bạn cầm mất món đồ con đang chơi.'),
    (NEWID(), @game_id, 1, 'image', '/assets/images/scenarios/thunder.jpg', 'Tiếng sấm đêm', 'sợ hãi', 'sợ hãi', 'Tiếng sấm rất to lúc trời tối.'),
    (NEWID(), @game_id, 1, 'image', '/assets/images/scenarios/disgust.jpg', 'Món ăn hư', 'ghê tởm', 'ghê tởm', 'Con ngửi thấy món ăn đã bị hư.')
```

## Cấu trúc dữ liệu

Mỗi scenario trong `game_content`:
- `question_text` = Tiêu đề tình huống
- `explanation` = Mô tả tình huống
- `media_path` = Đường dẫn ảnh minh họa
- `emotion` = Cảm xúc mục tiêu
- `correct_answer` = Cảm xúc mục tiêu (giống emotion)
- `content_type` = 'image'
- `level` = 1

## Kiểm tra

Sau khi seed, kiểm tra bằng API:

```bash
curl http://localhost:8000/games/cv/scenarios
```

Hoặc truy cập: http://localhost:8000/docs và test endpoint `/games/cv/scenarios`

## Lưu ý

- Ảnh minh họa cần được đặt trong `fe/assets/images/scenarios/`
- Nếu ảnh không có, game vẫn chạy được nhưng sẽ không hiển thị ảnh
- Có thể cập nhật scenarios sau bằng cách chạy lại script hoặc update trực tiếp trong DB

