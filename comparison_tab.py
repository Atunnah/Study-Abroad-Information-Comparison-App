import tkinter as tk
from tkinter import ttk, messagebox
import database 
import matplotlib.pyplot as plt
import seaborn as sns
import json
import tkinter as tk
from tkinter import ttk, messagebox
import database 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import json
import re

from g4f.client import Client

def chat_with_g4f(prompt):
        client = Client()
        response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                web_search=False
        )
        return response.choices[0].message.content
    
      
def llm_data_formatter(prompt):
        return chat_with_g4f(prompt)


def format_data_for_visualization(criteria, universities_data):
    """
    Sử dụng LLM để trích xuất và định dạng dữ liệu so sánh thành JSON.
    :param criteria: Tiêu chí so sánh (ví dụ: 'IELTS').
    :param universities_data: List các bản ghi đầy đủ của các trường được chọn.
    :return: Dữ liệu đã định dạng (JSON string) hoặc None nếu lỗi.
    """
    print("Đang định dạng dữ liệu cho tiêu chí:", criteria)
    
    # Tạo Prompt cho LLM
    data_str = ""
    for uni in universities_data:
        # uni: (id, name, country_name, state, domain, website, num_majors, tuition_fee_avg, entry_requirements)
        uni_id, name, country, state, _, _, num_majors, tuition_fee_avg, entry_req = uni
        
        # Tập trung vào các cột liên quan đến tiêu chí so sánh
        data_str += f"\n--- ID: {uni_id}, Name: {name}, Country: {country}, Tuition: {tuition_fee_avg}, Majors: {num_majors}, Requirements: {entry_req}"
        
    prompt = (
        f"Bạn là một chuyên gia phân tích dữ liệu giáo dục. Nhiệm vụ của bạn là trích xuất dữ liệu "
        f"từ danh sách các trường đại học sau và định dạng nó thành JSON để chuẩn bị cho việc vẽ biểu đồ. "
        f"Tiêu chí so sánh **chính** là: **{criteria}**. "
        f"Hãy cố gắng tìm kiếm giá trị số hoặc giá trị chính xác nhất (ví dụ: 6.0 cho IELTS, 23200.0 cho Học phí) "
        f"từ các trường đại học trong danh sách. Nếu có nhiều giá trị cho cùng một tiêu chí (ví dụ: 'ielts_diploma' và 'ielts_degree'), "
        f"hãy chọn giá trị **cơ bản/thấp nhất** có thể áp dụng cho sinh viên quốc tế (ví dụ: 6.0 cho Diploma)."
        f"Nếu không tìm thấy giá trị, hãy gán giá trị 0 hoặc -1 (đối với số) hoặc 'N/A' (đối với văn bản). "
        f"Đầu ra **BẮT BUỘC** phải là một JSON object duy nhất, không có giải thích hay mã Python bổ sung. "
        f"Cấu trúc JSON mong muốn: "
        f"{{\n  \"criteria\": \"{criteria}\",\n  \"data\": [\n    {{\"University\": \"Tên Trường\", \"Value\": Giá Trị Đã Trích Xuất}}\n  ]\n}}"
        f"\n\nDanh sách dữ liệu thô:\n{data_str}"
    )

    try:
        # Gọi hàm LLM đã chọn (thực tế hoặc mô phỏng)
        json_output = llm_data_formatter(prompt)
        
        # Loại bỏ các ký tự không phải JSON (nếu LLM vô tình thêm vào)
        json_output = json_output.strip().replace("```json", "").replace("```", "").strip()
        
        # Trả về chuỗi JSON
        return json_output
        
    except Exception as e:
        messagebox.showerror("LLM Error", f"Lỗi khi gọi LLM để định dạng dữ liệu: {e}")
        return None


def visualization(formated_data_json):
    """
    Nhận dữ liệu JSON đã định dạng từ LLM và vẽ biểu đồ so sánh.
    :param formated_data_json: Chuỗi JSON được trả về từ format_data_for_visualization.
    """
    try:
        data = json.loads(formated_data_json)
    except json.JSONDecodeError:
        messagebox.showerror("Lỗi Dữ liệu", "Dữ liệu định dạng không hợp lệ (không phải JSON).")
        return

    criteria = data.get("criteria", "So sánh")
    data_list = data.get("data", [])

    if not data_list:
        messagebox.showinfo("So sánh", "Không có dữ liệu để vẽ biểu đồ.")
        return

    # Trích xuất dữ liệu
    names = [d["University"] for d in data_list]
    raw_values = [d["Value"] for d in data_list]

    # Kiểm tra loại dữ liệu
    is_numeric = all(isinstance(v, (int, float)) for v in raw_values)
    
    if is_numeric:
        # --- Vẽ biểu đồ số (Bar Chart) ---
        values = raw_values
        
        # Tạo cửa sổ TopLevel mới để hiển thị biểu đồ
        vis_window = tk.Toplevel()
        vis_window.title(f"📈 Biểu đồ So sánh: {criteria}")
        vis_window.geometry("800x600")

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.set_style("whitegrid")
        
        # Vẽ biểu đồ
        sns.barplot(x=names, y=values, ax=ax, palette="viridis")
        
        # Tùy chỉnh biểu đồ
        ax.set_title(f"So sánh các trường theo tiêu chí: {criteria}", fontsize=14, fontweight='bold')
        ax.set_ylabel(f"Giá trị {criteria}", fontsize=10)
        ax.set_xlabel("Trường Đại học", fontsize=10)
        plt.xticks(rotation=20, ha='right', fontsize=8)
        
        # Hiển thị giá trị trên thanh
        max_val = max(values) if values else 1
        for i, v in enumerate(values):
            ax.text(i, v + (max_val * 0.01), f"{v}", color='black', ha='center', fontweight='bold', fontsize=8)
            
        plt.tight_layout()
        
        # Tích hợp Matplotlib vào Tkinter
        canvas = FigureCanvasTkAgg(fig, master=vis_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        canvas.draw()
        
    else:
        # --- Hiển thị dữ liệu văn bản (Text Data) ---
        messagebox.showinfo("So sánh", f"Tiêu chí '{criteria}' có định dạng văn bản (ví dụ: yêu cầu chi tiết GPA, IELTS có sub-band). "
                                        f"Không thể vẽ biểu đồ thanh. Sẽ hiển thị chi tiết văn bản.")
        
        detail_window = tk.Toplevel()
        detail_window.title(f"Chi tiết So sánh: {criteria}")
        detail_window.geometry("600x400")
        
        detail_tree = ttk.Treeview(detail_window, columns=("University", criteria), show="headings")
        detail_tree.heading("University", text="Trường Đại học")
        detail_tree.heading(criteria, text=criteria)
        
        detail_tree.column("University", width=250, stretch=tk.YES)
        detail_tree.column(criteria, width=300, stretch=tk.YES)
        
        for d in data_list:
            detail_tree.insert("", "end", values=(d["University"], d["Value"]))
        
        detail_tree.pack(expand=True, fill='both', padx=10, pady=10)


class ComparisonTab:
    CRITERIA_OPTIONS = [
        "IELTS", "TOEFL", "PTE", "GPA", 
        "tuition_fee_avg", "majors_quantity"
    ]
    
    DISPLAY_CRITERIA = {
        "IELTS": "IELTS",
        "TOEFL": "TOEFL",
        "PTE": "PTE",
        "GPA": "GPA",
        "tuition_fee_avg": "Học phí TB",
        "majors_quantity": "Số lượng ngành"
    }

    def __init__(self, parent_frame, current_user_data=None):
        self.frame = parent_frame
        self.current_user_id = current_user_data[0] if current_user_data else 2 # Default to uid 2 for demo
        self.all_countries = database.get_all_countries()
        self.country_names = [c[1] for c in self.all_countries]
        self.country_map = {name: code for code, name in self.all_countries}
        
        self.all_universities_data = [] # Data source for All Universities
        self.favorite_universities_data = [] # Data source for Favorites
        self.selected_universities = {} # {uni_id: full_record}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Thiết lập grid cho frame chính
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_rowconfigure(3, weight=1)

        # --- 1. Control Panel (Top) ---
        control_frame = ttk.Frame(self.frame, padding="10 10 10 10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        control_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(control_frame, text="Tiêu chí So sánh:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.criteria_var = tk.StringVar(control_frame)
        self.criteria_var.set(self.CRITERIA_OPTIONS[0]) # Default value
        
        criteria_dropdown = ttk.Combobox(
            control_frame, 
            textvariable=self.criteria_var, 
            values=self.CRITERIA_OPTIONS,
            state="readonly",
            width=20
        )
        criteria_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        criteria_dropdown.bind("<<ComboboxSelected>>", self.load_universities)
        
        ttk.Button(control_frame, text="Tải Dữ liệu", command=self.load_universities, width=15).grid(row=0, column=2, padx=15, pady=5, sticky="e")

        # --- 2. University Selection Areas ---
        selection_frame = ttk.Frame(self.frame, padding="10 0 10 0")
        selection_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10)
        selection_frame.grid_columnconfigure(0, weight=1)
        selection_frame.grid_columnconfigure(1, weight=1)

        # 2.1. All Universities
        self.all_uni_frame = self._create_uni_selection_frame(selection_frame, "TẤT CẢ TRƯỜNG ĐẠI HỌC", 0)
        self.all_uni_tree, self.all_uni_search_var, self.all_uni_country_var = self._setup_uni_treeview(self.all_uni_frame, self.all_universities_data, self.add_to_comparison, "all_uni")
        
        # 2.2. User Favorites
        self.fav_uni_frame = self._create_uni_selection_frame(selection_frame, "TRƯỜNG YÊU THÍCH", 1)
        self.fav_uni_tree, self.fav_uni_search_var, self.fav_uni_country_var = self._setup_uni_treeview(self.fav_uni_frame, self.favorite_universities_data, self.add_to_comparison, "fav_uni")
        
        # --- 3. Comparison List ---
        comp_frame = ttk.LabelFrame(self.frame, text="DANH SÁCH TRƯỜNG ĐƯỢC CHỌN ĐỂ SO SÁNH", padding="10")
        comp_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=(10, 5))
        comp_frame.grid_columnconfigure(0, weight=1)
        comp_frame.grid_rowconfigure(0, weight=1)
        
        self.comp_tree = self._setup_comparison_treeview(comp_frame)
        
        # --- 4. Action Button ---
        action_frame = ttk.Frame(self.frame, padding="5 5 5 5")
        action_frame.grid(row=3, column=0, columnspan=2, sticky="e", padx=10, pady=(0, 10))
        
        ttk.Button(action_frame, text="📈 SO SÁNH DỮ LIỆU", command=self.start_comparison, style='Accent.TButton').pack(padx=10)
        
        # Load initial data
        self.load_universities()


    def _create_uni_selection_frame(self, parent, title, col):
        """Helper to create university selection frame with title and filter/search."""
        frame = ttk.LabelFrame(parent, text=title, padding="10 10 10 10")
        frame.grid(row=0, column=col, sticky="nsew", padx=5, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        return frame

    def _setup_uni_treeview(self, parent, data_list, action_command, source_id):
        """Helper to set up search, filter, and treeview for a university list."""
        
        # Filter and Search Frame
        filter_frame = ttk.Frame(parent)
        filter_frame.grid(row=0, column=0, sticky="ew")
        filter_frame.grid_columnconfigure(1, weight=1)
        
        # 1. Search Entry
        search_var = tk.StringVar(parent)
        search_var.trace_add("write", lambda *args: self.filter_universities(data_list, search_var.get(), country_var.get(), tree, source_id))
        ttk.Label(filter_frame, text="Tìm kiếm:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(filter_frame, textvariable=search_var).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # 2. Country Filter
        country_var = tk.StringVar(parent)
        country_var.set("Tất cả Quốc gia")
        country_values = ["Tất cả Quốc gia"] + self.country_names
        
        ttk.Label(filter_frame, text="Quốc gia:").grid(row=1, column=0, padx=5, pady=5)
        country_dropdown = ttk.Combobox(
            filter_frame, 
            textvariable=country_var, 
            values=country_values,
            state="readonly",
            width=20
        )
        country_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        country_dropdown.bind("<<ComboboxSelected>>", lambda *args: self.filter_universities(data_list, search_var.get(), country_var.get(), tree, source_id))

        # Treeview for Universities
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=2, column=0, sticky="nsew", pady=10)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        columns = ("ID", "Tên trường", "Quốc gia", "State", "Hành động")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        tree.configure(yscrollcommand=vsb.set)

        # Column configuration
        tree.heading("ID", text="ID")
        tree.heading("Tên trường", text="Tên Trường")
        tree.heading("Quốc gia", text="Quốc gia")
        tree.heading("State", text="State")
        tree.heading("Hành động", text="")
        
        tree.column("ID", width=30, stretch=tk.NO, anchor="center")
        tree.column("Tên trường", width=250, stretch=tk.YES)
        tree.column("Quốc gia", width=80, stretch=tk.NO)
        tree.column("State", width=80, stretch=tk.NO)
        tree.column("Hành động", width=100, stretch=tk.NO, anchor="center")

        # Add "Add" buttons to the treeview
        tree.bind('<ButtonRelease-1>', lambda e: self.on_uni_tree_click(e, tree, action_command))

        return tree, search_var, country_var

    def _setup_comparison_treeview(self, parent):
        """Setup the treeview for the selected comparison list."""
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        columns = ("ID", "Tên trường", "Quốc gia", "Tiêu chí", "Hành động")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        tree.configure(yscrollcommand=vsb.set)

        # Column configuration
        tree.heading("ID", text="ID")
        tree.heading("Tên trường", text="Tên Trường")
        tree.heading("Quốc gia", text="Quốc gia")
        tree.heading("Tiêu chí", text="Tiêu chí")
        tree.heading("Hành động", text="")
        
        tree.column("ID", width=30, stretch=tk.NO, anchor="center")
        tree.column("Tên trường", width=300, stretch=tk.YES)
        tree.column("Quốc gia", width=100, stretch=tk.NO)
        tree.column("Tiêu chí", width=250, stretch=tk.YES)
        tree.column("Hành động", width=80, stretch=tk.NO, anchor="center")

        # Add "Remove" buttons to the treeview
        tree.bind('<ButtonRelease-1>', self.on_comp_tree_click)
        
        return tree

    def load_universities(self, event=None):
        """Loads and displays universities based on selected criteria and source."""
        criteria = self.criteria_var.get()
        if not criteria:
            return

        # 1. Load All Universities
        self.all_universities_data = database.get_universities_by_criteria(criteria)
        self.filter_universities(
            self.all_universities_data, 
            self.all_uni_search_var.get(), 
            self.all_uni_country_var.get(), 
            self.all_uni_tree, 
            "all_uni"
        )

        # 2. Load Favorite Universities (requires user ID)
        if self.current_user_id:
            self.favorite_universities_data = database.get_favorite_universities_by_criteria(self.current_user_id, criteria)
            self.filter_universities(
                self.favorite_universities_data, 
                self.fav_uni_search_var.get(), 
                self.fav_uni_country_var.get(), 
                self.fav_uni_tree, 
                "fav_uni"
            )
        else:
            self.favorite_universities_data = []
            self.fav_uni_tree.delete(*self.fav_uni_tree.get_children())
            
        # Cập nhật danh sách so sánh để lấy lại Tiêu chí hiển thị mới
        self.refresh_comparison_list()


    def filter_universities(self, data_source, search_text, country_name, tree, source_id):
        """Filters the university list based on search and country filter."""
        tree.delete(*tree.get_children())
        search_term = search_text.lower().strip()
        
        for uni_data in data_source:
            # uni_data: (id, name, country_name, state, num_majors, tuition_fee_avg, entry_requirements)
            uni_id, name, country, state, _, _, _ = uni_data
            
            # Check Country Filter
            if country_name != "Tất cả Quốc gia" and country != country_name:
                continue

            # Check Search Text (on name, state, country)
            if search_term and not (search_term in name.lower() or 
                                    (country and search_term in country.lower()) or
                                    (state and search_term in state.lower())):
                continue

            # Insert into Treeview
            # Columns: ("ID", "Tên trường", "Quốc gia", "State", "Hành động")
            tree.insert("", "end", values=(uni_id, name, country or "N/A", state or "N/A", "Thêm"), 
                        tags=(uni_id, source_id)) # Use tags to store uni_id

    def on_uni_tree_click(self, event, tree, action_command):
        """Handles click on the 'Add' button column in the university list."""
        item = tree.identify_row(event.y)
        if not item:
            return
            
        col = tree.identify_column(event.x)
        # Check if click is on the "Hành động" column (column #5, index #4)
        if tree.heading(col)['text'] == "":
            try:
                values = tree.item(item, 'values')
                uni_id = int(values[0])
                action_command(uni_id)
            except (ValueError, IndexError):
                pass
                
    def on_comp_tree_click(self, event):
        """Handles click on the 'Remove' button column in the comparison list."""
        item = self.comp_tree.identify_row(event.y)
        if not item:
            return
            
        col = self.comp_tree.identify_column(event.x)
        # Check if click is on the "Hành động" column (column #5, index #4)
        if self.comp_tree.heading(col)['text'] == "":
            try:
                values = self.comp_tree.item(item, 'values')
                uni_id = int(values[0])
                self.remove_from_comparison(uni_id)
            except (ValueError, IndexError):
                pass

    def add_to_comparison(self, uni_id):
        """Adds a university to the comparison list if not already present."""
        if uni_id in self.selected_universities:
            messagebox.showwarning("Cảnh báo", "Trường này đã có trong danh sách so sánh.")
            return

        full_record = database.get_university_by_id(uni_id)
        if full_record:
            self.selected_universities[uni_id] = full_record
            self.refresh_comparison_list()
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu đầy đủ của trường.")

    def remove_from_comparison(self, uni_id):
        """Removes a university from the comparison list."""
        if uni_id in self.selected_universities:
            del self.selected_universities[uni_id]
            self.refresh_comparison_list()

    def refresh_comparison_list(self):
        """Refreshes the comparison list Treeview."""
        self.comp_tree.delete(*self.comp_tree.get_children())
        criteria = self.criteria_var.get()
        criteria_display = self.DISPLAY_CRITERIA.get(criteria, criteria)
        
        for uni_id, record in self.selected_universities.items():
            # record: (id, name, country_name, state, domain, website, num_majors, tuition_fee_avg, entry_requirements)
            _, name, country_name, _, _, _, num_majors, tuition_fee_avg, entry_requirements_json = record
            
            # Extract criteria value for display
            criteria_value = "N/A"
            if criteria == "tuition_fee_avg":
                criteria_value = f"{tuition_fee_avg:,.2f} USD" if tuition_fee_avg is not None else criteria_value
            elif criteria == "majors_quantity":
                criteria_value = str(num_majors) if num_majors is not None else criteria_value
            else: # Language/GPA criteria (need to parse JSON)
                if entry_requirements_json:
                    try:
                        requirements = json.loads(entry_requirements_json)
                        key_to_find = criteria.lower().replace(' ', '')
                        for req in requirements:
                            if isinstance(req, dict) and 'key' in req:
                                if req['key'].lower().replace(' ', '') == key_to_find:
                                    criteria_value = f"{criteria}: {req.get('value', 'N/A')}"
                                    break
                    except json.JSONDecodeError:
                        pass # JSON error
            
            # Columns: ("ID", "Tên trường", "Quốc gia", "Tiêu chí", "Hành động")
            self.comp_tree.insert("", "end", values=(
                uni_id, 
                name, 
                country_name or "N/A", 
                f"{criteria_display}: {criteria_value}", 
                "Xóa"
            ), tags=(uni_id,))

    def start_comparison(self):
        """Triggers the data formatting and visualization process."""
        if not self.selected_universities:
            messagebox.showwarning("So sánh", "Vui lòng chọn ít nhất một trường để so sánh.")
            return

        criteria = self.criteria_var.get()
        universities_to_compare = list(self.selected_universities.values())
        
        # 1. Format Data
        formated_data = format_data_for_visualization(criteria, universities_to_compare)
        
        # 2. Visualize
        print("Dữ liệu đã định dạng:", formated_data)
        visualization(formated_data)
        
        # Cập nhật: Sau khi so sánh, hỏi người dùng có muốn xóa danh sách không
        # if messagebox.askyesno("Hoàn thành So sánh", "Bạn có muốn xóa danh sách các trường đã chọn để so sánh không?"):
        #     self.selected_universities.clear()
        #     self.refresh_comparison_list()