# import tkinter as tk
# from tkinter import scrolledtext
# import threading
# from .config.prompts import SYSTEM_PROMPT
# from .config.ui_config import ChatbotConfig
# from .engine.chat_engine import ChatEngine


# class ChatbotTab:
#     """
#     Tab Chatbot AI tư vấn du học
#     Được tích hợp vào hệ thống University Management
#     """
    
#     def __init__(self, parent_frame):
#         """
#         Khởi tạo ChatbotTab
        
#         Args:
#             parent_frame: Frame cha từ main application
#         """
#         self.frame = parent_frame
#         self.chat_engine = ChatEngine(SYSTEM_PROMPT, db_path="universities_db.db")
#         self.is_processing = False
#         self.config = ChatbotConfig()
#         self.typing_animation_running = False
#         self.typing_mark = None  # Đánh dấu vị trí của animation
#         self.setup_ui()
        
#     def setup_ui(self):
#         """Thiết lập giao diện chính"""
#         # Main container với padding
#         main_container = tk.Frame(
#             self.frame, 
#             bg=self.config.BACKGROUND
#         )
#         main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
#         # Tạo các thành phần UI
#         self._create_header(main_container)
#         self._create_chat_area(main_container)
#         self._create_input_area(main_container)
        
#     def _create_header(self, parent):
#         """
#         Tạo header với tiêu đề
        
#         Args:
#             parent: Widget cha
#         """
#         header_frame = tk.Frame(
#             parent, 
#             bg=self.config.HEADER_BG, 
#             height=80
#         )
#         header_frame.pack(fill=tk.X, pady=(0, 15))
#         header_frame.pack_propagate(False)
        
#         # Icon
#         tk.Label(
#             header_frame, 
#             text="🎓", 
#             font=("Arial", 32), 
#             bg=self.config.HEADER_BG, 
#             fg=self.config.HEADER_FG
#         ).pack(side=tk.LEFT, padx=20)
        
#         # Title section
#         title_frame = tk.Frame(header_frame, bg=self.config.HEADER_BG)
#         title_frame.pack(side=tk.LEFT, fill=tk.Y, pady=10)
        
#         tk.Label(
#             title_frame, 
#             text="TƯ VẤN DU HỌC AI", 
#             font=self.config.FONT_HEADER_TITLE, 
#             bg=self.config.HEADER_BG, 
#             fg=self.config.HEADER_FG
#         ).pack(anchor="w")
        
#         tk.Label(
#             title_frame, 
#             text="Trợ lý thông minh hỗ trợ tìm kiếm trường đại học", 
#             font=self.config.FONT_HEADER_SUB, 
#             bg=self.config.HEADER_BG, 
#             fg="#ecf0f1"
#         ).pack(anchor="w")
        
#         # Clear chat button
#         tk.Button(
#             header_frame,
#             text="🔄 Làm mới",
#             font=("Arial", 10),
#             bg="#e74c3c",
#             fg="white",
#             relief=tk.FLAT,
#             padx=15,
#             pady=8,
#             cursor="hand2",
#             command=self.clear_chat
#         ).pack(side=tk.RIGHT, padx=20)
    
#     def _create_chat_area(self, parent):
#         """
#         Tạo khu vực hiển thị chat
        
#         Args:
#             parent: Widget cha
#         """
#         chat_frame = tk.Frame(
#             parent, 
#             bg=self.config.CHAT_BG, 
#             relief=tk.GROOVE, 
#             bd=2
#         )
#         chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
#         # ScrolledText widget
#         self.output = scrolledtext.ScrolledText(
#             chat_frame, 
#             wrap=tk.WORD, 
#             state="disabled", 
#             font=self.config.FONT_TEXT, 
#             bg=self.config.CHAT_BG, 
#             fg=self.config.TEXT_PRIMARY, 
#             padx=15, 
#             pady=15, 
#             relief=tk.FLAT
#         )
#         self.output.pack(fill=tk.BOTH, expand=True)
        
#         # Cấu hình text tags cho styling
#         self.output.tag_config(
#             "user_label", 
#             foreground=self.config.USER_COLOR, 
#             font=self.config.FONT_TEXT_BOLD
#         )
#         self.output.tag_config(
#             "user_text", 
#             foreground=self.config.TEXT_PRIMARY
#         )
#         self.output.tag_config(
#             "assistant_label", 
#             foreground=self.config.ASSISTANT_COLOR, 
#             font=self.config.FONT_TEXT_BOLD
#         )
#         self.output.tag_config(
#             "assistant_text", 
#             foreground=self.config.TEXT_SECONDARY
#         )
#         self.output.tag_config(
#             "error", 
#             foreground=self.config.ERROR_COLOR, 
#             font=("Segoe UI", 11, "italic")
#         )
#         self.output.tag_config(
#             "typing", 
#             foreground=self.config.STATUS_COLOR,
#             font=("Segoe UI", 14)
#         )
        
#         # Hiển thị welcome message
#         self.output.config(state="normal")
#         self.output.insert(tk.END, self.config.WELCOME_MSG, "assistant_text")
#         self.output.config(state="disabled")
    
#     def _create_input_area(self, parent):
#         """
#         Tạo khu vực nhập liệu
        
#         Args:
#             parent: Widget cha
#         """
#         input_frame = tk.Frame(parent, bg=self.config.BACKGROUND)
#         input_frame.pack(fill=tk.X)
        
#         # Entry container
#         entry_container = tk.Frame(
#             input_frame, 
#             bg=self.config.CHAT_BG, 
#             relief=tk.SOLID, 
#             bd=1
#         )
#         entry_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
#         # Entry widget
#         self.entry = tk.Entry(
#             entry_container, 
#             font=("Segoe UI", 12), 
#             bg=self.config.CHAT_BG, 
#             fg=self.config.TEXT_PRIMARY, 
#             relief=tk.FLAT, 
#             bd=5
#         )
#         self.entry.pack(fill=tk.BOTH, expand=True)
#         self.entry.bind("<Return>", lambda e: self.send_message())
#         self.entry.focus()
        
#         # Send button
#         self.send_btn = tk.Button(
#             input_frame, 
#             text="Gửi 📤", 
#             command=self.send_message,
#             font=self.config.FONT_BUTTON,
#             bg=self.config.BUTTON_BG, 
#             fg=self.config.BUTTON_FG,
#             relief=tk.FLAT, 
#             bd=0,
#             padx=25, 
#             pady=10,
#             cursor="hand2",
#             activebackground=self.config.BUTTON_ACTIVE,
#             activeforeground=self.config.BUTTON_FG
#         )
#         self.send_btn.pack(side=tk.RIGHT)
        
#         # Status label
#         self.status_label = tk.Label(
#             parent, 
#             text="", 
#             font=self.config.FONT_STATUS, 
#             bg=self.config.BACKGROUND, 
#             fg=self.config.STATUS_COLOR
#         )
#         self.status_label.pack(pady=(5, 0))

#     def start_typing_animation(self):
#         """Bắt đầu animation dấu ba chấm"""
#         self.typing_animation_running = True
        
#         # Thêm label "Trợ lý:" và đánh dấu vị trí
#         self.output.config(state="normal")
#         self.output.insert(tk.END, "🤖 Trợ lý: ", "assistant_label")
#         self.typing_mark = self.output.index(tk.END)
#         self.output.config(state="disabled")
        
#         # Bắt đầu animation
#         self._animate_typing(0)
    
#     def _animate_typing(self, dot_count):
#         """
#         Animation dấu ba chấm
        
#         Args:
#             dot_count: Số lượng dấu chấm hiện tại (0-3)
#         """
#         if not self.typing_animation_running:
#             return
        
#         # Tạo chuỗi dấu chấm
#         dots = "●" * (dot_count + 1) + "○" * (2 - dot_count)
        
#         # Cập nhật text
#         self.output.config(state="normal")
        
#         # Xóa dấu chấm cũ nếu có
#         if self.typing_mark:
#             self.output.delete(self.typing_mark, tk.END)
        
#         # Thêm dấu chấm mới
#         self.output.insert(tk.END, dots, "typing")
#         self.output.see(tk.END)
#         self.output.config(state="disabled")
        
#         # Lặp lại animation
#         next_count = (dot_count + 1) % 3
#         self.output.after(400, lambda: self._animate_typing(next_count))
    
#     def stop_typing_animation(self):
#         """Dừng animation và xóa dấu ba chấm"""
#         self.typing_animation_running = False
        
#         if self.typing_mark:
#             self.output.config(state="normal")
#             # Xóa dấu ba chấm
#             self.output.delete(self.typing_mark, tk.END)
#             self.output.config(state="disabled")
#             self.typing_mark = None

#     def send_message(self):
#         """Xử lý gửi tin nhắn"""
#         if self.is_processing:
#             return
            
#         user_text = self.entry.get().strip()
#         if not user_text:
#             return

#         # Hiển thị tin nhắn của user
#         self.output.config(state="normal")
#         self.output.insert(tk.END, "👤 Bạn: ", "user_label")
#         self.output.insert(tk.END, f"{user_text}\n\n", "user_text")
#         self.output.config(state="disabled")
#         self.output.see(tk.END)

#         # Clear entry
#         self.entry.delete(0, tk.END)
        
#         # Update UI state
#         self.is_processing = True
#         self.send_btn.config(state="disabled", bg=self.config.BUTTON_DISABLED)
#         self.status_label.config(text="⏳ Đang xử lý...")
        
#         # Bắt đầu typing animation
#         self.start_typing_animation()

#         # Gửi request trong background thread
#         threading.Thread(
#             target=self.chat_engine.ask_stream,
#             args=(user_text, self.output, self.on_response_start, self.update_status),
#             daemon=True
#         ).start()

#     def on_response_start(self):
#         """Callback khi bắt đầu nhận response từ AI"""
#         # Dừng typing animation
#         self.stop_typing_animation()

#     def update_status(self, is_processing):
#         """
#         Cập nhật trạng thái UI
        
#         Args:
#             is_processing: True nếu đang xử lý, False nếu hoàn thành
#         """
#         self.is_processing = is_processing
#         if not is_processing:
#             self.send_btn.config(state="normal", bg=self.config.BUTTON_BG)
#             self.status_label.config(text="")

#     def clear_chat(self):
#         """Xóa lịch sử chat"""
#         # Dừng animation nếu đang chạy
#         self.stop_typing_animation()
        
#         self.output.config(state="normal")
#         self.output.delete(1.0, tk.END)
#         self.output.insert(tk.END, self.config.WELCOME_MSG, "assistant_text")
#         self.output.config(state="disabled")
        
#         # Reset chat engine
#         self.chat_engine.clear_history(SYSTEM_PROMPT)








#chatbot.py:
import tkinter as tk
from tkinter import ttk
import threading
from .config.prompts import SYSTEM_PROMPT
from .config.ui_config import ChatbotConfig
from .engine.chat_engine import ChatEngine

class ChatBubble(tk.Frame):
    """Component hiển thị một tin nhắn (Bong bóng chat)"""
    def __init__(self, parent, text, is_user=False, is_status=False, **kwargs):
        super().__init__(parent, **kwargs)
        self.config = ChatbotConfig()
        self.is_user = is_user
        
        # Thiết lập màu sắc
        bg_color = self.config.USER_COLOR if is_user else "#ffffff"
        fg_color = "white" if is_user else "#2c3e50"
        
        if is_status:
            bg_color = self.config.BACKGROUND # Trùng màu nền để tàng hình
            fg_color = "#7f8c8d"
            font_style = ("Segoe UI", 9, "italic")
            relief = tk.FLAT
            bd = 0
        else:
            font_style = ("Segoe UI", 11)
            relief = tk.RAISED if not is_user else tk.FLAT
            bd = 1

        # Container cho dòng chat (để căn trái/phải)
        self.configure(bg=self.config.BACKGROUND)
        
        # Avatar (Chỉ hiện cho Bot hoặc User)
        avatar_text = "👤" if is_user else "🤖"
        if is_status: avatar_text = "⚙️"
        
        self.avatar = tk.Label(
            self, 
            text=avatar_text, 
            font=("Arial", 16), 
            bg=self.config.BACKGROUND,
            fg="#555"
        )
        
        # Bong bóng chứa text
        self.bubble_frame = tk.Frame(
            self,
            bg=bg_color,
            bd=bd,
            relief=relief
        )
        
        # Label hiển thị nội dung
        self.msg_label = tk.Label(
            self.bubble_frame,
            text=text,
            font=font_style,
            bg=bg_color,
            fg=fg_color,
            wraplength=450, # Tự xuống dòng nếu quá dài
            justify="left"
        )
        self.msg_label.pack(padx=10, pady=8)

        # Layout: User bên phải, Bot bên trái
        if is_user:
            self.avatar.pack(side=tk.RIGHT, padx=(5, 0), anchor="n")
            self.bubble_frame.pack(side=tk.RIGHT, anchor="n")
        else:
            self.avatar.pack(side=tk.LEFT, padx=(0, 5), anchor="n")
            self.bubble_frame.pack(side=tk.LEFT, anchor="n")

    def update_text(self, new_text):
        """Cập nhật nội dung cho bong bóng (dùng cho streaming)"""
        self.msg_label.config(text=new_text)


class ChatbotTab:
    """Tab Chatbot AI với giao diện Bong bóng"""
    
    def __init__(self, parent_frame):
        self.frame = parent_frame
        # Truyền self vào ChatEngine để Engine gọi lại các hàm UI
        self.chat_engine = ChatEngine(SYSTEM_PROMPT, db_path="universities_db.db", ui_controller=self)
        self.config = ChatbotConfig()
        self.is_processing = False
        
        # Biến lưu bong bóng đang stream hiện tại
        self.current_streaming_bubble = None
        self.current_stream_text = ""
        self.typing_bubble = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # 1. Main Layout
        main_container = tk.Frame(self.frame, bg=self.config.BACKGROUND)
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 2. Header
        self._create_header(main_container)
        
        # 3. Khu vực Chat (Scrollable Canvas)
        self._create_chat_area(main_container)
        
        # 4. Khu vực nhập liệu
        self._create_input_area(main_container)
        
        # 5. Welcome Message
        self.add_bot_message(self.config.WELCOME_MSG)

    def _create_header(self, parent):
        header = tk.Frame(parent, bg=self.config.HEADER_BG, height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        tk.Label(header, text="🎓 AI DU HỌC", font=("Arial", 14, "bold"), 
                 bg=self.config.HEADER_BG, fg="white").pack(side=tk.LEFT, padx=20)
        
        tk.Button(header, text="Làm mới", command=self.clear_chat, 
                  bg="#e74c3c", fg="white", bd=0, padx=10).pack(side=tk.RIGHT, padx=10)

    def _create_chat_area(self, parent):
        # Frame chứa Canvas và Scrollbar
        chat_frame = tk.Frame(parent, bg=self.config.BACKGROUND)
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas
        self.canvas = tk.Canvas(chat_frame, bg=self.config.BACKGROUND, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.canvas.yview)
        
        # Frame nội dung bên trong Canvas
        self.inner_frame = tk.Frame(self.canvas, bg=self.config.BACKGROUND)
        
        # Tạo window trong canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        # Config scroll
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Binding events để update scroll region
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Scroll bằng chuột
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _create_input_area(self, parent):
        input_frame = tk.Frame(parent, bg="white", pady=10)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.entry = tk.Entry(input_frame, font=("Segoe UI", 12), bd=0, bg="#f0f2f5")
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, ipady=8)
        self.entry.bind("<Return>", lambda e: self.send_message())
        
        self.send_btn = tk.Button(input_frame, text="Gửi ➤", command=self.send_message,
                                  bg=self.config.BUTTON_BG, fg="white", bd=0, font=("Arial", 10, "bold"), padx=15)
        self.send_btn.pack(side=tk.RIGHT, padx=10)

    # --- UI EVENT HANDLERS ---
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # Resize inner_frame theo canvas width
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _scroll_to_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    # --- CHAT LOGIC ---
    def add_user_message(self, text):
        bubble = ChatBubble(self.inner_frame, text, is_user=True)
        bubble.pack(fill=tk.X, pady=5, padx=10)
        self._scroll_to_bottom()

    def add_bot_message(self, text):
        """Thêm tin nhắn bot hoàn chỉnh"""
        bubble = ChatBubble(self.inner_frame, text, is_user=False)
        bubble.pack(fill=tk.X, pady=5, padx=10)
        self._scroll_to_bottom()

    def add_log_message(self, text, log_type="status"):
        """Thêm tin nhắn log (nhỏ, màu xám)"""
        # Mapping icon cho đẹp
        icon = ""
        if log_type == "sql": icon = "📝 SQL: "
        elif log_type == "error": icon = "❌ "
        elif log_type == "success": icon = "✅ "
        elif log_type == "thinking": icon = "🔍 "
        
        display_text = f"{icon}{text}"
        bubble = ChatBubble(self.inner_frame, display_text, is_user=False, is_status=True)
        bubble.pack(fill=tk.X, pady=2, padx=30) # Padding lớn hơn để thụt vào
        self._scroll_to_bottom()

    # --- STREAMING LOGIC ---
    def start_bot_stream(self):
        """Được gọi khi bắt đầu nhận chunk đầu tiên của câu trả lời"""
        # 1. Xóa animation typing
        self.stop_typing_animation()
        
        # 2. Tạo bong bóng Bot rỗng để hứng text
        self.current_stream_text = ""
        self.current_streaming_bubble = ChatBubble(self.inner_frame, "", is_user=False)
        self.current_streaming_bubble.pack(fill=tk.X, pady=5, padx=10)
        self._scroll_to_bottom()

    def update_bot_stream(self, chunk):
        """Được gọi liên tục khi có text mới"""
        if self.current_streaming_bubble:
            self.current_stream_text += chunk
            self.current_streaming_bubble.update_text(self.current_stream_text)
            self._scroll_to_bottom()

    def show_typing_animation(self):
        """Hiện bong bóng '...'"""
        if not self.typing_bubble:
            self.typing_bubble = ChatBubble(self.inner_frame, " ● ● ● ", is_user=False, is_status=True)
            self.typing_bubble.pack(fill=tk.X, pady=5, padx=10)
            self._scroll_to_bottom()

    def stop_typing_animation(self):
        """Xóa bong bóng '...'"""
        if self.typing_bubble:
            self.typing_bubble.destroy()
            self.typing_bubble = None

    def send_message(self):
        if self.is_processing: return
        
        text = self.entry.get().strip()
        if not text: return
        
        # 1. UI: Hiện tin nhắn User
        self.add_user_message(text)
        self.entry.delete(0, tk.END)
        
        # 2. UI: Khóa nút & Hiện typing
        self.is_processing = True
        self.send_btn.config(state="disabled")
        self.show_typing_animation()
        
        # 3. Logic: Gọi Engine trong thread
        threading.Thread(
            target=self.chat_engine.ask_stream,
            args=(text, self.on_process_complete),
            daemon=True
        ).start()

    def on_process_complete(self):
        """Callback khi toàn bộ quy trình kết thúc"""
        self.is_processing = False
        self.send_btn.config(state="normal")
        self.current_streaming_bubble = None # Reset bubble

    def clear_chat(self):
        # Xóa tất cả widget con trong inner_frame
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.chat_engine.clear_history(SYSTEM_PROMPT)
        self.add_bot_message(self.config.WELCOME_MSG)