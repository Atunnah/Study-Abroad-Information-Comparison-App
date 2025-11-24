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
        self.config = ChatbotConfig()
        self.typing_animation_running = False
        self.typing_mark = None  # Đánh dấu vị trí của animation
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
        
        # Cấu hình text tags cho styling
        self.output.tag_config(
            "user_label", 
            foreground=self.config.USER_COLOR, 
            font=self.config.FONT_TEXT_BOLD
        )
        self.output.tag_config(
            "user_text", 
            foreground=self.config.TEXT_PRIMARY
        )
        self.output.tag_config(
            "assistant_label", 
            foreground=self.config.ASSISTANT_COLOR, 
            font=self.config.FONT_TEXT_BOLD
        )
        self.output.tag_config(
            "assistant_text", 
            foreground=self.config.TEXT_SECONDARY
        )
        self.output.tag_config(
            "error", 
            foreground=self.config.ERROR_COLOR, 
            font=("Segoe UI", 11, "italic")
        )
        self.output.tag_config(
            "typing", 
            foreground=self.config.STATUS_COLOR,
            font=("Segoe UI", 14)
        )
        self.output.tag_config(
            "status", 
            foreground="#9b59b6",
            font=("Segoe UI", 10, "italic")
        )
        self.output.tag_config(
            "sql", 
            foreground="#2980b9",
            font=("Consolas", 10),
            background="#ecf0f1"
        )
        self.output.tag_config(
            "explanation", 
            foreground="#16a085",
            font=("Segoe UI", 10, "italic")
        )
        self.output.tag_config(
            "success", 
            foreground="#27ae60",
            font=("Segoe UI", 10, "bold")
        )
        
        # Hiển thị welcome message
        self.output.config(state="normal")
        self.output.insert(tk.END, self.config.WELCOME_MSG, "assistant_text")
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
        
        # Entry widget
        self.entry = tk.Entry(
            entry_container, 
            font=("Segoe UI", 12), 
            bg=self.config.CHAT_BG, 
            fg=self.config.TEXT_PRIMARY, 
            relief=tk.FLAT, 
            bd=5
        )
        self.entry.pack(fill=tk.BOTH, expand=True)
        self.entry.bind("<Return>", lambda e: self.send_message())
        self.entry.focus()
        
        # Send button
        self.send_btn = tk.Button(
            input_frame, 
            text="Gửi 📤", 
            command=self.send_message,
            font=self.config.FONT_BUTTON,
            bg=self.config.BUTTON_BG, 
            fg=self.config.BUTTON_FG,
            relief=tk.FLAT, 
            bd=0,
            padx=25, 
            pady=10,
            cursor="hand2",
            activebackground=self.config.BUTTON_ACTIVE,
            activeforeground=self.config.BUTTON_FG
        )
        self.send_btn.pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = tk.Label(
            parent, 
            text="", 
            font=self.config.FONT_STATUS, 
            bg=self.config.BACKGROUND, 
            fg=self.config.STATUS_COLOR
        )
        self.status_label.pack(pady=(5, 0))

    def start_typing_animation(self):
        """Bắt đầu animation dấu ba chấm"""
        self.typing_animation_running = True
        
        # Thêm label "Trợ lý:" và đánh dấu vị trí
        self.output.config(state="normal")
        self.output.insert(tk.END, "🤖 Trợ lý: ", "assistant_label")
        self.typing_mark = self.output.index(tk.END)
        self.output.config(state="disabled")
        
        # Bắt đầu animation
        self._animate_typing(0)
    
    def _animate_typing(self, dot_count):
        """
        Animation dấu ba chấm
        
        Args:
            dot_count: Số lượng dấu chấm hiện tại (0-3)
        """
        if not self.typing_animation_running:
            return
        
        # Tạo chuỗi dấu chấm
        dots = "●" * (dot_count + 1) + "○" * (2 - dot_count)
        
        # Cập nhật text
        self.output.config(state="normal")
        
        # Xóa dấu chấm cũ nếu có
        if self.typing_mark:
            self.output.delete(self.typing_mark, tk.END)
        
        # Thêm dấu chấm mới
        self.output.insert(tk.END, dots, "typing")
        self.output.see(tk.END)
        self.output.config(state="disabled")
        
        # Lặp lại animation
        next_count = (dot_count + 1) % 3
        self.output.after(400, lambda: self._animate_typing(next_count))
    
    def stop_typing_animation(self):
        """Dừng animation và xóa dấu ba chấm"""
        self.typing_animation_running = False
        
        if self.typing_mark:
            self.output.config(state="normal")
            # Xóa dấu ba chấm
            self.output.delete(self.typing_mark, tk.END)
            self.output.config(state="disabled")
            self.typing_mark = None

    def send_message(self):
        """Xử lý gửi tin nhắn"""
        if self.is_processing:
            return
            
        user_text = self.entry.get().strip()
        if not user_text:
            return

        # Hiển thị tin nhắn của user
        self.output.config(state="normal")
        self.output.insert(tk.END, "👤 Bạn: ", "user_label")
        self.output.insert(tk.END, f"{user_text}\n\n", "user_text")
        self.output.config(state="disabled")
        self.output.see(tk.END)

        # Clear entry
        self.entry.delete(0, tk.END)
        
        # Update UI state
        self.is_processing = True
        self.send_btn.config(state="disabled", bg=self.config.BUTTON_DISABLED)
        self.status_label.config(text="⏳ Đang xử lý...")
        
        # Bắt đầu typing animation
        self.start_typing_animation()

        # Gửi request trong background thread
        threading.Thread(
            target=self.chat_engine.ask_stream,
            args=(user_text, self.output, self.on_response_start, self.update_status),
            daemon=True
        ).start()

    def on_response_start(self):
        """Callback khi bắt đầu nhận response từ AI"""
        # Dừng typing animation
        self.stop_typing_animation()

    def update_status(self, is_processing):
        """
        Cập nhật trạng thái UI
        
        Args:
            is_processing: True nếu đang xử lý, False nếu hoàn thành
        """
        self.is_processing = is_processing
        if not is_processing:
            self.send_btn.config(state="normal", bg=self.config.BUTTON_BG)
            self.status_label.config(text="")

    def clear_chat(self):
        """Xóa lịch sử chat"""
        # Dừng animation nếu đang chạy
        self.stop_typing_animation()
        
        self.output.config(state="normal")
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, self.config.WELCOME_MSG, "assistant_text")
        self.output.config(state="disabled")
        
        # Reset chat engine
        self.chat_engine.clear_history(SYSTEM_PROMPT)