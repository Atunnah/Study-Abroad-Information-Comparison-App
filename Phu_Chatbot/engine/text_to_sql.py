import g4f
import json
import re

class TextToSQLEngine:
    """Engine chuyển đổi câu hỏi tự nhiên thành SQL query (Đã tối ưu Prompt cho Schema cụ thể + Ngữ cảnh)"""

    def __init__(self, db_helper):
        self.db_helper = db_helper
        self.client = g4f.Client()

    def generate_sql(self, user_question, chat_history=[]):
        """
        Tạo câu SQL từ câu hỏi tự nhiên, có sử dụng lịch sử chat để hiểu ngữ cảnh.
        """
        
        # --- 1. XỬ LÝ LỊCH SỬ CHAT ---
        # Lấy 6 tin nhắn gần nhất (trừ system) để làm ngữ cảnh
        history_str = ""
        if chat_history:
            recent_msgs = chat_history[-6:]
            for msg in recent_msgs:
                role = "User" if msg['role'] == 'user' else "AI"
                content = msg['content']
                if msg['role'] != 'system':
                    history_str += f"{role}: {content}\n"

        # --- 2. ĐỊNH NGHĨA SCHEMA ---
        schema_context = """
### 1. DATABASE SCHEMA (SQLite):

Table: countries
- id (PK)
- name (TEXT): Tên tiếng Anh (VD: 'United States', 'United Kingdom', 'Vietnam', 'Australia')
- code (TEXT): Mã quốc gia (VD: 'US', 'UK', 'VN')

Table: universities
- id (PK)
- name (TEXT): Tên trường
- country_id (FK): Liên kết countries.id
- tuition_fee_avg (REAL): Học phí trung bình (USD/năm)
- entry_requirements (TEXT): Yêu cầu đầu vào (VD: 'IELTS 6.5, GPA 3.0')
- num_majors (INTEGER): Số lượng ngành

Table: scholarships
- id (PK)
- name (TEXT): Tên học bổng
- university_id (FK): Liên kết universities.id
- value (REAL): Giá trị (USD)
- criteria (TEXT): Điều kiện

Table: user (Thông tin người dùng - Thường không dùng cho tra cứu trường học)
- uid, email, full_name...
"""

        # --- 3. QUY TẮC NGHIỆP VỤ ---
        rules = """
### 2. QUY TẮC QUAN TRỌNG:
1. **Mapping Quốc Gia:** - "Mỹ" -> LIKE '%United States%'
   - "Anh" -> LIKE '%United Kingdom%'
   - "Úc" -> LIKE '%Australia%'
   - "Hàn" -> LIKE '%Korea%'
   - "Nhật" -> LIKE '%Japan%'
   
2. **Quy tắc JOIN:**
   - Tìm trường theo quốc gia: `universities` JOIN `countries`
   - Tìm học bổng theo quốc gia: `scholarships` JOIN `universities` JOIN `countries`

3. **Lọc dữ liệu:**
   - So sánh học phí/học bổng: Dùng <, >, = (VD: tuition_fee_avg < 20000)
   - Tìm theo yêu cầu (IELTS/GPA): Dùng LIKE (VD: entry_requirements LIKE '%IELTS 6.0%')
   
4. **Ngữ cảnh:** - Nếu câu hỏi thiếu chủ ngữ (VD: "Còn ở Anh thì sao?"), hãy nhìn vào LỊCH SỬ CHAT để biết người dùng đang tìm Trường hay Học bổng.
"""

        # --- 4. VÍ DỤ MẪU ---
        examples = """
### 3. VÍ DỤ MẪU:

User: "Tìm các trường ở Mỹ có học phí dưới 25000"
SQL:
```sql
SELECT u.name, u.tuition_fee_avg, c.name as country_name
FROM universities u
JOIN countries c ON u.country_id = c.id
WHERE c.name LIKE '%United States%' AND u.tuition_fee_avg < 25000
LIMIT 10;
User: "Có những học bổng nào tại Úc giá trị trên 5000?" SQL:
SELECT s.name, s.value, u.name as uni_name
FROM scholarships s
JOIN universities u ON s.university_id = u.id
JOIN countries c ON u.country_id = c.id
WHERE c.name LIKE '%Australia%' AND s.value > 5000
LIMIT 10;
User: "Liệt kê các trường yêu cầu IELTS 6.5" SQL:
SELECT name, entry_requirements
FROM universities
WHERE entry_requirements LIKE '%IELTS%' AND entry_requirements LIKE '%6.5%'
LIMIT 10;
"""
        # --- 5. GHÉP PROMPT ---
        full_prompt = f"""Bạn là chuyên gia SQL.
        {schema_context} {rules} {examples}
LỊCH SỬ CHAT (Context): {history_str}
CÂU HỎI USER: "{user_question}"
Yêu cầu:

Dựa vào Lịch sử chat để hiểu rõ câu hỏi nếu nó không đầy đủ.

Chỉ trả về JSON format: {{ "sql": "...", "explanation": "..." }}

JSON OUTPUT:"""
        try:
            # Gọi AI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.1 # Quan trọng: Nhiệt độ thấp để code chính xác
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean JSON (xóa markdown ```json)
            result_text = re.sub(r'```json\s*|\s*```', '', result_text).strip()
            
            # Parse
            result = json.loads(result_text)
            
            if "sql" not in result:
                return False, "AI không trả về SQL."
            
            # Validate an toàn
            sql = result['sql'].strip()
            if not sql.upper().startswith("SELECT"):
                return False, "Chỉ cho phép câu lệnh SELECT."
                
            return True, result

        except json.JSONDecodeError:
            return False, "Lỗi đọc JSON từ AI."
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
