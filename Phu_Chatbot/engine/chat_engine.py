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











#engine/chat_engine.py:
import g4f
from .database_helper import DatabaseHelper
from .text_to_sql import TextToSQLEngine

class ChatEngine:
    """Engine giao tiếp với AI và Database, điều khiển UI thông qua ui_controller"""
    
    def __init__(self, system_prompt, db_path="university.db", ui_controller=None):
        self.chat_history = [{"role": "system", "content": system_prompt}]
        self.client = g4f.Client()
        self.db_helper = DatabaseHelper(db_path)
        self.text_to_sql = TextToSQLEngine(self.db_helper)
        self.ui = ui_controller 
        self.last_search_context = {
            "university_ids": [],
            "last_sql": ""
        }
        
    def _needs_database_query(self, user_text):
        keywords = [
            'tìm', 'tìm kiếm', 'tra cứu', 'liệt kê', 'danh sách',
            'có bao nhiêu', 'những trường nào', 'trường nào',
            'học phí', 'gpa', 'ielts', 'toefl', 'học bổng',
            'yêu cầu', 'điều kiện', 'so sánh', 'xếp hạng',
            'ở quốc gia', 'tại', 'của'
        ]
        return any(k in user_text.lower() for k in keywords)

    def ask_stream(self, user_text, on_complete_callback=None):
        try:
            self.chat_history.append({"role": "user", "content": user_text})
            db_data = None
            
            # --- GIAI ĐOẠN 1: Xử lý Database ---
            if self._needs_database_query(user_text):
                self.ui.add_log_message("Đang phân tích câu hỏi...", "thinking")
                success, sql_result = self.text_to_sql.generate_sql(
                    user_text, 
                    self.chat_history[:-1],
                    self.last_search_context # <--- QUAN TRỌNG
                )
                if success:
                    sql_query = sql_result['sql']
                    explanation = sql_result.get('explanation', '')
                    self.ui.add_log_message(f"{explanation}\nSQL: {sql_query}", "sql")
                    
                    success, query_result = self.db_helper.execute_query(sql_query)
                    
                    if success:
                        db_data = query_result
                        self.ui.add_log_message(f"Tìm thấy {len(db_data)} kết quả", "success")
                        if db_data and len(db_data) > 0:
                            found_ids = [str(row['id']) for row in db_data if 'id' in row.keys()]
                            if found_ids:
                                self.last_search_context['university_ids'] = found_ids
                                self.last_search_context['last_sql'] = sql_query
                    else:
                        self.ui.add_log_message(f"Lỗi DB: {query_result}", "error")
                else:
                    self.ui.add_log_message(f"Không tạo được SQL: {sql_result}", "error")

            # --- GIAI ĐOẠN 2: Gọi AI & Streaming ---
            final_prompt = user_text
            if db_data:
                final_prompt = f"""Câu hỏi: {user_text}
Dữ liệu từ database:
{self._format_db_data(db_data)}
Hãy trả lời dựa trên dữ liệu này."""

            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.chat_history[:-1] + [{"role": "user", "content": final_prompt}],
                stream=True,
            )

            full_reply = ""
            is_first_chunk = True
            
            for chunk in stream:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    if is_first_chunk:
                        self.ui.start_bot_stream()
                        is_first_chunk = False
                    
                    full_reply += delta.content
                    self.ui.update_bot_stream(delta.content)

            self.chat_history.append({"role": "assistant", "content": full_reply})
        
        except Exception as e:
            self.ui.add_log_message(f"Lỗi hệ thống: {e}", "error")
            # Nếu lỗi xảy ra trước khi stream bắt đầu, cần tắt typing
            self.ui.stop_typing_animation()
            if self.chat_history and self.chat_history[-1]['role'] == 'user':
                self.chat_history.pop()
        
        finally:
            if on_complete_callback:
                on_complete_callback()

    def _format_db_data(self, data):
        if not data: return "Không có dữ liệu"
        limit = data[:5] # Lấy 5 dòng thôi cho đỡ tốn token
        return "\n".join([str(record) for record in limit])

    def clear_history(self, system_prompt):
        self.chat_history = [{"role": "system", "content": system_prompt}]