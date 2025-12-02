"""
Script để seed nhiều tình huống Game CV vào database cho nhiều level
Chạy: python scripts/seed_many_cv_scenarios.py
"""

import sys
import os
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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
            VALUES (:game_id, 'GameCV', 'Game CV - Nhận diện cảm xúc', 1, 1, 5, 3, 450)
        """), {"game_id": new_game_id})
        db.commit()
        game_id = new_game_id
        print(f"Created new GameCV with ID: {game_id}")
    
    # KHÔNG xóa scenarios cũ - chỉ thêm mới để có nhiều scenarios
    print("Adding new scenarios (keeping existing ones)...")
    
    # Danh sách scenarios cho nhiều level
    # Mỗi level có 15-20 scenarios để có thể random 10
    scenarios = [
        # LEVEL 1 - VUI (15 scenarios)
        {"level": 1, "target_emotion": "vui", "title": "Quà bất ngờ", "description": "Con mở hộp quà bất ngờ và thấy món con thích.", "image_path": "/assets/images/scenarios/gift.jpg"},
        {"level": 1, "target_emotion": "vui", "title": "Được khen", "description": "Cô giáo khen con làm bài tốt.", "image_path": "/assets/images/scenarios/praise.jpg"},
        {"level": 1, "target_emotion": "vui", "title": "Sinh nhật", "description": "Hôm nay là sinh nhật con, mọi người hát chúc mừng.", "image_path": "/assets/images/scenarios/birthday.jpg"},
        {"level": 1, "target_emotion": "vui", "title": "Đi chơi công viên", "description": "Bố mẹ đưa con đi chơi công viên vào cuối tuần.", "image_path": "/assets/images/scenarios/park.jpg"},
        {"level": 1, "target_emotion": "vui", "title": "Được điểm 10", "description": "Con làm bài kiểm tra đạt điểm 10.", "image_path": "/assets/images/scenarios/score10.jpg"},
        {"level": 1, "target_emotion": "vui", "title": "Gặp bạn thân", "description": "Con gặp lại bạn thân sau kỳ nghỉ hè.", "image_path": "/assets/images/scenarios/friend.jpg"},
        {"level": 1, "target_emotion": "vui", "title": "Được mua đồ chơi", "description": "Bố mẹ mua cho con món đồ chơi con thích.", "image_path": "/assets/images/scenarios/toy.jpg"},
        {"level": 1, "target_emotion": "vui", "title": "Thắng trò chơi", "description": "Con thắng trong trò chơi với bạn bè.", "image_path": "/assets/images/scenarios/win.jpg"},
        {"level": 1, "target_emotion": "vui", "title": "Được ăn kem", "description": "Bố mẹ cho con ăn kem sau bữa trưa.", "image_path": "/assets/images/scenarios/icecream.jpg"},
        {"level": 1, "target_emotion": "vui", "title": "Xem phim hoạt hình", "description": "Con được xem bộ phim hoạt hình yêu thích.", "image_path": "/assets/images/scenarios/cartoon.jpg"},
        {"level": 1, "target_emotion": "vui", "title": "Được ôm", "description": "Mẹ ôm con thật chặt sau khi đi làm về.", "image_path": "/assets/images/scenarios/hug.jpg"},
        {"level": 1, "target_emotion": "vui", "title": "Chơi với thú cưng", "description": "Con chơi đùa với chú chó dễ thương.", "image_path": "/assets/images/scenarios/pet.jpg"},
        {"level": 1, "target_emotion": "vui", "title": "Được đi bơi", "description": "Con được đi bơi ở hồ bơi gần nhà.", "image_path": "/assets/images/scenarios/swim.jpg"},
        {"level": 1, "target_emotion": "vui", "title": "Làm bánh cùng mẹ", "description": "Con và mẹ cùng làm bánh ngọt.", "image_path": "/assets/images/scenarios/baking.jpg"},
        {"level": 1, "target_emotion": "vui", "title": "Được đọc truyện", "description": "Bố đọc cho con nghe câu chuyện hay.", "image_path": "/assets/images/scenarios/story.jpg"},
        
        # LEVEL 1 - BUỒN (15 scenarios)
        {"level": 1, "target_emotion": "buồn", "title": "Mất đồ chơi", "description": "Con làm mất món đồ chơi yêu thích.", "image_path": "/assets/images/scenarios/lost_toy.jpg"},
        {"level": 1, "target_emotion": "buồn", "title": "Bạn đi xa", "description": "Bạn thân của con chuyển nhà đi xa.", "image_path": "/assets/images/scenarios/friend_away.jpg"},
        {"level": 1, "target_emotion": "buồn", "title": "Bị điểm kém", "description": "Con làm bài kiểm tra không tốt.", "image_path": "/assets/images/scenarios/bad_score.jpg"},
        {"level": 1, "target_emotion": "buồn", "title": "Trời mưa", "description": "Trời mưa nên con không thể đi chơi.", "image_path": "/assets/images/scenarios/rain.jpg"},
        {"level": 1, "target_emotion": "buồn", "title": "Bị mắng", "description": "Con bị mẹ mắng vì làm sai.", "image_path": "/assets/images/scenarios/scolded.jpg"},
        {"level": 1, "target_emotion": "buồn", "title": "Xem phim buồn", "description": "Con xem một bộ phim có đoạn buồn.", "image_path": "/assets/images/scenarios/sad_movie.jpg"},
        {"level": 1, "target_emotion": "buồn", "title": "Thú cưng ốm", "description": "Chú chó của con bị ốm.", "image_path": "/assets/images/scenarios/sick_pet.jpg"},
        {"level": 1, "target_emotion": "buồn", "title": "Không được đi chơi", "description": "Con không được đi chơi vì phải học bài.", "image_path": "/assets/images/scenarios/no_play.jpg"},
        {"level": 1, "target_emotion": "buồn", "title": "Bị bạn bỏ rơi", "description": "Các bạn không chơi với con.", "image_path": "/assets/images/scenarios/left_out.jpg"},
        {"level": 1, "target_emotion": "buồn", "title": "Đồ chơi bị hỏng", "description": "Món đồ chơi của con bị hỏng.", "image_path": "/assets/images/scenarios/broken_toy.jpg"},
        {"level": 1, "target_emotion": "buồn", "title": "Bị đau", "description": "Con bị ngã và đau chân.", "image_path": "/assets/images/scenarios/hurt.jpg"},
        {"level": 1, "target_emotion": "buồn", "title": "Phải về sớm", "description": "Con phải về nhà sớm khi đang chơi vui.", "image_path": "/assets/images/scenarios/go_home.jpg"},
        {"level": 1, "target_emotion": "buồn", "title": "Bị từ chối", "description": "Con xin mẹ mua đồ nhưng mẹ không đồng ý.", "image_path": "/assets/images/scenarios/refused.jpg"},
        {"level": 1, "target_emotion": "buồn", "title": "Bỏ lỡ sự kiện", "description": "Con bỏ lỡ một sự kiện vui ở trường.", "image_path": "/assets/images/scenarios/missed_event.jpg"},
        {"level": 1, "target_emotion": "buồn", "title": "Nghe tin buồn", "description": "Con nghe tin một người thân bị ốm.", "image_path": "/assets/images/scenarios/bad_news.jpg"},
        
        # LEVEL 1 - NGẠC NHIÊN (15 scenarios)
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Quà bất ngờ", "description": "Con nhận được món quà bất ngờ từ bố mẹ.", "image_path": "/assets/images/scenarios/surprise_gift.jpg"},
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Gặp người quen", "description": "Con gặp một người quen ở nơi không ngờ tới.", "image_path": "/assets/images/scenarios/unexpected_meeting.jpg"},
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Phát hiện bí mật", "description": "Con phát hiện một điều bất ngờ trong nhà.", "image_path": "/assets/images/scenarios/discovery.jpg"},
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Thấy điều lạ", "description": "Con thấy một điều gì đó rất lạ và bất ngờ.", "image_path": "/assets/images/scenarios/strange_thing.jpg"},
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Tin tốt bất ngờ", "description": "Con nhận được tin tốt không ngờ tới.", "image_path": "/assets/images/scenarios/good_news.jpg"},
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Bạn xuất hiện", "description": "Bạn thân của con xuất hiện đột ngột.", "image_path": "/assets/images/scenarios/friend_appear.jpg"},
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Thấy động vật lạ", "description": "Con thấy một con vật lạ trong vườn.", "image_path": "/assets/images/scenarios/strange_animal.jpg"},
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Điều bất ngờ", "description": "Một điều bất ngờ xảy ra với con.", "image_path": "/assets/images/scenarios/surprise.jpg"},
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Phát hiện mới", "description": "Con phát hiện một điều mới mẻ thú vị.", "image_path": "/assets/images/scenarios/new_discovery.jpg"},
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Tin sốc", "description": "Con nghe một tin làm con rất ngạc nhiên.", "image_path": "/assets/images/scenarios/shocking_news.jpg"},
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Gặp điều kỳ lạ", "description": "Con gặp một điều kỳ lạ chưa từng thấy.", "image_path": "/assets/images/scenarios/weird_thing.jpg"},
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Bất ngờ từ bố mẹ", "description": "Bố mẹ làm một điều bất ngờ cho con.", "image_path": "/assets/images/scenarios/parent_surprise.jpg"},
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Thấy điều không ngờ", "description": "Con thấy một điều hoàn toàn không ngờ tới.", "image_path": "/assets/images/scenarios/unexpected.jpg"},
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Phát hiện kho báu", "description": "Con phát hiện một 'kho báu' trong nhà.", "image_path": "/assets/images/scenarios/treasure.jpg"},
        {"level": 1, "target_emotion": "ngạc nhiên", "title": "Sự kiện bất ngờ", "description": "Một sự kiện bất ngờ xảy ra với con.", "image_path": "/assets/images/scenarios/unexpected_event.jpg"},
        
        # LEVEL 2 - VUI (15 scenarios)
        {"level": 2, "target_emotion": "vui", "title": "Thắng cuộc thi", "description": "Con thắng trong cuộc thi ở trường.", "image_path": "/assets/images/scenarios/contest_win.jpg"},
        {"level": 2, "target_emotion": "vui", "title": "Được công nhận", "description": "Con được mọi người công nhận nỗ lực của mình.", "image_path": "/assets/images/scenarios/recognized.jpg"},
        {"level": 2, "target_emotion": "vui", "title": "Hoàn thành mục tiêu", "description": "Con đạt được mục tiêu đã đặt ra.", "image_path": "/assets/images/scenarios/goal_achieved.jpg"},
        {"level": 2, "target_emotion": "vui", "title": "Được tặng quà đặc biệt", "description": "Con nhận được món quà đặc biệt từ người thân.", "image_path": "/assets/images/scenarios/special_gift.jpg"},
        {"level": 2, "target_emotion": "vui", "title": "Thành công trong học tập", "description": "Con đạt kết quả tốt trong học tập.", "image_path": "/assets/images/scenarios/study_success.jpg"},
        {"level": 2, "target_emotion": "vui", "title": "Được khen ngợi", "description": "Con được nhiều người khen ngợi.", "image_path": "/assets/images/scenarios/praised.jpg"},
        {"level": 2, "target_emotion": "vui", "title": "Trải nghiệm mới", "description": "Con có một trải nghiệm mới thú vị.", "image_path": "/assets/images/scenarios/new_experience.jpg"},
        {"level": 2, "target_emotion": "vui", "title": "Đạt thành tích", "description": "Con đạt thành tích tốt trong hoạt động.", "image_path": "/assets/images/scenarios/achievement.jpg"},
        {"level": 2, "target_emotion": "vui", "title": "Được tin vui", "description": "Con nhận được tin vui từ gia đình.", "image_path": "/assets/images/scenarios/good_news2.jpg"},
        {"level": 2, "target_emotion": "vui", "title": "Thành công", "description": "Con cảm thấy thành công trong việc mình làm.", "image_path": "/assets/images/scenarios/success.jpg"},
        {"level": 2, "target_emotion": "vui", "title": "Được yêu thương", "description": "Con cảm nhận được tình yêu thương từ mọi người.", "image_path": "/assets/images/scenarios/loved.jpg"},
        {"level": 2, "target_emotion": "vui", "title": "Hạnh phúc", "description": "Con cảm thấy rất hạnh phúc.", "image_path": "/assets/images/scenarios/happy.jpg"},
        {"level": 2, "target_emotion": "vui", "title": "Được công nhận tài năng", "description": "Con được công nhận tài năng của mình.", "image_path": "/assets/images/scenarios/talent_recognized.jpg"},
        {"level": 2, "target_emotion": "vui", "title": "Thành tựu", "description": "Con đạt được một thành tựu quan trọng.", "image_path": "/assets/images/scenarios/accomplishment.jpg"},
        {"level": 2, "target_emotion": "vui", "title": "Niềm vui lớn", "description": "Con có một niềm vui lớn trong ngày.", "image_path": "/assets/images/scenarios/great_joy.jpg"},
        
        # LEVEL 2 - TỨC GIẬN (15 scenarios)
        {"level": 2, "target_emotion": "tức giận", "title": "Bị hiểu lầm", "description": "Con bị hiểu lầm và cảm thấy tức giận.", "image_path": "/assets/images/scenarios/misunderstood.jpg"},
        {"level": 2, "target_emotion": "tức giận", "title": "Bị đối xử không công bằng", "description": "Con cảm thấy bị đối xử không công bằng.", "image_path": "/assets/images/scenarios/unfair.jpg"},
        {"level": 2, "target_emotion": "tức giận", "title": "Bị cướp đồ chơi", "description": "Bạn cướp mất đồ chơi của con.", "image_path": "/assets/images/scenarios/toy_stolen.jpg"},
        {"level": 2, "target_emotion": "tức giận", "title": "Bị chế nhạo", "description": "Con bị các bạn chế nhạo.", "image_path": "/assets/images/scenarios/mocked.jpg"},
        {"level": 2, "target_emotion": "tức giận", "title": "Bị đổ lỗi", "description": "Con bị đổ lỗi cho việc không phải do con làm.", "image_path": "/assets/images/scenarios/blamed.jpg"},
        {"level": 2, "target_emotion": "tức giận", "title": "Bị phá hỏng", "description": "Ai đó phá hỏng công việc của con.", "image_path": "/assets/images/scenarios/ruined.jpg"},
        {"level": 2, "target_emotion": "tức giận", "title": "Bị từ chối không lý do", "description": "Con bị từ chối một cách không công bằng.", "image_path": "/assets/images/scenarios/unfair_refusal.jpg"},
        {"level": 2, "target_emotion": "tức giận", "title": "Bị cắt ngang", "description": "Con bị cắt ngang khi đang nói.", "image_path": "/assets/images/scenarios/interrupted.jpg"},
        {"level": 2, "target_emotion": "tức giận", "title": "Bị bỏ qua", "description": "Con bị bỏ qua trong một hoạt động.", "image_path": "/assets/images/scenarios/ignored.jpg"},
        {"level": 2, "target_emotion": "tức giận", "title": "Bị chỉ trích", "description": "Con bị chỉ trích một cách không đúng.", "image_path": "/assets/images/scenarios/criticized.jpg"},
        {"level": 2, "target_emotion": "tức giận", "title": "Bị lừa dối", "description": "Con phát hiện mình bị lừa dối.", "image_path": "/assets/images/scenarios/deceived.jpg"},
        {"level": 2, "target_emotion": "tức giận", "title": "Bị phá rối", "description": "Ai đó cố tình phá rối công việc của con.", "image_path": "/assets/images/scenarios/sabotaged.jpg"},
        {"level": 2, "target_emotion": "tức giận", "title": "Bị đối xử tệ", "description": "Con bị đối xử tệ bạc.", "image_path": "/assets/images/scenarios/bad_treatment.jpg"},
        {"level": 2, "target_emotion": "tức giận", "title": "Bị bất công", "description": "Con cảm thấy bị đối xử bất công.", "image_path": "/assets/images/scenarios/injustice.jpg"},
        {"level": 2, "target_emotion": "tức giận", "title": "Bị xúc phạm", "description": "Con bị xúc phạm bởi ai đó.", "image_path": "/assets/images/scenarios/insulted.jpg"},
        
        # LEVEL 3 - SỢ HÃI (15 scenarios)
        {"level": 3, "target_emotion": "sợ hãi", "title": "Bóng tối", "description": "Con ở một mình trong phòng tối.", "image_path": "/assets/images/scenarios/darkness.jpg"},
        {"level": 3, "target_emotion": "sợ hãi", "title": "Tiếng động lạ", "description": "Con nghe thấy tiếng động lạ trong nhà.", "image_path": "/assets/images/scenarios/strange_sound.jpg"},
        {"level": 3, "target_emotion": "sợ hãi", "title": "Bị lạc", "description": "Con bị lạc trong siêu thị.", "image_path": "/assets/images/scenarios/lost.jpg"},
        {"level": 3, "target_emotion": "sợ hãi", "title": "Sấm chớp", "description": "Trời có sấm chớp lớn.", "image_path": "/assets/images/scenarios/thunder.jpg"},
        {"level": 3, "target_emotion": "sợ hãi", "title": "Con vật lớn", "description": "Con gặp một con vật lớn không quen.", "image_path": "/assets/images/scenarios/big_animal.jpg"},
        {"level": 3, "target_emotion": "sợ hãi", "title": "Bị đe dọa", "description": "Con cảm thấy bị đe dọa bởi ai đó.", "image_path": "/assets/images/scenarios/threatened.jpg"},
        {"level": 3, "target_emotion": "sợ hãi", "title": "Nơi lạ", "description": "Con ở một nơi hoàn toàn xa lạ.", "image_path": "/assets/images/scenarios/strange_place.jpg"},
        {"level": 3, "target_emotion": "sợ hãi", "title": "Bị bỏ lại", "description": "Con cảm thấy như bị bỏ lại một mình.", "image_path": "/assets/images/scenarios/abandoned.jpg"},
        {"level": 3, "target_emotion": "sợ hãi", "title": "Nguy hiểm", "description": "Con cảm thấy có nguy hiểm đang đến gần.", "image_path": "/assets/images/scenarios/danger.jpg"},
        {"level": 3, "target_emotion": "sợ hãi", "title": "Bất ngờ đáng sợ", "description": "Một điều đáng sợ xảy ra bất ngờ.", "image_path": "/assets/images/scenarios/scary_surprise.jpg"},
        {"level": 3, "target_emotion": "sợ hãi", "title": "Không an toàn", "description": "Con cảm thấy không an toàn.", "image_path": "/assets/images/scenarios/unsafe.jpg"},
        {"level": 3, "target_emotion": "sợ hãi", "title": "Sợ hãi", "description": "Con cảm thấy rất sợ hãi.", "image_path": "/assets/images/scenarios/afraid.jpg"},
        {"level": 3, "target_emotion": "sợ hãi", "title": "Lo lắng", "description": "Con cảm thấy lo lắng về điều gì đó.", "image_path": "/assets/images/scenarios/worried.jpg"},
        {"level": 3, "target_emotion": "sợ hãi", "title": "Hoảng sợ", "description": "Con cảm thấy hoảng sợ.", "image_path": "/assets/images/scenarios/panicked.jpg"},
        {"level": 3, "target_emotion": "sợ hãi", "title": "Bất an", "description": "Con cảm thấy bất an về tình huống hiện tại.", "image_path": "/assets/images/scenarios/uneasy.jpg"},
        
        # LEVEL 3 - GHÊ TỞM (15 scenarios)
        {"level": 3, "target_emotion": "ghê tởm", "title": "Thức ăn hỏng", "description": "Con thấy thức ăn đã bị hỏng.", "image_path": "/assets/images/scenarios/spoiled_food.jpg"},
        {"level": 3, "target_emotion": "ghê tởm", "title": "Mùi khó chịu", "description": "Con ngửi thấy mùi rất khó chịu.", "image_path": "/assets/images/scenarios/bad_smell.jpg"},
        {"level": 3, "target_emotion": "ghê tởm", "title": "Thấy côn trùng", "description": "Con thấy một con côn trùng đáng sợ.", "image_path": "/assets/images/scenarios/insect.jpg"},
        {"level": 3, "target_emotion": "ghê tởm", "title": "Đồ bẩn", "description": "Con thấy một thứ rất bẩn.", "image_path": "/assets/images/scenarios/dirty.jpg"},
        {"level": 3, "target_emotion": "ghê tởm", "title": "Vị khó chịu", "description": "Con nếm một vị rất khó chịu.", "image_path": "/assets/images/scenarios/bad_taste.jpg"},
        {"level": 3, "target_emotion": "ghê tởm", "title": "Thấy điều kinh tởm", "description": "Con thấy một điều rất kinh tởm.", "image_path": "/assets/images/scenarios/disgusting.jpg"},
        {"level": 3, "target_emotion": "ghê tởm", "title": "Chạm vào thứ bẩn", "description": "Con vô tình chạm vào thứ rất bẩn.", "image_path": "/assets/images/scenarios/touch_dirty.jpg"},
        {"level": 3, "target_emotion": "ghê tởm", "title": "Mùi hôi", "description": "Con ngửi thấy mùi hôi thối.", "image_path": "/assets/images/scenarios/rotten_smell.jpg"},
        {"level": 3, "target_emotion": "ghê tởm", "title": "Thấy rác", "description": "Con thấy một đống rác bẩn.", "image_path": "/assets/images/scenarios/trash.jpg"},
        {"level": 3, "target_emotion": "ghê tởm", "title": "Đồ hỏng", "description": "Con thấy một thứ đã hỏng và bẩn.", "image_path": "/assets/images/scenarios/rotten.jpg"},
        {"level": 3, "target_emotion": "ghê tởm", "title": "Khó chịu", "description": "Con cảm thấy rất khó chịu với điều gì đó.", "image_path": "/assets/images/scenarios/unpleasant.jpg"},
        {"level": 3, "target_emotion": "ghê tởm", "title": "Kinh tởm", "description": "Con thấy một điều rất kinh tởm.", "image_path": "/assets/images/scenarios/revolting.jpg"},
        {"level": 3, "target_emotion": "ghê tởm", "title": "Bẩn thỉu", "description": "Con thấy một thứ rất bẩn thỉu.", "image_path": "/assets/images/scenarios/filthy.jpg"},
        {"level": 3, "target_emotion": "ghê tởm", "title": "Không thích", "description": "Con cảm thấy rất không thích điều này.", "image_path": "/assets/images/scenarios/dislike.jpg"},
        {"level": 3, "target_emotion": "ghê tởm", "title": "Ghê sợ", "description": "Con cảm thấy ghê sợ với điều gì đó.", "image_path": "/assets/images/scenarios/repulsed.jpg"},
    ]
    
    # Insert scenarios vào game_content
    inserted_count = 0
    for scenario in scenarios:
        content_id = str(uuid4())
        try:
            db.execute(text("""
                INSERT INTO game_content (content_id, game_id, level, content_type, media_path, question_text, correct_answer, emotion, explanation)
                VALUES (:content_id, :game_id, :level, 'image', :image_path, :title, :target_emotion, :target_emotion, :description)
            """), {
                'content_id': content_id,
                'game_id': game_id,
                'level': scenario['level'],
                'image_path': scenario['image_path'],
                'title': scenario['title'],
                'target_emotion': scenario['target_emotion'],
                'description': scenario['description']
            })
            inserted_count += 1
            print(f"[OK] Inserted scenario: Level {scenario['level']} - {scenario['title']} ({scenario['target_emotion']})")
        except Exception as e:
            print(f"[WARNING] Error inserting scenario {scenario['title']}: {str(e)}")
            continue
    
    db.commit()
    print(f"\n[SUCCESS] Successfully seeded {inserted_count} scenarios for Game CV!")
    print(f"   Level 1: {sum(1 for s in scenarios if s['level'] == 1)} scenarios")
    print(f"   Level 2: {sum(1 for s in scenarios if s['level'] == 2)} scenarios")
    print(f"   Level 3: {sum(1 for s in scenarios if s['level'] == 3)} scenarios")
    
except Exception as e:
    db.rollback()
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

