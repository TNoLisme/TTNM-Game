from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

from dotenv import load_dotenv
import google.generativeai as genai

# Đọc biến môi trường từ file .env (nếu có)
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

router = APIRouter(prefix="/assistant", tags=["assistant"])


class ChatRequest(BaseModel):
    game_id: str  # ví dụ: "game_click_3", "gameCV"
    level: int | None = None
    message: str  # câu hỏi của người chơi


class ChatResponse(BaseModel):
    reply: str


# Mô tả luật/cách chơi cho từng game. Các chuỗi này đóng vai trò như "tài liệu game" để nhét vào prompt.
GAME_RULES: dict[str, str] = {
    # Trang trang chủ / tổng quan
    "home": (
        "Đây là trang chính của EmoGarden. Bé có thể xem các game gần đây, biểu đồ cảm xúc và đi tới mục Học hoặc Chơi game.\n"
        "Trợ lý có thể gợi ý nên vào game nào hoặc học cảm xúc nào dựa trên mô tả của phụ huynh/bé.\n"
    ),

    # Màn chọn game / chọn level
    "select_game": (
        "Đây là màn CHỌN GAME.\n"
        "Có 4 nhóm trò chơi chính về cảm xúc, mỗi game rèn kỹ năng khác nhau (nhận diện, ghép mặt, phân tích tình huống, dùng camera).\n"
        "Trợ lý nên gợi ý bé chọn game phù hợp với cảm xúc đang yếu hoặc sở thích (ví dụ: thích vẽ mặt thì chơi Xưởng cảm xúc).\n"
    ),
    "level_select": (
        "Đây là màn CHỌN CẤP ĐỘ cho game nhận diện cảm xúc.\n"
        "MỤC TIÊU: Bé chọn level (dễ → khó) để làm bài. Hoàn thành level trước mới mở được level sau.\n"
        "CÁCH CHƠI: Chọn 1 level trong lưới, đọc mô tả, sau đó bấm nút bắt đầu để vào game tương ứng.\n"
    ),

    # Game click 2 – Xưởng Cảm Xúc (xây khuôn mặt từ 3 bộ phận)
    "game_click_2": (
        "TÊN GAME: Xưởng Cảm Xúc.\n"
        "MỤC TIÊU: Bé lắp ráp đủ 3 bộ phận (lông mày, mắt, miệng) để khuôn mặt thể hiện đúng cảm xúc của tình huống.\n"
        "CÁCH CHƠI:\n"
        "1. Đọc phần tình huống ở bên trái (tiếng Anh nhưng giáo viên có thể giải thích thêm).\n"
        "2. Bên phải là khung khuôn mặt trống chia 3 phần: trên là lông mày, giữa là mắt, dưới là miệng.\n"
        "3. Bấm nút Lông mày / Mắt / Miệng để lần lượt đổi qua 6 lựa chọn cảm xúc khác nhau.\n"
        "4. Khi bé cảm thấy khuôn mặt đã khớp với tình huống, bấm nút 'Kiểm tra'.\n"
        "5. Nếu đúng, hiện thông báo chúc mừng; nếu sai, game gợi ý bé thử thay đổi và chơi lại.\n"
        "6. Bé có thể bấm 'Bắt đầu lại' để xóa lựa chọn hiện tại, hoặc 'Bỏ qua' để sang tình huống khác.\n"
        "GỢI Ý CHO TRỢ LÝ: Giải thích cho bé nên chú ý lông mày, mắt, miệng thay đổi ra sao khi vui, buồn, sợ, tức giận...\n"
    ),

    # Game click 3 – Ai là ai? (kéo thả tên vào khuôn mặt, đã có mô tả cơ bản)
    "game_click_3": (
        "TÊN GAME: Ai là ai.\n"
        "MỤC TIÊU: Bé kéo đúng thẻ tên vào khuôn mặt phù hợp với tình huống và cảm xúc.\n"
        "CÁCH CHƠI:\n"
        "1. Đọc kỹ phần 'Tình huống' ở khung trên cùng (mô tả ngắn về các bạn nhỏ và cảm xúc của từng bạn).\n"
        "2. Quan sát từng khuôn mặt trong lưới: ai đang vui, buồn, giận, ngạc nhiên...\n"
        "3. Kéo thẻ tên ở kho thẻ phía dưới vào đúng ô bên dưới mỗi khuôn mặt. Mỗi tên dùng đúng một lần.\n"
        "4. Khi đã đặt đủ, bấm 'Nộp bài' để kiểm tra kết quả.\n"
        "5. Nếu sai, game cho biết chỗ sai và có thể cho chơi lại hoặc sang câu mới.\n"
        "GỢI Ý CHO TRỢ LÝ: Khuyến khích bé giải thích vì sao bạn đó đang có cảm xúc đó (dựa trên tình huống).\n"
    ),

    # Game click 4 – Thám tử cảm xúc (chọn 1 trong 6 cảm xúc cho tình huống)
    "game_click_4": (
        "TÊN GAME: Thám tử cảm xúc.\n"
        "MỤC TIÊU: Bé đọc tình huống và chọn cảm xúc phù hợp nhất trong 6 lựa chọn.\n"
        "CÁCH CHƠI:\n"
        "1. Đọc đoạn mô tả tình huống ở thẻ câu hỏi (có thể kèm hình hoặc tiếng đọc lại).\n"
        "2. Nhìn 6 nút cảm xúc (Vui, Buồn, Ngạc nhiên, Tức giận, Sợ hãi, Ghê tởm) phía dưới.\n"
        "3. Chọn cảm xúc mà bé nghĩ là phù hợp nhất với nhân vật trong tình huống.\n"
        "4. Game hiển thị đúng/sai, cộng điểm và cho biết đáp án đúng nếu bé chọn sai.\n"
        "5. Bé có thể bấm 'Gợi ý' để đọc phần giải thích thêm, hoặc 'Nghe lại câu hỏi'.\n"
        "6. Bấm 'Tiếp tục' để sang câu tiếp theo; khi hết câu sẽ hiện thông báo hoàn thành và tổng điểm.\n"
    ),

    # Game nhận diện cảm xúc với hình ảnh trắc nghiệm – Chiếc hộp cảm xúc
    "recognize_emotion": (
        "TÊN GAME: Chiếc hộp cảm xúc.\n"
        "MỤC TIÊU: Bé nhìn hình (hoặc đọc tình huống ngắn) và chọn đúng cảm xúc trong 6 lựa chọn.\n"
        "CÁCH CHƠI:\n"
        "1. Mỗi câu hỏi có thể có một bức ảnh và một câu mô tả đi kèm.\n"
        "2. Bên dưới là 6 nút cảm xúc cố định: Vui vẻ, Buồn bã, Ngạc nhiên, Tức giận, Sợ hãi, Ghê tởm.\n"
        "3. Bé chọn 1 cảm xúc mà bé nghĩ là đúng với bức ảnh/tình huống.\n"
        "4. Nếu chưa chọn đã bấm sang câu mới, game nhắc bé phải chọn trước.\n"
        "5. Mỗi câu đúng cộng điểm; sau nhiều lần sai cùng một cảm xúc, game có thể mở 'Góc học tập' để bé xem thẻ học thêm về cảm xúc đó.\n"
        "6. Có nút 'Gợi ý' và 'Nghe lại câu hỏi' để hỗ trợ bé.\n"
    ),

    # Game CV dùng camera – 2 chế độ: theo tình huống (GV1) và theo yêu cầu (GV2)
    "gameCV": (
        "TÊN GAME: Game CV – Nhận diện cảm xúc bằng khuôn mặt.\n"
        "CÓ HAI CHẾ ĐỘ CHÍNH:\n"
        "- GV1 (Câu chuyện trên khuôn mặt): hệ thống hiển thị một tình huống, bé đọc và thể hiện khuôn mặt theo cảm xúc được yêu cầu trong câu chuyện.\n"
        "- GV2 (Thử thách cảm xúc): bé chọn trước một cảm xúc (ví dụ: vui), sau đó game liên tục yêu cầu bé thể hiện đúng cảm xúc đó trong nhiều tình huống.\n"
        "CÁCH CHƠI CHUNG:\n"
        "1. Cho phép truy cập camera, khuôn mặt bé sẽ hiện ở khung bên phải.\n"
        "2. Đọc tình huống/yêu cầu ở bên trái, chú ý dòng Cảm xúc mục tiêu (vui, buồn, tức giận...).\n"
        "3. Bấm 'Bắt đầu', sau đó biểu cảm khuôn mặt giống với cảm xúc mục tiêu. Hệ thống sẽ nhận diện và hiển thị % khớp.\n"
        "4. Khi bé giữ được biểu cảm đúng đủ lâu và tỉ lệ nhận diện đủ cao, game tính là HOÀN THÀNH màn đó.\n"
        "5. Nếu bé sai nhiều lần với một cảm xúc, game có thể mở 'Góc học cảm xúc' để giải thích thêm và gợi ý xem video trên trang Học.\n"
        "6. Hoàn thành nhiều màn, game hiển thị tổng kết và gợi ý luyện thêm cảm xúc nào.\n"
        "GỢI Ý CHO TRỢ LÝ: Khi bé hỏi, tập trung giải thích cách đứng trước camera, giữ khuôn mặt rõ, và gợi ý cách thể hiện từng cảm xúc (mắt, miệng, lông mày).\n"
    ),
}


def build_prompt(req: ChatRequest) -> str:
    rules = GAME_RULES.get(req.game_id, "")

    prompt = f"""
Bạn là trợ lý ảo của trò chơi EmoGarden.

Nhiệm vụ của bạn:
- Giải thích LUẬT CHƠI và cách qua màn cho từng game.
- Trả lời bằng TIẾNG VIỆT, câu ngắn gọn, dễ hiểu cho trẻ 6-10 tuổi.
- Mỗi lần trả lời chỉ dùng 1-3 câu ngắn. Tránh liệt kê quá chi tiết.
- KHÔNG dùng Markdown: không dùng *, -, **, tiêu đề, bảng hay danh sách đánh số.
- Nếu cần nêu nhiều ý, hãy gộp trong 1-2 câu văn nói tự nhiên, giống giáo viên nói chuyện với học sinh.
- Không nói chuyện ngoài lề (chỉ nói về game và cảm xúc trong game).
- Nếu câu hỏi không liên quan tới game hoặc bạn không đủ thông tin, hãy nói nhẹ nhàng rằng bạn không trả lời được.

Thông tin game hiện tại:
- game_id: {req.game_id}
- level: {req.level}

Luật/mô tả game (nếu có):
{rules}

Người chơi hỏi: {req.message}
""".strip()

    return prompt


def build_fallback_reply(req: ChatRequest) -> str:
    """Sinh câu trả lời fallback thân thiện, không nhắc tới lỗi kỹ thuật.

    Ưu tiên tóm tắt lại luật/mục tiêu game hiện tại dựa trên GAME_RULES.
    """
    user_text = (req.message or "").lower()
    rules = (GAME_RULES.get(req.game_id, "") or "").strip()

    # Trường hợp đặc biệt cho màn CHỌN GAME: gợi ý 1 trò chơi cụ thể
    if req.game_id == "select_game":
        suggest_keywords = [
            "nên chơi", "nen choi", "chơi gì", "choi gi",
            "gợi ý", "goi y", "trò đầu tiên", "tro dau tien",
            "chọn cho", "chon cho", "nên chơi trò nào", "nen choi tro nao",
        ]
        if any(kw in user_text for kw in suggest_keywords):
            return (
                "Nếu là lần đầu, mình gợi ý con chơi game 'Chiếc hộp cảm xúc' trước. "
                "Đó là game nhìn hình và chọn cảm xúc, khá dễ và giúp con làm quen với cảm xúc cơ bản."
            )

    if rules:
        # Lấy 1-2 câu ngắn đầu tiên từ luật game để nhắc lại cho bé
        sentences: list[str] = []
        current = []
        for ch in rules:
            current.append(ch)
            if ch in ".!?":
                sentence = "".join(current).strip()
                if sentence:
                    sentences.append(sentence)
                current = []
                if len(sentences) >= 2:
                    break

        # Nếu không bắt được câu theo dấu chấm, lấy dòng đầu tiên
        if not sentences:
            first_line = rules.splitlines()[0].strip()
            if first_line:
                sentences.append(first_line)

        summary = " ".join(sentences)
        if summary:
            return (
                "Bây giờ mình nhắc nhanh lại luật game này cho con nhé: "
                f"{summary}"
            )

    # Không có luật game cụ thể
    return (
        "Hiện tại mình chưa trả lời chi tiết được. "
        "Con cứ làm theo hướng dẫn trên màn hình game hoặc hỏi người lớn giúp nhé."
    )


@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(req: ChatRequest) -> ChatResponse:
    """Endpoint chính cho chatbot hướng dẫn chơi game.

    FE sẽ gửi: game_id, level (tuỳ chọn), message.
    Backend gọi Gemini với luật game + câu hỏi, rồi trả về câu trả lời tiếng Việt.
    """

    if not GEMINI_API_KEY:
        # Không cấu hình key: trả về fallback thân thiện thay vì 500
        return ChatResponse(reply=build_fallback_reply(req))

    prompt = build_prompt(req)

    try:
        # Dùng alias gemini-flash-latest (nội suy sang models/gemini-flash-latest)
        # Model này có trong list_models và hỗ trợ generateContent.
        model = genai.GenerativeModel("gemini-flash-latest")
        result = model.generate_content(prompt)

        text: str = ""

        # 1. Thử dùng tiện ích result.text, nhưng bọc try để tránh lỗi "response.text quick accessor"
        try:
            maybe_text = getattr(result, "text", None)
            if maybe_text:
                text = str(maybe_text).strip()
        except Exception:
            text = ""

        # 2. Nếu vẫn chưa có, cố gắng đọc từ candidates[0].content.parts
        if not text:
            try:
                candidates = getattr(result, "candidates", None) or []
                if candidates:
                    first = candidates[0]
                    content = getattr(first, "content", None)
                    parts = getattr(content, "parts", None) or []
                    collected: list[str] = []
                    for p in parts:
                        # Mỗi part có thể có thuộc tính text
                        t = getattr(p, "text", None)
                        if t:
                            collected.append(str(t))
                    if collected:
                        text = "".join(collected).strip()
            except Exception:
                text = ""
    except Exception as e:
        # Lỗi mạng hoặc lỗi SDK: log nội bộ, nhưng vẫn trả lời fallback thân thiện
        print(f"[assistant_controller] Gemini error: {e}")
        text = ""

    if not text:
        text = build_fallback_reply(req)

    return ChatResponse(reply=text)
