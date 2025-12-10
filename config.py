# ===== CONFIGURATION =====
import os

# Get base directory (สำหรับ portable)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Captcha Service API
CAPTCHA_API_KEY = "YOUR_ANYCAPTCHA_API_KEY"
CAPTCHA_API_URL = "https://api.anycaptcha.com"

# ABC Proxy Settings (Rotating Proxy)
# Format: http://username:password@host:port
ABC_PROXY_HOST = "as.7ca2c8ca73824063.abcproxy.vip"
ABC_PROXY_PORT = "4950"
ABC_PROXY_USER = "CJPq9PbdU3-zone-star-region-TH"
ABC_PROXY_PASS = "27606332"
ABC_PROXY_URL = f"http://{ABC_PROXY_USER}:{ABC_PROXY_PASS}@{ABC_PROXY_HOST}:{ABC_PROXY_PORT}"

# Proxy API (สำหรับเช็ค IP)
PROXY_CHECK_URL = "https://proxyinfo.abcproxy.com/generate_proxy_list?pkg_type=flow&proxy_address=as.7ca2c8ca73824063.abcproxy.vip:4950&username=CJPq9PbdU3-zone-star-region-TH&password=27606332&format=2&num=1"

# Python Portable Path (ถ้าใช้ portable python)
PORTABLE_PYTHON = os.path.join(BASE_DIR, "python", "python.exe")

# Chrome Driver Path (relative to project)
CHROME_DRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")

# Settings
MAX_THREADS = 3  # จำนวน browser ที่รันพร้อมกัน
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 700
WAIT_BETWEEN_ACTIONS = 1  # วินาที
WAIT_FOR_CAPTCHA = 50  # วินาทีรอ captcha โหลด

# Email Settings
EMAIL_DOMAIN = "@outlook.co.th"  # Outlook Thailand

# Output File
OUTPUT_FILE = os.path.join(BASE_DIR, "accounts.txt")

# Birth Year Range
BIRTH_YEAR_MIN = 1968
BIRTH_YEAR_MAX = 2004
