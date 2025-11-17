import tkinter as tk
from tkinter import ttk, messagebox
from database import get_all_users, delete_user, update_user_profile

class UserManagementTab:
    """Admin only - User management"""
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        tk.Label(self.frame, text="QUẢN LÝ NGƯỜI DÙNG", 
                font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=20)
        
        # Treeview
        tree_frame = tk.Frame(self.frame)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.tree = ttk.Treeview(tree_frame, 
                                columns=("UID","Email","Full Name","Address","Phone"), 
                                show="headings", height=15)
        
        for col in ("UID","Email","Full Name","Address","Phone"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        btn_frame = tk.Frame(self.frame, bg="#f0f0f0")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Xóa người dùng", bg="#f44336", fg="white", 
                 width=15, command=self.delete_user).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Làm mới", bg="#2196F3", fg="white", 
                 width=15, command=self.refresh).pack(side=tk.LEFT, padx=5)
        
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
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn người dùng cần xóa")
            return
        values = self.tree.item(selected[0])['values']
        uid = values[0]
        email = values[1]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa người dùng {email}?"):
            if delete_user(uid):
                messagebox.showinfo("Thành công", "Đã xóa người dùng")
                self.refresh()


class ProfileTab:
    """User profile management"""
    def __init__(self, parent_frame, user_data):
        self.frame = parent_frame
        self.user_data = user_data
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        tk.Label(self.frame, text="THÔNG TIN CÁ NHÂN", 
                font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=20)
        
        # Form frame
        form_frame = tk.Frame(self.frame, bg="#f0f0f0")
        form_frame.pack(pady=20)
        
        # Read-only info
        tk.Label(form_frame, text="UID:", bg="#f0f0f0", width=15, 
                anchor="e").grid(row=0, column=0, padx=5, pady=10)
        tk.Label(form_frame, text=self.user_data[0], bg="#f0f0f0", 
                anchor="w").grid(row=0, column=1, padx=5, pady=10, sticky="w")
        
        tk.Label(form_frame, text="Email:", bg="#f0f0f0", width=15, 
                anchor="e").grid(row=1, column=0, padx=5, pady=10)
        tk.Label(form_frame, text=self.user_data[1], bg="#f0f0f0", 
                anchor="w").grid(row=1, column=1, padx=5, pady=10, sticky="w")
        
        # Editable fields
        tk.Label(form_frame, text="Họ tên:", bg="#f0f0f0", width=15, 
                anchor="e").grid(row=2, column=0, padx=5, pady=10)
        self.fullname_entry = tk.Entry(form_frame, width=30)
        self.fullname_entry.insert(0, self.user_data[2] or "")
        self.fullname_entry.grid(row=2, column=1, padx=5, pady=10)
        
        tk.Label(form_frame, text="Địa chỉ:", bg="#f0f0f0", width=15, 
                anchor="e").grid(row=3, column=0, padx=5, pady=10)
        self.address_entry = tk.Entry(form_frame, width=30)
        self.address_entry.insert(0, self.user_data[3] or "")
        self.address_entry.grid(row=3, column=1, padx=5, pady=10)
        
        tk.Label(form_frame, text="Số điện thoại:", bg="#f0f0f0", width=15, 
                anchor="e").grid(row=4, column=0, padx=5, pady=10)
        self.phone_entry = tk.Entry(form_frame, width=30)
        self.phone_entry.insert(0, self.user_data[4] or "")
        self.phone_entry.grid(row=4, column=1, padx=5, pady=10)
        
        # Save button
        tk.Button(form_frame, text="Lưu thay đổi", bg="#4CAF50", fg="white", 
                 width=15, command=self.save_profile).grid(
                     row=5, column=0, columnspan=2, pady=20)
        
    def save_profile(self):
        fullname = self.fullname_entry.get().strip()
        address = self.address_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not fullname:
            messagebox.showwarning("Cảnh báo", "Họ tên không được để trống")
            return
            
        if update_user_profile(self.user_data[0], fullname, address, phone):
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin cá nhân")
            # Update local user data
            self.user_data = (self.user_data[0], self.user_data[1], 
                            fullname, address, phone, self.user_data[5])
        else:
            messagebox.showerror("Lỗi", "Không thể cập nhật thông tin")