import sqlite3
import json


class DatabaseHelper:
    """Helper class để làm việc với SQLite database"""
   
    def __init__(self, db_path="universities_db.db"):
        """
        Khởi tạo DatabaseHelper
       
        Args:
            db_path: Đường dẫn đến file database
        """
        self.db_path = db_path
   
    def get_schema_info(self):
        """
        Lấy thông tin schema của database với mô tả chi tiết
       
        Returns:
            str: Mô tả chi tiết về các bảng và cột
        """
        schema_description = """
# DATABASE SCHEMA - HỆ THỐNG QUẢN LÝ TRƯỜNG ĐẠI HỌC


## 1. Bảng: countries (Quốc gia)
Lưu trữ thông tin các quốc gia
**Các cột:**
  - id: INTEGER (PRIMARY KEY) - ID quốc gia
  - code: TEXT (UNIQUE, NOT NULL) - Mã quốc gia (ví dụ: US, UK, VN)
  - name: TEXT (NOT NULL) - Tên quốc gia (ví dụ: United States, Vietnam)
  - flag_url: TEXT - URL hình ảnh cờ quốc gia


## 2. Bảng: universities (Trường đại học)
Lưu trữ thông tin các trường đại học
**Các cột:**
  - id: INTEGER (PRIMARY KEY) - ID trường đại học
  - name: TEXT (NOT NULL) - Tên trường đại học
  - country_id: INTEGER - ID quốc gia (foreign key đến countries.id)
  - state: TEXT - Bang/Tỉnh thành (nếu có)
  - domain: TEXT - Domain của trường (ví dụ: mit.edu)
  - website: TEXT - Website chính thức
  - num_majors: INTEGER - Số lượng ngành học
  - tuition_fee_avg: REAL - Học phí trung bình (USD/năm)
  - entry_requirements: TEXT - Yêu cầu đầu vào (GPA, IELTS, TOEFL, SAT, v.v.)
**Foreign Keys:**
  - country_id → countries(id)


## 3. Bảng: scholarships (Học bổng)
Lưu trữ thông tin các học bổng
**Các cột:**
  - id: INTEGER (PRIMARY KEY) - ID học bổng
  - name: TEXT (NOT NULL) - Tên học bổng
  - university_id: INTEGER - ID trường đại học (foreign key)
  - value: REAL - Giá trị học bổng (USD)
  - duration: TEXT - Thời hạn học bổng (ví dụ: "4 years", "1 year")
  - criteria: TEXT - Điều kiện nhận học bổng
**Foreign Keys:**
  - university_id → universities(id)


## 4. Bảng: user (Người dùng)
Lưu trữ thông tin tài khoản người dùng
**Các cột:**
  - uid: INTEGER (PRIMARY KEY) - ID người dùng
  - email: TEXT (UNIQUE, NOT NULL) - Email đăng nhập
  - password: TEXT (NOT NULL) - Mật khẩu đã hash
  - full_name: TEXT - Họ tên đầy đủ
  - address: TEXT - Địa chỉ
  - phone: TEXT - Số điện thoại
  - is_admin: BOOLEAN - Có phải admin không (0/1)


## 5. Bảng: user_favorites (Danh sách yêu thích)
Liên kết người dùng với trường đại học yêu thích (Many-to-Many)
**Các cột:**
  - id: INTEGER (PRIMARY KEY)
  - user_id: INTEGER (NOT NULL) - ID người dùng
  - university_id: INTEGER (NOT NULL) - ID trường đại học
  - created_at: TIMESTAMP - Thời gian thêm vào yêu thích
**Foreign Keys:**
  - user_id → user(uid)
  - university_id → universities(id)


## QUAN HỆ GIỮA CÁC BẢNG:
- universities.country_id → countries.id (Many-to-One)
- scholarships.university_id → universities.id (Many-to-One)
- user_favorites.user_id → user.uid (Many-to-One)
- user_favorites.university_id → universities.id (Many-to-One)


## LƯU Ý KHI TRUY VẤN:
- Để lấy tên quốc gia: JOIN universities với countries
- Để lấy học bổng: JOIN scholarships với universities
- Học phí (tuition_fee_avg) tính theo USD/năm
- entry_requirements chứa text mô tả yêu cầu (có thể dùng LIKE để tìm kiếm)
"""
        return schema_description
   
    def execute_query(self, sql_query):
        """
        Thực thi câu truy vấn SQL
       
        Args:
            sql_query: Câu lệnh SQL cần thực thi
           
        Returns:
            tuple: (success, data/error_message)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Để trả về kết quả dạng dict
            cursor = conn.cursor()
           
            # Chỉ cho phép SELECT query
            sql_normalized = sql_query.strip().upper()
            if not sql_normalized.startswith('SELECT'):
                return False, "⚠️ Chỉ được phép thực hiện câu lệnh SELECT"
           
            cursor.execute(sql_query)
            rows = cursor.fetchall()
           
            # Convert sang list of dicts
            results = []
            for row in rows:
                results.append(dict(row))
           
            conn.close()
           
            return True, results
           
        except sqlite3.Error as e:
            return False, f"SQL Error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
   
    def get_sample_data(self, table_name, limit=3):
        """
        Lấy dữ liệu mẫu từ một bảng
       
        Args:
            table_name: Tên bảng
            limit: Số lượng records
           
        Returns:
            list: Danh sách các records
        """
        success, data = self.execute_query(f"SELECT * FROM {table_name} LIMIT {limit}")
        if success:
            return data
        return []
   
    def get_statistics(self):
        """
        Lấy thống kê tổng quan về database
       
        Returns:
            dict: Thống kê
        """
        stats = {}
       
        tables = ['countries', 'universities', 'scholarships', 'user']
        for table in tables:
            success, result = self.execute_query(f"SELECT COUNT(*) as count FROM {table}")
            if success and result:
                stats[table] = result[0]['count']
       
        return stats
