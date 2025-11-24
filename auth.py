import tkinter as tk
from tkinter import ttk, messagebox
from database import register_user, login_user

class LoginWindow:
    def __init__(self, parent, on_login_success):
        self.window = tk.Toplevel(parent)
        self.window.title("Login")
        self.window.geometry("550x650")
        self.window.configure(bg="#ffffff")
        self.on_login_success = on_login_success
        
        # Center window
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header với gradient effect (dùng frame màu)
        header_frame = tk.Frame(self.window, bg="#1976D2", height=120)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Icon/Logo placeholder
        icon_label = tk.Label(header_frame, text="🔐", font=("Arial", 40), 
                             bg="#1976D2", fg="white")
        icon_label.pack(pady=15)
        
        tk.Label(header_frame, text="Welcome Back", font=("Arial", 20, "bold"), 
                bg="#1976D2", fg="white").pack()
        
        # Main content container
        content_frame = tk.Frame(self.window, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Input fields với shadow effect
        input_container = tk.Frame(content_frame, bg="#ffffff")
        input_container.pack(fill="x", pady=10)
        
        # Email field
        tk.Label(input_container, text="Email Address", bg="#ffffff", 
                fg="#424242", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        email_frame = tk.Frame(input_container, bg="#E3F2FD", relief="flat", bd=0)
        email_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(email_frame, text="📧", bg="#E3F2FD", font=("Arial", 14)).pack(
            side="left", padx=(10, 5))
        self.email_entry = tk.Entry(email_frame, font=("Arial", 11), bg="#E3F2FD",
                                    relief="flat", bd=0, fg="#424242")
        self.email_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=12)
        
        # Password field
        tk.Label(input_container, text="Password", bg="#ffffff", 
                fg="#424242", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        password_frame = tk.Frame(input_container, bg="#E3F2FD", relief="flat", bd=0)
        password_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(password_frame, text="🔒", bg="#E3F2FD", font=("Arial", 14)).pack(
            side="left", padx=(10, 5))
        self.password_entry = tk.Entry(password_frame, font=("Arial", 11), show="●",
                                      bg="#E3F2FD", relief="flat", bd=0, fg="#424242")
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=12)
        
        # Login button với hover effect simulation
        login_btn = tk.Button(content_frame, text="LOGIN", bg="#1976D2", fg="white",
                             font=("Arial", 12, "bold"), relief="flat", bd=0,
                             cursor="hand2", command=self.login, pady=12)
        login_btn.pack(fill="x", pady=(20, 10))
        
        # Cancel button
        cancel_btn = tk.Button(content_frame, text="Cancel", bg="#ffffff", 
                              fg="#757575", font=("Arial", 10), relief="flat",
                              bd=0, cursor="hand2", command=self.window.destroy)
        cancel_btn.pack(pady=(0, 20))
        
        # Divider
        divider_frame = tk.Frame(content_frame, bg="#ffffff")
        divider_frame.pack(fill="x", pady=10)
        
        tk.Frame(divider_frame, bg="#E0E0E0", height=1).pack(side="left", fill="x", expand=True)
        tk.Label(divider_frame, text=" OR ", bg="#ffffff", fg="#9E9E9E",
                font=("Arial", 9)).pack(side="left", padx=5)
        tk.Frame(divider_frame, bg="#E0E0E0", height=1).pack(side="left", fill="x", expand=True)
        
        # Register section
        register_container = tk.Frame(content_frame, bg="#F5F5F5", relief="flat")
        register_container.pack(fill="x", pady=10)
        
        register_inner = tk.Frame(register_container, bg="#F5F5F5")
        register_inner.pack(pady=15)
        
        tk.Label(register_inner, text="Don't have an account?", 
                bg="#F5F5F5", fg="#616161", font=("Arial", 10)).pack(side="left", padx=5)
        
        register_btn = tk.Button(register_inner, text="Sign Up", bg="#F5F5F5",
                                fg="#1976D2", font=("Arial", 10, "bold"), 
                                relief="flat", bd=0, cursor="hand2",
                                command=self.open_register)
        register_btn.pack(side="left")
        
    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not email or not password:
            messagebox.showwarning("Warning", "Please enter all required fields.")
            return
            
        user_data = login_user(email, password)
        if user_data:
            messagebox.showinfo("Success", "Login successful!")
            self.window.destroy()
            self.on_login_success(user_data)
        else:
            messagebox.showerror("Error", "Incorrect email or password!")
            
    def open_register(self):
        self.window.destroy()
        RegisterWindow(self.window.master, self.on_login_success)


class RegisterWindow:
    def __init__(self, parent, on_login_success):
        self.window = tk.Toplevel(parent)
        self.window.title("Register")
        self.window.geometry("500x700")
        self.window.configure(bg="#ffffff")
        self.on_login_success = on_login_success
        
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.window, bg="#4CAF50", height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        icon_label = tk.Label(header_frame, text="✨", font=("Arial", 35), 
                             bg="#4CAF50", fg="white")
        icon_label.pack(pady=10)
        
        tk.Label(header_frame, text="Create Account", font=("Arial", 20, "bold"), 
                bg="#4CAF50", fg="white").pack()
        
        # Scrollable content
        canvas = tk.Canvas(self.window, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Main content
        content_frame = tk.Frame(scrollable_frame, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        fields_info = [
            ("Email Address", "email", "📧", False),
            ("Password", "password", "🔒", True),
            ("Full Name", "fullname", "👤", False),
            ("Address", "address", "📍", False),
            ("Phone Number", "phone", "📱", False)
        ]
        
        self.entries = {}
        
        for label_text, field_name, icon, is_password in fields_info:
            # Label
            tk.Label(content_frame, text=label_text, bg="#ffffff", 
                    fg="#424242", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 5))
            
            # Input frame
            input_frame = tk.Frame(content_frame, bg="#E8F5E9" if field_name != "password" else "#FFF3E0", 
                                  relief="flat", bd=0)
            input_frame.pack(fill="x", pady=(0, 5))
            
            tk.Label(input_frame, text=icon, 
                    bg="#E8F5E9" if field_name != "password" else "#FFF3E0",
                    font=("Arial", 14)).pack(side="left", padx=(10, 5))
            
            entry = tk.Entry(input_frame, font=("Arial", 11), 
                           bg="#E8F5E9" if field_name != "password" else "#FFF3E0",
                           relief="flat", bd=0, fg="#424242",
                           show="●" if is_password else None)
            entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=12)
            self.entries[field_name] = entry
        
        # Buttons container
        btn_container = tk.Frame(content_frame, bg="#ffffff")
        btn_container.pack(fill="x", pady=(30, 10))
        
        # Register button
        register_btn = tk.Button(btn_container, text="CREATE ACCOUNT", 
                                bg="#4CAF50", fg="white",
                                font=("Arial", 12, "bold"), relief="flat", bd=0,
                                cursor="hand2", command=self.register, pady=12)
        register_btn.pack(fill="x", pady=(0, 10))
        
        # Back to login
        back_frame = tk.Frame(btn_container, bg="#F5F5F5", relief="flat")
        back_frame.pack(fill="x")
        
        back_inner = tk.Frame(back_frame, bg="#F5F5F5")
        back_inner.pack(pady=12)
        
        tk.Label(back_inner, text="Already have an account?", 
                bg="#F5F5F5", fg="#616161", font=("Arial", 10)).pack(side="left", padx=5)
        
        login_btn = tk.Button(back_inner, text="Sign In", bg="#F5F5F5",
                             fg="#4CAF50", font=("Arial", 10, "bold"), 
                             relief="flat", bd=0, cursor="hand2",
                             command=self.back_to_login)
        login_btn.pack(side="left")
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def register(self):
        email = self.entries["email"].get().strip()
        password = self.entries["password"].get().strip()
        fullname = self.entries["fullname"].get().strip()
        address = self.entries["address"].get().strip()
        phone = self.entries["phone"].get().strip()
        
        if not email or not password or not fullname:
            messagebox.showwarning("Warning", "Please fill in all required fields.")
            return
            
        if register_user(email, password, fullname, address, phone):
            messagebox.showinfo("Success", "Registration successful! Please log in.")
            self.back_to_login()
        else:
            messagebox.showerror("Error", "Email already exists or an error occurred!")
            
    def back_to_login(self):
        self.window.destroy()
        LoginWindow(self.window.master, self.on_login_success)