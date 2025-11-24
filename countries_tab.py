import tkinter as tk
from tkinter import ttk, messagebox
from database import execute_db

class CountriesTab:
    def __init__(self, parent_frame, is_admin=True):
        self.frame = parent_frame
        self.is_admin = is_admin
        self.setup_ui()
        
    def setup_ui(self):
        # Main container với padding
        main_container = tk.Frame(self.frame, bg="#FAFAFA")
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header section
        header_frame = tk.Frame(main_container, bg="#FFFFFF", relief="flat")
        header_frame.pack(fill="x", pady=(0, 15))
        
        header_content = tk.Frame(header_frame, bg="#FFFFFF")
        header_content.pack(fill="x", padx=20, pady=15)
        
        # Title với icon
        title_frame = tk.Frame(header_content, bg="#FFFFFF")
        title_frame.pack(side="left")
        
        tk.Label(title_frame, text="🌍", font=("Arial", 24), bg="#FFFFFF").pack(side="left", padx=(0, 10))
        tk.Label(title_frame, text="Countries Management" if self.is_admin else "Countries Directory", 
                font=("Arial", 18, "bold"), bg="#FFFFFF", fg="#212121").pack(side="left")
        
        # Search bar - modern design
        search_container = tk.Frame(main_container, bg="#FFFFFF", relief="flat")
        search_container.pack(fill="x", pady=(0, 15))
        
        search_inner = tk.Frame(search_container, bg="#FFFFFF")
        search_inner.pack(fill="x", padx=20, pady=15)
        
        # Search input với icon
        search_frame = tk.Frame(search_inner, bg="#F5F5F5", relief="flat")
        search_frame.pack(side="left", fill="x", expand=True)
        
        tk.Label(search_frame, text="🔍", bg="#F5F5F5", font=("Arial", 14)).pack(
            side="left", padx=(15, 5))
        
        self.search_entry = tk.Entry(search_frame, font=("Arial", 11), bg="#F5F5F5",
                                     relief="flat", bd=0, fg="#424242")
        self.search_entry.insert(0, "Search by code or name...")
        self.search_entry.config(fg="#9E9E9E")
        self.search_entry.bind("<FocusIn>", self.on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search())
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 15), pady=12)
        
        # Refresh button
        refresh_btn = tk.Button(search_inner, text="↻ Refresh", bg="#607D8B", fg="white",
                               font=("Arial", 10, "bold"), relief="flat", bd=0,
                               cursor="hand2", command=self.refresh, padx=20, pady=8)
        refresh_btn.pack(side="left", padx=(10, 0))
        
        # Admin input section hoặc info banner
        if self.is_admin:
            input_container = tk.Frame(main_container, bg="#FFFFFF", relief="flat")
            input_container.pack(fill="x", pady=(0, 15))
            
            input_content = tk.Frame(input_container, bg="#FFFFFF")
            input_content.pack(fill="both", padx=20, pady=20)
            
            # Input section title
            tk.Label(input_content, text="Country Information", 
                    font=("Arial", 13, "bold"), bg="#FFFFFF", fg="#212121").pack(anchor="w", pady=(0, 15))
            
            # Grid layout cho inputs
            fields_frame = tk.Frame(input_content, bg="#FFFFFF")
            fields_frame.pack(fill="x")
            
            # Configure grid weights
            for i in range(3):
                fields_frame.columnconfigure(i, weight=1)
            
            fields = [
                ("Country Code", "code", "🏷️"),
                ("Country Name", "name", "📝"),
                ("Flag URL", "flag", "🚩")
            ]
            
            self.entries_widgets = {}
            
            for idx, (label_text, field_key, icon) in enumerate(fields):
                col = idx
                
                # Label
                label_frame = tk.Frame(fields_frame, bg="#FFFFFF")
                label_frame.grid(row=0, column=col, padx=8, pady=(0, 8), sticky="ew")
                
                tk.Label(label_frame, text=icon, bg="#FFFFFF", font=("Arial", 12)).pack(side="left", padx=(0, 5))
                tk.Label(label_frame, text=label_text, bg="#FFFFFF", fg="#424242",
                        font=("Arial", 9, "bold")).pack(side="left")
                
                # Input
                input_frame = tk.Frame(fields_frame, bg="#E3F2FD", relief="flat")
                input_frame.grid(row=1, column=col, padx=8, pady=(0, 15), sticky="ew")
                
                entry = tk.Entry(input_frame, font=("Arial", 10), bg="#E3F2FD",
                               relief="flat", bd=0, fg="#424242")
                entry.pack(fill="x", padx=10, pady=10)
                
                if field_key == "code":
                    self.country_code = entry
                elif field_key == "name":
                    self.country_name = entry
                else:
                    self.country_flag = entry
            
            # Action buttons
            btn_frame = tk.Frame(input_content, bg="#FFFFFF")
            btn_frame.pack(fill="x", pady=(10, 0))
            
            buttons = [
                ("➕ Add Country", "#4CAF50", self.add_country),
                ("✏️ Update", "#2196F3", self.update_country),
                ("🗑️ Delete", "#F44336", self.delete_country)
            ]
            
            for btn_text, btn_color, btn_command in buttons:
                btn = tk.Button(btn_frame, text=btn_text, bg=btn_color, fg="white",
                               font=("Arial", 10, "bold"), relief="flat", bd=0,
                               cursor="hand2", command=btn_command, padx=25, pady=10)
                btn.pack(side="left", padx=5, expand=True, fill="x")
        else:
            # Info banner cho user thường
            info_container = tk.Frame(main_container, bg="#E3F2FD", relief="flat")
            info_container.pack(fill="x", pady=(0, 15))
            
            info_inner = tk.Frame(info_container, bg="#E3F2FD")
            info_inner.pack(fill="x", padx=20, pady=15)
            
            tk.Label(info_inner, text="ℹ️", bg="#E3F2FD", font=("Arial", 16)).pack(side="left", padx=(0, 10))
            tk.Label(info_inner, text="You are in view-only mode. Contact administrator for editing permissions.", 
                    bg="#E3F2FD", fg="#1565C0", font=("Arial", 10)).pack(side="left")
        
        # Treeview section
        tree_container = tk.Frame(main_container, bg="#FFFFFF", relief="flat")
        tree_container.pack(fill="both", expand=True)
        
        tree_header = tk.Frame(tree_container, bg="#FFFFFF")
        tree_header.pack(fill="x", padx=20, pady=(15, 5))
        
        tk.Label(tree_header, text="📊 Data Table", font=("Arial", 12, "bold"), 
                bg="#FFFFFF", fg="#212121").pack(side="left")
        
        # Treeview với custom style
        tree_frame = tk.Frame(tree_container, bg="#FFFFFF")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Custom style cho Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                       background="#FFFFFF",
                       foreground="#212121",
                       fieldbackground="#FFFFFF",
                       borderwidth=0,
                       font=("Arial", 10))
        style.configure("Custom.Treeview.Heading",
                       background="#1976D2",
                       foreground="white",
                       borderwidth=0,
                       font=("Arial", 10, "bold"))
        style.map("Custom.Treeview",
                 background=[("selected", "#4F46E5")])
        style.map("Custom.Treeview.Heading",
                 background=[("active", "#1565C0")])
        
        self.tree = ttk.Treeview(tree_frame, columns=("ID","Code","Name","Flag"), 
                                show="headings", height=12, style="Custom.Treeview")
        
        # Configure columns
        columns_config = [
            ("ID", 80),
            ("Code", 120),
            ("Name", 250),
            ("Flag", 300)
        ]
        
        for col, width in columns_config:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="w" if col != "ID" else "center")
        
        # Scrollbar với custom style
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        if self.is_admin:
            self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        self.refresh()
    
    def on_search_focus_in(self, event):
        if self.search_entry.get() == "Search by code or name...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="#424242")
    
    def on_search_focus_out(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search by code or name...")
            self.search_entry.config(fg="#9E9E9E")
        
    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = execute_db("SELECT * FROM countries", fetch=True)
        if rows:
            for r in rows:
                self.tree.insert("", "end", values=r)
    
    def search(self):
        """Search countries by code or name"""
        search_term = self.search_entry.get().strip().lower()
        
        if search_term == "search by code or name...":
            self.refresh()
            return
        
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        if not search_term:
            self.refresh()
            return
        
        rows = execute_db("SELECT * FROM countries", fetch=True)
        if rows:
            for r in rows:
                if search_term in str(r[1]).lower() or search_term in str(r[2]).lower():
                    self.tree.insert("", "end", values=r)
                
    def add_country(self):
        if not self.is_admin:
            return
        code = self.country_code.get().strip()
        name = self.country_name.get().strip()
        flag = self.country_flag.get().strip()
        if not code or not name:
            messagebox.showwarning("Input Error", "Code and Name are required")
            return
        if execute_db("INSERT INTO countries (code,name,flag_url) VALUES (?,?,?)", 
                     (code, name, flag)):
            messagebox.showinfo("Success", "Country added successfully!")
            self.clear_inputs()
            self.refresh()
            
    def on_select(self, event):
        if not self.is_admin:
            return
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            self.country_code.delete(0, tk.END)
            self.country_code.insert(0, values[1])
            self.country_name.delete(0, tk.END)
            self.country_name.insert(0, values[2])
            self.country_flag.delete(0, tk.END)
            self.country_flag.insert(0, values[3])
            
    def update_country(self):
        if not self.is_admin:
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Error", "Please select a country first")
            return
        values = self.tree.item(selected[0])['values']
        country_id = values[0]
        code = self.country_code.get().strip()
        name = self.country_name.get().strip()
        flag = self.country_flag.get().strip()
        if execute_db("UPDATE countries SET code=?, name=?, flag_url=? WHERE id=?", 
                     (code, name, flag, country_id)):
            messagebox.showinfo("Success", "Country updated successfully!")
            self.clear_inputs()
            self.refresh()
            
    def delete_country(self):
        if not self.is_admin:
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Error", "Please select a country first")
            return
        values = self.tree.item(selected[0])['values']
        country_id = values[0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{values[2]}'?"):
            if execute_db("DELETE FROM countries WHERE id=?", (country_id,)):
                messagebox.showinfo("Success", "Country deleted successfully!")
                self.clear_inputs()
                self.refresh()
                
    def clear_inputs(self):
        if not self.is_admin:
            return
        self.country_code.delete(0, tk.END)
        self.country_name.delete(0, tk.END)
        self.country_flag.delete(0, tk.END)