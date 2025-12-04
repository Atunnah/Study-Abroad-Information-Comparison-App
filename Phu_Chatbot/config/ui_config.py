# config/ui_config.py
class ChatbotConfig:
    # ... (Giữ nguyên các màu cũ) ...
    BACKGROUND = "#f5f5f5"
    SIDEBAR_BG = "#2c3e50"
    SIDEBAR_FG = "white"
    
    # Header
    HEADER_BG = "#ecf0f1"
    HEADER_FG = "#2c3e50"
    
    CHAT_BG = "white"
    
    # Text Colors
    TEXT_PRIMARY = "#2c3e50"
    TEXT_SECONDARY = "#34495e"
    
    # Sidebar Items
    ITEM_BG = "#34495e"
    ITEM_ACTIVE_BG = "#3498db"
    ITEM_HOVER_BG = "#2980b9"
    
    # User/Assistant Bubbles
    USER_BG = "#3498db"
    USER_FG = "white"  
    ASSISTANT_BG = "#ecf0f1"
    ASSISTANT_FG = "#2c3e50"
    
    # Status Colors
    ERROR_COLOR = "#e74c3c"
    STATUS_COLOR = "#7f8c8d"
    
    # Buttons
    BUTTON_BG = "#3498db"
    BUTTON_FG = "white"
    BUTTON_ACTIVE = "#2980b9"
    BUTTON_CANCEL = "#e74c3c"
    BUTTON_DISABLED = "#95a5a6"
    
    # --- THÊM MỚI CHO NÚT TOGGLE ---
    BUTTON_TOGGLE_BG = "#ecf0f1"      # Cùng màu header
    BUTTON_TOGGLE_FG = "#2c3e50"      # Cùng màu chữ header
    BUTTON_TOGGLE_HOVER = "#bdc3c7"
    
    # Fonts
    FONT_HEADER_TITLE = ("Segoe UI", 14, "bold")
    FONT_HEADER_SUB = ("Segoe UI", 10)
    FONT_TEXT = ("Segoe UI", 11)
    FONT_TEXT_BOLD = ("Segoe UI", 11, "bold")
    FONT_BUTTON = ("Segoe UI", 10, "bold")
    FONT_SIDEBAR_ITEM = ("Segoe UI", 10)
    FONT_STATUS = ("Segoe UI", 9, "italic")
    
    # --- THÊM FONT CHO ICON ---
    FONT_ICON = ("Segoe UI", 16) 

    # Messages (Giữ nguyên)
    WELCOME_MSG = """Xin chào! 👋 Tôi là trợ lý AI tư vấn du học.

Tôi có thể giúp bạn tìm hiểu yêu cầu đầu vào, học phí và so sánh các trường đại học.
Hãy hỏi tôi bất cứ điều gì! 🎓
"""