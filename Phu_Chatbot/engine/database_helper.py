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
        self._init_chat_tables() # Tự động tạo bảng chat khi khởi tạo

    def _init_chat_tables(self):
        """Tạo bảng lưu lịch sử chat nếu chưa có"""
        sql_sessions = """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        sql_messages = """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
        )
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(sql_sessions)
            cursor.execute(sql_messages)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Init DB Error: {e}")

    # ================= CÁC HÀM XỬ LÝ LỊCH SỬ CHAT (MỚI) =================

    def save_session(self, session_id, user_id, title):
        """Lưu hoặc cập nhật thông tin session"""
        sql = "INSERT OR REPLACE INTO chat_sessions (session_id, user_id, title) VALUES (?, ?, ?)"
        self._execute_non_query(sql, (session_id, user_id, title))

    def save_message(self, session_id, role, content):
        """Lưu tin nhắn mới"""
        sql = "INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)"
        self._execute_non_query(sql, (session_id, role, content))

    def get_user_sessions(self, user_id):
        """Lấy danh sách các đoạn chat của user"""
        sql = "SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC"
        success, data = self.execute_query(sql, (user_id,))
        return data if success else []

    def get_session_history(self, session_id):
        """Lấy toàn bộ tin nhắn của một session"""
        sql = "SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY id ASC"
        success, data = self.execute_query(sql, (session_id,))
        return data if success else []

    def delete_session(self, session_id):
        """Xóa session và tin nhắn liên quan"""
        sql = "DELETE FROM chat_sessions WHERE session_id = ?"
        self._execute_non_query(sql, (session_id,))

    def _execute_non_query(self, sql, params=()):
        """Hàm nội bộ để thực thi INSERT, UPDATE, DELETE"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False

    # ================= CÁC HÀM CŨ (CÓ CẬP NHẬT) =================

    def get_schema_info(self):
        """
        Lấy thông tin schema của database với mô tả chi tiết
        """
        schema_description = """
# DATABASE SCHEMA - HỆ THỐNG QUẢN LÝ TRƯỜNG ĐẠI HỌC

## 1. Bảng: countries (Quốc gia)
... (Giữ nguyên nội dung mô tả cũ của bạn ở đây) ...
"""
        # Lưu ý: Tôi đã rút gọn phần string schema để code ngắn gọn, 
        # bạn hãy giữ nguyên phần schema_description cũ của bạn nhé.
        return schema_description
   
    def execute_query(self, sql_query, params=()):
        """
        Thực thi câu truy vấn SQL (Cho phép truyền params)
       
        Args:
            sql_query: Câu lệnh SQL
            params: Tuple chứa các tham số (để tránh SQL Injection)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Để trả về kết quả dạng dict
            cursor = conn.cursor()
           
            # Kiểm tra bảo mật cơ bản (chỉ áp dụng cho câu lệnh text thuần từ AI)
            # Nếu có params truyền vào thì thường là query nội bộ an toàn
            if not params:
                sql_normalized = sql_query.strip().upper()
                if not sql_normalized.startswith('SELECT'):
                    return False, "⚠️ Chỉ được phép thực hiện câu lệnh SELECT"
           
            cursor.execute(sql_query, params)
            rows = cursor.fetchall()
           
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
        """Lấy dữ liệu mẫu từ một bảng"""
        success, data = self.execute_query(f"SELECT * FROM {table_name} LIMIT {limit}")
        if success:
            return data
        return []
   
    def get_statistics(self):
        """Lấy thống kê tổng quan về database"""
        stats = {}
        tables = ['countries', 'universities', 'scholarships', 'user']
        for table in tables:
            success, result = self.execute_query(f"SELECT COUNT(*) as count FROM {table}")
            if success and result:
                stats[table] = result[0]['count']
       
        return stats