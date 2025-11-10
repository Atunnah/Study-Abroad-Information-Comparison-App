import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from database import Database
from crud_operations import UniversityCRUD, AdmissionRequirementCRUD
from config import APP_TITLE, APP_WIDTH, APP_HEIGHT
from datetime import datetime

class UniversityComparisonApp:
    """Main Application Class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        
        # Kết nối database
        self.db = Database()
        if not self.db.connect():
            messagebox.showerror("Lỗi", "Không thể kết nối database!")
            return
        
        # Khởi tạo CRUD operations
        self.university_crud = UniversityCRUD(self.db)
        self.admission_crud = AdmissionRequirementCRUD(self.db)
        
        # Tạo notebook (tab control)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tạo các tab
        self.create_university_tab()
        self.create_admission_tab()
        self.create_comparison_tab()
        
    def create_university_tab(self):
        """Tab quản lý trường đại học"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Quản lý Trường Đại học")
        
        # Frame cho form nhập liệu
        form_frame = ttk.LabelFrame(tab, text="Thông tin Trường Đại học", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)
        
        # Các trường nhập liệu
        ttk.Label(form_frame, text="Tên trường:").grid(row=0, column=0, sticky='w', pady=2)
        self.uni_name = ttk.Entry(form_frame, width=40)
        self.uni_name.grid(row=0, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Quốc gia:").grid(row=0, column=2, sticky='w', pady=2)
        self.uni_country = ttk.Entry(form_frame, width=25)
        self.uni_country.grid(row=0, column=3, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Thành phố:").grid(row=1, column=0, sticky='w', pady=2)
        self.uni_city = ttk.Entry(form_frame, width=40)
        self.uni_city.grid(row=1, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Xếp hạng:").grid(row=1, column=2, sticky='w', pady=2)
        self.uni_ranking = ttk.Entry(form_frame, width=25)
        self.uni_ranking.grid(row=1, column=3, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Website:").grid(row=2, column=0, sticky='w', pady=2)
        self.uni_website = ttk.Entry(form_frame, width=40)
        self.uni_website.grid(row=2, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Năm thành lập:").grid(row=2, column=2, sticky='w', pady=2)
        self.uni_year = ttk.Entry(form_frame, width=25)
        self.uni_year.grid(row=2, column=3, pady=2, padx=5)
        
        # Frame cho các nút
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Thêm", command=self.add_university).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cập nhật", command=self.update_university).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Xóa", command=self.delete_university).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Làm mới", command=self.clear_university_form).pack(side='left', padx=5)
        
        # Frame tìm kiếm
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side='left', padx=5)
        self.uni_search = ttk.Entry(search_frame, width=40)
        self.uni_search.pack(side='left', padx=5)
        ttk.Button(search_frame, text="Tìm", command=self.search_university).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Hiển thị tất cả", command=self.load_universities).pack(side='left', padx=5)
        
        # Treeview để hiển thị danh sách
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        self.uni_tree = ttk.Treeview(tree_frame, 
                                     columns=('ID', 'Tên', 'Quốc gia', 'Thành phố', 'Xếp hạng', 'Website', 'Năm'),
                                     show='headings',
                                     yscrollcommand=vsb.set,
                                     xscrollcommand=hsb.set)
        
        vsb.config(command=self.uni_tree.yview)
        hsb.config(command=self.uni_tree.xview)
        
        # Cấu hình cột
        self.uni_tree.heading('ID', text='ID')
        self.uni_tree.heading('Tên', text='Tên trường')
        self.uni_tree.heading('Quốc gia', text='Quốc gia')
        self.uni_tree.heading('Thành phố', text='Thành phố')
        self.uni_tree.heading('Xếp hạng', text='Xếp hạng')
        self.uni_tree.heading('Website', text='Website')
        self.uni_tree.heading('Năm', text='Năm thành lập')
        
        self.uni_tree.column('ID', width=50)
        self.uni_tree.column('Tên', width=250)
        self.uni_tree.column('Quốc gia', width=120)
        self.uni_tree.column('Thành phố', width=120)
        self.uni_tree.column('Xếp hạng', width=80)
        self.uni_tree.column('Website', width=200)
        self.uni_tree.column('Năm', width=100)
        
        # Pack treeview và scrollbars
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.uni_tree.pack(fill='both', expand=True)
        
        # Bind double click để chọn
        self.uni_tree.bind('<Double-1>', self.on_university_select)
        
        # Load dữ liệu
        self.load_universities()
    
    def create_admission_tab(self):
        """Tab quản lý yêu cầu đầu vào"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Quản lý Yêu cầu Đầu vào")
        
        # Frame cho form nhập liệu
        form_frame = ttk.LabelFrame(tab, text="Thông tin Yêu cầu Đầu vào", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)
        
        # Dòng 1
        ttk.Label(form_frame, text="Trường:").grid(row=0, column=0, sticky='w', pady=2)
        self.adm_university = ttk.Combobox(form_frame, width=37, state='readonly')
        self.adm_university.grid(row=0, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Chương trình:").grid(row=0, column=2, sticky='w', pady=2)
        self.adm_program = ttk.Entry(form_frame, width=25)
        self.adm_program.grid(row=0, column=3, pady=2, padx=5)
        
        # Dòng 2
        ttk.Label(form_frame, text="Bậc học:").grid(row=1, column=0, sticky='w', pady=2)
        self.adm_degree = ttk.Combobox(form_frame, width=37, 
                                       values=['Bachelor', 'Master', 'PhD', 'Diploma'],
                                       state='readonly')
        self.adm_degree.grid(row=1, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="GPA tối thiểu:").grid(row=1, column=2, sticky='w', pady=2)
        self.adm_gpa = ttk.Entry(form_frame, width=25)
        self.adm_gpa.grid(row=1, column=3, pady=2, padx=5)
        
        # Dòng 3
        ttk.Label(form_frame, text="IELTS tối thiểu:").grid(row=2, column=0, sticky='w', pady=2)
        self.adm_ielts = ttk.Entry(form_frame, width=37)
        self.adm_ielts.grid(row=2, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="TOEFL tối thiểu:").grid(row=2, column=2, sticky='w', pady=2)
        self.adm_toefl = ttk.Entry(form_frame, width=25)
        self.adm_toefl.grid(row=2, column=3, pady=2, padx=5)
        
        # Dòng 4
        ttk.Label(form_frame, text="SAT tối thiểu:").grid(row=3, column=0, sticky='w', pady=2)
        self.adm_sat = ttk.Entry(form_frame, width=37)
        self.adm_sat.grid(row=3, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="GRE tối thiểu:").grid(row=3, column=2, sticky='w', pady=2)
        self.adm_gre = ttk.Entry(form_frame, width=25)
        self.adm_gre.grid(row=3, column=3, pady=2, padx=5)
        
        # Dòng 5
        ttk.Label(form_frame, text="Học phí (USD):").grid(row=4, column=0, sticky='w', pady=2)
        self.adm_tuition = ttk.Entry(form_frame, width=37)
        self.adm_tuition.grid(row=4, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Deadline (YYYY-MM-DD):").grid(row=4, column=2, sticky='w', pady=2)
        self.adm_deadline = ttk.Entry(form_frame, width=25)
        self.adm_deadline.grid(row=4, column=3, pady=2, padx=5)
        
        # Yêu cầu bổ sung
        ttk.Label(form_frame, text="Yêu cầu bổ sung:").grid(row=5, column=0, sticky='w', pady=2)
        self.adm_additional = ttk.Entry(form_frame, width=100)
        self.adm_additional.grid(row=5, column=1, columnspan=3, pady=2, padx=5)
        
        # Frame cho các nút
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Thêm", command=self.add_admission).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cập nhật", command=self.update_admission).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Xóa", command=self.delete_admission).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Làm mới", command=self.clear_admission_form).pack(side='left', padx=5)
        
        # Frame tìm kiếm
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(search_frame, text="Tìm theo chương trình:").pack(side='left', padx=5)
        self.adm_search = ttk.Entry(search_frame, width=40)
        self.adm_search.pack(side='left', padx=5)
        ttk.Button(search_frame, text="Tìm", command=self.search_admission).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Hiển thị tất cả", command=self.load_admissions).pack(side='left', padx=5)
        
        # Treeview
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        self.adm_tree = ttk.Treeview(tree_frame,
                                     columns=('ID', 'Trường', 'Chương trình', 'Bậc học', 'GPA', 'IELTS', 
                                             'TOEFL', 'SAT', 'Học phí'),
                                     show='headings',
                                     yscrollcommand=vsb.set,
                                     xscrollcommand=hsb.set)
        
        vsb.config(command=self.adm_tree.yview)
        hsb.config(command=self.adm_tree.xview)
        
        # Cấu hình cột
        self.adm_tree.heading('ID', text='ID')
        self.adm_tree.heading('Trường', text='Trường')
        self.adm_tree.heading('Chương trình', text='Chương trình')
        self.adm_tree.heading('Bậc học', text='Bậc học')
        self.adm_tree.heading('GPA', text='GPA')
        self.adm_tree.heading('IELTS', text='IELTS')
        self.adm_tree.heading('TOEFL', text='TOEFL')
        self.adm_tree.heading('SAT', text='SAT')
        self.adm_tree.heading('Học phí', text='Học phí (USD)')
        
        self.adm_tree.column('ID', width=50)
        self.adm_tree.column('Trường', width=200)
        self.adm_tree.column('Chương trình', width=150)
        self.adm_tree.column('Bậc học', width=80)
        self.adm_tree.column('GPA', width=60)
        self.adm_tree.column('IELTS', width=60)
        self.adm_tree.column('TOEFL', width=60)
        self.adm_tree.column('SAT', width=60)
        self.adm_tree.column('Học phí', width=100)
        
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.adm_tree.pack(fill='both', expand=True)
        
        self.adm_tree.bind('<Double-1>', self.on_admission_select)
        
        # Load dữ liệu
        self.load_university_combobox()
        self.load_admissions()
    
    def create_comparison_tab(self):
        """Tab so sánh các chương trình"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="So sánh Chương trình")
        
        # Frame hướng dẫn
        info_frame = ttk.LabelFrame(tab, text="Hướng dẫn", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(info_frame, text="Chọn các chương trình từ danh sách bên dưới và nhấn 'So sánh' để xem chi tiết.",
                 font=('Arial', 10)).pack()
        
        # Frame danh sách chương trình
        list_frame = ttk.LabelFrame(tab, text="Danh sách Chương trình", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview với checkbox
        tree_scroll = ttk.Scrollbar(list_frame)
        tree_scroll.pack(side='right', fill='y')
        
        self.comp_tree = ttk.Treeview(list_frame,
                                      columns=('ID', 'Trường', 'Chương trình', 'Bậc học', 'GPA', 'IELTS', 'Học phí'),
                                      show='tree headings',
                                      yscrollcommand=tree_scroll.set)
        
        tree_scroll.config(command=self.comp_tree.yview)
        
        self.comp_tree.heading('#0', text='☐')
        self.comp_tree.heading('ID', text='ID')
        self.comp_tree.heading('Trường', text='Trường')
        self.comp_tree.heading('Chương trình', text='Chương trình')
        self.comp_tree.heading('Bậc học', text='Bậc học')
        self.comp_tree.heading('GPA', text='GPA')
        self.comp_tree.heading('IELTS', text='IELTS')
        self.comp_tree.heading('Học phí', text='Học phí (USD)')
        
        self.comp_tree.column('#0', width=30)
        self.comp_tree.column('ID', width=50)
        self.comp_tree.column('Trường', width=200)
        self.comp_tree.column('Chương trình', width=150)
        self.comp_tree.column('Bậc học', width=80)
        self.comp_tree.column('GPA', width=60)
        self.comp_tree.column('IELTS', width=60)
        self.comp_tree.column('Học phí', width=100)
        
        self.comp_tree.pack(fill='both', expand=True)
        
        # Dictionary để lưu trạng thái checkbox
        self.selected_programs = {}
        self.comp_tree.bind('<Button-1>', self.toggle_selection)
        
        # Frame nút
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="So sánh", command=self.compare_programs, 
                  style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Làm mới", command=self.load_comparison_list).pack(side='left', padx=5)
        
        # Load dữ liệu
        self.load_comparison_list()
    
    # =============== University CRUD Methods ===============
    
    def add_university(self):
        """Thêm trường đại học mới"""
        try:
            data = {
                'university_name': self.uni_name.get().strip(),
                'country': self.uni_country.get().strip(),
                'city': self.uni_city.get().strip(),
                'ranking': int(self.uni_ranking.get()) if self.uni_ranking.get() else None,
                'website': self.uni_website.get().strip() or None,
                'established_year': int(self.uni_year.get()) if self.uni_year.get() else None
            }
            
            if not data['university_name'] or not data['country']:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên trường và quốc gia!")
                return
            
            if self.university_crud.create(data):
                messagebox.showinfo("Thành công", "Đã thêm trường đại học!")
                self.clear_university_form()
                self.load_universities()
                self.load_university_combobox()
        except ValueError:
            messagebox.showerror("Lỗi", "Xếp hạng và năm thành lập phải là số!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm: {str(e)}")
    
    def update_university(self):
        """Cập nhật thông tin trường đại học"""
        selected = self.uni_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn trường cần cập nhật!")
            return
        
        try:
            item = self.uni_tree.item(selected[0])
            university_id = item['values'][0]
            
            data = {
                'university_name': self.uni_name.get().strip(),
                'country': self.uni_country.get().strip(),
                'city': self.uni_city.get().strip(),
                'ranking': int(self.uni_ranking.get()) if self.uni_ranking.get() else None,
                'website': self.uni_website.get().strip() or None,
                'established_year': int(self.uni_year.get()) if self.uni_year.get() else None
            }
            
            if not data['university_name'] or not data['country']:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên trường và quốc gia!")
                return
            
            if self.university_crud.update(university_id, data):
                messagebox.showinfo("Thành công", "Đã cập nhật thông tin!")
                self.clear_university_form()
                self.load_universities()
                self.load_university_combobox()
        except ValueError:
            messagebox.showerror("Lỗi", "Xếp hạng và năm thành lập phải là số!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật: {str(e)}")
    
    def delete_university(self):
        """Xóa trường đại học"""
        selected = self.uni_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn trường cần xóa!")
            return
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa trường này?"):
            try:
                item = self.uni_tree.item(selected[0])
                university_id = item['values'][0]
                
                if self.university_crud.delete(university_id):
                    messagebox.showinfo("Thành công", "Đã xóa trường đại học!")
                    self.clear_university_form()
                    self.load_universities()
                    self.load_university_combobox()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {str(e)}")
    
    def search_university(self):
        """Tìm kiếm trường đại học"""
        keyword = self.uni_search.get().strip()
        if not keyword:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập từ khóa tìm kiếm!")
            return
        
        results = self.university_crud.search(keyword)
        self.display_universities(results)
    
    def load_universities(self):
        """Load danh sách trường đại học"""
        universities = self.university_crud.read_all()
        self.display_universities(universities)
    
    def display_universities(self, universities):
        """Hiển thị danh sách trường đại học"""
        # Xóa dữ liệu cũ
        for item in self.uni_tree.get_children():
            self.uni_tree.delete(item)
        
        # Thêm dữ liệu mới
        for uni in universities:
            self.uni_tree.insert('', 'end', values=(
                uni['id'],
                uni['university_name'],
                uni['country'],
                uni['city'],
                uni['ranking'] or '',
                uni['website'] or '',
                uni['established_year'] or ''
            ))
    
    def on_university_select(self, event):
        """Xử lý khi chọn trường đại học"""
        selected = self.uni_tree.selection()
        if selected:
            item = self.uni_tree.item(selected[0])
            values = item['values']
            
            self.uni_name.delete(0, 'end')
            self.uni_name.insert(0, values[1])
            
            self.uni_country.delete(0, 'end')
            self.uni_country.insert(0, values[2])
            
            self.uni_city.delete(0, 'end')
            self.uni_city.insert(0, values[3])
            
            self.uni_ranking.delete(0, 'end')
            self.uni_ranking.insert(0, values[4])
            
            self.uni_website.delete(0, 'end')
            self.uni_website.insert(0, values[5])
            
            self.uni_year.delete(0, 'end')
            self.uni_year.insert(0, values[6])
    
    def clear_university_form(self):
        """Xóa form nhập liệu trường đại học"""
        self.uni_name.delete(0, 'end')
        self.uni_country.delete(0, 'end')
        self.uni_city.delete(0, 'end')
        self.uni_ranking.delete(0, 'end')
        self.uni_website.delete(0, 'end')
        self.uni_year.delete(0, 'end')
        self.uni_search.delete(0, 'end')
    
    # =============== Admission CRUD Methods ===============
    
    def load_university_combobox(self):
        """Load danh sách trường vào combobox"""
        universities = self.university_crud.read_all()
        self.university_list = {f"{u['university_name']} ({u['country']})": u['id'] for u in universities}
        self.adm_university['values'] = list(self.university_list.keys())
    
    def add_admission(self):
        """Thêm yêu cầu đầu vào mới"""
        try:
            selected_uni = self.adm_university.get()
            if not selected_uni:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn trường!")
                return
            
            data = {
                'university_id': self.university_list[selected_uni],
                'program_name': self.adm_program.get().strip(),
                'degree_level': self.adm_degree.get(),
                'min_gpa': float(self.adm_gpa.get()) if self.adm_gpa.get() else None,
                'min_ielts': float(self.adm_ielts.get()) if self.adm_ielts.get() else None,
                'min_toefl': int(self.adm_toefl.get()) if self.adm_toefl.get() else None,
                'min_sat': int(self.adm_sat.get()) if self.adm_sat.get() else None,
                'min_gre': int(self.adm_gre.get()) if self.adm_gre.get() else None,
                'tuition_fee_usd': float(self.adm_tuition.get()) if self.adm_tuition.get() else None,
                'application_deadline': self.adm_deadline.get() or None,
                'additional_requirements': self.adm_additional.get().strip() or None
            }
            
            if not data['program_name'] or not data['degree_level']:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập chương trình và bậc học!")
                return
            
            if self.admission_crud.create(data):
                messagebox.showinfo("Thành công", "Đã thêm yêu cầu đầu vào!")
                self.clear_admission_form()
                self.load_admissions()
                self.load_comparison_list()
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập đúng định dạng số!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm: {str(e)}")
    
    def update_admission(self):
        """Cập nhật yêu cầu đầu vào"""
        selected = self.adm_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn yêu cầu cần cập nhật!")
            return
        
        try:
            item = self.adm_tree.item(selected[0])
            admission_id = item['values'][0]
            
            selected_uni = self.adm_university.get()
            if not selected_uni:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn trường!")
                return
            
            data = {
                'university_id': self.university_list[selected_uni],
                'program_name': self.adm_program.get().strip(),
                'degree_level': self.adm_degree.get(),
                'min_gpa': float(self.adm_gpa.get()) if self.adm_gpa.get() else None,
                'min_ielts': float(self.adm_ielts.get()) if self.adm_ielts.get() else None,
                'min_toefl': int(self.adm_toefl.get()) if self.adm_toefl.get() else None,
                'min_sat': int(self.adm_sat.get()) if self.adm_sat.get() else None,
                'min_gre': int(self.adm_gre.get()) if self.adm_gre.get() else None,
                'tuition_fee_usd': float(self.adm_tuition.get()) if self.adm_tuition.get() else None,
                'application_deadline': self.adm_deadline.get() or None,
                'additional_requirements': self.adm_additional.get().strip() or None
            }
            
            if self.admission_crud.update(admission_id, data):
                messagebox.showinfo("Thành công", "Đã cập nhật yêu cầu!")
                self.clear_admission_form()
                self.load_admissions()
                self.load_comparison_list()
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập đúng định dạng số!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật: {str(e)}")
    
    def delete_admission(self):
        """Xóa yêu cầu đầu vào"""
        selected = self.adm_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn yêu cầu cần xóa!")
            return
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa yêu cầu này?"):
            try:
                item = self.adm_tree.item(selected[0])
                admission_id = item['values'][0]
                
                if self.admission_crud.delete(admission_id):
                    messagebox.showinfo("Thành công", "Đã xóa yêu cầu!")
                    self.clear_admission_form()
                    self.load_admissions()
                    self.load_comparison_list()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {str(e)}")
    
    def search_admission(self):
        """Tìm kiếm yêu cầu đầu vào"""
        keyword = self.adm_search.get().strip()
        if not keyword:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập từ khóa!")
            return
        
        results = self.admission_crud.search_by_program(keyword)
        self.display_admissions(results)
    
    def load_admissions(self):
        """Load danh sách yêu cầu đầu vào"""
        admissions = self.admission_crud.read_all()
        self.display_admissions(admissions)
    
    def display_admissions(self, admissions):
        """Hiển thị danh sách yêu cầu đầu vào"""
        for item in self.adm_tree.get_children():
            self.adm_tree.delete(item)
        
        for adm in admissions:
            self.adm_tree.insert('', 'end', values=(
                adm['id'],
                adm['university_name'],
                adm['program_name'],
                adm['degree_level'],
                adm['min_gpa'] or '',
                adm['min_ielts'] or '',
                adm['min_toefl'] or '',
                adm['min_sat'] or '',
                f"{adm['tuition_fee_usd']:,.2f}" if adm['tuition_fee_usd'] else ''
            ))
    
    def on_admission_select(self, event):
        """Xử lý khi chọn yêu cầu đầu vào"""
        selected = self.adm_tree.selection()
        if selected:
            item = self.adm_tree.item(selected[0])
            admission_id = item['values'][0]
            
            # Lấy thông tin chi tiết
            adm = self.admission_crud.read_by_id(admission_id)
            if adm:
                # Chọn trường
                uni_key = f"{adm['university_name']} ({adm['country']})"
                self.adm_university.set(uni_key)
                
                self.adm_program.delete(0, 'end')
                self.adm_program.insert(0, adm['program_name'])
                
                self.adm_degree.set(adm['degree_level'])
                
                self.adm_gpa.delete(0, 'end')
                if adm['min_gpa']:
                    self.adm_gpa.insert(0, adm['min_gpa'])
                
                self.adm_ielts.delete(0, 'end')
                if adm['min_ielts']:
                    self.adm_ielts.insert(0, adm['min_ielts'])
                
                self.adm_toefl.delete(0, 'end')
                if adm['min_toefl']:
                    self.adm_toefl.insert(0, adm['min_toefl'])
                
                self.adm_sat.delete(0, 'end')
                if adm['min_sat']:
                    self.adm_sat.insert(0, adm['min_sat'])
                
                self.adm_gre.delete(0, 'end')
                if adm['min_gre']:
                    self.adm_gre.insert(0, adm['min_gre'])
                
                self.adm_tuition.delete(0, 'end')
                if adm['tuition_fee_usd']:
                    self.adm_tuition.insert(0, adm['tuition_fee_usd'])
                
                self.adm_deadline.delete(0, 'end')
                if adm['application_deadline']:
                    self.adm_deadline.insert(0, adm['application_deadline'])
                
                self.adm_additional.delete(0, 'end')
                if adm['additional_requirements']:
                    self.adm_additional.insert(0, adm['additional_requirements'])
    
    def clear_admission_form(self):
        """Xóa form yêu cầu đầu vào"""
        self.adm_university.set('')
        self.adm_program.delete(0, 'end')
        self.adm_degree.set('')
        self.adm_gpa.delete(0, 'end')
        self.adm_ielts.delete(0, 'end')
        self.adm_toefl.delete(0, 'end')
        self.adm_sat.delete(0, 'end')
        self.adm_gre.delete(0, 'end')
        self.adm_tuition.delete(0, 'end')
        self.adm_deadline.delete(0, 'end')
        self.adm_additional.delete(0, 'end')
        self.adm_search.delete(0, 'end')
    
    # =============== Comparison Methods ===============
    
    def load_comparison_list(self):
        """Load danh sách cho so sánh"""
        for item in self.comp_tree.get_children():
            self.comp_tree.delete(item)
        
        self.selected_programs = {}
        admissions = self.admission_crud.read_all()
        
        for adm in admissions:
            item_id = self.comp_tree.insert('', 'end', text='☐', values=(
                adm['id'],
                adm['university_name'],
                adm['program_name'],
                adm['degree_level'],
                adm['min_gpa'] or '',
                adm['min_ielts'] or '',
                f"{adm['tuition_fee_usd']:,.2f}" if adm['tuition_fee_usd'] else ''
            ))
            self.selected_programs[item_id] = False
    
    def toggle_selection(self, event):
        """Toggle checkbox khi click"""
        region = self.comp_tree.identify_region(event.x, event.y)
        if region == "tree":
            item = self.comp_tree.identify_row(event.y)
            if item:
                self.selected_programs[item] = not self.selected_programs[item]
                self.comp_tree.item(item, text='☑' if self.selected_programs[item] else '☐')
    
    def compare_programs(self):
        """So sánh các chương trình được chọn"""
        selected_ids = [
            self.comp_tree.item(item)['values'][0]
            for item, checked in self.selected_programs.items()
            if checked
        ]
        
        if len(selected_ids) < 2:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất 2 chương trình để so sánh!")
            return
        
        # Lấy thông tin các chương trình
        programs = self.admission_crud.compare_programs(selected_ids)
        
        # Tạo cửa sổ so sánh
        self.show_comparison_window(programs)
    
    def show_comparison_window(self, programs):
        """Hiển thị cửa sổ so sánh chi tiết"""
        comp_window = tk.Toplevel(self.root)
        comp_window.title("Kết quả So sánh")
        comp_window.geometry("1000x600")
        
        # Frame chứa bảng so sánh
        frame = ttk.Frame(comp_window, padding=10)
        frame.pack(fill='both', expand=True)
        
        # Tạo text widget với scrollbar
        text_scroll = ttk.Scrollbar(frame)
        text_scroll.pack(side='right', fill='y')
        
        text = tk.Text(frame, wrap='none', yscrollcommand=text_scroll.set, font=('Courier', 10))
        text_scroll.config(command=text.yview)
        text.pack(fill='both', expand=True)
        
        # Tạo nội dung so sánh
        content = "=" * 100 + "\n"
        content += "KẾT QUẢ SO SÁNH CÁC CHƯƠNG TRÌNH\n"
        content += "=" * 100 + "\n\n"
        
        for i, prog in enumerate(programs, 1):
            content += f"{'=' * 100}\n"
            content += f"CHƯƠNG TRÌNH {i}: {prog['program_name']} - {prog['degree_level']}\n"
            content += f"{'=' * 100}\n"
            content += f"Trường:           {prog['university_name']}\n"
            content += f"Quốc gia:         {prog['country']}\n"
            content += f"Xếp hạng:         #{prog['ranking']}\n"
            content += f"\nYÊU CẦU ĐẦU VÀO:\n"
            content += f"{'-' * 50}\n"
            content += f"GPA tối thiểu:    {prog['min_gpa'] if prog['min_gpa'] else 'N/A'}\n"
            content += f"IELTS tối thiểu:  {prog['min_ielts'] if prog['min_ielts'] else 'N/A'}\n"
            content += f"TOEFL tối thiểu:  {prog['min_toefl'] if prog['min_toefl'] else 'N/A'}\n"
            content += f"SAT tối thiểu:    {prog['min_sat'] if prog['min_sat'] else 'N/A'}\n"
            content += f"GRE tối thiểu:    {prog['min_gre'] if prog['min_gre'] else 'N/A'}\n"
            content += f"\nTHÔNG TIN KHÁC:\n"
            content += f"{'-' * 50}\n"
            content += f"Học phí:          ${prog['tuition_fee_usd']:,.2f} USD/năm\n" if prog['tuition_fee_usd'] else "Học phí:          N/A\n"
            content += f"Deadline:         {prog['application_deadline']}\n" if prog['application_deadline'] else "Deadline:         N/A\n"
            content += f"Yêu cầu bổ sung:  {prog['additional_requirements']}\n" if prog['additional_requirements'] else "Yêu cầu bổ sung:  N/A\n"
            content += f"\n"
        
        content += "=" * 100 + "\n"
        content += "PHÂN TÍCH SO SÁNH\n"
        content += "=" * 100 + "\n\n"
        
        # Tính toán và hiển thị thống kê
        gpas = [p['min_gpa'] for p in programs if p['min_gpa']]
        ielts = [p['min_ielts'] for p in programs if p['min_ielts']]
        fees = [p['tuition_fee_usd'] for p in programs if p['tuition_fee_usd']]
        
        if gpas:
            content += f"GPA cao nhất yêu cầu:     {max(gpas)}\n"
            content += f"GPA thấp nhất yêu cầu:    {min(gpas)}\n"
            content += f"GPA trung bình:           {sum(gpas)/len(gpas):.2f}\n\n"
        
        if ielts:
            content += f"IELTS cao nhất yêu cầu:   {max(ielts)}\n"
            content += f"IELTS thấp nhất yêu cầu:  {min(ielts)}\n\n"
        
        if fees:
            content += f"Học phí cao nhất:         ${max(fees):,.2f} USD/năm\n"
            content += f"Học phí thấp nhất:        ${min(fees):,.2f} USD/năm\n"
            content += f"Học phí trung bình:       ${sum(fees)/len(fees):,.2f} USD/năm\n"
        
        text.insert('1.0', content)
        text.config(state='disabled')
        
        # Nút đóng
        ttk.Button(comp_window, text="Đóng", command=comp_window.destroy).pack(pady=10)
    
    def on_close(self):
        """Xử lý khi đóng ứng dụng"""
        self.db.disconnect()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = UniversityComparisonApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
