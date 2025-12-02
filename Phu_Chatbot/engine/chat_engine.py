# # import g4f

# # class ChatEngine:
# #     def __init__(self, system_prompt):
# #         self.chat_history = [{"role": "system", "content": system_prompt}]
# #         self.client = g4f.Client()

# #     def ask_stream(self, user_text, output_widget, on_response_start=None, status_callback=None):
# #         try:
# #             self.chat_history.append({"role": "user", "content": user_text})

# #             stream = self.client.chat.completions.create(
# #                 model="gpt-4o-mini",
# #                 messages=self.chat_history,
# #                 stream=True,
# #             )

# #             full_reply = ""
# #             first_chunk = True
            
# #             for chunk in stream:
# #                 delta = chunk.choices[0].delta
# #                 if hasattr(delta, "content") and delta.content:
# #                     # ✅ Gọi callback khi nhận chunk đầu tiên
# #                     if first_chunk and on_response_start:
# #                         on_response_start()
# #                         first_chunk = False
                    
# #                     full_reply += delta.content
# #                     output_widget.config(state="normal")
# #                     output_widget.insert("end", delta.content, "assistant_text")
# #                     output_widget.config(state="disabled")
# #                     output_widget.see("end")

# #             self.chat_history.append({"role": "assistant", "content": full_reply})

# #             output_widget.config(state="normal")
# #             output_widget.insert("end", "\n\n")
# #             output_widget.config(state="disabled")
            
# #             if status_callback:
# #                 status_callback(False)

# #         except Exception as e:
# #             output_widget.config(state="normal")
# #             output_widget.insert("end", f"\n❌ Lỗi: {e}\n\n", "error")
# #             output_widget.config(state="disabled")
# #             if status_callback:
# #                 status_callback(False)

# #     def clear_history(self, system_prompt):
# #         self.chat_history = [{"role": "system", "content": system_prompt}]



# import g4f
# from .database_helper import DatabaseHelper
# from .text_to_sql import TextToSQLEngine

# class ChatEngine:
#     """Engine để giao tiếp với AI model và database"""
    
#     def __init__(self, system_prompt, db_path="university.db"):
#         """
#         Khởi tạo ChatEngine
        
#         Args:
#             system_prompt: System prompt cho AI
#             db_path: Đường dẫn đến database
#         """
#         self.chat_history = [{"role": "system", "content": system_prompt}]
#         self.client = g4f.Client()
        
#         # Khởi tạo database helper và text-to-sql engine
#         self.db_helper = DatabaseHelper(db_path)
#         self.text_to_sql = TextToSQLEngine(self.db_helper)

#     def _needs_database_query(self, user_text):
#         """
#         Kiểm tra xem câu hỏi có cần truy vấn database không
        
#         Args:
#             user_text: Câu hỏi của người dùng
            
#         Returns:
#             bool: True nếu cần truy vấn database
#         """
#         keywords = [
#             'tìm', 'tìm kiếm', 'tra cứu', 'liệt kê', 'danh sách',
#             'có bao nhiêu', 'những trường nào', 'trường nào',
#             'học phí', 'gpa', 'ielts', 'toefl', 'học bổng',
#             'yêu cầu', 'điều kiện', 'so sánh', 'xếp hạng',
#             'ở quốc gia', 'tại', 'của'
#         ]
        
#         user_text_lower = user_text.lower()
#         return any(keyword in user_text_lower for keyword in keywords)

#     def ask_stream(self, user_text, output_widget, on_response_start=None, status_callback=None):
#         """
#         Gửi tin nhắn và nhận phản hồi dạng stream
        
#         Args:
#             user_text: Nội dung tin nhắn từ user
#             output_widget: Widget để hiển thị kết quả
#             on_response_start: Callback khi bắt đầu nhận response
#             status_callback: Callback để cập nhật trạng thái
#         """
#         try:
#             self.chat_history.append({"role": "user", "content": user_text})
            
#             # Kiểm tra xem có cần truy vấn database không
#             db_data = None
#             sql_info = None
            
#             if self._needs_database_query(user_text):
#                 # Hiển thị thông báo đang tạo SQL
#                 output_widget.config(state="normal")
#                 output_widget.insert("end", "🔍 Đang phân tích câu hỏi...\n", "status")
#                 output_widget.config(state="disabled")
#                 output_widget.see("end")
                
#                 # Tạo SQL query
#                 success, sql_result = self.text_to_sql.generate_sql(user_text)
                
#                 if success:
#                     sql_query = sql_result['sql']
#                     explanation = sql_result.get('explanation', '')
                    
#                     # Hiển thị SQL query
#                     output_widget.config(state="normal")
#                     output_widget.insert("end", f"📝 SQL: {sql_query}\n", "sql")
#                     if explanation:
#                         output_widget.insert("end", f"💡 {explanation}\n", "explanation")
#                     output_widget.insert("end", "⏳ Đang truy vấn database...\n", "status")
#                     output_widget.config(state="disabled")
#                     output_widget.see("end")
                    
#                     # Thực thi query
#                     success, query_result = self.db_helper.execute_query(sql_query)
                    
#                     if success:
#                         db_data = query_result
#                         output_widget.config(state="normal")
#                         output_widget.insert("end", f"✅ Tìm thấy {len(db_data)} kết quả\n\n", "success")
#                         output_widget.config(state="disabled")
#                         sql_info = {
#                             'query': sql_query,
#                             'explanation': explanation,
#                             'result_count': len(db_data)
#                         }
#                     else:
#                         output_widget.config(state="normal")
#                         output_widget.insert("end", f"❌ Lỗi truy vấn: {query_result}\n\n", "error")
#                         output_widget.config(state="disabled")
#                 else:
#                     output_widget.config(state="normal")
#                     output_widget.insert("end", f"❌ {sql_result}\n\n", "error")
#                     output_widget.config(state="disabled")
            
#             # Tạo prompt cho AI với dữ liệu từ database (nếu có)
#             final_prompt = user_text
#             if db_data:
#                 final_prompt = f"""Câu hỏi: {user_text}

# Dữ liệu từ database (đã truy vấn thành công):
# {self._format_db_data(db_data)}

# Hãy phân tích và trả lời câu hỏi dựa trên dữ liệu trên. Trả lời chi tiết, có cấu trúc rõ ràng."""

#             # Gọi AI để tạo response
#             stream = self.client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=self.chat_history[:-1] + [{"role": "user", "content": final_prompt}],
#                 stream=True,
#             )

#             full_reply = ""
#             first_chunk = True
            
#             for chunk in stream:
#                 delta = chunk.choices[0].delta
#                 if hasattr(delta, "content") and delta.content:
#                     if first_chunk and on_response_start:
#                         on_response_start()
#                         first_chunk = False
                    
#                     full_reply += delta.content
#                     output_widget.config(state="normal")
#                     output_widget.insert("end", delta.content, "assistant_text")
#                     output_widget.config(state="disabled")
#                     output_widget.see("end")

#             self.chat_history.append({"role": "assistant", "content": full_reply})

#             output_widget.config(state="normal")
#             output_widget.insert("end", "\n\n")
#             output_widget.config(state="disabled")
            
#             if status_callback:
#                 status_callback(False)

#         except Exception as e:
#             output_widget.config(state="normal")
#             output_widget.insert("end", f"\n❌ Lỗi: {e}\n\n", "error")
#             output_widget.config(state="disabled")
#             if status_callback:
#                 status_callback(False)

#     def _format_db_data(self, data):
#         """
#         Format dữ liệu database thành chuỗi dễ đọc
        
#         Args:
#             data: List of dicts từ database
            
#         Returns:
#             str: Dữ liệu đã format
#         """
#         if not data:
#             return "Không có dữ liệu"
        
#         # Giới hạn số lượng records để không quá dài
#         max_records = 10
#         limited_data = data[:max_records]
        
#         result = []
#         for i, record in enumerate(limited_data, 1):
#             result.append(f"\n[{i}] " + ", ".join([f"{k}: {v}" for k, v in record.items()]))
        
#         if len(data) > max_records:
#             result.append(f"\n... và {len(data) - max_records} kết quả khác")
        
#         return "\n".join(result)

#     def clear_history(self, system_prompt):
#         """
#         Reset lịch sử chat
        
#         Args:
#             system_prompt: System prompt mới
#         """
#         self.chat_history = [{"role": "system", "content": system_prompt}]

import g4f
import json
from .database_helper import DatabaseHelper
from .text_to_sql import TextToSQLEngine

class ChatEngine:
    """Engine để giao tiếp với AI model và database"""
    
    def __init__(self, system_prompt, db_path="universities_db.db"):
        self.chat_history = [{"role": "system", "content": system_prompt}]
        self.client = g4f.Client()
        
        # Database & Tools
        self.db_helper = DatabaseHelper(db_path)
        self.text_to_sql = TextToSQLEngine(self.db_helper)
        
        # ✅ NEW: Lưu ngữ cảnh tìm kiếm gần nhất (List các trường vừa tìm thấy)
        self.last_search_context = [] 

    def _contextualize_question(self, user_text):
        """
        Viết lại câu hỏi, thay thế các từ quy chiếu (này, đó, trên...) bằng tên thực thể cụ thể
        từ kết quả tìm kiếm trước đó.
        """
        if len(self.chat_history) <= 1:
            return user_text

        # Tạo context string từ kết quả tìm kiếm trước đó
        context_str = ""
        if self.last_search_context:
            # Lấy tên các trường từ lần tìm trước
            school_names = [item.get('name', '') for item in self.last_search_context[:5]] # Lấy tối đa 5 trường để prompt không quá dài
            context_str = f"Danh sách các trường vừa tìm thấy ở lượt trước: {', '.join(school_names)}"

        recent_history = self.chat_history[-2:]

        prompt = f"""
Nhiệm vụ: Viết lại câu hỏi của người dùng thành câu hỏi ĐẦY ĐỦ, CỤ THỂ để có thể truy vấn Database.

Ngữ cảnh:
1. Lịch sử chat: {str(recent_history)}
2. {context_str}

Yêu cầu xử lý:
- Nếu người dùng dùng từ thay thế (ví dụ: "các trường trên", "trường đó", "chúng", "họ"), hãy THAY THẾ bằng TÊN CỤ THỂ trong danh sách trường vừa tìm thấy.
- Ví dụ: User hỏi "yêu cầu của các trường trên là gì?" và context có "Đại học A, Đại học B" -> Viết lại: "Yêu cầu đầu vào của Đại học A và Đại học B là gì?"
- Giữ nguyên ý định tìm kiếm (tìm học phí, yêu cầu, học bổng...).

Câu hỏi gốc: "{user_text}"

Câu hỏi viết lại (chỉ trả về text):
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            rewritten_q = response.choices[0].message.content.strip()
            # print(f"DEBUG - Rewritten: {rewritten_q}") # Uncomment để debug xem AI viết lại thế nào
            return rewritten_q
        except:
            return user_text

    def _needs_database_query(self, user_text):
        keywords = [
            'tìm', 'tìm kiếm', 'tra cứu', 'liệt kê', 'danh sách',
            'có bao nhiêu', 'những trường nào', 'trường nào',
            'học phí', 'gpa', 'ielts', 'toefl', 'học bổng',
            'yêu cầu', 'điều kiện', 'so sánh', 'xếp hạng',
            'ở quốc gia', 'tại', 'của', 'chi phí', 'rẻ nhất', 'đắt nhất',
            'như thế nào', 'ra sao', 'gồm những gì'
        ]
        return any(keyword in user_text.lower() for keyword in keywords)

    def ask_stream(self, user_text, output_widget, on_response_start=None, status_callback=None):
        try:
            # 1. Contextualize: Viết lại câu hỏi dựa trên lịch sử + KẾT QUẢ DATABASE TRƯỚC ĐÓ
            processing_text = user_text
            if len(self.chat_history) > 1:
                processing_text = self._contextualize_question(user_text)
            
            # 2. Xử lý Database
            db_data = None
            sql_query_log = None
            
            if self._needs_database_query(processing_text):
                if status_callback: status_callback(True)
                
                # Tạo SQL từ câu hỏi ĐÃ VIẾT LẠI (chứa tên trường cụ thể)
                success, sql_result = self.text_to_sql.generate_sql(processing_text)
                
                if success:
                    sql_query = sql_result['sql']
                    sql_query_log = sql_query # Lưu để debug nếu cần
                    
                    q_success, query_result = self.db_helper.execute_query(sql_query)
                    
                    if q_success and query_result:
                        db_data = query_result
                        # ✅ NEW: Cập nhật ngữ cảnh tìm kiếm mới nhất
                        # Chỉ cập nhật nếu tìm thấy kết quả mới, nếu không giữ lại context cũ
                        if len(db_data) > 0:
                            self.last_search_context = db_data
            
            # 3. Chuẩn bị Prompt
            self.chat_history.append({"role": "user", "content": user_text})
            
            final_prompt = user_text
            
            if db_data:
                final_prompt = f"""
Câu hỏi (đã hiểu theo ngữ cảnh): "{processing_text}"

Dữ liệu chính xác tìm thấy từ Database:
{self._format_db_data(db_data)}

Hãy trả lời câu hỏi dựa trên dữ liệu trên. 
- Nếu là so sánh hoặc liệt kê yêu cầu, hãy trình bày rõ ràng từng trường.
- Quy đổi USD sang VNĐ (x25000).
"""
            elif processing_text != user_text:
                # Trường hợp không tìm thấy DB nhưng câu hỏi đã được làm rõ
                final_prompt = f"Tôi muốn hỏi: {processing_text}. (Hiện không tìm thấy dữ liệu trong DB, hãy trả lời dựa trên kiến thức của bạn nếu có thể hoặc báo không tìm thấy)."

            # 4. Streaming Response
            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.chat_history[:-1] + [{"role": "user", "content": final_prompt}],
                stream=True,
            )

            full_reply = ""
            first_chunk = True
            
            for chunk in stream:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    if first_chunk and on_response_start:
                        on_response_start()
                        first_chunk = False
                    
                    full_reply += delta.content
                    output_widget.config(state="normal")
                    output_widget.insert("end", delta.content, "assistant_text")
                    output_widget.config(state="disabled")
                    output_widget.see("end")

            self.chat_history.append({"role": "assistant", "content": full_reply})

            output_widget.config(state="normal")
            output_widget.insert("end", "\n\n")
            output_widget.config(state="disabled")
            
            if status_callback:
                status_callback(False)

        except Exception as e:
            output_widget.config(state="normal")
            output_widget.insert("end", f"\n❌ Lỗi hệ thống: {e}\n\n", "error")
            output_widget.config(state="disabled")
            if status_callback:
                status_callback(False)

    def _format_db_data(self, data):
        if not data: return "Không có dữ liệu."
        max_records = 15
        return json.dumps(data[:max_records], ensure_ascii=False, indent=2)

    def clear_history(self, system_prompt):
        self.chat_history = [{"role": "system", "content": system_prompt}]
        self.last_search_context = [] # Reset cả context tìm kiếm