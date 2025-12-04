# chatbot.py
import tkinter as tk
from tkinter import scrolledtext
import threading
import uuid
from datetime import datetime
from .config.prompts import SYSTEM_PROMPT
from .config.ui_config import ChatbotConfig
from .engine.chat_engine import ChatEngine
from .engine.database_helper import DatabaseHelper  # Import DatabaseHelper

class ChatbotTab:
    """
    Tab Chatbot AI với giao diện Đa hội thoại (Sidebar + Chat) + Lưu Database
    """
    
    # [SỬA ĐỔI] Thêm tham số current_user_id
    def __init__(self, parent_frame, current_user_id):
        self.master_frame = parent_frame
        self.config = ChatbotConfig()
        
        # Lưu ID người dùng để biết load lịch sử của ai
        self.user_id = current_user_id 
        self.db_helper = DatabaseHelper() # Khởi tạo DB Helper
        
        # Quản lý đa hội thoại
        self.sessions = {}
        self.current_session_id = None
        
        # State xử lý
        self.is_processing = False
        self.stop_event = threading.Event()
        self.typing_animation_running = False
        self.typing_mark = None
        
        # State giao diện
        self.is_sidebar_visible = True
        
        self.setup_ui()
        
        # [SỬA ĐỔI] Thay vì tạo mới, load từ DB trước
        self.load_sessions_from_db()
        
    def setup_ui(self):
        """Chia layout thành Sidebar (Trái) và Main Chat (Phải)"""
        
        # 1. Sidebar Frame
        self.sidebar_frame = tk.Frame(self.master_frame, bg=self.config.SIDEBAR_BG, width=250)
        self.sidebar_frame.pack_propagate(False) 
        
        self._create_sidebar_content()
        
        # 2. Main Chat Area Frame
        self.main_chat_frame = tk.Frame(self.master_frame, bg=self.config.BACKGROUND)
        
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.main_chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._create_main_chat_ui()

    # ================= UI SIDEBAR (GIỮ NGUYÊN) =================
    
    def _create_sidebar_content(self):
        # 1. Khu vực Header của Sidebar
        top_frame = tk.Frame(self.sidebar_frame, bg=self.config.SIDEBAR_BG, pady=20, padx=15)
        top_frame.pack(fill=tk.X)

        title_lbl = tk.Label(
            top_frame, text="LỊCH SỬ CHAT",
            bg=self.config.SIDEBAR_BG, fg=self.config.SIDEBAR_FG,
            font=("Segoe UI", 11, "bold"), anchor="w"
        )
        title_lbl.pack(fill=tk.X, pady=(0, 15)) 
        
        new_chat_btn = tk.Button(
            top_frame, text="+  Đoạn chat mới",
            bg=self.config.BUTTON_BG, fg="white",
            activebackground=self.config.BUTTON_ACTIVE, activeforeground="white",
            relief=tk.FLAT, font=self.config.FONT_BUTTON,
            cursor="hand2", pady=6,
            command=self.create_new_session
        )
        new_chat_btn.pack(fill=tk.X)
        
        separator = tk.Frame(self.sidebar_frame, bg=self.config.SEPARATOR_COLOR, height=1)
        separator.pack(fill=tk.X, padx=15, pady=(0, 10))

        # 2. Khu vực Danh sách
        list_container = tk.Frame(self.sidebar_frame, bg=self.config.SIDEBAR_BG)
        list_container.pack(fill=tk.BOTH, expand=True)

        self.session_list_canvas = tk.Canvas(list_container, bg=self.config.SIDEBAR_BG, highlightthickness=0, bd=0)
        self.session_list_frame = tk.Frame(self.session_list_canvas, bg=self.config.SIDEBAR_BG)
        
        self.session_list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_window = self.session_list_canvas.create_window((0, 0), window=self.session_list_frame, anchor="nw", width=220)
        
        self.session_list_frame.bind("<Configure>", self._on_frame_configure)
        self.session_list_canvas.bind("<Configure>", self._on_canvas_configure)
        
        self.sidebar_frame.bind("<Enter>", self._bind_mouse_scroll)
        self.sidebar_frame.bind("<Leave>", self._unbind_mouse_scroll)
        self._bind_to_mousewheel(top_frame)
        self._bind_to_mousewheel(self.sidebar_frame)

    def _on_frame_configure(self, event):
        self.session_list_canvas.configure(scrollregion=self.session_list_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        canvas_width = event.width
        self.session_list_canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _on_mousewheel(self, event):
        try:
            self.session_list_canvas.update_idletasks()
            bbox = self.session_list_canvas.bbox("all")
            if not bbox: return
            
            content_height = bbox[3] - bbox[1]
            visible_height = self.session_list_canvas.winfo_height()
            
            if content_height > visible_height:
                if event.delta > 0:
                    self.session_list_canvas.yview_scroll(-1, "units")
                elif event.delta < 0:
                    self.session_list_canvas.yview_scroll(1, "units")
        except Exception:
            pass

    def _bind_mouse_scroll(self, event):
        self.session_list_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse_scroll(self, event):
        self.session_list_canvas.unbind_all("<MouseWheel>")

    def _bind_to_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        for child in widget.winfo_children():
            self._bind_to_mousewheel(child)

    def _update_sidebar_list(self):
        for widget in self.session_list_frame.winfo_children():
            widget.destroy()
            
        sorted_sessions = sorted(self.sessions.items(), key=lambda x: x[1]['created_at'], reverse=True)
        
        for s_id, data in sorted_sessions:
            is_active = (s_id == self.current_session_id)
            bg_color = self.config.ITEM_ACTIVE_BG if is_active else self.config.SIDEBAR_BG
            fg_color = "white" if is_active else "#bdc3c7"
            
            item_frame = tk.Frame(self.session_list_frame, bg=bg_color)
            item_frame.pack(fill=tk.X, pady=1) 
            
            inner_frame = tk.Frame(item_frame, bg=bg_color, padx=15, pady=10)
            inner_frame.pack(fill=tk.X)
            
            icon_lbl = tk.Label(inner_frame, text="💬", bg=bg_color, fg=fg_color, font=("Segoe UI", 10))
            icon_lbl.pack(side=tk.LEFT)
            
            title_text = data['title']
            if len(title_text) > 18: title_text = title_text[:16] + "..."
            
            title_btn = tk.Button(
                inner_frame, text=title_text, bg=bg_color, fg=fg_color,
                anchor="w", relief=tk.FLAT, bd=0,
                font=("Segoe UI", 10, "bold" if is_active else "normal"),
                cursor="hand2", activebackground=bg_color, activeforeground=fg_color,
                command=lambda i=s_id: self.switch_session(i)
            )
            title_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
            
            del_btn = tk.Label(inner_frame, text="×", bg=bg_color, fg="#636e72", font=("Arial", 14), cursor="hand2")
            del_btn.pack(side=tk.RIGHT)
            
            del_btn.bind("<Enter>", lambda e, btn=del_btn: btn.config(fg="#ff7675"))
            del_btn.bind("<Leave>", lambda e, btn=del_btn: btn.config(fg="#636e72"))
            del_btn.bind("<Button-1>", lambda e, i=s_id: self.delete_session(i))
            inner_frame.bind("<Button-1>", lambda e, i=s_id: self.switch_session(i))
            icon_lbl.bind("<Button-1>", lambda e, i=s_id: self.switch_session(i))

        self.session_list_frame.update_idletasks()
        self.session_list_canvas.configure(scrollregion=self.session_list_canvas.bbox("all"))
        self._bind_to_mousewheel(self.session_list_frame)
        self.session_list_canvas.bind("<MouseWheel>", self._on_mousewheel)


    # ================= UI MAIN CHAT (GIỮ NGUYÊN) =================
    
    def _create_main_chat_ui(self):
        self.header_frame = tk.Frame(self.main_chat_frame, bg=self.config.HEADER_BG, height=50)
        self.header_frame.pack(fill=tk.X)
        self.header_frame.pack_propagate(False)
        
        self.toggle_btn = tk.Button(
            self.header_frame, text="≡", bg=self.config.BUTTON_TOGGLE_BG, fg=self.config.BUTTON_TOGGLE_FG,
            font=self.config.FONT_ICON, relief=tk.FLAT, activebackground=self.config.BUTTON_TOGGLE_HOVER,
            cursor="hand2", command=self.toggle_sidebar
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=(10, 5), pady=5)
        
        self.header_title = tk.Label(
            self.header_frame, text="Hội thoại mới", bg=self.config.HEADER_BG, fg=self.config.HEADER_FG,
            font=self.config.FONT_HEADER_TITLE
        )
        self.header_title.pack(side=tk.LEFT, padx=5, pady=10)
        
        chat_frame = tk.Frame(self.main_chat_frame, bg=self.config.CHAT_BG)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 10))
        
        self.output = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, state="disabled", font=self.config.FONT_TEXT, bg=self.config.CHAT_BG,
            padx=15, pady=15, relief=tk.FLAT
        )
        self.output.pack(fill=tk.BOTH, expand=True)
        
        self.output.tag_config("user_msg", justify='right', lmargin1=100, lmargin2=100, rmargin=10, foreground=self.config.USER_BG)
        self.output.tag_config("assistant_msg", justify='left', lmargin1=10, lmargin2=10, rmargin=100, foreground=self.config.TEXT_PRIMARY)
        self.output.tag_config("typing", justify='left', lmargin1=10, foreground=self.config.STATUS_COLOR, font=("Segoe UI", 14, "bold"))
        self.output.tag_config("error", justify='center', foreground=self.config.ERROR_COLOR)
        
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

    def toggle_sidebar(self):
        if self.is_sidebar_visible:
            self.sidebar_frame.pack_forget()
            self.is_sidebar_visible = False
        else:
            self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, before=self.main_chat_frame)
            self.is_sidebar_visible = True

    # ================= LOGIC DATABASE & SESSION (MỚI) =================

    def load_sessions_from_db(self):
        """[MỚI] Tải lịch sử chat từ Database của user hiện tại"""
        saved_sessions = self.db_helper.get_user_sessions(self.user_id)
        
        if saved_sessions:
            for s in saved_sessions:
                s_id = s['session_id']
                title = s['title']
                created_at = s['created_at'] 
                
                # Tạo engine
                engine = ChatEngine(SYSTEM_PROMPT, db_path="universities_db.db")
                
                # Load lịch sử tin nhắn từ bảng chat_messages
                messages = self.db_helper.get_session_history(s_id)
                # Ghép System prompt vào đầu
                full_history = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
                engine.chat_history = full_history
                
                self.sessions[s_id] = {
                    'engine': engine,
                    'title': title,
                    'created_at': created_at
                }
            
            # Switch sang session mới nhất
            if saved_sessions:
                first_id = saved_sessions[0]['session_id']
                self.switch_session(first_id)
        else:
            self.create_new_session()

    def create_new_session(self):
        """Tạo hội thoại mới và lưu vào DB"""
        if self.is_processing: return
            
        session_id = str(uuid.uuid4())
        session_count = len(self.sessions) + 1
        title = f"Hội thoại {session_count}"
        
        new_session = {
            'engine': ChatEngine(SYSTEM_PROMPT, db_path="universities_db.db"),
            'title': title,
            'created_at': datetime.now().isoformat()
        }
        
        self.sessions[session_id] = new_session
        
        # [MỚI] Lưu session vào DB
        self.db_helper.save_session(session_id, self.user_id, title)
        
        self.switch_session(session_id)

    def switch_session(self, session_id):
        if self.is_processing:
            self.cancel_request()
            
        self.current_session_id = session_id
        
        self._update_sidebar_list()
        current_data = self.sessions[session_id]
        self.header_title.config(text=current_data['title'])
        self._render_current_history()

    def delete_session(self, session_id):
        """Xóa hội thoại khỏi RAM và DB"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            
            # [MỚI] Xóa khỏi DB
            self.db_helper.delete_session(session_id)
            
            if self.current_session_id == session_id:
                if self.sessions:
                    first_id = list(self.sessions.keys())[0]
                    self.switch_session(first_id)
                else:
                    self.create_new_session()
            else:
                self._update_sidebar_list()

    def _render_current_history(self):
        engine = self.sessions[self.current_session_id]['engine']
        history = engine.chat_history
        
        self.output.config(state="normal")
        self.output.delete(1.0, tk.END)
        
        if len(history) <= 1:
            self.append_message("assistant", self.config.WELCOME_MSG)
        else:
            for msg in history[1:]:
                self.append_message(msg['role'], msg['content'])
                
        self.output.config(state="disabled")
        self.output.see(tk.END)

    # ================= LOGIC CHAT (CẬP NHẬT GỬI DB) =================

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

        # 1. UI & DB (Lưu tin nhắn User)
        self.append_message("user", user_text)
        self.entry.delete(0, tk.END)
        
        # [MỚI] Lưu tin nhắn user vào DB
        self.db_helper.save_message(self.current_session_id, "user", user_text)
        
        # 2. Update Title (nếu cần)
        current_sess = self.sessions[self.current_session_id]
        engine = current_sess['engine']
        
        if len(engine.chat_history) == 1: 
            new_title = (user_text[:25] + '..') if len(user_text) > 25 else user_text
            current_sess['title'] = new_title
            self.header_title.config(text=new_title)
            
            # [MỚI] Cập nhật title trong DB
            self.db_helper.save_session(self.current_session_id, self.user_id, new_title)
            self._update_sidebar_list()

        # 3. Trạng thái xử lý
        self.is_processing = True
        self.stop_event.clear()
        self.action_btn.config(text="Hủy ❌", bg=self.config.BUTTON_CANCEL, command=self.cancel_request)
        self.status_label.config(text="⏳ Đang suy nghĩ...")
        self.start_typing_animation()

        # 4. Gửi request (Dùng Wrapper để lưu tin nhắn AI sau khi xong)
        threading.Thread(
            target=self._ask_stream_wrapper, 
            args=(engine, user_text),
            daemon=True
        ).start()

    def _ask_stream_wrapper(self, engine, user_text):
        """Wrapper để gọi engine và lưu kết quả vào DB sau khi xong"""
        # Gọi hàm stream gốc
        engine.ask_stream(
            user_text, 
            self.output, 
            self.on_response_start, 
            self.update_status, 
            self.stop_event
        )
        
        # [MỚI] Sau khi stream xong (hoặc bị cancel), lưu tin nhắn cuối cùng của AI vào DB
        # Kiểm tra nếu message cuối cùng là assistant thì mới lưu
        if len(engine.chat_history) > 0:
            last_msg = engine.chat_history[-1]
            if last_msg['role'] == 'assistant':
                self.db_helper.save_message(self.current_session_id, "assistant", last_msg['content'])

    # --- Animation & Callbacks ---
    
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