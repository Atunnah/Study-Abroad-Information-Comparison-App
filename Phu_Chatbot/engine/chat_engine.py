import g4f
from .database_helper import DatabaseHelper
from .text_to_sql import TextToSQLEngine
import tkinter as tk


class ChatEngine:
    """Engine để giao tiếp với AI model và database"""
   
    def __init__(self, system_prompt, db_path="university.db"):
        """
        Khởi tạo ChatEngine
       
        Args:
            system_prompt: System prompt cho AI
            db_path: Đường dẫn đến database
        """
        self.chat_history = [{"role": "system", "content": system_prompt}]
        self.client = g4f.Client()
       
        # Khởi tạo database helper và text-to-sql engine
        self.db_helper = DatabaseHelper(db_path)
        self.text_to_sql = TextToSQLEngine(self.db_helper)


    def _needs_database_query(self, user_text):
        """
        Kiểm tra xem câu hỏi có cần truy vấn database không
       
        Args:
            user_text: Câu hỏi của người dùng
           
        Returns:
            bool: True nếu cần truy vấn database
        """
        keywords = [
            'tìm', 'tìm kiếm', 'tra cứu', 'liệt kê', 'danh sách',
            'có bao nhiêu', 'những trường nào', 'trường nào',
            'học phí', 'gpa', 'ielts', 'toefl', 'học bổng',
            'yêu cầu', 'điều kiện', 'so sánh', 'xếp hạng',
            'ở quốc gia', 'tại', 'của'
        ]
       
        user_text_lower = user_text.lower()
        return any(keyword in user_text_lower for keyword in keywords)


    def ask_stream(self, user_text, output_widget, on_response_start, status_callback, stop_event):
        """
        Gửi tin nhắn và nhận phản hồi dạng stream, có hỗ trợ hủy (stop_event)
        
        Args:
            user_text: Nội dung tin nhắn từ user
            output_widget: Widget để hiển thị kết quả
            on_response_start: Callback khi bắt đầu nhận response
            status_callback: Callback để cập nhật trạng thái
            stop_event: Event để kiểm tra tín hiệu hủy từ người dùng
        """
        try:
            self.chat_history.append({"role": "user", "content": user_text})
            
            db_data = None
            
            # --- GIAI ĐOẠN 1: SUY NGHĨ & TRUY VẤN DB ---
            if self._needs_database_query(user_text):
                # Kiểm tra hủy trước khi chạy Text-to-SQL
                if stop_event.is_set(): 
                    self._handle_cancel(output_widget, status_callback)
                    return 

                # Text to SQL
                success, sql_result = self.text_to_sql.generate_sql(user_text)
                
                # Kiểm tra hủy sau khi chạy Text-to-SQL
                if stop_event.is_set(): 
                    self._handle_cancel(output_widget, status_callback)
                    return 

                if success:
                    sql_query = sql_result['sql']
                    # Thực thi query nhưng KHÔNG in log ra UI để giữ giao diện sạch
                    success_db, query_result = self.db_helper.execute_query(sql_query)
                    
                    if success_db:
                        db_data = query_result
                        print(f"[DEBUG] SQL Executed: {sql_query}") # Log ra console
            
            # Kiểm tra hủy trước khi gọi AI
            if stop_event.is_set(): 
                self._handle_cancel(output_widget, status_callback)
                return

            # --- GIAI ĐOẠN 2: CHUẨN BỊ PROMPT CUỐI ---
            final_prompt = user_text
            if db_data:
                final_prompt = f"""Câu hỏi: {user_text}

Dữ liệu từ database (đã truy vấn thành công):
{self._format_db_data(db_data)}

Hãy phân tích và trả lời câu hỏi dựa trên dữ liệu trên. Trả lời chi tiết, có cấu trúc rõ ràng."""

            # --- GIAI ĐOẠN 3: GỌI AI & STREAMING ---
            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.chat_history[:-1] + [{"role": "user", "content": final_prompt}],
                stream=True,
            )

            full_reply = ""
            first_chunk = True
            
            for chunk in stream:
                # Kiểm tra hủy ngay trong vòng lặp stream (Real-time cancel)
                if stop_event.is_set():
                    self._handle_cancel(output_widget, status_callback)
                    return

                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    # Nếu là chunk đầu tiên -> Gọi callback để tắt animation "..."
                    if first_chunk:
                        # Dùng after để gọi an toàn trên UI thread
                        output_widget.after(0, on_response_start)
                        first_chunk = False
                    
                    full_reply += delta.content
                    
                    # Hiển thị text streaming
                    output_widget.config(state="normal")
                    output_widget.insert(tk.END, delta.content, "assistant_msg")
                    output_widget.config(state="disabled")
                    output_widget.see("end")

            self.chat_history.append({"role": "assistant", "content": full_reply})
            
            # Xuống dòng kết thúc
            output_widget.config(state="normal")
            output_widget.insert(tk.END, "\n\n")
            output_widget.config(state="disabled")
            
            # Báo hiệu hoàn tất
            status_callback(False)

        except Exception as e:
            # Chỉ hiện lỗi nếu không phải do người dùng hủy
            if not stop_event.is_set():
                output_widget.config(state="normal")
                output_widget.insert("end", f"\n❌ Lỗi: {e}\n\n", "error")
                output_widget.config(state="disabled")
            status_callback(False)

    def _handle_cancel(self, output_widget, status_callback):
        """Xử lý khi người dùng hủy"""
        output_widget.config(state="normal")
        output_widget.insert(tk.END, "\n⛔ [Đã dừng bởi người dùng]\n\n", "error")
        output_widget.config(state="disabled")
        output_widget.see("end")
        status_callback(False)

    def _format_db_data(self, data):
        """Format dữ liệu database thành chuỗi dễ đọc"""
        if not data:
            return "Không có dữ liệu"
        
        max_records = 10
        limited_data = data[:max_records]
        
        result = []
        for i, record in enumerate(limited_data, 1):
            result.append(f"\n[{i}] " + ", ".join([f"{k}: {v}" for k, v in record.items()]))
        
        if len(data) > max_records:
            result.append(f"\n... và {len(data) - max_records} kết quả khác")
        
        return "\n".join(result)

    def clear_history(self, system_prompt):
        """Reset lịch sử chat"""
        self.chat_history = [{"role": "system", "content": system_prompt}]