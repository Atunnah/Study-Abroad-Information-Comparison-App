# engine/search_tool.py
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

class OnlineSearchEngine:
    def __init__(self, local_engine):
        # Lấy API Key từ biến môi trường hoặc điền trực tiếp
        self.api_key = os.getenv("TAVILY_API_KEY") 
        self.client = TavilyClient(api_key=self.api_key) if self.api_key else None
        self.local_engine = local_engine # Dùng Gemini để tóm tắt

    def search_and_answer(self, user_query, context_info=""):
        """
        1. Search Tavily
        2. Đưa kết quả search cho Gemini tóm tắt
        """
        if not self.client:
            yield "❌ Chưa cấu hình Tavily API Key."
            return

        try:
            # 1. Search Online
            print(f"[Tavily] Searching: {user_query}")
            search_result = self.client.search(
                query=user_query,
                search_depth="advanced",
                max_results=5,
                include_answer=True
            )
            
            context_text = search_result.get("answer", "")
            results = search_result.get("results", [])
            
            web_content = "\n".join([f"- [{r['title']}]({r['url']}): {r['content'][:300]}..." for r in results])

            # 2. Prompt cho Gemini tóm tắt
            prompt = f"""
NHIỆM VỤ: Bạn là chuyên gia tư vấn du học. Dữ liệu trong Database nội bộ bị thiếu, nên đây là thông tin TÌM KIẾM ONLINE MỚI NHẤT.

CÂU HỎI CỦA USER: "{user_query}"
BỐI CẢNH (Trường đang tìm): {context_info}

THÔNG TIN TỪ WEB (TAVILY):
{web_content}

YÊU CẦU:
- Trả lời câu hỏi dựa trên thông tin web vừa tìm được.
- Nếu tìm thấy học phí hoặc yêu cầu đầu vào, hãy ghi rõ.
- Cuối câu trả lời, hãy dẫn nguồn (URL) để user tham khảo.
"""
            # Gọi Gemini Stream
            for chunk in self.local_engine.generate_filter_stream(prompt):
                yield chunk

        except Exception as e:
            yield f"❌ Lỗi khi tìm kiếm online: {str(e)}"