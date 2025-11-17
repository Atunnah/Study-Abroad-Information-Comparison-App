import tkinter as tk
from tkinter import ttk, messagebox
from database import init_db
from auth import LoginWindow
from countries_tab import CountriesTab
from universities_tab import UniversitiesTab
from user_management import UserManagementTab, ProfileTab
from placeholder_tabs import ComparisonTab, ChatbotTab

class UniversityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("University Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        
        self.current_user = None
        self.is_admin = False
        
        # Create menu bar
        self.create_menu()
        
        # Main container
        self.main_container = tk.Frame(root, bg="#f0f0f0")
        self.main_container.pack(fill="both", expand=True)
        
        # Show welcome screen
        self.show_welcome_screen()
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tệp", menu=file_menu)
        
        self.login_menu_item = file_menu.add_command(
            label="Đăng nhập", command=self.show_login)
        self.logout_menu_item = None  # Will be added after login
        file_menu.add_separator()
        file_menu.add_command(label="Thoát", command=self.root.quit)
        
        # Data menu
        self.data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dữ liệu", menu=self.data_menu)
        self.data_menu.add_command(label="Quốc gia", command=self.show_countries, 
                                   state="disabled")
        self.data_menu.add_command(label="Trường đại học", command=self.show_universities, 
                                   state="disabled")
        
        # Tools menu
        self.tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Công cụ", menu=self.tools_menu)
        self.tools_menu.add_command(label="So sánh", command=self.show_comparison, 
                                    state="disabled")
        self.tools_menu.add_command(label="Chatbot AI", command=self.show_chatbot, 
                                    state="disabled")
        
        # User menu (will be populated after login)
        self.user_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tài khoản", menu=self.user_menu)
        
    def show_welcome_screen(self):
        """Show welcome screen before login"""
        self.clear_main_container()
        
        welcome_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        welcome_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(welcome_frame, text="🎓", font=("Arial", 64), 
                bg="#f0f0f0").pack(pady=20)
        tk.Label(welcome_frame, text="HỆ THỐNG QUẢN LÝ TRƯỜNG ĐẠI HỌC", 
                font=("Arial", 24, "bold"), bg="#f0f0f0").pack(pady=10)
        tk.Label(welcome_frame, text="Vui lòng đăng nhập để tiếp tục", 
                font=("Arial", 14), bg="#f0f0f0").pack(pady=10)
        
        tk.Button(welcome_frame, text="Đăng nhập", bg="#4CAF50", fg="white", 
                 font=("Arial", 14), width=15, 
                 command=self.show_login).pack(pady=20)
        
    def show_login(self):
        """Show login window"""
        LoginWindow(self.root, self.on_login_success)
        
    def on_login_success(self, user_data):
        """Handle successful login"""
        # user_data: (uid, email, full_name, address, phone, is_admin)
        self.current_user = user_data
        self.is_admin = bool(user_data[5])
        
        # Update menu
        self.update_menu_after_login()
        
        # Show home screen
        self.show_home_screen()
        
    def update_menu_after_login(self):
        """Update menu items after login"""
        # Enable data menu
        self.data_menu.entryconfig("Quốc gia", state="normal")
        self.data_menu.entryconfig("Trường đại học", state="normal")
        
        # Enable tools menu
        self.tools_menu.entryconfig("So sánh", state="normal")
        self.tools_menu.entryconfig("Chatbot AI", state="normal")
        
        # Update user menu
        self.user_menu.delete(0, tk.END)
        
        if self.is_admin:
            self.user_menu.add_command(label="Quản lý người dùng", 
                                      command=self.show_user_management)
        else:
            self.user_menu.add_command(label="Thông tin cá nhân", 
                                      command=self.show_profile)
        
        self.user_menu.add_separator()
        self.user_menu.add_command(label="Đăng xuất", command=self.logout)
        
    def logout(self):
        """Logout user"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn đăng xuất?"):
            self.current_user = None
            self.is_admin = False
            
            # Reset menu
            self.data_menu.entryconfig("Quốc gia", state="disabled")
            self.data_menu.entryconfig("Trường đại học", state="disabled")
            self.tools_menu.entryconfig("So sánh", state="disabled")
            self.tools_menu.entryconfig("Chatbot AI", state="disabled")
            
            self.user_menu.delete(0, tk.END)
            
            # Show welcome screen
            self.show_welcome_screen()
            
    def show_home_screen(self):
        """Show home screen after login"""
        self.clear_main_container()
        
        home_frame = tk.Frame(self.main_container, bg="#f0f0f0")
        home_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Welcome message
        user_type = "Quản trị viên" if self.is_admin else "Người dùng"
        tk.Label(home_frame, 
                text=f"Chào mừng {user_type}: {self.current_user[2] or self.current_user[1]}", 
                font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=20)
        
        # Quick access buttons
        btn_frame = tk.Frame(home_frame, bg="#f0f0f0")
        btn_frame.pack(pady=30)
        
        tk.Button(btn_frame, text="📚 Quản lý Quốc gia", 
                 font=("Arial", 12), width=20, height=3,
                 bg="#4CAF50", fg="white", 
                 command=self.show_countries).grid(row=0, column=0, padx=10, pady=10)
        
        tk.Button(btn_frame, text="🎓 Quản lý Trường ĐH", 
                 font=("Arial", 12), width=20, height=3,
                 bg="#2196F3", fg="white", 
                 command=self.show_universities).grid(row=0, column=1, padx=10, pady=10)
        
        tk.Button(btn_frame, text="🔍 So sánh", 
                 font=("Arial", 12), width=20, height=3,
                 bg="#FF9800", fg="white", 
                 command=self.show_comparison).grid(row=1, column=0, padx=10, pady=10)
        
        tk.Button(btn_frame, text="🤖 Chatbot AI", 
                 font=("Arial", 12), width=20, height=3,
                 bg="#9C27B0", fg="white", 
                 command=self.show_chatbot).grid(row=1, column=1, padx=10, pady=10)
        
    def clear_main_container(self):
        """Clear all widgets in main container"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
            
    def show_countries(self):
        """Show countries management"""
        if not self.current_user:
            return
        self.clear_main_container()
        frame = tk.Frame(self.main_container, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)
        CountriesTab(frame, is_admin=self.is_admin)
        
    def show_universities(self):
        """Show universities management"""
        if not self.current_user:
            return
        self.clear_main_container()
        frame = tk.Frame(self.main_container, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)
        UniversitiesTab(frame, is_admin=self.is_admin)
        
    def show_comparison(self):
        """Show comparison feature (placeholder)"""
        if not self.current_user:
            return
        self.clear_main_container()
        frame = tk.Frame(self.main_container, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)
        ComparisonTab(frame)
        
    def show_chatbot(self):
        """Show chatbot feature (placeholder)"""
        if not self.current_user:
            return
        self.clear_main_container()
        frame = tk.Frame(self.main_container, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)
        ChatbotTab(frame)
        
    def show_user_management(self):
        """Show user management (admin only)"""
        if not self.current_user or not self.is_admin:
            return
        self.clear_main_container()
        frame = tk.Frame(self.main_container, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)
        UserManagementTab(frame)
        
    def show_profile(self):
        """Show user profile"""
        if not self.current_user:
            return
        self.clear_main_container()
        frame = tk.Frame(self.main_container, bg="#f0f0f0")
        frame.pack(fill="both", expand=True)
        ProfileTab(frame, self.current_user)


if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Create and run application
    root = tk.Tk()
    app = UniversityApp(root)
    root.mainloop()