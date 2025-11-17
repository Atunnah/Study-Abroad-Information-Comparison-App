import tkinter as tk
from tkinter import ttk, messagebox
from database import register_user, login_user

class LoginWindow:
    def __init__(self, parent, on_login_success):
        self.window = tk.Toplevel(parent)
        self.window.title("Đăng nhập")
        self.window.geometry("400x300")
        self.window.configure(bg="#f0f0f0")
        self.on_login_success = on_login_success
        
        # Center window
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        tk.Label(self.window, text="ĐĂNG NHẬP", font=("Arial", 18, "bold"), 
                bg="#f0f0f0").pack(pady=20)
        
        # Frame for inputs
        frame = tk.Frame(self.window, bg="#f0f0f0")
        frame.pack(pady=10)
        
        tk.Label(frame, text="Email:", bg="#f0f0f0", width=10, anchor="e").grid(
            row=0, column=0, padx=5, pady=10)
        self.email_entry = tk.Entry(frame, width=25)
        self.email_entry.grid(row=0, column=1, padx=5, pady=10)
        
        tk.Label(frame, text="Password:", bg="#f0f0f0", width=10, anchor="e").grid(
            row=1, column=0, padx=5, pady=10)
        self.password_entry = tk.Entry(frame, width=25, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(self.window, bg="#f0f0f0")
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="Đăng nhập", bg="#4CAF50", fg="white", 
                 width=12, command=self.login).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Hủy", bg="#f44336", fg="white", 
                 width=12, command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Register link
        self.register_frame = tk.Frame(self.window, bg="#f0f0f0")
        self.register_frame.pack(pady=10)
        
        tk.Label(self.register_frame, text="Chưa có tài khoản?", 
                bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        tk.Button(self.register_frame, text="Đăng ký ngay", bg="#2196F3", 
                 fg="white", command=self.open_register).pack(side=tk.LEFT)
        
    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not email or not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin")
            return
            
        user_data = login_user(email, password)
        if user_data:
            messagebox.showinfo("Thành công", "Đăng nhập thành công!")
            self.window.destroy()
            self.on_login_success(user_data)
        else:
            messagebox.showerror("Lỗi", "Email hoặc mật khẩu không đúng!")
            
    def open_register(self):
        self.window.destroy()
        RegisterWindow(self.window.master, self.on_login_success)


class RegisterWindow:
    def __init__(self, parent, on_login_success):
        self.window = tk.Toplevel(parent)
        self.window.title("Đăng ký")
        self.window.geometry("450x450")
        self.window.configure(bg="#f0f0f0")
        self.on_login_success = on_login_success
        
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        tk.Label(self.window, text="ĐĂNG KÝ TÀI KHOẢN", font=("Arial", 18, "bold"), 
                bg="#f0f0f0").pack(pady=20)
        
        # Frame for inputs
        frame = tk.Frame(self.window, bg="#f0f0f0")
        frame.pack(pady=10)
        
        fields = [
            ("Email:", "email"),
            ("Password:", "password"),
            ("Họ tên:", "fullname"),
            ("Địa chỉ:", "address"),
            ("Số điện thoại:", "phone")
        ]
        
        self.entries = {}
        for idx, (label, field) in enumerate(fields):
            tk.Label(frame, text=label, bg="#f0f0f0", width=15, anchor="e").grid(
                row=idx, column=0, padx=5, pady=8)
            entry = tk.Entry(frame, width=30, show="*" if field == "password" else None)
            entry.grid(row=idx, column=1, padx=5, pady=8)
            self.entries[field] = entry
        
        # Buttons
        btn_frame = tk.Frame(self.window, bg="#f0f0f0")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Đăng ký", bg="#4CAF50", fg="white", 
                 width=12, command=self.register).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Hủy", bg="#f44336", fg="white", 
                 width=12, command=self.back_to_login).pack(side=tk.LEFT, padx=5)
        
    def register(self):
        email = self.entries["email"].get().strip()
        password = self.entries["password"].get().strip()
        fullname = self.entries["fullname"].get().strip()
        address = self.entries["address"].get().strip()
        phone = self.entries["phone"].get().strip()
        
        if not email or not password or not fullname:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin bắt buộc")
            return
            
        if register_user(email, password, fullname, address, phone):
            messagebox.showinfo("Thành công", "Đăng ký thành công! Vui lòng đăng nhập.")
            self.back_to_login()
        else:
            messagebox.showerror("Lỗi", "Email đã tồn tại hoặc có lỗi xảy ra!")
            
    def back_to_login(self):
        self.window.destroy()
        LoginWindow(self.window.master, self.on_login_success)