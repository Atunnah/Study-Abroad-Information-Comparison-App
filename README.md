# Ứng dụng So sánh Thông tin Đầu vào Trường Đại học

Ứng dụng desktop được xây dựng bằng Python Tkinter để quản lý và so sánh thông tin đầu vào của các trường đại học nước ngoài.

## Tính năng

### 1. Quản lý Trường Đại học
- ✅ Thêm, sửa, xóa thông tin trường đại học
- ✅ Tìm kiếm trường theo tên, quốc gia, thành phố
- ✅ Hiển thị danh sách tất cả trường đại học
- ✅ Lưu trữ thông tin: tên trường, quốc gia, thành phố, xếp hạng, website, năm thành lập

### 2. Quản lý Yêu cầu Đầu vào
- ✅ Thêm, sửa, xóa yêu cầu đầu vào của các chương trình
- ✅ Tìm kiếm theo tên chương trình
- ✅ Quản lý thông tin: chương trình, bậc học, điểm GPA, IELTS, TOEFL, SAT, GRE, học phí, deadline
- ✅ Yêu cầu bổ sung cho từng chương trình

### 3. So sánh Chương trình
- ✅ Chọn nhiều chương trình để so sánh
- ✅ Hiển thị chi tiết yêu cầu đầu vào của từng chương trình
- ✅ Phân tích thống kê: GPA, IELTS, học phí cao nhất/thấp nhất/trung bình
- ✅ Sắp xếp theo thứ hạng trường

## Yêu cầu Hệ thống

- Python 3.7 trở lên
- MySQL Server 5.7 trở lên
- Windows/Linux/MacOS

## Cài đặt

### Bước 1: Cài đặt Python packages
```bash
pip install -r requirements.txt
```

### Bước 2: Cài đặt MySQL
1. Tải và cài đặt MySQL Server từ: https://dev.mysql.com/downloads/mysql/
2. Khởi động MySQL Server
3. Tạo user và password (hoặc sử dụng root)

### Bước 3: Tạo Database
1. Mở MySQL Workbench hoặc command line
2. Chạy script SQL từ file `database_schema.sql`:

**Cách 1: Sử dụng MySQL Workbench**
- Mở MySQL Workbench
- File → Open SQL Script → Chọn file `database_schema.sql`
- Nhấn nút Execute (⚡)

**Cách 2: Sử dụng Command Line**
```bash
mysql -u root -p < database_schema.sql
```

### Bước 4: Cấu hình kết nối Database
Mở file `config.py` và chỉnh sửa thông tin kết nối:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',           # Thay bằng username của bạn
    'password': 'your_password',  # Thay bằng password của bạn
    'database': 'university_comparison'
}
```

## Chạy ứng dụng

```bash
python main.py
```

## Cấu trúc Project

```
final_project/
│
├── main.py                    # File chính chạy ứng dụng
├── database.py                # Module quản lý kết nối database
├── crud_operations.py         # Module xử lý CRUD operations
├── config.py                  # File cấu hình
├── database_schema.sql        # Script tạo database và dữ liệu mẫu
├── requirements.txt           # Danh sách thư viện cần thiết
└── README.md                  # Hướng dẫn sử dụng
```

## Thiết kế Database

### Bảng `universities`
Lưu trữ thông tin các trường đại học:
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `university_name` (VARCHAR 255)
- `country` (VARCHAR 100)
- `city` (VARCHAR 100)
- `ranking` (INT)
- `website` (VARCHAR 255)
- `established_year` (INT)
- `created_at`, `updated_at` (TIMESTAMP)

### Bảng `admission_requirements`
Lưu trữ yêu cầu đầu vào:
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `university_id` (INT, FOREIGN KEY)
- `program_name` (VARCHAR 255)
- `degree_level` (ENUM: Bachelor, Master, PhD, Diploma)
- `min_gpa` (DECIMAL 3,2)
- `min_ielts` (DECIMAL 3,1)
- `min_toefl` (INT)
- `min_sat` (INT)
- `min_gre` (INT)
- `tuition_fee_usd` (DECIMAL 10,2)
- `application_deadline` (DATE)
- `additional_requirements` (TEXT)
- `created_at`, `updated_at` (TIMESTAMP)

## Hướng dẫn Sử dụng

### 1. Tab Quản lý Trường Đại học
1. **Thêm trường mới:**
   - Nhập thông tin vào các trường
   - Nhấn nút "Thêm"

2. **Cập nhật trường:**
   - Double-click vào dòng cần sửa trong bảng
   - Chỉnh sửa thông tin
   - Nhấn nút "Cập nhật"

3. **Xóa trường:**
   - Click chọn dòng cần xóa
   - Nhấn nút "Xóa"
   - Xác nhận xóa

4. **Tìm kiếm:**
   - Nhập từ khóa vào ô tìm kiếm
   - Nhấn nút "Tìm"

### 2. Tab Quản lý Yêu cầu Đầu vào
1. **Thêm yêu cầu mới:**
   - Chọn trường từ dropdown
   - Nhập thông tin chương trình
   - Nhập các yêu cầu (GPA, IELTS, TOEFL, SAT, GRE)
   - Nhập học phí và deadline (định dạng: YYYY-MM-DD)
   - Nhấn nút "Thêm"

2. **Cập nhật/Xóa:**
   - Tương tự như tab Quản lý Trường

### 3. Tab So sánh Chương trình
1. Click vào checkbox (☐) bên trái để chọn chương trình
2. Chọn ít nhất 2 chương trình
3. Nhấn nút "So sánh"
4. Xem kết quả so sánh chi tiết trong cửa sổ mới

## Dữ liệu Mẫu

Ứng dụng đã được tích hợp sẵn dữ liệu mẫu của 8 trường đại học hàng đầu:
- Harvard University (USA)
- Stanford University (USA)
- University of Oxford (UK)
- University of Cambridge (UK)
- MIT (USA)
- National University of Singapore (Singapore)
- University of Toronto (Canada)
- University of Melbourne (Australia)

Với 11 chương trình đào tạo ở các bậc học khác nhau.

## Xử lý Lỗi Thường gặp

### Lỗi: "Không thể kết nối database"
- Kiểm tra MySQL Server đã chạy chưa
- Kiểm tra thông tin trong `config.py` (user, password, host)
- Đảm bảo database `university_comparison` đã được tạo

### Lỗi: "Import mysql.connector could not be resolved"
- Chạy: `pip install mysql-connector-python`

### Lỗi: "Table doesn't exist"
- Chạy lại script `database_schema.sql` để tạo các bảng

## Tác giả

Project được phát triển bởi GitHub Copilot

## License

MIT License
