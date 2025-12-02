import tkinter as tk
from tkinter import ttk, messagebox
# Giữ nguyên imports logic của bạn
from database import get_all_users, delete_user, update_user_profile, get_user_favorites, remove_favorite

# --- CẤU HÌNH MÀU SẮC & FONT (UI CONFIG) ---
COLORS = {
    "bg_main": "#F3F4F6",       # Màu nền tổng thể (Xám nhạt hiện đại)
    "bg_card": "#FFFFFF",       # Màu nền các khối (Trắng)
    "primary": "#4F46E5",       # Màu chủ đạo (Indigo)
    "primary_hover": "#4338CA", # Màu khi hover nút chính
    "danger": "#EF4444",        # Màu xóa/cảnh báo (Đỏ dịu)
    "danger_hover": "#DC2626",  # Màu khi hover nút xóa
    "text_main": "#1F2937",     # Màu chữ chính (Đen xám)
    "text_sub": "#6B7280",      # Màu chữ phụ (Xám ghi)
    "input_bg": "#F9FAFB",      # Màu nền ô nhập liệu
    "border": "#E5E7EB"         # Màu đường viền
}

FONTS = {
    "h1": ("Segoe UI", 20, "bold"),
    "h2": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9)
}

class UserManagementTab:
    """Admin only - User management"""
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.setup_ui()
        
    def setup_ui(self):
        # Main container (Full màn hình, nền xám nhạt)
        self.frame.configure(bg=COLORS["bg_main"])
        main_container = tk.Frame(self.frame, bg=COLORS["bg_main"])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- 1. HEADER CARD ---
        header_card = tk.Frame(main_container, bg=COLORS["bg_card"], padx=20, pady=15)
        header_card.pack(fill="x", pady=(0, 20))
        
        # Title Layout
        header_top = tk.Frame(header_card, bg=COLORS["bg_card"])
        header_top.pack(fill="x")
        
        # Icon & Text
        tk.Label(header_top, text="👥", font=("Segoe UI", 24), bg=COLORS["bg_card"]).pack(side="left", padx=(0, 15))
        
        title_box = tk.Frame(header_top, bg=COLORS["bg_card"])
        title_box.pack(side="left", fill="y")
        tk.Label(title_box, text="User Management", font=FONTS["h1"], bg=COLORS["bg_card"], fg=COLORS["text_main"]).pack(anchor="w")
        tk.Label(title_box, text="Manage system users and permissions", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_sub"]).pack(anchor="w")

        # Admin Badge (Góc phải)
        badge = tk.Label(header_top, text="🔐 ADMIN ACCESS", bg="#FEF3C7", fg="#D97706", font=("Segoe UI", 9, "bold"), padx=10, pady=5)
        badge.pack(side="right")

        # --- 2. TOOLBAR (Action Buttons) ---
        toolbar = tk.Frame(main_container, bg=COLORS["bg_main"])
        toolbar.pack(fill="x", pady=(0, 10))

        # Refresh Button
        btn_refresh = tk.Button(toolbar, text="↻ Refresh List", bg=COLORS["primary"], fg="white",
                                font=FONTS["body_bold"], relief="flat", cursor="hand2",
                                activebackground=COLORS["primary_hover"], activeforeground="white",
                                padx=15, pady=8, command=self.refresh)
        btn_refresh.pack(side="left")

        # Delete Button
        btn_delete = tk.Button(toolbar, text="🗑️ Delete User", bg=COLORS["danger"], fg="white",
                               font=FONTS["body_bold"], relief="flat", cursor="hand2",
                               activebackground=COLORS["danger_hover"], activeforeground="white",
                               padx=15, pady=8, command=self.delete_user)
        btn_delete.pack(side="right")

        # --- 3. DATA TABLE (TREEVIEW) ---
        table_frame = tk.Frame(main_container, bg=COLORS["bg_card"], bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal")

        # Style configuration (Xử lý màu sắc Treeview)
        style = ttk.Style()
        style.theme_use("clam")
        
        # Style cho Heading
        style.configure("User.Treeview.Heading", 
                        background=COLORS["bg_main"], 
                        foreground=COLORS["text_main"], 
                        font=FONTS["body_bold"], 
                        relief="flat",
                        padding=10)
        
        # Style cho Rows
        style.configure("User.Treeview", 
                        background="white",
                        fieldbackground="white",
                        foreground=COLORS["text_main"],
                        rowheight=40, # Tăng chiều cao dòng cho thoáng
                        font=FONTS["body"],
                        borderwidth=0)
        
        # Xử lý màu khi Select (Quan trọng: giữ text màu trắng để dễ đọc)
        style.map("User.Treeview", 
                  background=[('selected', COLORS["primary"])], 
                  foreground=[('selected', 'white')])

        columns = ("UID", "Email", "Full Name", "Address", "Phone")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", 
                                 style="User.Treeview", 
                                 yscrollcommand=scrollbar_y.set,
                                 xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        # Cấu hình cột (Responsive layout)
        col_configs = [
            ("UID", 60, "center"),
            ("Email", 200, "w"),
            ("Full Name", 180, "w"),
            ("Address", 250, "w"),
            ("Phone", 120, "center")
        ]

        for col, width, anchor in col_configs:
            self.tree.heading(col, text=col, anchor=anchor)
            self.tree.column(col, width=width, anchor=anchor, minwidth=50)

        self.refresh()
        
    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        users = get_all_users()
        if users:
            for user in users:
                self.tree.insert("", "end", values=user)
                
    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a user row to delete.")
            return
        
        values = self.tree.item(selected[0])['values']
        uid = values[0]
        email = values[1]
        
        if messagebox.askyesno("Confirm Deletion", f"Permanently delete user:\n\n{email}\n\nThis action cannot be undone."):
            if delete_user(uid):
                messagebox.showinfo("Success", "User deleted successfully.")
                self.refresh()


class ProfileTab:
    """User profile management"""
    def __init__(self, parent_frame, user_data):
        self.frame = parent_frame
        self.user_data = user_data
        self.setup_ui()
        
    def setup_ui(self):
        self.frame.configure(bg=COLORS["bg_main"])
        
        # --- SCROLLABLE CONTAINER SETUP ---
        canvas = tk.Canvas(self.frame, bg=COLORS["bg_main"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        
        self.scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_main"])
        
        # Bind sự kiện để update vùng scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Responsive width cho frame bên trong canvas
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", configure_canvas_width)

        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- KHẮC PHỤC LỖI SCROLL TẠI ĐÂY ---
        def _on_mousewheel(event):
            # Chỉ cuộn nếu canvas còn tồn tại
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception:
                pass

        # Chỉ bind event khi chuột nằm trong vùng Canvas
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Gỡ bind khi chuột rời khỏi vùng Canvas
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        # Gán sự kiện Enter/Leave cho canvas
        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)
        
        # --- CONTENT ---
        content_padding = tk.Frame(self.scrollable_frame, bg=COLORS["bg_main"], padx=30, pady=30)
        content_padding.pack(fill="both", expand=True)

        # 1. HEADER SECTION
        header_frame = tk.Frame(content_padding, bg=COLORS["bg_main"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="👤", font=("Segoe UI", 32), bg=COLORS["bg_main"]).pack(side="left", padx=(0, 15))
        header_text = tk.Frame(header_frame, bg=COLORS["bg_main"])
        header_text.pack(side="left")
        tk.Label(header_text, text="My Profile", font=FONTS["h1"], bg=COLORS["bg_main"], fg=COLORS["text_main"]).pack(anchor="w")
        tk.Label(header_text, text="View and update your personal information", font=FONTS["small"], bg=COLORS["bg_main"], fg=COLORS["text_sub"]).pack(anchor="w")

        # 2. INFO & FORM CARDS
        
        # --- CARD: ACCOUNT INFO (Read Only) ---
        info_card = tk.Frame(content_padding, bg=COLORS["bg_card"], padx=25, pady=25)
        info_card.pack(fill="x", pady=(0, 20))
        
        tk.Label(info_card, text="Account Details", font=FONTS["h2"], bg=COLORS["bg_card"], fg=COLORS["text_main"]).pack(anchor="w", pady=(0, 15))
        
        # Grid layout
        info_grid = tk.Frame(info_card, bg=COLORS["bg_card"])
        info_grid.pack(fill="x")
        info_grid.columnconfigure(1, weight=1)

        # Row 1: ID
        tk.Label(info_grid, text="User ID:", font=FONTS["body"], fg=COLORS["text_sub"], bg=COLORS["bg_card"]).grid(row=0, column=0, sticky="w", pady=5, padx=(0, 20))
        lbl_uid = tk.Label(info_grid, text=self.user_data[0], font=("Segoe UI", 11, "bold"), fg=COLORS["text_main"], bg="#F3F4F6", padx=10, pady=5, width=10, anchor="w")
        lbl_uid.grid(row=0, column=1, sticky="w", pady=5)

        # Row 2: Email
        tk.Label(info_grid, text="Email Address:", font=FONTS["body"], fg=COLORS["text_sub"], bg=COLORS["bg_card"]).grid(row=1, column=0, sticky="w", pady=5, padx=(0, 20))
        lbl_email = tk.Label(info_grid, text=self.user_data[1], font=("Segoe UI", 11, "bold"), fg=COLORS["text_main"], bg="#F3F4F6", padx=10, pady=5, width=30, anchor="w")
        lbl_email.grid(row=1, column=1, sticky="w", pady=5)

        # --- CARD: EDIT PROFILE ---
        edit_card = tk.Frame(content_padding, bg=COLORS["bg_card"], padx=25, pady=25)
        edit_card.pack(fill="x", pady=(0, 20))
        
        tk.Label(edit_card, text="Personal Information", font=FONTS["h2"], bg=COLORS["bg_card"], fg=COLORS["text_main"]).pack(anchor="w", pady=(0, 20))
        
        # Form Grid
        form_grid = tk.Frame(edit_card, bg=COLORS["bg_card"])
        form_grid.pack(fill="x")
        form_grid.columnconfigure(1, weight=1)

        fields = [
            ("Full Name", "fullname", self.user_data[2]),
            ("Address", "address", self.user_data[3]),
            ("Phone Number", "phone", self.user_data[4])
        ]
        
        self.entries = {}
        
        for idx, (label_text, field_key, value) in enumerate(fields):
            # Label
            tk.Label(form_grid, text=label_text, font=FONTS["body_bold"], fg=COLORS["text_main"], bg=COLORS["bg_card"])\
                .grid(row=idx, column=0, sticky="nw", pady=(10, 0), padx=(0, 20))
            
            # Entry Frame
            entry_frame = tk.Frame(form_grid, bg=COLORS["input_bg"], bd=1, relief="solid")
            entry_frame.grid(row=idx, column=1, sticky="ew", pady=(5, 10))
            
            # Entry
            entry = tk.Entry(entry_frame, font=FONTS["body"], bg=COLORS["input_bg"], relief="flat", fg=COLORS["text_main"])
            entry.insert(0, value or "")
            entry.pack(fill="x", padx=10, pady=8)
            
            if field_key == "fullname": self.fullname_entry = entry
            elif field_key == "address": self.address_entry = entry
            else: self.phone_entry = entry

        # Save Button
        btn_frame = tk.Frame(edit_card, bg=COLORS["bg_card"])
        btn_frame.pack(fill="x", pady=(20, 0))
        
        save_btn = tk.Button(btn_frame, text="💾 Save Changes", bg=COLORS["primary"], fg="white",
                            font=FONTS["body_bold"], relief="flat", cursor="hand2",
                            activebackground=COLORS["primary_hover"], activeforeground="white",
                            padx=20, pady=10, command=self.save_profile)
        save_btn.pack(side="right")

        # --- CARD: FAVORITES ---
        fav_card = tk.Frame(content_padding, bg=COLORS["bg_card"], padx=25, pady=25)
        fav_card.pack(fill="both", expand=True)
        
        # Fav Header
        fav_header = tk.Frame(fav_card, bg=COLORS["bg_card"])
        fav_header.pack(fill="x", pady=(0, 15))
        tk.Label(fav_header, text="⭐ Favorite Universities", font=FONTS["h2"], bg=COLORS["bg_card"], fg="#F59E0B").pack(side="left")
        
        # Fav Treeview
        fav_tree_frame = tk.Frame(fav_card, bg="white", bd=1, relief="solid")
        fav_tree_frame.pack(fill="both", expand=True)
        
        fav_style = ttk.Style()
        fav_style.configure("Fav.Treeview.Heading", 
                            background=COLORS["bg_main"], 
                            foreground=COLORS["text_main"], 
                            font=FONTS["body_bold"],
                            relief="flat", padding=5)
        fav_style.configure("Fav.Treeview", 
                            rowheight=35, 
                            font=FONTS["body"],
                            borderwidth=0)
        
        self.fav_tree = ttk.Treeview(
            fav_tree_frame,
            columns=("No", "University", "Country", "Date Added"),
            show="headings",
            height=8,
            style="Fav.Treeview"
        )
        
        # Columns
        fav_cols = [
            ("No", 50, "center"),
            ("University", 300, "w"),
            ("Country", 150, "w"),
            ("Date Added", 150, "center")
        ]
        for col, width, anchor in fav_cols:
            self.fav_tree.heading(col, text=col, anchor=anchor)
            self.fav_tree.column(col, width=width, anchor=anchor)
            
        fav_scroll = ttk.Scrollbar(fav_tree_frame, orient="vertical", command=self.fav_tree.yview)
        self.fav_tree.configure(yscroll=fav_scroll.set)
        
        self.fav_tree.pack(side="left", fill="both", expand=True)
        fav_scroll.pack(side="right", fill="y")

        # Remove Button
        remove_btn = tk.Button(fav_card, text="Remove Selected", bg="white", fg=COLORS["danger"],
                               font=FONTS["body_bold"], relief="solid", bd=1, cursor="hand2",
                               activebackground=COLORS["danger"], activeforeground="white",
                               padx=15, pady=6, command=self.delete_selected_favorite)
        remove_btn.pack(anchor="e", pady=(15, 0))
        
        self.load_favorites()

    def save_profile(self):
        fullname = self.fullname_entry.get().strip()
        address = self.address_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not fullname:
            messagebox.showwarning("Required Field", "Full name cannot be empty.")
            return
            
        if update_user_profile(self.user_data[0], fullname, address, phone):
            messagebox.showinfo("Profile Updated", "Your profile information has been updated successfully.")
            self.user_data = (
                self.user_data[0], self.user_data[1], 
                fullname, address, phone, self.user_data[5]
            )
        else:
            messagebox.showerror("Update Failed", "Could not update profile. Please try again.")
            
    def load_favorites(self):
        for item in self.fav_tree.get_children():
            self.fav_tree.delete(item)

        favorites = get_user_favorites(self.user_data[0])

        if not favorites:
            return

        for idx, (uid, name, country, added_time) in enumerate(favorites, start=1):
            self.fav_tree.insert("", "end", values=(idx, name, country or "N/A", added_time),
                                tags=(uid,))
                      
    def delete_selected_favorite(self):
        selected = self.fav_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a university from the list to remove.")
            return
        
        item = selected[0]
        tags = self.fav_tree.item(item)['tags']
        
        if not tags:
            return
            
        university_id = tags[0]
        
        if messagebox.askyesno("Confirm Removal", "Remove this university from your favorites?"):
            if remove_favorite(self.user_data[0], university_id):
                messagebox.showinfo("Success", "Removed from favorites.")
                self.load_favorites()
            else:
                messagebox.showerror("Error", "Could not remove favorite.")