# engine/local_chitchat.py
import google.generativeai as genai
import random

class LocalChitchatEngine:
    """
    Engine chitchat sử dụng Google Gemini API.
    Tự động dò tìm model khả dụng để tránh lỗi 404.
    """
    def __init__(self):
        # ---------------------------------------------------------
        # [QUAN TRỌNG] Dán API Key của bạn vào đây
        # ---------------------------------------------------------
        self.api_key = "AIzaSyCHnYW8eDmqKOQzZC5nyfpm665XkO54e1Y" 
        
        self.model = None
        self.chat_session = None
        
        # Cấu hình và tự động chọn model
        try:
            genai.configure(api_key=self.api_key)
            
            # 1. Lấy danh sách tất cả model mà key này dùng được
            all_models = list(genai.list_models())
            
            # 2. Lọc ra các model hỗ trợ chat (generateContent)
            valid_models = [
                m.name for m in all_models 
                if 'generateContent' in m.supported_generation_methods
            ]
            
            print(f"[Gemini] Các model khả dụng: {valid_models}")
            
            if not valid_models:
                print("❌ Không tìm thấy model nào hỗ trợ chat trong API Key này.")
                return

            # 3. Chiến thuật chọn model: Ưu tiên Flash -> Pro -> Cái đầu tiên tìm thấy
            # Tìm model có chữ 'flash' (nhanh nhất)
            chosen_model_name = next((m for m in valid_models if 'flash' in m), None)
            
            # Nếu không có flash, tìm 'pro'
            if not chosen_model_name:
                chosen_model_name = next((m for m in valid_models if 'pro' in m), None)
            
            # Nếu không có cả hai, lấy cái đầu tiên trong danh sách
            if not chosen_model_name:
                chosen_model_name = valid_models[0]
                
            print(f"✅ Đã tự động chọn model: {chosen_model_name}")

            # 4. Khởi tạo
            self.model = genai.GenerativeModel(chosen_model_name)
            self.chat_session = self.model.start_chat(history=[])
            
            # System prompt
            self.system_prompt = "Bạn là trợ lý ảo tư vấn du học vui tính. Hãy trả lời xã giao ngắn gọn, tự nhiên bằng tiếng Việt."
            self.chat_session.send_message(self.system_prompt)
            
        except Exception as e:
            print(f"❌ Lỗi cấu hình Gemini: {e}")

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