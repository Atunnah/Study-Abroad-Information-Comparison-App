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
        self.chat_engine = ChatEngine(SYSTEM_PROMPT)
        self.is_processing = False
        self.config = ChatbotConfig()
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

        # Gửi request trong background thread
        threading.Thread(
            target=self.chat_engine.ask_stream,
            args=(user_text, self.output, self.update_status),
            daemon=True
        ).start()

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
        self.output.config(state="normal")
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, self.config.WELCOME_MSG, "assistant_text")
        self.output.config(state="disabled")
        
        # Reset chat engine
        self.chat_engine.clear_history(SYSTEM_PROMPT)