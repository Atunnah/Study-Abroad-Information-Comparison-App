# import g4f
# import tkinter as tk
# from .database_helper import DatabaseHelper
# from .text_to_sql import TextToSQLEngine
# from .router import IntentRouter          
# from .local_chitchat import LocalChitchatEngine 

# class ChatEngine:
#     """Engine điều phối chính: Router -> Local LLM (Chitchat) hoặc Online LLM (DB)"""
    
#     def __init__(self, system_prompt, db_path="university.db"):
#         self.system_prompt = system_prompt
#         # History này dùng cho luồng Domain (Online LLM)
#         self.chat_history = [{"role": "system", "content": system_prompt}]
        
#         self.client = g4f.Client()
        
#         # Khởi tạo database helper và text-to-sql engine
#         self.db_helper = DatabaseHelper(db_path)
#         self.text_to_sql = TextToSQLEngine(self.db_helper)
        
#         # --- KHỞI TẠO ROUTER & CHITCHAT ---
#         self.router = IntentRouter()
        
#         print("[System] Đang khởi động Chitchat Engine...")
#         try:
#             self.local_engine = LocalChitchatEngine()
#         except Exception as e:
#             print(f"❌ Lỗi khởi tạo Chitchat: {e}")
#             self.local_engine = None

#     def _needs_database_query(self, user_text):
#         """Kiểm tra xem câu hỏi có cần truy vấn database không"""
#         keywords = [
#             'tìm', 'tìm kiếm', 'tra cứu', 'liệt kê', 'danh sách',
#             'có bao nhiêu', 'những trường nào', 'trường nào',
#             'học phí', 'gpa', 'ielts', 'toefl', 'học bổng',
#             'yêu cầu', 'điều kiện', 'so sánh', 'xếp hạng',
#             'ở quốc gia', 'tại', 'của', 'giá', 'tiền'
#         ]
#         user_text_lower = user_text.lower()
#         return any(keyword in user_text_lower for keyword in keywords)

#     def ask_stream(self, user_text, output_widget, on_response_start, status_callback, stop_event):
#         """
#         Xử lý câu hỏi:
#         1. Router phân loại.
#         2. Nếu Chitchat -> Dùng self.local_engine (Gemini).
#         3. Nếu Domain -> Dùng Logic cũ (Text2SQL + g4f).
#         """
#         try:
#             # --- BƯỚC 1: PHÂN LOẠI Ý ĐỊNH ---
#             intent = self.router.classify(user_text)
#             print(f"[ROUTER] User Input: '{user_text}' -> Intent: {intent}")

#             # =================================================================
#             # TRƯỜNG HỢP 1: CHITCHAT (Xã giao - Dùng Engine Gemini)
#             # =================================================================
#             if intent == 'CHITCHAT':
#                 # Báo cho UI biết đã bắt đầu
#                 output_widget.after(0, on_response_start)
                
#                 if self.local_engine:
#                     # Streaming từ Gemini
#                     for chunk in self.local_engine.generate_response_stream(user_text):
#                         if stop_event.is_set():
#                             self._handle_cancel(output_widget, status_callback)
#                             return
                        
#                         output_widget.config(state="normal")
#                         output_widget.insert(tk.END, chunk, "assistant_msg")
#                         output_widget.config(state="disabled")
#                         output_widget.see("end")
#                 else:
#                     # Fallback nếu engine bị lỗi khởi tạo
#                     output_widget.config(state="normal")
#                     output_widget.insert(tk.END, "Hệ thống chitchat đang khởi động hoặc gặp lỗi, vui lòng thử câu hỏi về du học nhé!", "assistant_msg")
#                     output_widget.config(state="disabled")
                
#                 # Kết thúc luồng Chitchat
#                 self._finalize_ui(output_widget, status_callback)
#                 return

#             # =================================================================
#             # TRƯỜNG HỢP 2: DOMAIN (Nghiệp vụ - Có ngữ cảnh)
#             # =================================================================
            
#             # 1. Lưu user message vào history TRƯỚC khi xử lý DB 
#             # (Để câu hỏi này cũng nằm trong context khi TextToSQL xử lý)
#             self.chat_history.append({"role": "user", "content": user_text})
            
#             db_data = None
            
#             # --- 2.1: SUY NGHĨ & TRUY VẤN DB ---
#             if self._needs_database_query(user_text):
#                 if stop_event.is_set(): 
#                     self._handle_cancel(output_widget, status_callback)
#                     return 

#                 # [THAY ĐỔI QUAN TRỌNG]: Truyền lịch sử chat vào TextToSQL
#                 # Truyền toàn bộ history trừ câu cuối (vì câu cuối đã là user_text)
#                 # Hoặc truyền hết tùy vào logic prompt. Ở đây ta truyền self.chat_history[:-1]
#                 history_context = self.chat_history[:-1]
                
#                 success, sql_result = self.text_to_sql.generate_sql(user_text, history_context)
                
#                 if stop_event.is_set(): 
#                     self._handle_cancel(output_widget, status_callback)
#                     return 

#                 if success:
#                     sql_query = sql_result['sql']
#                     success_db, query_result = self.db_helper.execute_query(sql_query)
                    
#                     if success_db:
#                         db_data = query_result
#                         print(f"[DEBUG] SQL Executed: {sql_query}")
            
#             if stop_event.is_set(): 
#                 self._handle_cancel(output_widget, status_callback)
#                 return

#             # --- 2.2: CHUẨN BỊ PROMPT CUỐI ---
#             final_prompt = user_text
#             if db_data:
#                 final_prompt = f"""
# DỮ LIỆU TÌM ĐƯỢC TỪ DATABASE (Đây là sự thật duy nhất):
# {self._format_db_data(db_data)}

# YÊU CẦU TRẢ LỜI:
# 1. Chỉ sử dụng thông tin từ "DỮ LIỆU TÌM ĐƯỢC" ở trên.
# 2. Nếu dữ liệu rỗng hoặc không tìm thấy, hãy nói: "Xin lỗi, tôi không tìm thấy trường nào trong cơ sở dữ liệu phù hợp với tiêu chí của bạn."
# 3. KHÔNG ĐƯỢC tự bịa ra các trường không có trong danh sách trên.
# 4. Trình bày đẹp, dùng emoji.

# Câu hỏi của người dùng: {user_text}
# """
#             else:
#                 final_prompt = f"""
# TÌNH HUỐNG:
# User đang hỏi: "{user_text}" (trong ngữ cảnh đang tìm trường du học).
# Hệ thống đã tìm kiếm trong Database với các tiêu chí đó nhưng KẾT QUẢ TRẢ VỀ LÀ: 0 (KHÔNG CÓ TRƯỜNG NÀO).

# NHIỆM VỤ CỦA BẠN:
# 1. Hãy trả lời thẳng thắn với User rằng: Hiện tại trong dữ liệu hệ thống **không có trường nào đáp ứng được yêu cầu này** (ví dụ: ở Pháp mà không cần tiếng Anh).
# 2. Giải thích nhẹ nhàng: Hầu hết các trường (đặc biệt là trường công giá rẻ) đều yêu cầu chứng chỉ ngoại ngữ (Tiếng Anh hoặc Tiếng Pháp/Tiếng bản địa).
# 3. Đưa ra lời khuyên: Khuyên user nên chuẩn bị thi chứng chỉ hoặc tìm các chương trình dự bị tiếng trước.
# 4. Đừng dùng câu "Lỗi hệ thống", hãy trả lời như một tư vấn viên chuyên nghiệp.
# """
#             # --- 2.3: GỌI ONLINE AI (GPT-4o-mini via g4f) ---
#             stream = self.client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[
#                     {"role": "system", "content": "Bạn là tư vấn viên trung thực. Chỉ trả lời dựa trên dữ liệu được cung cấp có thật trong database."},
#                     {"role": "user", "content": final_prompt}
#                 ],
#                 stream=True,
#             )

#             full_reply = ""
#             first_chunk = True
            
#             for chunk in stream:
#                 if stop_event.is_set():
#                     self._handle_cancel(output_widget, status_callback)
#                     return

#                 delta = chunk.choices[0].delta
#                 if hasattr(delta, "content") and delta.content:
#                     if first_chunk:
#                         output_widget.after(0, on_response_start)
#                         first_chunk = False
                    
#                     full_reply += delta.content
                    
#                     output_widget.config(state="normal")
#                     output_widget.insert(tk.END, delta.content, "assistant_msg")
#                     output_widget.config(state="disabled")
#                     output_widget.see("end")

#             # Cập nhật câu trả lời vào history
#             self.chat_history.append({"role": "assistant", "content": full_reply})
#             self._finalize_ui(output_widget, status_callback)

#         except Exception as e:
#             if not stop_event.is_set():
#                 output_widget.config(state="normal")
#                 output_widget.insert("end", f"\n❌ Lỗi: {e}\n\n", "error")
#                 output_widget.config(state="disabled")
#             status_callback(False)

#     def _finalize_ui(self, output_widget, status_callback):
#         """Hàm phụ: Xuống dòng và báo kết thúc"""
#         output_widget.config(state="normal")
#         output_widget.insert(tk.END, "\n\n")
#         output_widget.config(state="disabled")
#         status_callback(False)

#     def _handle_cancel(self, output_widget, status_callback):
#         """Xử lý khi người dùng hủy"""
#         output_widget.config(state="normal")
#         output_widget.insert(tk.END, "\n⛔ [Đã dừng bởi người dùng]\n\n", "error")
#         output_widget.config(state="disabled")
#         output_widget.see("end")
#         status_callback(False)

#     def _format_db_data(self, data):
#         """Format dữ liệu database thành chuỗi dễ đọc"""
#         if not data:
#             return "Không có dữ liệu"
        
#         max_records = 10
#         limited_data = data[:max_records]
        
#         result = []
#         for i, record in enumerate(limited_data, 1):
#             result.append(f"\n[{i}] " + ", ".join([f"{k}: {v}" for k, v in record.items()]))
        
#         if len(data) > max_records:
#             result.append(f"\n... và {len(data) - max_records} kết quả khác")
        
#         return "\n".join(result)

#     def clear_history(self, system_prompt):
#         """Reset lịch sử chat"""
#         self.chat_history = [{"role": "system", "content": system_prompt}]




import g4f
import json
import tkinter as tk
from .database_helper import DatabaseHelper
from .text_to_sql import TextToSQLEngine
from .router import IntentRouter          
from .local_chitchat import LocalChitchatEngine 

class ChatEngine:
    """Engine điều phối chính: Router -> Local LLM (Chitchat) hoặc Online LLM (DB)"""
    
    def __init__(self, system_prompt, db_path="university.db"):
        self.system_prompt = system_prompt
        # History này dùng cho luồng Domain (Online LLM)
        self.chat_history = [{"role": "system", "content": system_prompt}]
        
        self.client = g4f.Client()
        
        # Khởi tạo database helper và text-to-sql engine
        self.db_helper = DatabaseHelper(db_path)
        self.text_to_sql = TextToSQLEngine(self.db_helper)
        
        # --- KHỞI TẠO ROUTER & CHITCHAT ---
        self.router = IntentRouter()
        
        print("[System] Đang khởi động Chitchat Engine...")
        try:
            self.local_engine = LocalChitchatEngine()
        except Exception as e:
            print(f"❌ Lỗi khởi tạo Chitchat: {e}")
            self.local_engine = None

    def _needs_database_query(self, user_text):
        """Luôn trả về True để đảm bảo mọi câu hỏi nghiệp vụ đều được check DB"""
        return True 

    def ask_stream(self, user_text, output_widget, on_response_start, status_callback, stop_event):
        try:
            # --- BƯỚC 1: PHÂN LOẠI Ý ĐỊNH ---
            intent = self.router.classify(user_text)
            print(f"[ROUTER] User Input: '{user_text}' -> Intent: {intent}")

            # =================================================================
            # TRƯỜNG HỢP 1: CHITCHAT
            # =================================================================
            if intent == 'CHITCHAT':
                output_widget.after(0, on_response_start)
                if self.local_engine:
                    for chunk in self.local_engine.generate_response_stream(user_text):
                        if stop_event.is_set():
                            self._handle_cancel(output_widget, status_callback)
                            return
                        output_widget.config(state="normal")
                        output_widget.insert(tk.END, chunk, "assistant_msg")
                        output_widget.config(state="disabled")
                        output_widget.see("end")
                else:
                    output_widget.config(state="normal")
                    output_widget.insert(tk.END, "Hệ thống đang khởi động...", "assistant_msg")
                    output_widget.config(state="disabled")
                
                self._finalize_ui(output_widget, status_callback)
                return

            # =================================================================
            # TRƯỜNG HỢP 2: DOMAIN (BROAD SEARCH + LLM FILTER)
            # =================================================================
            
            # 1. Lưu user message vào history
            self.chat_history.append({"role": "user", "content": user_text})
            
            db_data = None
            
            # --- 2.1: SUY NGHĨ & TRUY VẤN DB (BROAD SEARCH) ---
            # Truyền lịch sử chat vào để lấy context
            history_context = self.chat_history[:-1]
            success, sql_result = self.text_to_sql.generate_sql(user_text, history_context)
            
            if stop_event.is_set(): 
                self._handle_cancel(output_widget, status_callback)
                return 

            if success:
                sql_query = sql_result['sql']
                success_db, query_result = self.db_helper.execute_query(sql_query)
                
                if success_db:
                    db_data = query_result
                    print(f"[DEBUG] SQL Broad Search Executed: {sql_query}")
                    print(f"[DEBUG] Found {len(db_data)} candidates.")
            
            if stop_event.is_set(): 
                self._handle_cancel(output_widget, status_callback)
                return

            # --- 2.2: CHUẨN BỊ PROMPT LỌC TINH (LLM FILTERING) ---
            if db_data:
                # Prompt này biến AI thành bộ lọc thông minh
                final_prompt = f"""
NHIỆM VỤ: Bạn là chuyên gia tuyển sinh. Hãy phân tích và LỌC danh sách trường sau đây.

1. YÊU CẦU CỦA NGƯỜI DÙNG: "{user_text}"
   (Lưu ý kỹ các yêu cầu về Tiếng Anh, GPA, Học phí...)

2. DANH SÁCH ỨNG VIÊN (Dữ liệu thô từ Database):
{self._format_db_data(db_data)}

3. HƯỚNG DẪN XỬ LÝ:
   - Hãy đọc kỹ cột 'entry_requirements' của từng trường trong danh sách trên.
   - **So sánh** yêu cầu của trường với khả năng của người dùng.
   - **LOẠI BỎ** những trường không phù hợp (Ví dụ: User không có IELTS mà trường yêu cầu IELTS bắt buộc -> Loại).
   - **GIỮ LẠI** những trường phù hợp (Ví dụ: Trường có khóa dự bị, hoặc không ghi yêu cầu tiếng Anh, hoặc User đủ điểm).
   
4. ĐẦU RA:
   - Chỉ liệt kê những trường **PHÙ HỢP**.
   - Nếu sau khi lọc mà không còn trường nào, hãy nói: "Tôi đã tìm trong danh sách nhưng không thấy trường nào phù hợp hoàn toàn với yêu cầu của bạn."
   - Trình bày đẹp, ngắn gọn, dùng emoji.
"""
            else:
                final_prompt = f"""
TÌNH HUỐNG:
User đang hỏi: "{user_text}".
Hệ thống đã tìm kiếm rộng trong Database nhưng KẾT QUẢ TRẢ VỀ LÀ: 0 (KHÔNG CÓ TRƯỜNG NÀO).

NHIỆM VỤ:
1. Thông báo khéo léo cho người dùng biết là không tìm thấy dữ liệu phù hợp trong hệ thống.
2. Gợi ý họ thử mở rộng tiêu chí tìm kiếm (ví dụ: đổi quốc gia khác, tăng mức học phí...).
"""

            # --- 2.3: GỌI ONLINE AI (GPT-4o-mini via g4f) ---
            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                # Chỉ gửi prompt lọc, không gửi toàn bộ history cũ để tránh nhiễu
                messages=[
                    {"role": "system", "content": "Bạn là trợ lý tư vấn du học trung thực, phân tích kỹ lưỡng."},
                    {"role": "user", "content": final_prompt}
                ],
                stream=True,
            )

            full_reply = ""
            first_chunk = True
            
            for chunk in stream:
                if stop_event.is_set():
                    self._handle_cancel(output_widget, status_callback)
                    return

                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    if first_chunk:
                        output_widget.after(0, on_response_start)
                        first_chunk = False
                    
                    full_reply += delta.content
                    output_widget.config(state="normal")
                    output_widget.insert(tk.END, delta.content, "assistant_msg")
                    output_widget.config(state="disabled")
                    output_widget.see("end")

            # Cập nhật câu trả lời vào history
            self.chat_history.append({"role": "assistant", "content": full_reply})
            self._finalize_ui(output_widget, status_callback)

        except Exception as e:
            if not stop_event.is_set():
                output_widget.config(state="normal")
                output_widget.insert("end", f"\n❌ Lỗi: {e}\n\n", "error")
                output_widget.config(state="disabled")
            status_callback(False)

    def _finalize_ui(self, output_widget, status_callback):
        output_widget.config(state="normal")
        output_widget.insert(tk.END, "\n\n")
        output_widget.config(state="disabled")
        status_callback(False)

    def _handle_cancel(self, output_widget, status_callback):
        output_widget.config(state="normal")
        output_widget.insert(tk.END, "\n⛔ [Đã dừng bởi người dùng]\n\n", "error")
        output_widget.config(state="disabled")
        output_widget.see("end")
        status_callback(False)

    def _format_db_data(self, data):
        """Format dữ liệu dạng JSON string để AI dễ đọc cấu trúc"""
        if not data:
            return "Không có dữ liệu"
        
        # Tăng giới hạn lên 15 để AI có không gian lọc
        max_records = 15
        limited_data = data[:max_records]
        
        result = []
        for i, record in enumerate(limited_data, 1):
            # Chuyển row thành chuỗi JSON để AI dễ parse
            # ensure_ascii=False để hiển thị tiếng Việt/ký tự đặc biệt đúng
            row_str = json.dumps(record, ensure_ascii=False)
            result.append(f"Candidate #{i}: {row_str}")
        
        return "\n".join(result)

    def clear_history(self, system_prompt):
        self.chat_history = [{"role": "system", "content": system_prompt}]