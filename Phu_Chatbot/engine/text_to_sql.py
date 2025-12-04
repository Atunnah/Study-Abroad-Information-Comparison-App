import g4f
import json
import re

class TextToSQLEngine:
    """Engine chuyển đổi câu hỏi tự nhiên thành SQL query"""
    
    def __init__(self, db_helper):
        """
        Khởi tạo TextToSQLEngine
        
        Args:
            db_helper: Instance của DatabaseHelper
        """
        self.db_helper = db_helper
        self.client = g4f.Client()
        self.schema_info = db_helper.get_schema_info()
    
    def generate_sql(self, user_question, chat_history=None, data_context=None):
        """
        Tạo câu SQL từ câu hỏi tự nhiên
        
        Args:
            user_question: Câu hỏi của người dùng
            chat_history: Lịch sử chat trước đó (mặc định None)
            
        Returns:
            tuple: (success, sql_query/error_message)
        """
        # 1. Xử lý Chat History (Text context)
        chat_context_str = ""
        if chat_history:
            relevant_history = [msg for msg in chat_history if msg['role'] != 'system'][-10:]
            if relevant_history:
                chat_context_str = "LỊCH SỬ CHAT:\n" + "\n".join([f"- {m['role']}: {m['content']}" for m in relevant_history])

        # 2. Xử lý Data Context (ID Context) - QUAN TRỌNG NHẤT
        data_ids_str = ""
        if data_context and data_context.get('university_ids'):
            ids = ", ".join(data_context['university_ids'])
            data_ids_str = f"""
*** DỮ LIỆU TỪ LẦN TÌM KIẾM TRƯỚC (QUAN TRỌNG) ***
Danh sách ID các trường vừa tìm thấy: [{ids}]
"""

        prompt = f"""Bạn là chuyên gia SQL.

{self.schema_info}

{chat_context_str}

{data_ids_str}

## CÂU HỎI HIỆN TẠI:
"{user_question}"

## QUY TẮC LOGIC QUAN TRỌNG:
1. **ƯU TIÊN TUYỆT ĐỐI**: Nếu người dùng dùng từ chỉ trỏ như "các trường trên", "những trường này", "trong số đó", "bọn chúng"... -> BẮT BUỘC phải dùng mệnh đề:
   `WHERE id IN ({", ".join(data_context['university_ids']) if data_context and data_context.get('university_ids') else "..."})`
   để lọc đúng các trường đã tìm thấy trước đó.

2. Nếu người dùng hỏi tiêu chí cụ thể (ví dụ: "yêu cầu đầu vào", "học phí") cho "các trường trên":
   -> `SELECT name, entry_requirements, tuition_fee_avg FROM universities WHERE id IN (...)`

3. Nếu câu hỏi là tìm kiếm mới hoàn toàn -> Bỏ qua danh sách ID cũ.
## HƯỚNG DẪN TẠO SQL:

### 1. CÁC TRƯỜNG HỢP THƯỜNG GẶP:

**Tìm trường theo quốc gia:**
```sql
SELECT u.*, c.name as country_name 
FROM universities u
JOIN countries c ON u.country_id = c.id
WHERE c.name LIKE '%tên_quốc_gia%'
```

**Tìm theo học phí:**
```sql
SELECT u.name, u.tuition_fee_avg, c.name as country_name
FROM universities u
JOIN countries c ON u.country_id = c.id
WHERE u.tuition_fee_avg < giá_trị
ORDER BY u.tuition_fee_avg ASC
```

**Tìm theo yêu cầu đầu vào (IELTS, GPA, TOEFL):**
```sql
SELECT u.name, u.entry_requirements, c.name as country_name
FROM universities u
JOIN countries c ON u.country_id = c.id
WHERE u.entry_requirements LIKE '%IELTS%' OR u.entry_requirements LIKE '%GPA%'
```

**Tìm học bổng:**
```sql
SELECT s.name, s.value, s.criteria, u.name as university_name
FROM scholarships s
JOIN universities u ON s.university_id = u.id
WHERE s.value > giá_trị
ORDER BY s.value DESC
```

**Thống kê số lượng:**
```sql
SELECT c.name, COUNT(u.id) as total_universities
FROM countries c
LEFT JOIN universities u ON c.id = u.country_id
GROUP BY c.id
ORDER BY total_universities DESC
```

### 2. QUY TẮC BẮT BUỘC:
- Chỉ tạo câu SELECT, KHÔNG dùng INSERT/UPDATE/DELETE
- LUÔN JOIN với bảng countries để lấy tên quốc gia
- Dùng LIKE '%...%' cho tìm kiếm text (tên trường, quốc gia, yêu cầu)
- Dùng toán tử số (<, >, =, BETWEEN) cho học phí, giá trị học bổng
- LIMIT kết quả nếu có thể có nhiều records (thường LIMIT 20)
- Sử dụng alias (u, c, s) để code ngắn gọn

### 3. XỬ LÝ CÁC TỪ KHÓA:
- "tìm", "liệt kê", "những trường nào" → SELECT với WHERE
- "có bao nhiêu", "số lượng" → COUNT(*)
- "rẻ nhất", "thấp nhất" → ORDER BY ASC LIMIT 1
- "đắt nhất", "cao nhất" → ORDER BY DESC LIMIT 1
- "so sánh" → SELECT với WHERE name IN (...)
- "trung bình" → AVG()

### 4. XỬ LÝ TÊN QUỐC GIA (quan trọng):
- "Mỹ" → "United States" hoặc LIKE '%United%' hoặc LIKE '%States%'
- "Anh" → "United Kingdom" hoặc LIKE '%Kingdom%'
- "Úc" → "Australia"
- "Canada" → "Canada"
- "Singapore" → "Singapore"
- Dùng LIKE để flexible hơn

## CÂU HỎI CỦA NGƯỜI DÙNG:
{user_question}

## TRẢ LỜI (chỉ JSON, không thêm markdown hay text khác):
{{
    "sql": "SELECT câu SQL của bạn ở đây",
    "explanation": "Giải thích ngắn gọn câu SQL làm gì"
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1  # Giảm nhiệt độ để có kết quả ổn định hơn
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Xử lý kết quả để lấy JSON
            # Loại bỏ markdown code blocks nếu có
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            result_text = result_text.strip()
            
            # Parse JSON
            result = json.loads(result_text)
            
            if "sql" not in result:
                return False, "❌ Không thể tạo câu SQL từ câu hỏi này"
            
            # Validate SQL
            sql_query = result['sql'].strip()
            if not sql_query.upper().startswith('SELECT'):
                return False, "❌ Chỉ hỗ trợ truy vấn SELECT"
            
            return True, result
            
        except json.JSONDecodeError as e:
            return False, f"❌ Lỗi parse JSON: {str(e)}"
        except Exception as e:
            return False, f"❌ Lỗi khi tạo SQL: {str(e)}"
