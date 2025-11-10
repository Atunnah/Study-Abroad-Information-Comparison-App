from database import Database

class UniversityCRUD:
    """Class xử lý các thao tác CRUD cho bảng Universities"""
    
    def __init__(self, db):
        self.db = db
    
    def create(self, university_data):
        """Thêm trường đại học mới"""
        query = """
            INSERT INTO universities (university_name, country, city, ranking, website, established_year)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            university_data['university_name'],
            university_data['country'],
            university_data['city'],
            university_data.get('ranking'),
            university_data.get('website'),
            university_data.get('established_year')
        )
        return self.db.execute_query(query, params)
    
    def read_all(self):
        """Lấy tất cả trường đại học"""
        query = "SELECT * FROM universities ORDER BY ranking"
        return self.db.fetch_all(query)
    
    def read_by_id(self, university_id):
        """Lấy thông tin trường đại học theo ID"""
        query = "SELECT * FROM universities WHERE id = %s"
        return self.db.fetch_one(query, (university_id,))
    
    def update(self, university_id, university_data):
        """Cập nhật thông tin trường đại học"""
        query = """
            UPDATE universities 
            SET university_name = %s, country = %s, city = %s, 
                ranking = %s, website = %s, established_year = %s
            WHERE id = %s
        """
        params = (
            university_data['university_name'],
            university_data['country'],
            university_data['city'],
            university_data.get('ranking'),
            university_data.get('website'),
            university_data.get('established_year'),
            university_id
        )
        return self.db.execute_query(query, params)
    
    def delete(self, university_id):
        """Xóa trường đại học"""
        query = "DELETE FROM universities WHERE id = %s"
        return self.db.execute_query(query, (university_id,))
    
    def search(self, keyword):
        """Tìm kiếm trường đại học theo tên hoặc quốc gia"""
        query = """
            SELECT * FROM universities 
            WHERE university_name LIKE %s OR country LIKE %s OR city LIKE %s
            ORDER BY ranking
        """
        search_term = f"%{keyword}%"
        return self.db.fetch_all(query, (search_term, search_term, search_term))


class AdmissionRequirementCRUD:
    """Class xử lý các thao tác CRUD cho bảng Admission Requirements"""
    
    def __init__(self, db):
        self.db = db
    
    def create(self, requirement_data):
        """Thêm yêu cầu đầu vào mới"""
        query = """
            INSERT INTO admission_requirements 
            (university_id, program_name, degree_level, min_gpa, min_ielts, 
             min_toefl, min_sat, min_gre, tuition_fee_usd, application_deadline, 
             additional_requirements)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            requirement_data['university_id'],
            requirement_data['program_name'],
            requirement_data['degree_level'],
            requirement_data.get('min_gpa'),
            requirement_data.get('min_ielts'),
            requirement_data.get('min_toefl'),
            requirement_data.get('min_sat'),
            requirement_data.get('min_gre'),
            requirement_data.get('tuition_fee_usd'),
            requirement_data.get('application_deadline'),
            requirement_data.get('additional_requirements')
        )
        return self.db.execute_query(query, params)
    
    def read_all(self):
        """Lấy tất cả yêu cầu đầu vào"""
        query = """
            SELECT ar.*, u.university_name, u.country 
            FROM admission_requirements ar
            JOIN universities u ON ar.university_id = u.id
            ORDER BY u.university_name
        """
        return self.db.fetch_all(query)
    
    def read_by_university(self, university_id):
        """Lấy yêu cầu đầu vào theo trường đại học"""
        query = """
            SELECT ar.*, u.university_name, u.country 
            FROM admission_requirements ar
            JOIN universities u ON ar.university_id = u.id
            WHERE ar.university_id = %s
        """
        return self.db.fetch_all(query, (university_id,))
    
    def read_by_id(self, requirement_id):
        """Lấy yêu cầu đầu vào theo ID"""
        query = """
            SELECT ar.*, u.university_name, u.country 
            FROM admission_requirements ar
            JOIN universities u ON ar.university_id = u.id
            WHERE ar.id = %s
        """
        return self.db.fetch_one(query, (requirement_id,))
    
    def update(self, requirement_id, requirement_data):
        """Cập nhật yêu cầu đầu vào"""
        query = """
            UPDATE admission_requirements 
            SET university_id = %s, program_name = %s, degree_level = %s,
                min_gpa = %s, min_ielts = %s, min_toefl = %s, min_sat = %s,
                min_gre = %s, tuition_fee_usd = %s, application_deadline = %s,
                additional_requirements = %s
            WHERE id = %s
        """
        params = (
            requirement_data['university_id'],
            requirement_data['program_name'],
            requirement_data['degree_level'],
            requirement_data.get('min_gpa'),
            requirement_data.get('min_ielts'),
            requirement_data.get('min_toefl'),
            requirement_data.get('min_sat'),
            requirement_data.get('min_gre'),
            requirement_data.get('tuition_fee_usd'),
            requirement_data.get('application_deadline'),
            requirement_data.get('additional_requirements'),
            requirement_id
        )
        return self.db.execute_query(query, params)
    
    def delete(self, requirement_id):
        """Xóa yêu cầu đầu vào"""
        query = "DELETE FROM admission_requirements WHERE id = %s"
        return self.db.execute_query(query, (requirement_id,))
    
    def search_by_program(self, program_name):
        """Tìm kiếm theo tên chương trình"""
        query = """
            SELECT ar.*, u.university_name, u.country 
            FROM admission_requirements ar
            JOIN universities u ON ar.university_id = u.id
            WHERE ar.program_name LIKE %s
            ORDER BY u.university_name
        """
        return self.db.fetch_all(query, (f"%{program_name}%",))
    
    def compare_programs(self, program_ids):
        """So sánh các chương trình đầu vào"""
        if not program_ids:
            return []
        
        placeholders = ','.join(['%s'] * len(program_ids))
        query = f"""
            SELECT ar.*, u.university_name, u.country, u.ranking
            FROM admission_requirements ar
            JOIN universities u ON ar.university_id = u.id
            WHERE ar.id IN ({placeholders})
            ORDER BY u.ranking
        """
        return self.db.fetch_all(query, tuple(program_ids))
