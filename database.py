import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class Database:
    """Class quản lý kết nối và thao tác với database"""
    
    def __init__(self):
        self.connection = None
        
    def connect(self):
        """Tạo kết nối đến MySQL database"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                print("Kết nối database thành công!")
                return True
        except Error as e:
            print(f"Lỗi kết nối database: {e}")
            return False
    
    def disconnect(self):
        """Đóng kết nối database"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Đã đóng kết nối database")
    
    def execute_query(self, query, params=None):
        """Thực thi query (INSERT, UPDATE, DELETE)"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return True
        except Error as e:
            print(f"Lỗi thực thi query: {e}")
            return False
        finally:
            cursor.close()
    
    def fetch_all(self, query, params=None):
        """Lấy tất cả dữ liệu từ query"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Lỗi fetch data: {e}")
            return []
        finally:
            cursor.close()
    
    def fetch_one(self, query, params=None):
        """Lấy một dòng dữ liệu từ query"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Lỗi fetch data: {e}")
            return None
        finally:
            cursor.close()
