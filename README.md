🎓 Chatbot Tư Vấn & So Sánh Đại Học Quốc Tế
Ứng dụng Tkinter + g4f + Python

Ứng dụng này cung cấp một chatbot giao diện đồ họa (GUI) giúp người dùng tra cứu và so sánh các thông tin du học giữa các trường đại học quốc tế.

Chatbot được xây dựng bằng Tkinter, sử dụng API miễn phí từ g4f (GPT-4o-mini), hỗ trợ phản hồi dạng streaming, nhanh và mượt.

📌 Tính năng chính
🔍 Tư vấn du học theo yêu cầu

Chatbot trả lời nhất quán theo cấu trúc:

GPA tối thiểu

Yêu cầu IELTS/TOEFL

Học phí trung bình mỗi năm

Cơ hội học bổng

Vị trí & ngành mạnh

📊 So sánh nhiều trường

Khi người dùng yêu cầu, chatbot tự động tạo:

Bảng so sánh

Danh sách rõ ràng

Thông tin ngắn gọn, dễ đọc

⚡ Streaming Real-time

Phản hồi được đẩy ra từng phần, giống ChatGPT thật:

Hiển thị mượt

Không bị đơ UI

Dùng Threading để tránh treo giao diện

🧩 Cấu trúc project rõ ràng

Tách thành nhiều file:

app.py – file chạy chính

ui.py – giao diện Tkinter

chatlogic.py – xử lý API & stream

config.py – chứa system prompt + lịch sử chat

📁 Cấu trúc thư mục
duhoc_chatbot/
│
├── app.py          # Điểm khởi chạy ứng dụng
├── ui.py           # Giao diện Tkinter
├── chatlogic.py    # Logic gọi API + streaming
├── config.py       # Prompt hệ thống & lịch sử hội thoại
└── README.md       # Tài liệu hướng dẫn

🛠️ Cài đặt
1. Cài Python (3.8+)

Nếu chưa có Python:
https://www.python.org/downloads/

2. Cài thư viện cần thiết
pip install g4f


⚠️ Tkinter thường có sẵn trong Python trên Windows & Linux.
Nếu không có, bạn phải cài thêm (tùy OS).

🚀 Chạy ứng dụng

Trong thư mục project:

python app.py

🧠 Công nghệ sử dụng

Python 3

Tkinter cho giao diện GUI

g4f (GPT-4o-mini) để gọi mô hình AI

Threading để xử lý streaming không khóa UI

📝 Mô tả hoạt động

Người dùng nhập câu hỏi vào ô input

Giao diện gửi câu hỏi cho chatlogic.send_message()

Hàm ask_g4f_stream() tạo request đến g4f và stream kết quả

Nội dung được đổ ra ScrolledText theo thời gian thực

Lịch sử hội thoại được lưu vào chat_history

📦 Dễ mở rộng

Bạn có thể:

Đổi theme giao diện (dark mode)

Kết nối API trả phí của OpenAI

Xuất lịch sử chat ra file

Tích hợp thêm giọng nói (speech-to-text)

Đóng gói thành file .exe bằng PyInstaller

📄 License

Bạn được phép sử dụng, chỉnh sửa, hoặc tích hợp vào dự án cá nhân/đồ án.