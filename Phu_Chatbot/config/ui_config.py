class ChatbotConfig:
    # Colors - General
    BACKGROUND = "#f5f5f5"
    HEADER_BG = "#2c3e50"
    HEADER_FG = "white"
    CHAT_BG = "white"
    
    # Text Colors (Thêm lại phần này)
    TEXT_PRIMARY = "#2c3e50"    # Màu chữ chính (Dùng cho chatbot)
    TEXT_SECONDARY = "#34495e"  # Màu chữ phụ
    
    # User Bubbles (Right side)
    USER_BG = "#3498db" # Xanh dương
    USER_FG = "white"   # Đổi thành trắng cho dễ đọc trên nền xanh
    
    # Assistant Bubbles (Left side)
    ASSISTANT_BG = "#ecf0f1" # Xám nhạt
    ASSISTANT_FG = "#2c3e50"
    
    # Status Colors
    ERROR_COLOR = "#e74c3c"
    STATUS_COLOR = "#7f8c8d"
    
    # Buttons
    BUTTON_BG = "#3498db"
    BUTTON_FG = "white"
    BUTTON_ACTIVE = "#2980b9"
    BUTTON_CANCEL = "#e74c3c" # Màu đỏ cho nút hủy
    BUTTON_DISABLED = "#95a5a6"
    
    # Fonts
    FONT_HEADER_TITLE = ("Arial", 16, "bold")
    FONT_HEADER_SUB = ("Arial", 10)
    FONT_TEXT = ("Segoe UI", 11)
    FONT_TEXT_BOLD = ("Segoe UI", 11, "bold")
    FONT_BUTTON = ("Segoe UI", 11, "bold")
    FONT_STATUS = ("Segoe UI", 9, "italic")
    
    # Messages
    WELCOME_MSG = """Xin chào! 👋 Tôi là trợ lý AI tư vấn du học.

Tôi có thể giúp bạn tìm hiểu yêu cầu đầu vào, học phí và so sánh các trường đại học.
Hãy hỏi tôi bất cứ điều gì! 🎓
"""