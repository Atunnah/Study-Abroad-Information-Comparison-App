import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from database import execute_db, add_favorite
import json

class UniversitiesTab:
    def __init__(self, parent_frame, uid=None, is_admin=True):
        self.frame = parent_frame
        self.is_admin = is_admin
        self.uid = uid
        self.requirements_list = []  # List of requirement dicts
        self.scholarships_list = []  # List of scholarship dicts
        
        # --- UI CONSTANTS ---
        self.colors = {
            "bg_main": "#ffffff",
            "bg_panel": "#f4f6f9",
            "primary": "#2196F3",    # Blue
            "success": "#4CAF50",    # Green
            "danger": "#F44336",     # Red
            "warning": "#FF9800",    # Orange
            "text": "#333333",
            "header_bg": "#E3F2FD"
        }
        self.fonts = {
            "h1": ("Segoe UI", 12, "bold"),
            "label": ("Segoe UI", 9, "bold"),
            "normal": ("Segoe UI", 9),
            "small": ("Segoe UI", 8)
        }

        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        """Configures custom styles for the application"""
        style = ttk.Style()
        style.theme_use('clam') # Use a flexible theme base

        # Treeview Styling
        style.configure("Treeview", 
                        background="white",
                        foreground="black", 
                        rowheight=25, 
                        fieldbackground="white",
                        font=self.fonts["normal"])
        
        style.configure("Treeview.Heading", 
                        font=self.fonts["label"], 
                        background=self.colors["bg_panel"])
        
        # CRITICAL: Fix Hover/Selection colors to ensure text is readable
        style.map("Treeview", 
                  background=[('selected', self.colors["primary"])], 
                  foreground=[('selected', 'white')])

        # Button Styling
        style.configure("Action.TButton", font=self.fonts["label"])

    def setup_ui(self):
        # Main container configuration
        self.frame.configure(bg=self.colors["bg_main"])
        
        # --- 1. SEARCH AREA (Top) ---
        search_frame = tk.Frame(self.frame, bg=self.colors["bg_panel"], bd=1, relief="solid")
        search_frame.pack(pady=(10, 5), padx=10, fill="x")
        
        tk.Label(search_frame, text="🔍 Search:", bg=self.colors["bg_panel"], 
                 font=self.fonts["label"], fg=self.colors["text"]).pack(side="left", padx=(10, 5), pady=10)
        
        self.search_entry = ttk.Entry(search_frame, width=30, font=self.fonts["normal"])
        self.search_entry.pack(side="left", padx=5, pady=10)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search())
        
        tk.Label(search_frame, text="Country:", bg=self.colors["bg_panel"], 
                 font=self.fonts["label"], fg=self.colors["text"]).pack(side="left", padx=(20, 5), pady=10)
        
        self.search_country = ttk.Combobox(search_frame, width=20, state="readonly", 
                                           values=["All"] + self.get_country_names(), font=self.fonts["normal"])
        self.search_country.set("All")
        self.search_country.pack(side="left", padx=5, pady=10)
        self.search_country.bind("<<ComboboxSelected>>", lambda e: self.search())
        
        tk.Button(search_frame, text="↻ Refresh", bg=self.colors["primary"], fg="white",
                  font=self.fonts["normal"], relief="flat", padx=10,
                  command=self.refresh).pack(side="right", padx=10, pady=10)
        
        # --- 2. ADMIN INPUT AREA (Middle - Scrollable) ---
        if self.is_admin:
            # Container for the scrollable canvas
            input_container = tk.LabelFrame(self.frame, text="University Management", 
                                          bg=self.colors["bg_main"], font=self.fonts["h1"], fg=self.colors["primary"])
            input_container.pack(pady=5, padx=10, fill="x")
            
            # Canvas and Scrollbar
            canvas = tk.Canvas(input_container, bg=self.colors["bg_main"], height=280, highlightthickness=0)
            scrollbar = ttk.Scrollbar(input_container, orient="vertical", command=canvas.yview)
            
            # The frame inside the canvas
            input_frame = tk.Frame(canvas, bg=self.colors["bg_main"])
            
            input_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=input_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            scrollbar.pack(side="right", fill="y", pady=5)
            
            # --- Form Layout using LabelFrames for grouping ---
            
            # Group A: Basic Information
            grp_basic = tk.LabelFrame(input_frame, text="Basic Info", bg=self.colors["bg_main"], font=self.fonts["label"])
            grp_basic.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            
            grid_opts = {'padx': 5, 'pady': 5, 'sticky': 'ew'}
            
            tk.Label(grp_basic, text="Name:", bg=self.colors["bg_main"]).grid(row=0, column=0, sticky="e")
            self.uni_name = ttk.Entry(grp_basic, width=25)
            self.uni_name.grid(row=0, column=1, **grid_opts)
            
            tk.Label(grp_basic, text="Country:", bg=self.colors["bg_main"]).grid(row=1, column=0, sticky="e")
            self.uni_country = ttk.Combobox(grp_basic, values=self.get_country_names(), width=23)
            self.uni_country.grid(row=1, column=1, **grid_opts)
            
            tk.Label(grp_basic, text="State:", bg=self.colors["bg_main"]).grid(row=2, column=0, sticky="e")
            self.uni_state = ttk.Entry(grp_basic, width=25)
            self.uni_state.grid(row=2, column=1, **grid_opts)
            
            # Group B: Details
            grp_details = tk.LabelFrame(input_frame, text="Details", bg=self.colors["bg_main"], font=self.fonts["label"])
            grp_details.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
            
            tk.Label(grp_details, text="Domain:", bg=self.colors["bg_main"]).grid(row=0, column=0, sticky="e")
            self.uni_domain = ttk.Entry(grp_details, width=25)
            self.uni_domain.grid(row=0, column=1, **grid_opts)
            
            tk.Label(grp_details, text="Website:", bg=self.colors["bg_main"]).grid(row=1, column=0, sticky="e")
            self.uni_website = ttk.Entry(grp_details, width=25)
            self.uni_website.grid(row=1, column=1, **grid_opts)

            tk.Label(grp_details, text="Majors Qty:", bg=self.colors["bg_main"]).grid(row=2, column=0, sticky="e")
            self.uni_num_majors = ttk.Entry(grp_details, width=25)
            self.uni_num_majors.grid(row=2, column=1, **grid_opts)

            tk.Label(grp_details, text="Tuition ($):", bg=self.colors["bg_main"]).grid(row=3, column=0, sticky="e")
            self.uni_tuition_fee = ttk.Entry(grp_details, width=25)
            self.uni_tuition_fee.grid(row=3, column=1, **grid_opts)

            # Group C: Complex Data (Requirements & Scholarships)
            grp_complex = tk.Frame(input_frame, bg=self.colors["bg_main"])
            grp_complex.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
            
            # Requirements Sub-section
            req_frame_cont = tk.LabelFrame(grp_complex, text="Entry Requirements", bg=self.colors["bg_main"], font=self.fonts["label"])
            req_frame_cont.pack(fill="x", pady=(0, 5))
            
            self.req_display = tk.Text(req_frame_cont, height=3, width=30, state="disabled", font=self.fonts["small"])
            self.req_display.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            req_btns = tk.Frame(req_frame_cont, bg=self.colors["bg_main"])
            req_btns.pack(side="right", padx=5)
            tk.Button(req_btns, text="+", bg=self.colors["success"], fg="white", width=3, command=self.add_requirement).pack(pady=2)
            tk.Button(req_btns, text="x", bg=self.colors["warning"], fg="white", width=3, command=self.clear_requirements).pack(pady=2)
            
            # Scholarships Sub-section
            schol_frame_cont = tk.LabelFrame(grp_complex, text="Scholarships", bg=self.colors["bg_main"], font=self.fonts["label"])
            schol_frame_cont.pack(fill="x")
            
            self.schol_display = tk.Text(schol_frame_cont, height=3, width=30, state="disabled", font=self.fonts["small"])
            self.schol_display.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            schol_btns = tk.Frame(schol_frame_cont, bg=self.colors["bg_main"])
            schol_btns.pack(side="right", padx=5)
            tk.Button(schol_btns, text="+", bg=self.colors["success"], fg="white", width=3, command=self.add_scholarship).pack(pady=2)
            tk.Button(schol_btns, text="x", bg=self.colors["warning"], fg="white", width=3, command=self.clear_scholarships).pack(pady=2)

            # Actions Row
            btn_frame = tk.Frame(input_frame, bg=self.colors["bg_main"])
            btn_frame.grid(row=1, column=0, columnspan=3, pady=15)
            
            btn_opts = {'font': self.fonts["label"], 'relief': 'flat', 'padx': 15, 'pady': 5}
            
            tk.Button(btn_frame, text="Add University", bg=self.colors["success"], fg="white", 
                      command=self.add_university, **btn_opts).pack(side="left", padx=5)
            
            tk.Button(btn_frame, text="Update", bg=self.colors["primary"], fg="white", 
                      command=self.update_university, **btn_opts).pack(side="left", padx=5)
            
            tk.Button(btn_frame, text="Delete", bg=self.colors["danger"], fg="white", 
                      command=self.delete_university, **btn_opts).pack(side="left", padx=5)
            
            tk.Button(btn_frame, text="Clear Form", bg="#90A4AE", fg="white", 
                      command=self.clear_inputs, **btn_opts).pack(side="left", padx=5)

        else:
            # User View Info
            info_frame = tk.Frame(self.frame, bg="#FFF3E0", relief="solid", bd=1)
            info_frame.pack(pady=5, padx=10, fill="x")
            tk.Label(info_frame, text="ℹ️ View mode: Search and select to see details or add to favorites.", 
                    bg="#FFF3E0", fg="#E65100", font=("Segoe UI", 10, "italic")).pack(pady=10)
            
            fav_btn_frame = tk.Frame(self.frame, bg=self.colors["bg_main"])
            fav_btn_frame.pack(pady=5)

            tk.Button(
                fav_btn_frame,
                text="❤️ Add to Favorites",
                bg="#E91E63",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                relief="flat",
                padx=20, pady=5,
                command=self.add_to_favorites
            ).pack()

        # --- 3. DATA TABLE (Bottom) ---
        tree_frame = tk.Frame(self.frame, bg=self.colors["bg_main"])
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        columns = ("ID", "Name", "Country", "State", "Domain", "Website", 
                   "Majors", "Tuition", "Requirements")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        col_configs = {
            "ID": 40, "Name": 200, "Country": 100, "State": 100,
            "Domain": 120, "Website": 150, "Majors": 60, "Tuition": 80, "Requirements": 100
        }
        
        for col, width in col_configs.items():
            self.tree.column(col, width=width, anchor="w")
            self.tree.heading(col, text=col, anchor="w")
        
        scrollbar_v = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar_h = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=scrollbar_v.set, xscroll=scrollbar_h.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_v.grid(row=0, column=1, sticky="ns")
        scrollbar_h.grid(row=1, column=0, sticky="ew")
        
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        if self.is_admin:
            self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.refresh()

    # --- LOGIC METHODS (UNCHANGED) ---
    def add_to_favorites(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please choose a university")
            return
        
        item = self.tree.item(selected[0])
        uni_id = item["values"][0]

        if not hasattr(self, "uid"):
            messagebox.showerror("Error", "User data not found")
            return

        result = add_favorite(self.uid, uni_id)

        if result:
            messagebox.showinfo("Success", "Add university to favorites!")
        else:
            messagebox.showerror("Error", "Unable to add")

    def get_country_names(self):
        rows = execute_db("SELECT name FROM countries", fetch=True)
        return [r[0] for r in rows] if rows else []
        
    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = execute_db("""
            SELECT u.id, u.name, c.name, u.state, u.domain, u.website, 
                   u.num_majors, u.tuition_fee_avg, u.entry_requirements
            FROM universities u
            JOIN countries c ON u.country_id = c.id
        """, fetch=True)
        if rows:
            for r in rows:
                display_vals = list(r[:8])
                req_text = "N/A" if not r[8] else "JSON data..."
                display_vals.append(req_text)
                self.tree.insert("", "end", values=display_vals)
        if self.is_admin:
            self.uni_country['values'] = self.get_country_names()
        self.search_country['values'] = ["All"] + self.get_country_names()
    
    def search(self):
        search_term = self.search_entry.get().strip().lower()
        country_filter = self.search_country.get()
        
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        rows = execute_db("""
            SELECT u.id, u.name, c.name, u.state, u.domain, u.website, 
                   u.num_majors, u.tuition_fee_avg, u.entry_requirements
            FROM universities u
            JOIN countries c ON u.country_id = c.id
        """, fetch=True)
        
        if rows:
            for r in rows:
                if country_filter != "All" and r[2] != country_filter:
                    continue
                
                if search_term:
                    searchable_text = " ".join(str(x).lower() for x in r[1:6] if x)
                    if search_term not in searchable_text:
                        continue
                
                display_vals = list(r[:8])
                req_text = "N/A" if not r[8] else "JSON data..."
                display_vals.append(req_text)
                self.tree.insert("", "end", values=display_vals)
    
    def add_requirement(self):
        dialog = Toplevel(self.frame)
        dialog.title("Add Entry Requirement")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors["bg_main"])
        
        tk.Label(dialog, text="Category:", font=self.fonts["label"], bg=self.colors["bg_main"]).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        category_var = ttk.Combobox(dialog, values=["language", "academic", "extra"], width=25)
        category_var.grid(row=0, column=1, padx=10, pady=10)
        category_var.current(0)
        
        tk.Label(dialog, text="Key:", font=self.fonts["label"], bg=self.colors["bg_main"]).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        key_entry = tk.Entry(dialog, width=28)
        key_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Value:", font=self.fonts["label"], bg=self.colors["bg_main"]).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        value_entry = tk.Entry(dialog, width=28)
        value_entry.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Type:", font=self.fonts["label"], bg=self.colors["bg_main"]).grid(row=3, column=0, padx=10, pady=10, sticky="e")
        type_var = ttk.Combobox(dialog, values=["text", "number", "boolean"], width=25)
        type_var.grid(row=3, column=1, padx=10, pady=10)
        type_var.current(0)
        
        def save_requirement():
            category = category_var.get().strip()
            key = key_entry.get().strip()
            value = value_entry.get().strip()
            req_type = type_var.get().strip()
            
            if not category or not key or not value:
                messagebox.showwarning("Input Error", "All fields are required!")
                return
            
            if req_type == "number":
                try:
                    value = float(value)
                except:
                    messagebox.showerror("Type Error", "Value must be a number!")
                    return
            elif req_type == "boolean":
                value = value.lower() in ["true", "1", "yes"]
            
            req_dict = {
                "category": category,
                "key": key,
                "value": value,
                "type": req_type
            }
            self.requirements_list.append(req_dict)
            self.update_requirements_display()
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog, bg=self.colors["bg_main"])
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        tk.Button(btn_frame, text="Save", bg=self.colors["success"], fg="white", 
                 command=save_requirement, width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", bg=self.colors["danger"], fg="white", 
                 command=dialog.destroy, width=12).pack(side="left", padx=5)
    
    def clear_requirements(self):
        self.requirements_list = []
        self.update_requirements_display()
    
    def update_requirements_display(self):
        self.req_display.config(state="normal")
        self.req_display.delete("1.0", tk.END)
        if self.requirements_list:
            for req in self.requirements_list:
                self.req_display.insert(tk.END, f"• {req['category']}: {req['key']}={req['value']}\n")
        else:
            self.req_display.insert(tk.END, "No requirements added")
        self.req_display.config(state="disabled")
    
    def add_scholarship(self):
        dialog = Toplevel(self.frame)
        dialog.title("Add Scholarship")
        dialog.geometry("400x280")
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors["bg_main"])
        
        tk.Label(dialog, text="Scholarship Name:", font=self.fonts["label"], bg=self.colors["bg_main"]).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        name_entry = tk.Entry(dialog, width=28)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Value ($):", font=self.fonts["label"], bg=self.colors["bg_main"]).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        value_entry = tk.Entry(dialog, width=28)
        value_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Duration:", font=self.fonts["label"], bg=self.colors["bg_main"]).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        duration_entry = tk.Entry(dialog, width=28)
        duration_entry.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Criteria:", font=self.fonts["label"], bg=self.colors["bg_main"]).grid(row=3, column=0, padx=10, pady=10, sticky="ne")
        criteria_text = tk.Text(dialog, width=28, height=4)
        criteria_text.grid(row=3, column=1, padx=10, pady=10)
        
        def save_scholarship():
            name = name_entry.get().strip()
            value = value_entry.get().strip()
            duration = duration_entry.get().strip()
            criteria = criteria_text.get("1.0", tk.END).strip()
            
            if not name:
                messagebox.showwarning("Input Error", "Scholarship name is required!")
                return
            
            try:
                value_float = float(value) if value else 0.0
            except:
                messagebox.showerror("Type Error", "Value must be a number!")
                return
            
            schol_dict = {
                "name": name,
                "value": value_float,
                "duration": duration,
                "criteria": criteria
            }
            self.scholarships_list.append(schol_dict)
            self.update_scholarships_display()
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog, bg=self.colors["bg_main"])
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        tk.Button(btn_frame, text="Save", bg=self.colors["success"], fg="white", 
                 command=save_scholarship, width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", bg=self.colors["danger"], fg="white", 
                 command=dialog.destroy, width=12).pack(side="left", padx=5)
    
    def clear_scholarships(self):
        self.scholarships_list = []
        self.update_scholarships_display()
    
    def update_scholarships_display(self):
        self.schol_display.config(state="normal")
        self.schol_display.delete("1.0", tk.END)
        if self.scholarships_list:
            for schol in self.scholarships_list:
                self.schol_display.insert(tk.END, f"• {schol['name']} (${schol['value']})\n")
        else:
            self.schol_display.insert(tk.END, "No scholarships added")
        self.schol_display.config(state="disabled")
    
    def add_university(self):
        if not self.is_admin:
            return
        name = self.uni_name.get().strip()
        country_name = self.uni_country.get().strip()
        state = self.uni_state.get().strip()
        domain = self.uni_domain.get().strip()
        website = self.uni_website.get().strip()
        num_majors = self.uni_num_majors.get().strip()
        tuition_fee = self.uni_tuition_fee.get().strip()
        
        if not name or not country_name:
            messagebox.showwarning("Input Error", "Name and Country required")
            return
        
        country_id = execute_db("SELECT id FROM countries WHERE name=?", 
                               (country_name,), fetch=True)
        if not country_id:
            messagebox.showerror("Error", f"Country {country_name} not found")
            return
        country_id = country_id[0][0]
        
        num_majors_int = int(num_majors) if num_majors else None
        tuition_fee_float = float(tuition_fee) if tuition_fee else None
        
        entry_requirements_json = json.dumps(self.requirements_list) if self.requirements_list else None
        
        result = execute_db("""INSERT INTO universities 
                (name, country_id, state, domain, website, num_majors, tuition_fee_avg, entry_requirements) 
                VALUES (?,?,?,?,?,?,?,?)""",
             (name, country_id, state, domain, website, num_majors_int, tuition_fee_float, entry_requirements_json),
             fetch=False)

        if result:
            uni_id = execute_db("SELECT last_insert_rowid()", fetch=True)[0][0]

            for schol in self.scholarships_list:
                execute_db("""INSERT INTO scholarships 
                            (name, university_id, value, duration, criteria) 
                            VALUES (?,?,?,?,?)""",
                         (schol['name'], uni_id, schol['value'], schol['duration'], schol['criteria']),
                         fetch=False)

            messagebox.showinfo("Success", "University added with scholarships!")
            self.clear_inputs()
            self.refresh()
        else:
            messagebox.showerror("Error", "Failed to add university")
            
    def on_select(self, event):
        if not self.is_admin:
            return
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            uni_id = values[0]
            
            uni_data = execute_db("""
                SELECT name, country_id, state, domain, website, 
                       num_majors, tuition_fee_avg, entry_requirements
                FROM universities WHERE id=?
            """, (uni_id,), fetch=True)
            
            if uni_data:
                uni_data = uni_data[0]
                self.uni_name.delete(0, tk.END)
                self.uni_name.insert(0, uni_data[0] or "")
                
                country_name = execute_db("SELECT name FROM countries WHERE id=?", 
                                         (uni_data[1],), fetch=True)
                if country_name:
                    self.uni_country.set(country_name[0][0])
                
                self.uni_state.delete(0, tk.END)
                self.uni_state.insert(0, uni_data[2] or "")
                
                self.uni_domain.delete(0, tk.END)
                self.uni_domain.insert(0, uni_data[3] or "")
                
                self.uni_website.delete(0, tk.END)
                self.uni_website.insert(0, uni_data[4] or "")
                
                self.uni_num_majors.delete(0, tk.END)
                self.uni_num_majors.insert(0, uni_data[5] or "")
                
                self.uni_tuition_fee.delete(0, tk.END)
                self.uni_tuition_fee.insert(0, uni_data[6] or "")
                
                if uni_data[7]:
                    try:
                        self.requirements_list = json.loads(uni_data[7])
                        self.update_requirements_display()
                    except:
                        self.requirements_list = []
                        self.update_requirements_display()
                else:
                    self.requirements_list = []
                    self.update_requirements_display()
                
                scholarships = execute_db("""
                    SELECT name, value, duration, criteria 
                    FROM scholarships 
                    WHERE university_id=?
                """, (uni_id,), fetch=True)
                
                self.scholarships_list = []
                if scholarships:
                    for s in scholarships:
                        self.scholarships_list.append({
                            "name": s[0],
                            "value": s[1],
                            "duration": s[2],
                            "criteria": s[3]
                        })
                self.update_scholarships_display()
            
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
        num_majors = self.uni_num_majors.get().strip()
        tuition_fee = self.uni_tuition_fee.get().strip()
        
        if not name or not country_name:
            messagebox.showwarning("Input Error", "Name and Country required")
            return
        
        country_id = execute_db("SELECT id FROM countries WHERE name=?", 
                               (country_name,), fetch=True)
        if not country_id:
            messagebox.showerror("Error", f"Country {country_name} not found")
            return
        country_id = country_id[0][0]
        
        num_majors_int = int(num_majors) if num_majors else None
        tuition_fee_float = float(tuition_fee) if tuition_fee else None
        entry_requirements_json = json.dumps(self.requirements_list) if self.requirements_list else None
        
        if execute_db("""UPDATE universities 
                        SET name=?, country_id=?, state=?, domain=?, website=?, 
                            num_majors=?, tuition_fee_avg=?, entry_requirements=?
                        WHERE id=?""",
                     (name, country_id, state, domain, website, num_majors_int, 
                      tuition_fee_float, entry_requirements_json, uni_id)):
            
            execute_db("DELETE FROM scholarships WHERE university_id=?", (uni_id,))
            
            for schol in self.scholarships_list:
                execute_db("""INSERT INTO scholarships 
                            (name, university_id, value, duration, criteria) 
                            VALUES (?,?,?,?,?)""",
                         (schol['name'], uni_id, schol['value'], schol['duration'], schol['criteria']))
            
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
        
        if messagebox.askyesno("Confirm Delete", f"Delete {values[1]}?\n\nThis will also delete all related scholarships."):
            execute_db("DELETE FROM scholarships WHERE university_id=?", (uni_id,))
            if execute_db("DELETE FROM universities WHERE id=?", (uni_id,)):
                messagebox.showinfo("Success", "University and related scholarships deleted")
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
        self.uni_num_majors.delete(0, tk.END)
        self.uni_tuition_fee.delete(0, tk.END)
        self.requirements_list = []
        self.scholarships_list = []
        self.update_requirements_display()
        self.update_scholarships_display()