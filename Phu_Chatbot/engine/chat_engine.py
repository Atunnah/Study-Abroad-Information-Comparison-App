import g4f
import tkinter as tk
from .database_helper import DatabaseHelper
from .text_to_sql import TextToSQLEngine
from .router import IntentRouter          # <--- Import bộ định tuyến
from .local_chitchat import LocalChitchatEngine # <--- Import engine chitchat (Gemini)

class ChatEngine:
    """Engine điều phối chính: Router -> Local LLM (Chitchat) hoặc Online LLM (DB)"""
    
    def __init__(self, system_prompt, db_path="university.db"):
        """
        Khởi tạo ChatEngine
        """
        self.system_prompt = system_prompt
        # History này chỉ dùng cho luồng Domain (Online LLM)
        self.chat_history = [{"role": "system", "content": system_prompt}]
        
        self.client = g4f.Client()
        
        # Khởi tạo database helper và text-to-sql engine
        self.db_helper = DatabaseHelper(db_path)
        self.text_to_sql = TextToSQLEngine(self.db_helper)
        
        # --- [TỐI ƯU HÓA] KHỞI TẠO CHITCHAT & ROUTER ---
        self.router = IntentRouter()
        
        # Khởi tạo engine chitchat 1 lần duy nhất và lưu vào biến self
        print("[System] Đang khởi động Chitchat Engine...")
        try:
            self.local_engine = LocalChitchatEngine()
        except Exception as e:
            print(f"❌ Lỗi khởi tạo Chitchat: {e}")
            self.local_engine = None

    def _needs_database_query(self, user_text):
        """Kiểm tra xem câu hỏi có cần truy vấn database không"""
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
        Xử lý câu hỏi:
        1. Router phân loại.
        2. Nếu Chitchat -> Dùng self.local_engine (Gemini).
        3. Nếu Domain -> Dùng Logic cũ (Text2SQL + g4f).
        """
        try:
            # --- BƯỚC 1: PHÂN LOẠI Ý ĐỊNH ---
            intent = self.router.classify(user_text)
            print(f"[ROUTER] User Input: '{user_text}' -> Intent: {intent}")

            # =================================================================
            # TRƯỜNG HỢP 1: CHITCHAT (Xã giao - Dùng Engine đã khởi tạo sẵn)
            # =================================================================
            if intent == 'CHITCHAT':
                # Báo cho UI biết đã bắt đầu
                output_widget.after(0, on_response_start)
                
                if self.local_engine:
                    # Streaming từ Gemini
                    for chunk in self.local_engine.generate_response_stream(user_text):
                        if stop_event.is_set():
                            self._handle_cancel(output_widget, status_callback)
                            return
                        
                        output_widget.config(state="normal")
                        output_widget.insert(tk.END, chunk, "assistant_msg")
                        output_widget.config(state="disabled")
                        output_widget.see("end")
                else:
                    # Fallback nếu engine bị lỗi khởi tạo
                    output_widget.config(state="normal")
                    output_widget.insert(tk.END, "Hệ thống chitchat đang khởi động hoặc gặp lỗi, vui lòng thử câu hỏi về du học nhé!", "assistant_msg")
                    output_widget.config(state="disabled")
                
                # Kết thúc luồng Chitchat
                self._finalize_ui(output_widget, status_callback)
                return

            # =================================================================
            # TRƯỜNG HỢP 2: DOMAIN (Nghiệp vụ - Logic cũ)
            # =================================================================
            
            # 1. Lưu user message vào history TRƯỚC khi xử lý DB
            self.chat_history.append({"role": "user", "content": user_text})
            
            db_data = None
            
            # --- 2.1: SUY NGHĨ & TRUY VẤN DB ---
            if self._needs_database_query(user_text):
                if stop_event.is_set(): 
                    self._handle_cancel(output_widget, status_callback)
                    return 

                # [THAY ĐỔI QUAN TRỌNG]: Truyền lịch sử chat vào TextToSQL
                # Lấy tất cả lịch sử TRỪ câu cuối (vì câu cuối là user_text đã được truyền riêng)
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
                        print(f"[DEBUG] SQL Executed: {sql_query}")
            
            if stop_event.is_set(): 
                self._handle_cancel(output_widget, status_callback)
                return

            # --- 2.2: CHUẨN BỊ PROMPT CUỐI ---
            final_prompt = user_text
            if db_data:
                final_prompt = f"""Câu hỏi: {user_text}

Dữ liệu từ database (đã truy vấn thành công):
{self._format_db_data(db_data)}

Hãy phân tích và trả lời câu hỏi dựa trên dữ liệu trên. Trả lời chi tiết, có cấu trúc rõ ràng."""

            # --- 2.3: GỌI ONLINE AI (GPT-4o-mini via g4f) ---
            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.chat_history[:-1] + [{"role": "user", "content": final_prompt}],
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

            self.chat_history.append({"role": "assistant", "content": full_reply})
            
            # Kết thúc luồng Domain
            self._finalize_ui(output_widget, status_callback)

        except Exception as e:
            if not stop_event.is_set():
                output_widget.config(state="normal")
                output_widget.insert("end", f"\n❌ Lỗi: {e}\n\n", "error")
                output_widget.config(state="disabled")
            status_callback(False)

    def _finalize_ui(self, output_widget, status_callback):
        """Hàm phụ: Xuống dòng và báo kết thúc"""
        output_widget.config(state="normal")
        output_widget.insert(tk.END, "\n\n")
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