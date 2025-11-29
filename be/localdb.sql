/*
user: ttin cơ bản dùng cho đăng ký đăng nhập, admin
child: thông tin chi tiết child
game: chứa thông tin cơ bản của các game: loại game, tên, số lượng level, level khó bắt đầu từ bao nhiêu, max error, ngưỡng vượt qua level,
	time limit
game content: chứa nội dung từng câu hỏi chi tiết cho các game: loại dữ liệu, level, đường dẫn, question text, gợi ý, 
	đáp án đúng (correct answer cho game click và emotion cho game cv)
	dùng để tạo nên nội dung câu hỏi, các đáp án
question: tạo nên 1 câu hỏi hoàn chỉnh từ nhiều game content

game data: lưu các câu hỏi cụ thể của 1 level của 1 game, nên thêm 1 cột user id để phân biệt giữa nhiều ng chơi
game data content: map giữa game data và game content

emotion concept: lưu các khái niệm cảm xúc dùng cho học
session: lưu 1 phiên chơi của child
session question: lưu lại câu trả lời của child sau mỗi câu hỏi
session history: lưu lại tổng kết của game đó sau mỗi level child chơi

=> game: bảng fix cứng, lấy ttin chung
game data: tập hợp các câu hỏi cho 1 level của 1 người chơi cụ thể
game content: chứa các thành phần tạo nên 1 câu hỏi: nội dung câu để hỏi, đáp án
game data content: map giữa 2 bảng trên

question: lưu câu hỏi hoàn chỉnh, tạo từ nhiều game content
emotion concept: lưu các khái niệm cảm xúc dùng cho học
session: lưu 1 phiên chơi của child
session question: lưu lại câu trả lời của child sau mỗi câu hỏi
session history: lưu lại tổng kết của game đó sau mỗi level child chơi
report	lưu nội dung báo cáo mỗi lần gửi phụ huynh (có thể thêm tính năng nhờ AI phân tích tiến độ học và đề xuất game nên chơi tiếp)

*/
SELECT * FROM [TTNM].[dbo].[users]
SELECT * FROM [TTNM].[dbo].[children]
SELECT * FROM [TTNM].[dbo].[child_progress]
SELECT * FROM [TTNM].[dbo].[games]
SELECT * FROM [TTNM].[dbo].[game_data]
SELECT * FROM [TTNM].[dbo].[game_content]
SELECT * FROM [TTNM].[dbo].[game_history]

SELECT * FROM [TTNM].[dbo].[game_data_contents]
SELECT * FROM [TTNM].[dbo].[questions]

SELECT * FROM [TTNM].[dbo].[session_questions]
SELECT * FROM [TTNM].[dbo].[reports]
SELECT * FROM [TTNM].[dbo].[emotion_concepts]
SELECT * FROM [TTNM].[dbo].[session_history]	
SELECT * FROM [TTNM].[dbo].[sessions]

-- Tắt ràng buộc FK tạm thời
EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL';

USE TTNM;
GO

BEGIN TRY
    DELETE FROM session_questions;
    DELETE FROM session_history;
    DELETE FROM game_history;
    DELETE FROM child_progress;
    DELETE FROM reports;
    DELETE FROM sessions;
    DELETE FROM game_data_contents;
    DELETE FROM game_data;
    DELETE FROM questions;
    DELETE FROM game_content;
    DELETE FROM games;
    DELETE FROM emotion_concepts;
    DELETE FROM children;
    DELETE FROM users;
    PRINT 'Đã xóa hết dữ liệu cũ!';
END TRY


-- Bật lại FK
EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL';

-- 1. Users
IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin')
    INSERT INTO users (user_id, username, email, password, role, name)
    VALUES (NEWID(), 'admin', 'admin@emogarden.com', '123456', 'admin', N'Quản trị viên');

IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'bebinh')
    INSERT INTO users (user_id, username, email, password, role, name)
    VALUES (NEWID(), 'bebinh', 'bebinh@gmail.com', '123456', 'child', N'Bé Bình');

DECLARE @child_user_id UNIQUEIDENTIFIER = (SELECT user_id FROM users WHERE username = 'bebinh');
PRINT 'User ID Bé Bình: ' + CAST(@child_user_id AS NVARCHAR(50));

-- 2. Children
DELETE FROM children WHERE user_id = @child_user_id;
INSERT INTO children (user_id, age, last_played, report_preferences, created_at, last_login, gender, date_of_birth, phone_number)
VALUES (@child_user_id, 6, GETDATE(), 'weekly', GETDATE(), GETDATE(), 'male', '2019-03-15', '0901234567');

-- 3. 6 GAMES
INSERT INTO games (game_id, game_type, name, level, difficulty_level, max_errors, level_threshold, time_limit)
VALUES 
(NEWID(), 'GameClick', N'Nhìn mặt đoán cảm xúc', 1, 1, 3, 70, 60),
(NEWID(), 'GameClick', N'Chọn đúng cảm xúc', 1, 1, 3, 75, 60),
(NEWID(), 'GameCV',   N'Bắt chước biểu cảm', 1, 2, 3, 70, 90),
(NEWID(), 'GameCV',   N'Camera đoán cảm xúc', 1, 2, 3, 80, 120),
(NEWID(), 'GameClick', N'Nhìn tình huống đoán cảm xúc', 2, 2, 3, 75, 70),
(NEWID(), 'GameCV',   N'Game CV - Nhận diện cảm xúc', 1, 1, 3, 5, 300);

-- Lấy game_id
DECLARE @g1 UNIQUEIDENTIFIER = (SELECT TOP 1 game_id FROM games WHERE name = N'Nhìn mặt đoán cảm xúc');
DECLARE @g2 UNIQUEIDENTIFIER = (SELECT TOP 1 game_id FROM games WHERE name = N'Chọn đúng cảm xúc');
DECLARE @g3 UNIQUEIDENTIFIER = (SELECT TOP 1 game_id FROM games WHERE name = N'Bắt chước biểu cảm');
DECLARE @g4 UNIQUEIDENTIFIER = (SELECT TOP 1 game_id FROM games WHERE name = N'Camera đoán cảm xúc');
DECLARE @g5 UNIQUEIDENTIFIER = (SELECT TOP 1 game_id FROM games WHERE name = N'Nhìn tình huống đoán cảm xúc');
DECLARE @g6 UNIQUEIDENTIFIER = (SELECT TOP 1 game_id FROM games WHERE name = N'Game CV - Nhận diện cảm xúc');

-- 4. GAME CONTENT CHO TẤT CẢ 6 GAME (ĐÃ GỘP SIÊU CHI TIẾT)

-- GAME 1: Nhìn mặt đoán cảm xúc
INSERT INTO game_content (content_id, game_id, level, content_type, media_path, question_text, correct_answer, emotion, explanation) VALUES
(NEWID(), @g1, 1, 'image', '/fe/assets/images/click1/vui1.jpg',     N'Bạn nhỏ này đang vui phải không?', N'Vui vẻ',     N'Vui vẻ',     N'Cười tươi, mắt híp lại → vui!'),
(NEWID(), @g1, 1, 'image', '/fe/assets/images/click1/buon1.jpg',    N'Bạn nhỏ đang buồn đúng không?',   N'Buồn bã',    N'Buồn bã',    N'Môi chúm, mắt rưng → buồn.'),
(NEWID(), @g1, 1, 'image', '/fe/assets/images/click1/tuc1.jpg',     N'Bạn nhỏ đang tức giận?',          N'Tức giận',   N'Tức giận',   N'Mặt đỏ, mày nhíu → tức giận.'),
(NEWID(), @g1, 1, 'image', '/fe/assets/images/click1/so1.jpg',      N'Bạn nhỏ đang sợ hãi?',            N'Sợ hãi',     N'Sợ hãi',     N'Mắt mở to, miệng há → sợ.'),
(NEWID(), @g1, 1, 'image', '/fe/assets/images/click1/ngac1.jpg',    N'Bạn nhỏ đang ngạc nhiên?',         N'Ngạc nhiên', N'Ngạc nhiên', N'Miệng chữ O → ngạc nhiên.'),
(NEWID(), @g1, 1, 'image', '/fe/assets/images/click1/ghe1.jpg',     N'Bạn nhỏ đang ghê tởm?',           N'Ghê tởm',    N'Ghê tởm',    N'Nhăn mũi → ghê tởm.');

-- GAME 2: Chọn đúng cảm xúc
INSERT INTO game_content (content_id, game_id, level, content_type, media_path, question_text, correct_answer, emotion, explanation) VALUES
(NEWID(), @g2, 1, 'text', NULL, N'Khi được mẹ khen, bé thường cảm thấy?',            N'Vui vẻ',     N'Vui vẻ',     N'Khen ngợi → vui!'),
(NEWID(), @g2, 1, 'text', NULL, N'Khi bị bạn giật đồ chơi, bé thường?',             N'Tức giận',   N'Tức giận',   N'Bị lấy đồ → tức giận.'),
(NEWID(), @g2, 1, 'text', NULL, N'Nghe tiếng nổ lớn, bé sẽ?',                       N'Sợ hãi',     N'Sợ hãi',     N'Tiếng to → sợ.'),
(NEWID(), @g2, 1, 'text', NULL, N'Nhìn thấy con vật dễ thương, bé sẽ?',             N'Vui vẻ',     N'Vui vẻ',     N'Dễ thương → vui.'),
(NEWID(), @g2, 1, 'text', NULL, N'Khi đồ chơi bị vỡ, bé cảm thấy?',                 N'Buồn bã',    N'Buồn bã',    N'Mất đồ → buồn.'),
(NEWID(), @g2, 1, 'text', NULL, N'Ngửi phải mùi hôi, bé sẽ?',                       N'Ghê tởm',    N'Ghê tởm',    N'Mùi hôi → ghê.');

-- GAME 3: Bắt chước biểu cảm
INSERT INTO game_content (content_id, game_id, level, content_type, media_path, question_text, correct_answer, emotion, explanation) VALUES
(NEWID(), @g3, 1, 'video', '/fe/assets/videos/cv/vui_demo.mp4',     N'Làm giống video nhé!', NULL, N'Vui vẻ',     N'Cười thật tươi!'),
(NEWID(), @g3, 1, 'video', '/fe/assets/videos/cv/ngac_demo.mp4',    N'Làm giống video nhé!', NULL, N'Ngạc nhiên', N'Mở to mắt, miệng O!'),
(NEWID(), @g3, 1, 'video', '/fe/assets/videos/cv/buon_demo.mp4',    N'Làm giống video nhé!', NULL, N'Buồn bã',    N'Mắt rũ, môi trễ.'),
(NEWID(), @g3, 1, 'video', '/fe/assets/videos/cv/tuc_demo.mp4',     N'Làm giống video nhé!', NULL, N'Tức giận',   N'Nhíu mày, miệng mím.'),
(NEWID(), @g3, 1, 'video', '/fe/assets/videos/cv/so_demo.mp4',      N'Làm giống video nhé!', NULL, N'Sợ hãi',     N'Mở to mắt, co vai.'),
(NEWID(), @g3, 1, 'video', '/fe/assets/videos/cv/ghe_demo.mp4',     N'Làm giống video nhé!', NULL, N'Ghê tởm',    N'Nhăn mũi, lưỡi thè.');

-- GAME 4: Camera đoán cảm xúc
INSERT INTO game_content (content_id, game_id, level, content_type, media_path, question_text, correct_answer, emotion, explanation) VALUES
(NEWID(), @g4, 1, 'image', '/fe/assets/images/cv_guide.jpg', N'Nhìn camera và thể hiện cảm xúc!', NULL, NULL, N'Camera sẽ đoán cảm xúc của con.'),
(NEWID(), @g4, 1, 'image', '/fe/assets/images/cv_guide.jpg', N'Hãy cười thật tươi nào!',         NULL, N'Vui vẻ',     N''),
(NEWID(), @g4, 1, 'image', '/fe/assets/images/cv_guide.jpg', N'Mở to mắt và há miệng!',          NULL, N'Ngạc nhiên', N''),
(NEWID(), @g4, 1, 'image', '/fe/assets/images/cv_guide.jpg', N'Làm mặt buồn nào!',               NULL, N'Buồn bã',    N''),
(NEWID(), @g4, 1, 'image', '/fe/assets/images/cv_guide.jpg', N'Nhíu mày, nhìn nghiêm!',          NULL, N'Tức giận',   N''),
(NEWID(), @g4, 1, 'image', '/fe/assets/images/cv_guide.jpg', N'Nhăn mũi nào!',                   NULL, N'Ghê tởm',    N'');

-- GAME 5: Nhìn tình huống đoán cảm xúc
INSERT INTO game_content (content_id, game_id, level, content_type, media_path, question_text, correct_answer, emotion, explanation) VALUES
(NEWID(), @g5, 2, 'image', '/assets/images/happy/situation_happy.png',     N'Con cảm thấy thế nào?', N'Vui vẻ',     N'Vui vẻ',     N'Nhận quà → vui!'),
(NEWID(), @g5, 2, 'image', '/assets/images/surprise/situation_surprise.png',N'Con cảm thấy thế nào?', N'Ngạc nhiên', N'Ngạc nhiên', N'Bóng nổ → bất ngờ!'),
(NEWID(), @g5, 2, 'image', '/assets/images/sad/situation_sad.png',        N'Con cảm thấy thế nào?', N'Buồn bã',    N'Buồn bã',    N'Đồ vỡ → buồn.'),
(NEWID(), @g5, 2, 'image', '/assets/images/angry/situation_angry.png',    N'Con cảm thấy thế nào?', N'Tức giận',   N'Tức giận',   N'Bị giật đồ → tức.'),
(NEWID(), @g5, 2, 'image', '/assets/images/fear/situation_fear.png',      N'Con cảm thấy thế nào?', N'Sợ hãi',     N'Sợ hãi',     N'Sấm to → sợ.'),
(NEWID(), @g5, 2, 'image', '/assets/images/disgust/situation_disgust.png',N'Con cảm thấy thế nào?', N'Ghê tởm',    N'Ghê tởm',    N'Mùi hôi → ghê.');

-- GAME 6: Game CV - Nhận diện cảm xúc (6 SCENARIO SIÊU CHI TIẾT - ĐÃ GỘP TỪ MIGRATION)
INSERT INTO game_content (content_id, game_id, level, content_type, media_path, question_text, correct_answer, emotion, explanation) VALUES
(NEWID(), @g6, 1, 'image', '/assets/images/happy/situation_happy.png',     N'Quà bất ngờ',           N'vui',       N'vui',       N'Con mở hộp quà bất ngờ và thấy món con thích. Hãy tưởng tượng con vừa nhận được món quà yêu thích!'),
(NEWID(), @g6, 1, 'image', '/assets/images/surprise/situation_surprise.png',N'Bất ngờ lớn',      N'ngạc nhiên',N'ngạc nhiên',N'Một quả bóng bỗng nổ to bên cạnh con. Hãy tưởng tượng một điều gì đó bất ngờ xảy ra!'),
(NEWID(), @g6, 1, 'image', '/assets/images/sad/situation_sad.png',        N'Món đồ yêu thích bị vỡ',N'buồn',      N'buồn',      N'Đồ chơi con thích bị rơi và vỡ. Hãy tưởng tượng món đồ yêu thích của con bị hỏng.'),
(NEWID(), @g6, 1, 'image', '/assets/images/angry/situation_angry.png',    N'Bạn lấy đồ',            N'tức giận',  N'tức giận',  N'Bạn cầm mất món đồ con đang chơi. Hãy tưởng tượng ai đó lấy mất đồ của con mà không hỏi.'),
(NEWID(), @g6, 1, 'image', '/assets/images/fear/situation_fear.png',      N'Tiếng sấm đêm',         N'sợ hãi',    N'sợ hãi',    N'Tiếng sấm rất to lúc trời tối. Hãy tưởng tượng một âm thanh lớn và đáng sợ.'),
(NEWID(), @g6, 1, 'image', '/assets/images/disgust/situation_disgust.png',N'Món ăn hư',             N'ghê tởm',   N'ghê tởm',   N'Con ngửi thấy món ăn đã bị hư. Hãy tưởng tượng mùi hôi khó chịu.');

-- 5. Questions (từ content có correct_answer)
INSERT INTO questions (question_id, game_id, level, content_id, correct_answer)
SELECT NEWID(), gc.game_id, gc.level, gc.content_id, gc.correct_answer
FROM game_content gc WHERE gc.correct_answer IS NOT NULL;

-- 6. Emotion concepts
INSERT INTO emotion_concepts (concept_id, emotion, level, title, video_path, image_path, audio_path, description) VALUES
(NEWID(), N'Vui vẻ', 1, N'Khi nào thì vui?', '/fe/assets/videos/concepts/vui.mp4', '/fe/assets/images/concepts/vui.jpg', '/fe/assets/audio/vui.mp3', N'Vui khi được khen, được quà...'),
(NEWID(), N'Buồn bã', 1, N'Khi nào buồn?', '/fe/assets/videos/concepts/buon.mp4', '/fe/assets/images/concepts/buon.jpg', NULL, N'Buồn khi mất đồ, bị mắng...'),
(NEWID(), N'Tức giận', 1, N'Khi nào tức giận?', '/fe/assets/videos/concepts/tuc.mp4', '/fe/assets/images/concepts/tuc.jpg', NULL, N'Tức khi bị lấy đồ...'),
(NEWID(), N'Sợ hãi', 1, N'Khi nào sợ?', NULL, '/fe/assets/images/concepts/so.jpg', '/fe/assets/audio/so.mp3', N'Sợ khi nghe tiếng to...'),
(NEWID(), N'Ngạc nhiên', 1, N'Khi nào ngạc nhiên?', '/fe/assets/videos/concepts/ngac.mp4', '/fe/assets/images/concepts/ngac.jpg', NULL, N'Ngạc nhiên khi bất ngờ...'),
(NEWID(), N'Ghê tởm', 1, N'Khi nào ghê?', NULL, '/fe/assets/images/concepts/ghe.jpg', NULL, N'Ghê khi ngửi mùi hôi...');

-- 7. Sessions mẫu
INSERT INTO sessions (session_id, user_id, game_id, start_time, end_time, state, score, emotion_errors, max_errors, level_threshold, ratio, time_limit, question_ids) VALUES
(NEWID(), @child_user_id, @g1, DATEADD(minute, -30, GETDATE()), DATEADD(minute, -10, GETDATE()), 'end', 90, N'{}', 3, 70, '[]', 60, '[]'),
(NEWID(), @child_user_id, @g6, DATEADD(hour, -1, GETDATE()), NULL, 'playing', 50, N'{"ghê tởm":1}', 3, 5, '[]', 300, '[]');

-- 8. Child progress
INSERT INTO child_progress (progress_id, child_id, game_id, level, accuracy, avg_response_time, score, last_played, ratio, review_emotions) VALUES
(NEWID(), @child_user_id, @g1, 1, 92.0, 2800, 180, GETDATE(), '[]', '[]'),
(NEWID(), @child_user_id, @g6, 1, 83.3, 4500, 150, GETDATE(), '[]', N'["ghê tởm"]');

-- 9. Reports
INSERT INTO reports (report_id, child_id, report_type, generated_at, summary, data) VALUES
(NEWID(), @child_user_id, 'weekly', GETDATE(), N'Bé đã chơi đủ 6 game, tiến bộ rõ rệt!', N'{"total":30,"correct":26}');

PRINT 'Done'