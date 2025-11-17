import tkinter as tk
from tkinter import ttk, messagebox
from database import execute_db

class UniversitiesTab:
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
        
        tk.Label(search_frame, text="Quốc gia:", bg="#f0f0f0").pack(side="left", padx=(20, 5))
        self.search_country = ttk.Combobox(search_frame, width=20, 
                                          values=["Tất cả"] + self.get_country_names())
        self.search_country.set("Tất cả")
        self.search_country.pack(side="left", padx=5)
        self.search_country.bind("<<ComboboxSelected>>", lambda e: self.search())
        
        tk.Button(search_frame, text="Làm mới", bg="#607D8B", fg="white",
                 command=self.refresh).pack(side="left", padx=5)
        
        # Input frame (only for admin)
        if self.is_admin:
            input_frame = tk.Frame(self.frame, bg="#f0f0f0")
            input_frame.pack(pady=10, padx=10, fill="x")
            
            # Labels & Entries
            tk.Label(input_frame, text="Name:", bg="#f0f0f0").grid(
                row=0, column=0, padx=5, pady=5, sticky="e")
            tk.Label(input_frame, text="Country:", bg="#f0f0f0").grid(
                row=1, column=0, padx=5, pady=5, sticky="e")
            tk.Label(input_frame, text="State:", bg="#f0f0f0").grid(
                row=2, column=0, padx=5, pady=5, sticky="e")
            tk.Label(input_frame, text="Domain:", bg="#f0f0f0").grid(
                row=3, column=0, padx=5, pady=5, sticky="e")
            tk.Label(input_frame, text="Website:", bg="#f0f0f0").grid(
                row=4, column=0, padx=5, pady=5, sticky="e")
            
            self.uni_name = tk.Entry(input_frame)
            self.uni_country = ttk.Combobox(input_frame, values=self.get_country_names())
            self.uni_state = tk.Entry(input_frame)
            self.uni_domain = tk.Entry(input_frame)
            self.uni_website = tk.Entry(input_frame)
            
            self.uni_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.uni_country.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            self.uni_state.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
            self.uni_domain.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
            self.uni_website.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
            
            input_frame.columnconfigure(1, weight=1)
            
            # Buttons
            tk.Button(input_frame, text="Add", bg="#4CAF50", fg="white", 
                     command=self.add_university).grid(row=0, column=2, padx=5, pady=5)
            tk.Button(input_frame, text="Update", bg="#2196F3", fg="white", 
                     command=self.update_university).grid(row=1, column=2, padx=5, pady=5)
            tk.Button(input_frame, text="Delete", bg="#f44336", fg="white", 
                     command=self.delete_university).grid(row=2, column=2, padx=5, pady=5)
        else:
            # Show info for regular users
            info_frame = tk.Frame(self.frame, bg="#FFF9C4", relief="solid", borderwidth=1)
            info_frame.pack(pady=5, padx=10, fill="x")
            tk.Label(info_frame, text="ℹ️ Bạn chỉ có quyền xem và tìm kiếm dữ liệu", 
                    bg="#FFF9C4", font=("Arial", 10, "italic")).pack(pady=8)
        
        # Treeview
        tree_frame = tk.Frame(self.frame)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.tree = ttk.Treeview(tree_frame, 
                                columns=("ID","Name","Country","State","Domain","Website"), 
                                show="headings", height=15)
        for col in ("ID","Name","Country","State","Domain","Website"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        if self.is_admin:
            self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.refresh()
        
    def get_country_names(self):
        rows = execute_db("SELECT name FROM countries", fetch=True)
        return [r[0] for r in rows] if rows else []
        
    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = execute_db("""
            SELECT u.id, u.name, c.name, u.state, u.domain, u.website
            FROM universities_basic u
            JOIN countries c ON u.country_id = c.id
        """, fetch=True)
        if rows:
            for r in rows:
                self.tree.insert("", "end", values=r)
        if self.is_admin:
            self.uni_country['values'] = self.get_country_names()
        self.search_country['values'] = ["Tất cả"] + self.get_country_names()
    
    def search(self):
        """Search universities by name, country, state, domain, or website"""
        search_term = self.search_entry.get().strip().lower()
        country_filter = self.search_country.get()
        
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        rows = execute_db("""
            SELECT u.id, u.name, c.name, u.state, u.domain, u.website
            FROM universities_basic u
            JOIN countries c ON u.country_id = c.id
        """, fetch=True)
        
        if rows:
            for r in rows:
                # Apply country filter
                if country_filter != "Tất cả" and r[2] != country_filter:
                    continue
                
                # Apply text search
                if search_term:
                    searchable_text = " ".join(str(x).lower() for x in r[1:])
                    if search_term not in searchable_text:
                        continue
                
                self.tree.insert("", "end", values=r)
        
    def add_university(self):
        if not self.is_admin:
            return
        name = self.uni_name.get().strip()
        country_name = self.uni_country.get().strip()
        state = self.uni_state.get().strip()
        domain = self.uni_domain.get().strip()
        website = self.uni_website.get().strip()
        if not name or not country_name:
            messagebox.showwarning("Input Error", "Name and Country required")
            return
        country_id = execute_db("SELECT id FROM countries WHERE name=?", 
                               (country_name,), fetch=True)
        if not country_id:
            messagebox.showerror("Error", f"Country {country_name} not found")
            return
        country_id = country_id[0][0]
        if execute_db("""INSERT INTO universities_basic 
                        (name,country_id,state,domain,website) VALUES (?,?,?,?,?)""",
                     (name, country_id, state, domain, website)):
            messagebox.showinfo("Success", "University added")
            self.clear_inputs()
            self.refresh()
            
    def on_select(self, event):
        if not self.is_admin:
            return
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            self.uni_name.delete(0, tk.END)
            self.uni_name.insert(0, values[1])
            self.uni_country.set(values[2])
            self.uni_state.delete(0, tk.END)
            self.uni_state.insert(0, values[3])
            self.uni_domain.delete(0, tk.END)
            self.uni_domain.insert(0, values[4])
            self.uni_website.delete(0, tk.END)
            self.uni_website.insert(0, values[5])
            
    def update_university(self):
        if not self.is_admin:
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Error", "Select a university first")
            return
        values = self.tree.item(selected[0])['values']
        uni_id = values[0]
        name = self.uni_name.get().strip()
        country_name = self.uni_country.get().strip()
        state = self.uni_state.get().strip()
        domain = self.uni_domain.get().strip()
        website = self.uni_website.get().strip()
        country_id = execute_db("SELECT id FROM countries WHERE name=?", 
                               (country_name,), fetch=True)
        if not country_id:
            messagebox.showerror("Error", f"Country {country_name} not found")
            return
        country_id = country_id[0][0]
        if execute_db("""UPDATE universities_basic 
                        SET name=?, country_id=?, state=?, domain=?, website=? 
                        WHERE id=?""",
                     (name, country_id, state, domain, website, uni_id)):
            messagebox.showinfo("Success", "University updated")
            self.clear_inputs()
            self.refresh()
            
    def delete_university(self):
        if not self.is_admin:
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Error", "Select a university first")
            return
        values = self.tree.item(selected[0])['values']
        uni_id = values[0]
        if messagebox.askyesno("Confirm Delete", f"Delete {values[1]}?"):
            if execute_db("DELETE FROM universities_basic WHERE id=?", (uni_id,)):
                messagebox.showinfo("Success", "University deleted")
                self.clear_inputs()
                self.refresh()
                
    def clear_inputs(self):
        if not self.is_admin:
            return
        self.uni_name.delete(0, tk.END)
        self.uni_country.set('')
        self.uni_state.delete(0, tk.END)
        self.uni_domain.delete(0, tk.END)
        self.uni_website.delete(0, tk.END)