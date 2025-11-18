import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from unittest import result
from database import execute_db
import json

class UniversitiesTab:
    def __init__(self, parent_frame, is_admin=True):
        self.frame = parent_frame
        self.is_admin = is_admin
        self.requirements_list = []  # List of requirement dicts
        self.scholarships_list = []  # List of scholarship dicts
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
            # Create a canvas with scrollbar for the input form
            input_container = tk.Frame(self.frame, bg="#f0f0f0")
            input_container.pack(pady=10, padx=10, fill="x")
            
            canvas = tk.Canvas(input_container, bg="#f0f0f0", height=250)
            scrollbar = ttk.Scrollbar(input_container, orient="vertical", command=canvas.yview)
            input_frame = tk.Frame(canvas, bg="#f0f0f0")
            
            input_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=input_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Labels & Entries - Column 1
            row = 0
            tk.Label(input_frame, text="Name:", bg="#f0f0f0", font=("Arial", 9, "bold")).grid(
                row=row, column=0, padx=5, pady=3, sticky="e")
            self.uni_name = tk.Entry(input_frame, width=30)
            self.uni_name.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
            
            row += 1
            tk.Label(input_frame, text="Country:", bg="#f0f0f0", font=("Arial", 9, "bold")).grid(
                row=row, column=0, padx=5, pady=3, sticky="e")
            self.uni_country = ttk.Combobox(input_frame, values=self.get_country_names(), width=28)
            self.uni_country.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
            
            row += 1
            tk.Label(input_frame, text="State:", bg="#f0f0f0", font=("Arial", 9, "bold")).grid(
                row=row, column=0, padx=5, pady=3, sticky="e")
            self.uni_state = tk.Entry(input_frame, width=30)
            self.uni_state.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
            
            row += 1
            tk.Label(input_frame, text="Domain:", bg="#f0f0f0", font=("Arial", 9, "bold")).grid(
                row=row, column=0, padx=5, pady=3, sticky="e")
            self.uni_domain = tk.Entry(input_frame, width=30)
            self.uni_domain.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
            
            row += 1
            tk.Label(input_frame, text="Website:", bg="#f0f0f0", font=("Arial", 9, "bold")).grid(
                row=row, column=0, padx=5, pady=3, sticky="e")
            self.uni_website = tk.Entry(input_frame, width=30)
            self.uni_website.grid(row=row, column=1, padx=5, pady=3, sticky="ew")
            
            # New fields - Column 2
            row_col2 = 0
            tk.Label(input_frame, text="Num Majors:", bg="#f0f0f0", font=("Arial", 9, "bold")).grid(
                row=row_col2, column=2, padx=5, pady=3, sticky="e")
            self.uni_num_majors = tk.Entry(input_frame, width=30)
            self.uni_num_majors.grid(row=row_col2, column=3, padx=5, pady=3, sticky="ew")
            
            row_col2 += 1
            tk.Label(input_frame, text="Tuition Fee (avg):", bg="#f0f0f0", font=("Arial", 9, "bold")).grid(
                row=row_col2, column=2, padx=5, pady=3, sticky="e")
            self.uni_tuition_fee = tk.Entry(input_frame, width=30)
            self.uni_tuition_fee.grid(row=row_col2, column=3, padx=5, pady=3, sticky="ew")
            
            # Entry Requirements section
            row_col2 += 1
            tk.Label(input_frame, text="Entry Requirements:", bg="#f0f0f0", 
                    font=("Arial", 9, "bold")).grid(row=row_col2, column=2, padx=5, pady=3, sticky="e")
            req_frame = tk.Frame(input_frame, bg="#f0f0f0")
            req_frame.grid(row=row_col2, column=3, padx=5, pady=3, sticky="ew")
            
            self.req_display = tk.Text(req_frame, height=3, width=25, state="disabled", 
                                       bg="#ffffff", font=("Arial", 8))
            self.req_display.pack(side="left", fill="both", expand=True)
            
            req_btn_frame = tk.Frame(req_frame, bg="#f0f0f0")
            req_btn_frame.pack(side="right", fill="y", padx=2)
            tk.Button(req_btn_frame, text="Add", bg="#4CAF50", fg="white", 
                     command=self.add_requirement, width=8, font=("Arial", 8)).pack(pady=2)
            tk.Button(req_btn_frame, text="Clear", bg="#FF9800", fg="white", 
                     command=self.clear_requirements, width=8, font=("Arial", 8)).pack(pady=2)
            
            # Scholarships section
            row_col2 += 1
            tk.Label(input_frame, text="Scholarships:", bg="#f0f0f0", 
                    font=("Arial", 9, "bold")).grid(row=row_col2, column=2, padx=5, pady=3, sticky="e")
            schol_frame = tk.Frame(input_frame, bg="#f0f0f0")
            schol_frame.grid(row=row_col2, column=3, padx=5, pady=3, sticky="ew")
            
            self.schol_display = tk.Text(schol_frame, height=3, width=25, state="disabled", 
                                         bg="#ffffff", font=("Arial", 8))
            self.schol_display.pack(side="left", fill="both", expand=True)
            
            schol_btn_frame = tk.Frame(schol_frame, bg="#f0f0f0")
            schol_btn_frame.pack(side="right", fill="y", padx=2)
            tk.Button(schol_btn_frame, text="Add", bg="#4CAF50", fg="white", 
                     command=self.add_scholarship, width=8, font=("Arial", 8)).pack(pady=2)
            tk.Button(schol_btn_frame, text="Clear", bg="#FF9800", fg="white", 
                     command=self.clear_scholarships, width=8, font=("Arial", 8)).pack(pady=2)
            
            input_frame.columnconfigure(1, weight=1)
            input_frame.columnconfigure(3, weight=1)
            
            # Action Buttons Frame
            btn_frame = tk.Frame(input_frame, bg="#f0f0f0")
            btn_frame.grid(row=row+1, column=0, columnspan=4, pady=10)
            
            tk.Button(btn_frame, text="Add University", bg="#4CAF50", fg="white", 
                     command=self.add_university, width=15, font=("Arial", 9, "bold")).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Update", bg="#2196F3", fg="white", 
                     command=self.update_university, width=15, font=("Arial", 9, "bold")).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Delete", bg="#f44336", fg="white", 
                     command=self.delete_university, width=15, font=("Arial", 9, "bold")).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Clear Form", bg="#9E9E9E", fg="white", 
                     command=self.clear_inputs, width=15, font=("Arial", 9, "bold")).pack(side="left", padx=5)
        else:
            # Show info for regular users
            info_frame = tk.Frame(self.frame, bg="#FFF9C4", relief="solid", borderwidth=1)
            info_frame.pack(pady=5, padx=10, fill="x")
            tk.Label(info_frame, text="ℹ️ Bạn chỉ có quyền xem và tìm kiếm dữ liệu", 
                    bg="#FFF9C4", font=("Arial", 10, "italic")).pack(pady=8)
        
        # Treeview
        tree_frame = tk.Frame(self.frame)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        columns = ("ID", "Name", "Country", "State", "Domain", "Website", 
                   "Majors", "Tuition", "Requirements")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        self.tree.column("ID", width=40)
        self.tree.column("Name", width=200)
        self.tree.column("Country", width=100)
        self.tree.column("State", width=100)
        self.tree.column("Domain", width=120)
        self.tree.column("Website", width=150)
        self.tree.column("Majors", width=60)
        self.tree.column("Tuition", width=80)
        self.tree.column("Requirements", width=100)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
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
                # Format display values
                display_vals = list(r[:8])
                # Show truncated requirements or "N/A"
                req_text = "N/A" if not r[8] else "JSON data..."
                display_vals.append(req_text)
                self.tree.insert("", "end", values=display_vals)
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
            SELECT u.id, u.name, c.name, u.state, u.domain, u.website,
                   u.num_majors, u.tuition_fee_avg, u.entry_requirements
            FROM universities u
            JOIN countries c ON u.country_id = c.id
        """, fetch=True)
        
        if rows:
            for r in rows:
                # Apply country filter
                if country_filter != "Tất cả" and r[2] != country_filter:
                    continue
                
                # Apply text search
                if search_term:
                    searchable_text = " ".join(str(x).lower() for x in r[1:6] if x)
                    if search_term not in searchable_text:
                        continue
                
                display_vals = list(r[:8])
                req_text = "N/A" if not r[8] else "JSON data..."
                display_vals.append(req_text)
                self.tree.insert("", "end", values=display_vals)
    
    def add_requirement(self):
        """Open dialog to add entry requirement"""
        dialog = Toplevel(self.frame)
        dialog.title("Add Entry Requirement")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="Category:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="e")
        category_var = ttk.Combobox(dialog, values=["english", "academic", "extra"], width=25)
        category_var.grid(row=0, column=1, padx=10, pady=10)
        category_var.current(0)
        
        tk.Label(dialog, text="Key:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, padx=10, pady=10, sticky="e")
        key_entry = tk.Entry(dialog, width=28)
        key_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Value:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, padx=10, pady=10, sticky="e")
        value_entry = tk.Entry(dialog, width=28)
        value_entry.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Type:", font=("Arial", 10, "bold")).grid(
            row=3, column=0, padx=10, pady=10, sticky="e")
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
            
            # Convert value based on type
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
        
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        tk.Button(btn_frame, text="Save", bg="#4CAF50", fg="white", 
                 command=save_requirement, width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", bg="#f44336", fg="white", 
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
        """Open dialog to add scholarship"""
        dialog = Toplevel(self.frame)
        dialog.title("Add Scholarship")
        dialog.geometry("400x280")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="Scholarship Name:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="e")
        name_entry = tk.Entry(dialog, width=28)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Value ($):", font=("Arial", 10, "bold")).grid(
            row=1, column=0, padx=10, pady=10, sticky="e")
        value_entry = tk.Entry(dialog, width=28)
        value_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Duration:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, padx=10, pady=10, sticky="e")
        duration_entry = tk.Entry(dialog, width=28)
        duration_entry.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Criteria:", font=("Arial", 10, "bold")).grid(
            row=3, column=0, padx=10, pady=10, sticky="ne")
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
        
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        tk.Button(btn_frame, text="Save", bg="#4CAF50", fg="white", 
                 command=save_scholarship, width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", bg="#f44336", fg="white", 
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
        
        # Get country_id
        country_id = execute_db("SELECT id FROM countries WHERE name=?", 
                               (country_name,), fetch=True)
        if not country_id:
            messagebox.showerror("Error", f"Country {country_name} not found")
            return
        country_id = country_id[0][0]
        
        # Parse numeric fields
        num_majors_int = int(num_majors) if num_majors else None
        tuition_fee_float = float(tuition_fee) if tuition_fee else None
        
        # Convert requirements to JSON
        entry_requirements_json = json.dumps(self.requirements_list) if self.requirements_list else None
        
        # Insert university
        result = execute_db("""INSERT INTO universities 
                (name, country_id, state, domain, website, num_majors, tuition_fee_avg, entry_requirements) 
                VALUES (?,?,?,?,?,?,?,?)""",
             (name, country_id, state, domain, website, num_majors_int, tuition_fee_float, entry_requirements_json),
             fetch=False)  # <-- fetch=False cho INSERT

        if result:  # True nếu insert thành công
            # Get the newly inserted university ID
            uni_id = execute_db("SELECT last_insert_rowid()", fetch=True)[0][0]

            # Insert scholarships
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
            
            # Load university data
            uni_data = execute_db("""
                SELECT name, country_id, state, domain, website, 
                       num_majors, tuition_fee_avg, entry_requirements
                FROM universities WHERE id=?
            """, (uni_id,), fetch=True)
            
            if uni_data:
                uni_data = uni_data[0]
                self.uni_name.delete(0, tk.END)
                self.uni_name.insert(0, uni_data[0] or "")
                
                # Get country name
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
                
                # Load requirements
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
                
                # Load scholarships
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
        
        # Update university
        if execute_db("""UPDATE universities 
                        SET name=?, country_id=?, state=?, domain=?, website=?, 
                            num_majors=?, tuition_fee_avg=?, entry_requirements=?
                        WHERE id=?""",
                     (name, country_id, state, domain, website, num_majors_int, 
                      tuition_fee_float, entry_requirements_json, uni_id)):
            
            # Delete old scholarships
            execute_db("DELETE FROM scholarships WHERE university_id=?", (uni_id,))
            
            # Insert new scholarships
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
            # Delete scholarships first
            execute_db("DELETE FROM scholarships WHERE university_id=?", (uni_id,))
            # Delete university
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