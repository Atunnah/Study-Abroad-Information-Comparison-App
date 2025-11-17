import tkinter as tk
from tkinter import ttk, messagebox
from database import execute_db

class CountriesTab:
    def __init__(self, parent_frame, is_admin=True):
        self.frame = parent_frame
        self.is_admin = is_admin
        self.setup_ui()
        
    def setup_ui(self):
        # Search frame (always visible)
        search_frame = tk.Frame(self.frame, bg="#f0f0f0")
        search_frame.pack(pady=10, padx=10, fill="x")
        
        tk.Label(search_frame, text="🔍 Tìm kiếm:", bg="#f0f0f0", 
                font=("Arial", 11, "bold")).pack(side="left", padx=5)
        self.search_entry = tk.Entry(search_frame, width=40, font=("Arial", 10))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search())
        
        tk.Button(search_frame, text="Làm mới", bg="#607D8B", fg="white",
                 command=self.refresh).pack(side="left", padx=5)
        
        # Input frame (only for admin)
        if self.is_admin:
            input_frame = tk.Frame(self.frame, bg="#f0f0f0")
            input_frame.pack(pady=10, padx=10, fill="x")
            
            # Labels & Entries
            tk.Label(input_frame, text="Code:", bg="#f0f0f0").grid(
                row=0, column=0, padx=5, pady=5, sticky="e")
            tk.Label(input_frame, text="Name:", bg="#f0f0f0").grid(
                row=1, column=0, padx=5, pady=5, sticky="e")
            tk.Label(input_frame, text="Flag URL:", bg="#f0f0f0").grid(
                row=2, column=0, padx=5, pady=5, sticky="e")
            
            self.country_code = tk.Entry(input_frame)
            self.country_name = tk.Entry(input_frame)
            self.country_flag = tk.Entry(input_frame)
            self.country_code.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.country_name.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            self.country_flag.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
            
            input_frame.columnconfigure(1, weight=1)
            
            # Buttons
            tk.Button(input_frame, text="Add", bg="#4CAF50", fg="white", 
                     command=self.add_country).grid(row=0, column=2, padx=5, pady=5)
            tk.Button(input_frame, text="Update", bg="#2196F3", fg="white", 
                     command=self.update_country).grid(row=1, column=2, padx=5, pady=5)
            tk.Button(input_frame, text="Delete", bg="#f44336", fg="white", 
                     command=self.delete_country).grid(row=2, column=2, padx=5, pady=5)
        else:
            # Show info for regular users
            info_frame = tk.Frame(self.frame, bg="#FFF9C4", relief="solid", borderwidth=1)
            info_frame.pack(pady=5, padx=10, fill="x")
            tk.Label(info_frame, text="ℹ️ Bạn chỉ có quyền xem và tìm kiếm dữ liệu", 
                    bg="#FFF9C4", font=("Arial", 10, "italic")).pack(pady=8)
        
        # Treeview
        tree_frame = tk.Frame(self.frame)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.tree = ttk.Treeview(tree_frame, columns=("ID","Code","Name","Flag"), 
                                show="headings", height=15)
        for col in ("ID","Code","Name","Flag"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        if self.is_admin:
            self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.refresh()
        
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
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        if not search_term:
            self.refresh()
            return
        
        rows = execute_db("SELECT * FROM countries", fetch=True)
        if rows:
            for r in rows:
                # Search in code and name
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
            messagebox.showinfo("Success", "Country added")
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
            messagebox.showwarning("Select Error", "Select a country first")
            return
        values = self.tree.item(selected[0])['values']
        country_id = values[0]
        code = self.country_code.get().strip()
        name = self.country_name.get().strip()
        flag = self.country_flag.get().strip()
        if execute_db("UPDATE countries SET code=?, name=?, flag_url=? WHERE id=?", 
                     (code, name, flag, country_id)):
            messagebox.showinfo("Success", "Country updated")
            self.clear_inputs()
            self.refresh()
            
    def delete_country(self):
        if not self.is_admin:
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Error", "Select a country first")
            return
        values = self.tree.item(selected[0])['values']
        country_id = values[0]
        if messagebox.askyesno("Confirm Delete", f"Delete {values[2]}?"):
            if execute_db("DELETE FROM countries WHERE id=?", (country_id,)):
                messagebox.showinfo("Success", "Country deleted")
                self.clear_inputs()
                self.refresh()
                
    def clear_inputs(self):
        if not self.is_admin:
            return
        self.country_code.delete(0, tk.END)
        self.country_name.delete(0, tk.END)
        self.country_flag.delete(0, tk.END)