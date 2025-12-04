import tkinter as tk
from tkinter import scrolledtext
import threading
import uuid
from datetime import datetime
from .config.prompts import SYSTEM_PROMPT
from .config.ui_config import ChatbotConfig
from .engine.chat_engine import ChatEngine

class ChatbotTab:
    """
    Tab Chatbot AI với giao diện Đa hội thoại (Sidebar + Chat)
    """
    
    def __init__(self, parent_frame):
        self.master_frame = parent_frame
        self.config = ChatbotConfig()
        
        # Quản lý đa hội thoại
        # sessions = { session_id: { 'engine': ChatEngine, 'title': str, 'created_at': datetime } }
        self.sessions = {} 
        self.current_session_id = None
        
        # State xử lý
        self.is_processing = False
        self.stop_event = threading.Event()
        self.typing_animation_running = False
        self.typing_mark = None
        
        self.setup_ui()
        
        # Tạo hội thoại đầu tiên mặc định
        self.create_new_session()
        
    def setup_ui(self):
        """Chia layout thành Sidebar (Trái) và Main Chat (Phải)"""
        
        # 1. Sidebar Frame
        self.sidebar_frame = tk.Frame(self.master_frame, bg=self.config.SIDEBAR_BG, width=250)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False) # Cố định chiều rộng
        
        self._create_sidebar_content()
        
        # 2. Main Chat Area Frame
        self.main_chat_frame = tk.Frame(self.master_frame, bg=self.config.BACKGROUND)
        self.main_chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._create_main_chat_ui()

    # ================= UI SIDEBAR =================
    
    def _create_sidebar_content(self):
        # Header Sidebar
        title_lbl = tk.Label(
            self.sidebar_frame, text="LỊCH SỬ CHAT", 
            bg=self.config.SIDEBAR_BG, fg=self.config.SIDEBAR_FG,
            font=("Segoe UI", 12, "bold"), pady=15
        )
        title_lbl.pack(fill=tk.X)
        
        # Nút "Đoạn chat mới"
        new_chat_btn = tk.Button(
            self.sidebar_frame, text="+ Đoạn chat mới",
            bg=self.config.BUTTON_BG, fg="white",
            relief=tk.FLAT, font=self.config.FONT_BUTTON,
            pady=8, cursor="hand2",
            command=self.create_new_session
        )
        new_chat_btn.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        # Container chứa danh sách các nút hội thoại (có scroll)
        self.session_list_canvas = tk.Canvas(self.sidebar_frame, bg=self.config.SIDEBAR_BG, highlightthickness=0)
        self.session_list_frame = tk.Frame(self.session_list_canvas, bg=self.config.SIDEBAR_BG)
        
        self.scrollbar = tk.Scrollbar(self.sidebar_frame, orient="vertical", command=self.session_list_canvas.yview)
        self.session_list_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.session_list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Tạo window trong canvas
        self.session_list_canvas.create_window((0, 0), window=self.session_list_frame, anchor="nw", width=230)
        
        self.session_list_frame.bind("<Configure>", lambda e: self.session_list_canvas.configure(scrollregion=self.session_list_canvas.bbox("all")))

    def _update_sidebar_list(self):
        """Vẽ lại danh sách các nút trong sidebar"""
        # Xóa các nút cũ
        for widget in self.session_list_frame.winfo_children():
            widget.destroy()
            
        # Sắp xếp sessions theo thời gian mới nhất -> cũ nhất
        sorted_sessions = sorted(self.sessions.items(), key=lambda x: x[1]['created_at'], reverse=True)
        
        for s_id, data in sorted_sessions:
            is_active = (s_id == self.current_session_id)
            bg_color = self.config.ITEM_ACTIVE_BG if is_active else self.config.SIDEBAR_BG
            fg_color = "white" if is_active else "#bdc3c7"
            font_style = ("Segoe UI", 10, "bold") if is_active else ("Segoe UI", 10)
            
            # Container cho 1 item (để căn lề đẹp hơn)
            item_frame = tk.Frame(self.session_list_frame, bg=bg_color, pady=2, padx=5)
            item_frame.pack(fill=tk.X, pady=1)
            
            # Nút chọn session
            btn = tk.Button(
                item_frame, text=f"💬 {data['title']}",
                bg=bg_color, fg=fg_color,
                anchor="w", relief=tk.FLAT,
                font=font_style, cursor="hand2",
                command=lambda i=s_id: self.switch_session(i)
            )
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Nút xóa (nhỏ)
            del_btn = tk.Label(
                item_frame, text="✕", bg=bg_color, fg="#e74c3c",
                cursor="hand2", font=("Arial", 10, "bold")
            )
            del_btn.pack(side=tk.RIGHT, padx=5)
            del_btn.bind("<Button-1>", lambda e, i=s_id: self.delete_session(i))

    # ================= UI MAIN CHAT =================
    
    def _create_main_chat_ui(self):
        # Header (đơn giản hơn version cũ)
        self.header_frame = tk.Frame(self.main_chat_frame, bg=self.config.HEADER_BG, height=50)
        self.header_frame.pack(fill=tk.X)
        
        self.header_title = tk.Label(
            self.header_frame, text="Hội thoại mới",
            bg=self.config.HEADER_BG, fg=self.config.HEADER_FG,
            font=self.config.FONT_HEADER_TITLE
        )
        self.header_title.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Chat Area
        chat_frame = tk.Frame(self.main_chat_frame, bg=self.config.CHAT_BG)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 10))
        
        self.output = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, state="disabled",
            font=self.config.FONT_TEXT, bg=self.config.CHAT_BG,
            padx=15, pady=15, relief=tk.FLAT
        )
        self.output.pack(fill=tk.BOTH, expand=True)
        
        # Config Tags
        self.output.tag_config("user_msg", justify='right', lmargin1=100, lmargin2=100, rmargin=10, foreground=self.config.USER_BG)
        self.output.tag_config("assistant_msg", justify='left', lmargin1=10, lmargin2=10, rmargin=100, foreground=self.config.TEXT_PRIMARY)
        self.output.tag_config("typing", justify='left', lmargin1=10, foreground=self.config.STATUS_COLOR, font=("Segoe UI", 14, "bold"))
        self.output.tag_config("error", justify='center', foreground=self.config.ERROR_COLOR)
        
        # Input Area
        input_frame = tk.Frame(self.main_chat_frame, bg=self.config.BACKGROUND)
        input_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        entry_container = tk.Frame(input_frame, bg=self.config.CHAT_BG, relief=tk.SOLID, bd=1)
        entry_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.entry = tk.Entry(entry_container, font=("Segoe UI", 12), bg=self.config.CHAT_BG, relief=tk.FLAT, bd=8)
        self.entry.pack(fill=tk.BOTH, expand=True)
        self.entry.bind("<Return>", lambda e: self.handle_button_click())
        
        self.action_btn = tk.Button(
            input_frame, text="Gửi 📤", command=self.handle_button_click,
            font=self.config.FONT_BUTTON, bg=self.config.BUTTON_BG, fg=self.config.BUTTON_FG,
            relief=tk.FLAT, padx=20, pady=10, cursor="hand2"
        )
        self.action_btn.pack(side=tk.RIGHT)
        
        self.status_label = tk.Label(self.main_chat_frame, text="", font=self.config.FONT_STATUS, bg=self.config.BACKGROUND, fg=self.config.STATUS_COLOR)
        self.status_label.pack(pady=(0, 5))

    # ================= LOGIC QUẢN LÝ SESSION =================

    def create_new_session(self):
        """Tạo hội thoại mới và switch qua nó"""
        if self.is_processing:
            return # Không cho tạo khi đang chat
            
        session_id = str(uuid.uuid4())
        session_count = len(self.sessions) + 1
        
        new_session = {
            'engine': ChatEngine(SYSTEM_PROMPT, db_path="universities_db.db"),
            'title': f"Hội thoại {session_count}",
            'created_at': datetime.now()
        }
        
        self.sessions[session_id] = new_session
        self.switch_session(session_id)

    def switch_session(self, session_id):
        """Chuyển đổi màn hình sang hội thoại session_id"""
        if self.is_processing:
            # Nếu đang chat ở tab cũ, hủy nó đi
            self.cancel_request()
            
        self.current_session_id = session_id
        
        # Cập nhật UI
        self._update_sidebar_list()
        current_data = self.sessions[session_id]
        self.header_title.config(text=current_data['title'])
        
        # Render lại lịch sử
        self._render_current_history()

    def delete_session(self, session_id):
        """Xóa một hội thoại"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            
            # Nếu xóa đúng session đang mở -> tạo mới hoặc mở cái khác
            if self.current_session_id == session_id:
                if self.sessions:
                    # Mở cái đầu tiên còn lại
                    first_id = list(self.sessions.keys())[0]
                    self.switch_session(first_id)
                else:
                    self.create_new_session()
            else:
                self._update_sidebar_list()

    def _render_current_history(self):
        """Vẽ lại toàn bộ tin nhắn từ ChatEngine của session hiện tại"""
        engine = self.sessions[self.current_session_id]['engine']
        history = engine.chat_history
        
        self.output.config(state="normal")
        self.output.delete(1.0, tk.END)
        
        # Render Welcome message nếu history chỉ có system prompt
        if len(history) <= 1:
            self.append_message("assistant", self.config.WELCOME_MSG)
        else:
            # Skip system prompt (index 0)
            for msg in history[1:]:
                self.append_message(msg['role'], msg['content'])
                
        self.output.config(state="disabled")
        self.output.see(tk.END)

    # ================= LOGIC CHAT (Giống version cũ) =================

    def append_message(self, role, text):
        self.output.config(state="normal")
        if role == "user":
            self.output.insert(tk.END, f"👤 BẠN:\n{text}\n\n", "user_msg")
        else:
            self.output.insert(tk.END, f"🤖 TRỢ LÝ:\n{text}\n\n", "assistant_msg")
        self.output.config(state="disabled")
        self.output.see(tk.END)

    def handle_button_click(self):
        if self.is_processing:
            self.cancel_request()
        else:
            self.send_message()

    def cancel_request(self):
        self.stop_event.set()
        self.status_label.config(text="⛔ Đã hủy")
        self.stop_typing_animation()
        self.is_processing = False
        self._reset_button_state()

    def send_message(self):
        user_text = self.entry.get().strip()
        if not user_text: return

        # 1. Hiển thị User Msg
        self.append_message("user", user_text)
        self.entry.delete(0, tk.END)
        
        # 2. Cập nhật Tiêu đề nếu đây là tin nhắn đầu tiên của user
        current_sess = self.sessions[self.current_session_id]
        engine = current_sess['engine']
        if len(engine.chat_history) == 1: # Chỉ có system prompt
            # Lấy 20 ký tự đầu làm title
            new_title = (user_text[:25] + '..') if len(user_text) > 25 else user_text
            current_sess['title'] = new_title
            self.header_title.config(text=new_title)
            self._update_sidebar_list()

        # 3. Trạng thái xử lý
        self.is_processing = True
        self.stop_event.clear()
        self.action_btn.config(text="Hủy ❌", bg=self.config.BUTTON_CANCEL, command=self.cancel_request)
        self.status_label.config(text="⏳ Đang suy nghĩ...")
        self.start_typing_animation()

        # 4. Gửi request vào engine của session hiện tại
        threading.Thread(
            target=engine.ask_stream, # Dùng engine của session hiện tại
            args=(user_text, self.output, self.on_response_start, self.update_status, self.stop_event),
            daemon=True
        ).start()

    # --- Animation & Callbacks (Giữ nguyên logic) ---
    
    def start_typing_animation(self):
        self.typing_animation_running = True
        self.output.config(state="normal")
        self.output.insert(tk.END, "🤖 TRỢ LÝ:\n", "assistant_msg")
        self.typing_mark = self.output.index("end-1c")
        self.output.insert(tk.END, "●", "typing") 
        self.output.config(state="disabled")
        self._animate_typing(0)

    def _animate_typing(self, dot_count):
        if not self.typing_animation_running: return
        dots = "●" * (dot_count + 1) + "○" * (2 - dot_count)
        self.output.config(state="normal")
        if self.typing_mark:
            self.output.delete(self.typing_mark, tk.END)
            self.output.insert(tk.END, f"\n{dots}\n", "typing")
        self.output.config(state="disabled")
        self.output.see(tk.END)
        self.master_frame.after(400, lambda: self._animate_typing((dot_count + 1) % 3))

    def stop_typing_animation(self):
        self.typing_animation_running = False
        if self.typing_mark:
            self.output.config(state="normal")
            start_del = self.output.index(f"{self.typing_mark} lineend")
            self.output.delete(self.typing_mark, tk.END) 
            self.output.config(state="disabled")
            self.typing_mark = None

    def on_response_start(self):
        self.master_frame.after(0, self.stop_typing_animation)

    def update_status(self, is_processing):
        self.master_frame.after(0, lambda: self._finish_processing(is_processing))

    def _finish_processing(self, is_processing):
        self.is_processing = is_processing
        if not is_processing:
            self._reset_button_state()
            self.status_label.config(text="")
            self.stop_typing_animation()

    def _reset_button_state(self):
        self.action_btn.config(text="Gửi 📤", bg=self.config.BUTTON_BG, command=self.handle_button_click)