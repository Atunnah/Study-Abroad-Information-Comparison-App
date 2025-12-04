import g4f

import json
import tkinter as tk
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

   

    def generate_sql(self, user_question):

        """

        Tạo câu SQL từ câu hỏi tự nhiên

       

        Args:

            user_question: Câu hỏi của người dùng

           

        Returns:

            tuple: (success, sql_query/error_message)

        """

        prompt = f"""Bạn là chuyên gia SQL cho hệ thống quản lý trường đại học. Chuyển câu hỏi thành SQL query.





{self.schema_info}





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

