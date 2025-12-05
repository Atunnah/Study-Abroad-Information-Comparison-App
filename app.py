import tkinter as tk
from tkinter import ttk, messagebox
from database import init_db
from auth import LoginWindow
from countries_tab import CountriesTab
from universities_tab import UniversitiesTab
from user_management import UserManagementTab, ProfileTab
from comparison_tab import ComparisonTab
from Phu_Chatbot.chatbot import ChatbotTab

class UniversityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("University Management System")
        self.root.geometry("1400x800")
        
        # Modern color scheme
        self.colors = {
            'primary': '#2C3E50',      # Dark blue-gray
            'secondary': '#3498DB',    # Bright blue
            'success': '#27AE60',      # Green
            'warning': '#F39C12',      # Orange
            'danger': '#E74C3C',       # Red
            'info': '#9B59B6',         # Purple
            'light': '#ECF0F1',        # Light gray
            'bg': '#FFFFFF',           # White background
            'text': '#2C3E50',         # Dark text
            'text_light': '#7F8C8D',   # Light text
            'hover': '#34495E'         # Hover state
        }
        
        self.root.configure(bg=self.colors['light'])
        
        self.current_user = None
        self.is_admin = False
        
        # Create menu bar
        self.create_menu()
        
        # Main container with shadow effect
        self.main_container = tk.Frame(root, bg=self.colors['bg'], 
                                     relief='flat', bd=0)
        self.main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Show welcome screen
        self.show_welcome_screen()
        
    def create_menu(self):
        """Create modern menu bar"""
        menubar = tk.Menu(self.root, bg=self.colors['primary'], 
                         fg='white', activebackground=self.colors['secondary'],
                         activeforeground='white', relief='flat')
        self.root.config(menu=menubar)
        
        
        # Home menu
        home_menu = tk.Menu(menubar, tearoff=0, bg='white',
                           fg=self.colors['text'],
                           activebackground=self.colors['secondary'],
                           activeforeground='white')
        menubar.add_cascade(label="  🏠 Home  ", menu=home_menu)

        home_menu.add_command(label="🏠 Go to Home", command=self.show_home_screen)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='white', fg=self.colors['text'],
                           activebackground=self.colors['secondary'], 
                           activeforeground='white')
        menubar.add_cascade(label="  📁 File  ", menu=file_menu)
        
        self.login_menu_item = file_menu.add_command(
            label="🔐 Login", command=self.show_login)
        self.logout_menu_item = None
        file_menu.add_separator()
        file_menu.add_command(label="❌ Exit", command=self.root.quit)
        
        # Data menu
        self.data_menu = tk.Menu(menubar, tearoff=0, bg='white', 
                                fg=self.colors['text'],
                                activebackground=self.colors['secondary'], 
                                activeforeground='white')
        menubar.add_cascade(label="  📊 Data  ", menu=self.data_menu)
        self.data_menu.add_command(label="🌍 Countries", command=self.show_countries, 
                                   state="disabled")
        self.data_menu.add_command(label="🎓 Universities", command=self.show_universities, 
                                   state="disabled")
        
        # Tools menu
        self.tools_menu = tk.Menu(menubar, tearoff=0, bg='white', 
                                 fg=self.colors['text'],
                                 activebackground=self.colors['secondary'], 
                                 activeforeground='white')
        menubar.add_cascade(label="  🔧 Tools  ", menu=self.tools_menu)
        self.tools_menu.add_command(label="📈 Visualization", command=self.show_comparison, 
                                    state="disabled")
        self.tools_menu.add_command(label="🤖 AI Assistant", command=self.show_chatbot, 
                                    state="disabled")
        
        # User menu
        self.user_menu = tk.Menu(menubar, tearoff=0, bg='white', 
                                fg=self.colors['text'],
                                activebackground=self.colors['secondary'], 
                                activeforeground='white')
        menubar.add_cascade(label="  👤 Account  ", menu=self.user_menu)
        
    def show_welcome_screen(self):
        """Show modern welcome screen"""
        self.clear_main_container()
        
        # Gradient-like effect with multiple frames
        top_section = tk.Frame(self.main_container, bg=self.colors['primary'], height=250)
        top_section.pack(fill="x", side="top")
        top_section.pack_propagate(False)
        
        # Welcome content in center
        welcome_frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        welcome_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # University icon with circular background
        icon_frame = tk.Frame(welcome_frame, bg=self.colors['secondary'], 
                             width=140, height=140)
        icon_frame.pack(pady=(0, 25))
        icon_frame.pack_propagate(False)
        
        tk.Label(icon_frame, text="🎓", font=("Segoe UI Emoji", 72), 
                bg=self.colors['secondary'], fg='white').place(relx=0.5, rely=0.5, 
                                                               anchor="center")
        
        # Title with modern font
        tk.Label(welcome_frame, text="University Management System", 
                font=("Segoe UI", 32, "bold"), bg=self.colors['bg'],
                fg=self.colors['primary']).pack(pady=(0, 10))
        
        # Subtitle
        tk.Label(welcome_frame, text="Comprehensive solution for academic administration", 
                font=("Segoe UI", 13), bg=self.colors['bg'],
                fg=self.colors['text_light']).pack(pady=(0, 40))
        
        # Modern login button
        login_btn = tk.Button(welcome_frame, text="LOGIN TO CONTINUE", 
                             bg=self.colors['secondary'], fg="white", 
                             font=("Segoe UI", 12, "bold"), width=25, height=2,
                             relief='flat', cursor="hand2",
                             activebackground=self.colors['hover'],
                             activeforeground='white',
                             command=self.show_login)
        login_btn.pack(pady=10)
        
        # Hover effect
        login_btn.bind('<Enter>', lambda e: login_btn.config(bg=self.colors['hover']))
        login_btn.bind('<Leave>', lambda e: login_btn.config(bg=self.colors['secondary']))
        
        # Footer
        footer = tk.Label(welcome_frame, text="Version 1.0 | © 2025 University System", 
                         font=("Segoe UI", 9), bg=self.colors['bg'],
                         fg=self.colors['text_light'])
        footer.pack(pady=(50, 0))
        
    def show_login(self):
        """Show login window"""
        LoginWindow(self.root, self.on_login_success)
        
    def on_login_success(self, user_data):
        """Handle successful login"""
        self.current_user = user_data
        self.is_admin = bool(user_data[5])
        
        self.update_menu_after_login()
        self.show_home_screen()
        
    def update_menu_after_login(self):
        """Update menu items after login"""
        self.data_menu.entryconfig("🌍 Countries", state="normal")
        self.data_menu.entryconfig("🎓 Universities", state="normal")
        
        self.tools_menu.entryconfig("📈 Visualization", state="normal")
        self.tools_menu.entryconfig("🤖 AI Assistant", state="normal")
        
        self.user_menu.delete(0, tk.END)
        
        if self.is_admin:
            self.user_menu.add_command(label="👥 User Management", 
                                     command=self.show_user_management)
        else:
            self.user_menu.add_command(label="ℹ️ Account Information", 
                                     command=self.show_profile)
        
        self.user_menu.add_separator()
        self.user_menu.add_command(label="🚪 Logout", command=self.logout)
        
    def logout(self):
        """Logout user"""
        if messagebox.askyesno("Confirm Logout", 
                              "Are you sure you want to logout?",
                              icon='question'):
            self.current_user = None
            self.is_admin = False
            
            self.data_menu.entryconfig("🌍 Countries", state="disabled")
            self.data_menu.entryconfig("🎓 Universities", state="disabled")
            self.tools_menu.entryconfig("📈 Visualization", state="disabled")
            self.tools_menu.entryconfig("🤖 AI Assistant", state="disabled")
            
            self.user_menu.delete(0, tk.END)
            
            self.show_welcome_screen()
            
    def show_home_screen(self):
        """Show modern home dashboard"""
        self.clear_main_container()
        
        # Header section
        header = tk.Frame(self.main_container, bg=self.colors['primary'], height=120)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        # User info in header
        user_type = "Administrator" if self.is_admin else "User"
        user_name = self.current_user[2] or self.current_user[1]
        
        header_content = tk.Frame(header, bg=self.colors['primary'])
        header_content.pack(expand=True)
        
        tk.Label(header_content, text=f"Welcome back, {user_name}!", 
                font=("Segoe UI", 24, "bold"), bg=self.colors['primary'],
                fg='white').pack(pady=(10, 0))
        
        tk.Label(header_content, text=f"Role: {user_type}", 
                font=("Segoe UI", 12), bg=self.colors['primary'],
                fg=self.colors['light']).pack()
        
        # Main content area
        content = tk.Frame(self.main_container, bg=self.colors['bg'])
        content.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Dashboard title
        tk.Label(content, text="Quick Access Dashboard", 
                font=("Segoe UI", 18, "bold"), bg=self.colors['bg'],
                fg=self.colors['primary']).pack(pady=(0, 30))
        
        # Cards container
        cards_frame = tk.Frame(content, bg=self.colors['bg'])
        cards_frame.pack(expand=True)
        
        # Define cards with modern styling
        cards = [
            {
                'title': 'Countries',
                'icon': '🌍',
                'desc': 'Manage country data',
                'color': self.colors['success'],
                'command': self.show_countries,
                'row': 0, 'col': 0
            },
            {
                'title': 'Universities',
                'icon': '🎓',
                'desc': 'Manage universities',
                'color': self.colors['secondary'],
                'command': self.show_universities,
                'row': 0, 'col': 1
            },
            {
                'title': 'Visualization',
                'icon': '📈',
                'desc': 'Data analytics & charts',
                'color': self.colors['warning'],
                'command': self.show_comparison,
                'row': 1, 'col': 0
            },
            {
                'title': 'AI Assistant',
                'icon': '🤖',
                'desc': 'Intelligent chatbot',
                'color': self.colors['info'],
                'command': self.show_chatbot,
                'row': 1, 'col': 1
            }
        ]
        
        # Create modern cards
        for card in cards:
            self.create_dashboard_card(cards_frame, card)
    
    def create_dashboard_card(self, parent, card_info):
        """Create modern dashboard card"""
        # Logic: Để frame có thể click được, ta gán sự kiện Button-1 và đổi cursor thành hand2
        card = tk.Frame(parent, bg='white', relief='flat', 
                       highlightbackground=self.colors['light'],
                       highlightthickness=2, cursor="hand2")
        card.grid(row=card_info['row'], column=card_info['col'], 
                 padx=20, pady=20, sticky='nsew')
        
        # Configure grid weights
        parent.grid_rowconfigure(card_info['row'], weight=1)
        parent.grid_columnconfigure(card_info['col'], weight=1)
        
        # Card content
        card_content = tk.Frame(card, bg='white', cursor="hand2")
        card_content.pack(expand=True, fill='both', padx=30, pady=30)
        
        # Icon with colored background
        icon_bg = tk.Frame(card_content, bg=card_info['color'], 
                          width=80, height=80, cursor="hand2")
        icon_bg.pack(pady=(0, 20))
        icon_bg.pack_propagate(False)
        
        # Icon label
        icon_label = tk.Label(icon_bg, text=card_info['icon'], font=("Segoe UI Emoji", 36),
                bg=card_info['color'], fg='white', cursor="hand2")
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title_label = tk.Label(card_content, text=card_info['title'], 
                font=("Segoe UI", 16, "bold"), bg='white',
                fg=self.colors['primary'], cursor="hand2")
        title_label.pack()
        
        # Description
        desc_label = tk.Label(card_content, text=card_info['desc'], 
                font=("Segoe UI", 10), bg='white',
                fg=self.colors['text_light'], cursor="hand2")
        desc_label.pack(pady=(5, 20))
        
        # Button
        btn = tk.Button(card_content, text="OPEN", 
                        bg=card_info['color'], fg='white',
                        font=("Segoe UI", 10, "bold"), width=15,
                        relief='flat', cursor="hand2",
                        activebackground=self.colors['hover'],
                        activeforeground='white',
                        command=card_info['command'])
        btn.pack()
        
        # Logic: Hàm xử lý sự kiện click
        def on_click(event):
            # Gọi command được định nghĩa trong card_info
            card_info['command']()

        # Logic: Gắn sự kiện click (Button-1) cho Frame cha và tất cả widget con
        # Lưu ý: Button đã có command riêng nên không cần bind
        widgets_to_bind = [card, card_content, icon_bg, icon_label, title_label, desc_label]
        for widget in widgets_to_bind:
            widget.bind('<Button-1>', on_click)
        
        # Hover effects for card
        def on_enter(e):
            card.config(highlightbackground=card_info['color'], 
                       highlightthickness=3)
            btn.config(bg=self.colors['hover'])
        
        def on_leave(e):
            card.config(highlightbackground=self.colors['light'], 
                       highlightthickness=2)
            btn.config(bg=card_info['color'])
        
        # Logic: Bind hover effect cho toàn bộ cây widget trong card
        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
        for child in card.winfo_children():
            child.bind('<Enter>', on_enter)
            child.bind('<Leave>', on_leave)
            for subchild in child.winfo_children():
                subchild.bind('<Enter>', on_enter)
                subchild.bind('<Leave>', on_leave)
        
    def clear_main_container(self):
        """Clear all widgets in main container"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
            
    def show_countries(self):
        """Show countries management"""
        if not self.current_user:
            return
        self.clear_main_container()
        frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        frame.pack(fill="both", expand=True)
        CountriesTab(frame, is_admin=self.is_admin)
        
    def show_universities(self):
        """Show universities management"""
        if not self.current_user:
            return
        self.clear_main_container()
        frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        frame.pack(fill="both", expand=True)
        UniversitiesTab(frame, uid=self.current_user[0], is_admin=self.is_admin)
        
    def show_comparison(self):
        if not self.current_user:
            return
        self.clear_main_container()
        frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        frame.pack(fill="both", expand=True)
        ComparisonTab(frame, current_user_data=self.current_user)
        
    def show_chatbot(self):
        """Show chatbot feature"""
        if not self.current_user:
            return
        self.clear_main_container()
        frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        frame.pack(fill="both", expand=True)
        ChatbotTab(frame, current_user_id=self.current_user[0])
        
    def show_user_management(self):
        """Show user management (admin only)"""
        if not self.current_user or not self.is_admin:
            return
        self.clear_main_container()
        frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        frame.pack(fill="both", expand=True)
        UserManagementTab(frame)
        
    def show_profile(self):
        """Show user profile"""
        if not self.current_user:
            return
        self.clear_main_container()
        frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        frame.pack(fill="both", expand=True)
        ProfileTab(frame, self.current_user)


if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Create and run application
    root = tk.Tk()
    app = UniversityApp(root)
    root.mainloop()