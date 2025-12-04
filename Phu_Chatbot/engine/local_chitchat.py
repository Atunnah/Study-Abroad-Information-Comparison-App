# engine/local_chitchat.py
import google.generativeai as genai
import random
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_KEY")

class LocalChitchatEngine:
    """
    Engine chitchat sử dụng Google Gemini API.
    Sử dụng cố định model Flash để tối ưu tốc độ, bỏ qua bước dò tìm.
    """
    def __init__(self):
        self.api_key = GEMINI_KEY
        
        self.model = None
        self.chat_session = None
        
        # Cấu hình model cố định
        # Lưu ý: Hiện tại chưa có bản 2.5, bản Flash mới nhất là "gemini-1.5-flash"
        # Nếu muốn dùng bản 2.0 (thử nghiệm), hãy đổi thành "gemini-2.0-flash-exp"
        target_model = "gemini-2.5-flash"

        try:
            genai.configure(api_key=self.api_key)
            
            print(f"[Gemini] Đang kết nối với model: {target_model}...")
            
            # Khởi tạo trực tiếp model, không cần list_models() dò tìm nữa
            self.model = genai.GenerativeModel(target_model)
            self.chat_session = self.model.start_chat(history=[])
            
            # System prompt
            self.system_prompt = "Bạn là trợ lý ảo tư vấn du học điềm đạm, hiểu biết và lịch sự. Hãy trả lời xã giao ngắn gọn, tự nhiên bằng tiếng Việt."
            self.chat_session.send_message(self.system_prompt)
            
            print("✅ Kết nối Gemini thành công!")

        except Exception as e:
            print(f"❌ Lỗi cấu hình Gemini: {e}")
            # Nếu lỗi 404 nghĩa là tài khoản chưa hỗ trợ Flash, hãy thử đổi target_model = "gemini-pro"

    def generate_response_stream(self, user_text):
        """
        Gửi tin nhắn đến Gemini và stream câu trả lời về
        """
        if not self.model or not self.chat_session:
            yield self._get_fallback_response()
            return

        try:
            # Gửi tin nhắn (stream=True)
            response = self.chat_session.send_message(user_text, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            print(f"❌ [Lỗi Gemini API]: {e}")
            yield self._get_fallback_response()

    def _get_fallback_response(self):
        """Trả lời cứng khi lỗi"""
        responses = [
            "Kết nối AI đang gặp chút trục trặc, bạn chờ xíu nhé!",
            "Mình đây! Bạn cần giúp gì về du học không?",
            "Chào bạn, mình đang khởi động lại server, quay lại ngay đây.",
            "Alo, mình nghe nè! (Mạng đang hơi lag tí 😅)"
        ]
        return random.choice(responses)