import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_DATABASE', 'university_comparison')
}

# Application Configuration
APP_TITLE = os.getenv('APP_TITLE', 'Ứng dụng So sánh Thông tin Đầu vào Trường Đại học')
APP_WIDTH = int(os.getenv('APP_WIDTH', 1200))
APP_HEIGHT = int(os.getenv('APP_HEIGHT', 700))
