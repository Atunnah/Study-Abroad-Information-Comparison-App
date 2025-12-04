import tkinter as tk
from tkinter import scrolledtext
import threading
from .config.prompts import SYSTEM_PROMPT
from .config.ui_config import ChatbotConfig
from .engine.chat_engine import ChatEngine




class ChatbotTab:
    """
    Tab Chatbot AI tư vấn du học
    Được tích hợp vào hệ thống University Management
    """
   
    def __init__(self, parent_frame):
        """
        Khởi tạo ChatbotTab
       
        Args:
            parent_frame: Frame cha từ main application
        """
        self.frame = parent_frame
        self.chat_engine = ChatEngine(SYSTEM_PROMPT, db_path="universities_db.db")
        self.is_processing = False
        self.stop_event = threading.Event()
        self.config = ChatbotConfig()

        self.typing_animation_running = False
        self.typing_mark = None  

        self.setup_ui()
       
    def setup_ui(self):
        """Thiết lập giao diện chính"""
        # Main container với padding
        main_container = tk.Frame(
            self.frame,
            bg=self.config.BACKGROUND
        )
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
       
        # Tạo các thành phần UI
        self._create_header(main_container)
        self._create_chat_area(main_container)
        self._create_input_area(main_container)
       
    def _create_header(self, parent):
        """
        Tạo header với tiêu đề
       
        Args:
            parent: Widget cha
        """
        header_frame = tk.Frame(
            parent,
            bg=self.config.HEADER_BG,
            height=80
        )
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.pack_propagate(False)
       
        # Icon
        tk.Label(
            header_frame,
            text="🎓",
            font=("Arial", 32),
            bg=self.config.HEADER_BG,
            fg=self.config.HEADER_FG
        ).pack(side=tk.LEFT, padx=20)
       
        # Title section
        title_frame = tk.Frame(header_frame, bg=self.config.HEADER_BG)
        title_frame.pack(side=tk.LEFT, fill=tk.Y, pady=10)
       
        tk.Label(
            title_frame,
            text="TƯ VẤN DU HỌC AI",
            font=self.config.FONT_HEADER_TITLE,
            bg=self.config.HEADER_BG,
            fg=self.config.HEADER_FG
        ).pack(anchor="w")
       
        tk.Label(
            title_frame,
            text="Trợ lý thông minh hỗ trợ tìm kiếm trường đại học",
            font=self.config.FONT_HEADER_SUB,
            bg=self.config.HEADER_BG,
            fg="#ecf0f1"
        ).pack(anchor="w")
       
        # Clear chat button
        tk.Button(
            header_frame,
            text="🔄 Làm mới",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.clear_chat
        ).pack(side=tk.RIGHT, padx=20)
   
    def _create_chat_area(self, parent):
        """
        Tạo khu vực hiển thị chat
       
        Args:
            parent: Widget cha
        """
        chat_frame = tk.Frame(
            parent,
            bg=self.config.CHAT_BG,
            relief=tk.GROOVE,
            bd=2
        )
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
       
        # ScrolledText widget
        self.output = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            state="disabled",
            font=self.config.FONT_TEXT,
            bg=self.config.CHAT_BG,
            fg=self.config.TEXT_PRIMARY,
            padx=15,
            pady=15,
            relief=tk.FLAT
        )
        self.output.pack(fill=tk.BOTH, expand=True)
       
        self.output.tag_config("user_msg", justify='right', lmargin1=100, lmargin2=100, rmargin=10, foreground=self.config.USER_BG)
        
        # Assistant: Căn trái, lùi lề phải nhiều
        self.output.tag_config("assistant_msg", justify='left', lmargin1=10, lmargin2=10, rmargin=100, foreground=self.config.TEXT_PRIMARY)
        
        # Typing: Căn trái
        self.output.tag_config("typing", justify='left', lmargin1=10, foreground=self.config.STATUS_COLOR, font=("Segoe UI", 14, "bold"))
        
        self.output.tag_config("error", justify='center', foreground=self.config.ERROR_COLOR)
       
        # Hiển thị welcome message
        self.output.config(state="normal")
        self.output.insert(tk.END, self.config.WELCOME_MSG, "assistant_msg")
        self.output.config(state="disabled")
   
    def _create_input_area(self, parent):
        """
        Tạo khu vực nhập liệu
       
        Args:
            parent: Widget cha
        """
        input_frame = tk.Frame(parent, bg=self.config.BACKGROUND)
        input_frame.pack(fill=tk.X)
       
        # Entry container
        entry_container = tk.Frame(
            input_frame,
            bg=self.config.CHAT_BG,
            relief=tk.SOLID,
            bd=1
        )
        entry_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
       
        self.entry = tk.Entry(entry_container, font=("Segoe UI", 12), bg=self.config.CHAT_BG, relief=tk.FLAT, bd=5)
        self.entry.pack(fill=tk.BOTH, expand=True)
        self.entry.bind("<Return>", lambda e: self.handle_button_click())
        self.entry.focus()
       
        self.action_btn = tk.Button(
            input_frame, text="Gửi 📤", command=self.handle_button_click,
            font=self.config.FONT_BUTTON, bg=self.config.BUTTON_BG, fg=self.config.BUTTON_FG,
            relief=tk.FLAT, padx=25, pady=10, cursor="hand2"
        )
        self.action_btn.pack(side=tk.RIGHT)
       
        self.status_label = tk.Label(parent, text="", font=self.config.FONT_STATUS, bg=self.config.BACKGROUND, fg=self.config.STATUS_COLOR)
        self.status_label.pack(pady=(5, 0))

    def append_message(self, role, text):
        """Hàm helper để thêm tin nhắn vào khung chat"""
        self.output.config(state="normal")
        
        if role == "user":
            # Thêm user icon hoặc tên nếu muốn, ở đây ta dùng màu sắc và căn lề
            msg_content = f"👤 BẠN:\n{text}\n\n"
            self.output.insert(tk.END, msg_content, "user_msg")
        else:
            msg_content = f"🤖 TRỢ LÝ:\n{text}\n\n"
            self.output.insert(tk.END, msg_content, "assistant_msg")
            
        self.output.config(state="disabled")
        self.output.see(tk.END)

    def start_typing_animation(self):
        self.typing_animation_running = True
        self.output.config(state="normal")

        self.output.insert(tk.END, "🤖 TRỢ LÝ:\n", "assistant_msg")
        self.typing_mark = self.output.index("end-1c") # Lưu vị trí
        self.output.insert(tk.END, "●", "typing") 
        self.output.config(state="disabled")
        self._animate_typing(0)
   
    def _animate_typing(self, dot_count):
        """
        Animation dấu ba chấm
       
        Args:
            dot_count: Số lượng dấu chấm hiện tại (0-3)
        """
        if not self.typing_animation_running:
            return
       
        dots = "●" * (dot_count + 1) + "○" * (2 - dot_count)
        
        self.output.config(state="normal")
        # Xóa dòng animation cũ và ghi lại
        if self.typing_mark:
            self.output.delete(self.typing_mark, tk.END)
            self.output.insert(tk.END, f"\n{dots}\n", "typing")
        self.output.config(state="disabled")
        self.output.see(tk.END)
        
        next_count = (dot_count + 1) % 3
        self.frame.after(400, lambda: self._animate_typing(next_count))
   
    def stop_typing_animation(self):
        """Dừng animation và xóa dấu ba chấm"""
        self.typing_animation_running = False
       
        if self.typing_mark:
            self.output.config(state="normal")
            start_del = self.output.index(f"{self.typing_mark} lineend")
            self.output.delete(self.typing_mark, tk.END) 
            self.output.config(state="disabled")
            self.typing_mark = None

    def handle_button_click(self):
        """Xử lý nút bấm: Nếu đang chạy thì Hủy, nếu không thì Gửi"""
        if self.is_processing:
            self.cancel_request()
        else:
            self.send_message()

    def cancel_request(self):
        """Hủy yêu cầu hiện tại"""
        self.stop_event.set() # Kích hoạt cờ hủy
        self.status_label.config(text="⛔ Đã hủy yêu cầu")
        self.stop_typing_animation()
        self.is_processing = False
        self._reset_button_state()

    def send_message(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return

        # 1. Hiển thị User message bên phải
        self.append_message("user", user_text)
        self.entry.delete(0, tk.END)
        
        # 2. Update trạng thái UI
        self.is_processing = True
        self.stop_event.clear() # Reset cờ hủy
        
        # Đổi nút thành "Hủy"
        self.action_btn.config(text="Hủy ❌", bg=self.config.BUTTON_CANCEL, command=self.cancel_request)
        self.status_label.config(text="⏳ Đang suy nghĩ...")
        
        # 3. Bắt đầu animation suy nghĩ
        self.start_typing_animation()

        # 4. Chạy thread xử lý
        threading.Thread(
            target=self.chat_engine.ask_stream,
            args=(user_text, self.output, self.on_response_start, self.update_status, self.stop_event),
            daemon=True
        ).start()

    def on_response_start(self):
        """Callback khi bắt đầu có chữ trả về từ AI"""
        self.frame.after(0, self.stop_typing_animation)

    def update_status(self, is_processing):
        """Callback khi hoàn tất"""
        # Sử dụng after để đảm bảo chạy trên Main Thread của UI
        self.frame.after(0, lambda: self._finish_processing(is_processing))

    def _finish_processing(self, is_processing):
        self.is_processing = is_processing
        if not is_processing:
            self._reset_button_state()
            self.status_label.config(text="")
            self.stop_typing_animation() # Đảm bảo animation tắt hẳn

    def _reset_button_state(self):
        self.action_btn.config(text="Gửi 📤", bg=self.config.BUTTON_BG, command=self.handle_button_click)

    def clear_chat(self):
        self.stop_typing_animation()
        self.output.config(state="normal")
        self.output.delete(1.0, tk.END)
        self.output.config(state="disabled")
        self.append_message("assistant", self.config.WELCOME_MSG)
        self.chat_engine.clear_history(SYSTEM_PROMPT)
