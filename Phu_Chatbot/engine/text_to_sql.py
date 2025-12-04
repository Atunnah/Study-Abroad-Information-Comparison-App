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
        
        valid_countries_str = self.db_helper.get_all_country_names()
        history_str = ""
        if chat_history:
            recent_msgs = chat_history[-30:]
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
- code (TEXT): Mã quốc gia (VD: 'US', 'VN', 'UK')
- name (TEXT): Tên tiếng Anh (VD: 'United States', 'Vietnam')
- flag_url (TEXT)

Table: universities
- id (PK)
- name (TEXT): Tên trường
- country_id (FK): Link to countries.id
- state (TEXT): Bang/Tỉnh
- domain (TEXT), website (TEXT)
- num_majors (INTEGER): Số lượng ngành
- tuition_fee_avg (REAL): Học phí trung bình (USD/năm).
- entry_requirements (TEXT): Chứa thông tin tổng hợp, được chia làm 3 loại chính:
    1. **Language:** IELTS, TOEFL, ESL, Conditional, Foundation...
    2. **Academic:** GPA, SAT, GMAT, GRE, Bachelor degree...
    3. **Extra:** Essay, Recommendation Letter, Interview...
    **LƯU Ý VỀ CỘT `entry_requirements`:**
Đây là cột chứa văn bản hỗn hợp (Unstructured Text), bao gồm 3 nhóm thông tin:
1. **Language:** IELTS, TOEFL, ESL...
2. **Academic:** GPA, SAT, Bachelor degree...
3. **Extra (Rất đa dạng):** Portfolio, Interview, Work Experience, GMAT, GRE, Reference Letter, Essay, Personal Statement...


Table: scholarships
- id (PK)
- name (TEXT): Tên học bổng
- university_id (FK): Link to universities.id
- value (REAL): Giá trị (USD)
- duration (TEXT), criteria (TEXT)

Table: user_favorites (Bảng phụ - Danh sách yêu thích)
- user_id, university_id

Table: user (Thông tin user)
- uid, email, full_name...
"""

        # --- 3. QUY TẮC NGHIỆP VỤ ---
        rules = """
### 2. QUY TẮC NGHIỆP VỤ (BẮT BUỘC TUÂN THỦ):

1. **Nhận diện Quốc Gia (Dynamic Mapping):**
   - Danh sách quốc gia HỢP LỆ trong Database: [{valid_countries_str}].
   - Nhiệm vụ của bạn: Nếu User hỏi tên quốc gia bằng tiếng Việt (ví dụ: "Pháp", "Đức", "Hàn"), hãy tự dịch sang tiếng Anh và tìm tên **gần giống nhất** trong danh sách trên để đưa vào câu lệnh SQL.
   - Ví dụ: User nói "Pháp" -> Tìm trong danh sách thấy "France" -> SQL: `c.name LIKE '%France%'`.
   
2. **VỚI CỘT `entry_requirements` (Yêu cầu đầu vào/Tiếng Anh):**
   - **TUYỆT ĐỐI KHÔNG DÙNG TRONG MỆNH ĐỀ `WHERE`**.
   - **BẮT BUỘC PHẢI `SELECT` CỘT NÀY RA**.
   - Lý do: Logic so sánh tiếng Anh/GPA rất phức tạp, hãy để AI xử lý sau. SQL chỉ cần lấy dữ liệu thô.

3. **Xử lý "Ranking" / "Trường top":**
   - Database KHÔNG CÓ cột ranking. 
   - Nếu user hỏi "top", "hàng đầu" -> Chỉ cần sắp xếp theo học phí cao (`ORDER BY tuition_fee_avg DESC`) hoặc lấy ngẫu nhiên `LIMIT 5`, KHÔNG được bịa cột ranking.

4. **Xử lý "Thạc sĩ" (Master):**
   - Database KHÔNG phân loại bậc học. Mặc định coi tất cả là trường phù hợp. KHÔNG filter cột `master`.

5. **Ngữ cảnh (Context):**
   - Nếu câu hỏi thiếu chủ ngữ (VD: "Còn ở Anh thì sao?", "Giá bao nhiêu?"), hãy nhìn vào LỊCH SỬ CHAT để biết người dùng đang tìm Trường hay Học bổng và áp dụng các điều kiện cũ (nếu có).
   - Luôn kết hợp điều kiện từ LỊCH SỬ CHAT.

6. **Sắp xếp:** Luôn ưu tiên sắp xếp theo học phí (`ORDER BY tuition_fee_avg ASC`) nếu user tìm trường rẻ.
"""

        # --- 4. VÍ DỤ MẪU ---
        examples = """

### 3. VÍ DỤ MẪU:

User: "Tìm trường ở Pháp giá rẻ chưa cần tiếng anh"
Thinking: 
- Lọc Quốc gia = France. 
- Lọc Giá rẻ = ORDER BY tuition_fee_avg ASC.
- "Chưa cần tiếng anh" -> Bỏ qua điều kiện này trong WHERE, nhưng phải SELECT cột entry_requirements để check sau.
SQL:
```sql
SELECT u.name, u.tuition_fee_avg, u.entry_requirements, c.name as country_name
FROM universities u
JOIN countries c ON u.country_id = c.id
WHERE c.name LIKE '%France%'
ORDER BY u.tuition_fee_avg ASC
LIMIT 15;
"""
        # --- 5. GHÉP PROMPT ---
        full_prompt = f"""Bạn là chuyên gia SQL.
        {schema_context} {rules} {examples}
LỊCH SỬ CHAT (Context): {history_str}
CÂU HỎI HIỆN TẠI: "{user_question}"
Yêu cầu:

Phân tích Lịch sử chat để hiểu ngữ cảnh.

KHÔNG trả lời bằng lời văn.

Chỉ trả về JSON format: {{ "sql": "...", "explanation": "..." }}

JSON OUTPUT:"""
        try:
            # Gọi AI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.1 # Nhiệt độ thấp để code chính xác
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean JSON
            result_text = re.sub(r'```json\s*|\s*```', '', result_text).strip()
            result_text = re.sub(r'```sql\s*|\s*```', '', result_text).strip()
            
            # Fallback: Nếu AI trả về text không phải JSON nhưng có chứ SELECT
            if not result_text.strip().startswith("{") and "SELECT" in result_text.upper():
                sql_match = re.search(r'SELECT.*', result_text, re.DOTALL | re.IGNORECASE)
                if sql_match:
                    return True, {"sql": sql_match.group(0), "explanation": "Generated from raw text"}

            # Parse JSON
            result = json.loads(result_text)
            
            if "sql" not in result:
                return False, "AI không trả về key 'sql' trong JSON."
            
            # Validate an toàn
            sql = result['sql'].strip()
            if not sql.upper().startswith("SELECT"):
                return False, "Chỉ cho phép câu lệnh SELECT."
                
            return True, result

        except json.JSONDecodeError:
            print(f"[TextToSQL Error] Invalid JSON: {result_text}")
            return False, "Lỗi đọc dữ liệu JSON từ AI."
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
