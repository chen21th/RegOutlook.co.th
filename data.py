# ===== DATA LISTS =====

import random
import string

# รายชื่อคนไทย (ชื่อจริงๆ ที่ใช้บ่อย)
THAI_NAMES = [
    # ชื่อผู้ชาย
    "สมชาย ใจดี",
    "วิชัย สุขสันต์",
    "สมศักดิ์ รักไทย",
    "ประเสริฐ มั่งมี",
    "สมหมาย จันทร์เพ็ญ",
    "สุรชัย พงศ์พันธุ์",
    "วีระ ศรีสวัสดิ์",
    "ชาติชาย เจริญสุข",
    "ณัฐพล วงศ์สกุล",
    "ธนกฤต สิริมงคล",
    "กิตติพงษ์ แสงทอง",
    "ภานุพงศ์ ทองคำ",
    "พีรพัฒน์ ชัยวัฒน์",
    "ศุภกิจ มหาชัย",
    "อนุชา บุญเลิศ",
    "ปิยะ รุ่งโรจน์",
    "วรพจน์ สมบูรณ์",
    "จักรพันธ์ ศิริพร",
    "เอกชัย นิลเพชร",
    "ธีรศักดิ์ วิไลลักษณ์",
    # ชื่อผู้หญิง
    "สุดา มีสุข",
    "สมหญิง รักดี",
    "วิภา แสงจันทร์",
    "นารี ศรีสุข",
    "พรทิพย์ งามวงศ์",
    "สุภาพร เจริญศรี",
    "รัตนา บุญมา",
    "อรุณี ทองสุข",
    "ปราณี วัฒนา",
    "จินตนา สุขใจ",
    "กัลยา เพชรรัตน์",
    "ณิชา พิมพ์ทอง",
    "พิมพ์ใจ ดวงแก้ว",
    "ศิริพร ลาภเจริญ",
    "มณีรัตน์ ศรีทอง",
    "วราภรณ์ พรหมมา",
    "สุกัญญา นาคทอง",
    "ธัญญา เกษมสุข",
    "ปวีณา รักษ์ไทย",
    "อัญชลี สุวรรณ",
]

# รายชื่อเวียดนาม (จาก original code)
VIET_NAMES = [
    "Nguyễn Văn Vinh",
    "Đỗ Trọng Bảo",
    "Đỗ Trọng Chi",
    "Đỗ Bình Linh",
    "Đặng Tuấn Anh",
    "Lưu Trang Anh",
    "Hoàng Đức Anh",
    "Phạm Hoàng Anh",
    "Phạm Thị Anh",
    "Đỗ Gia Bảo",
    "Trần Thị Châu",
    "Tăng Phương Chi",
    "Phạm Tiến Dũng",
    "Trần An Dương",
    "Mạc Trung Đức",
    "Vũ Hương Giang",
    "Nguyễn Thị Ngân",
    "Nguyễn Lê Hiếu",
    "Phạm Xuân Hòa",
    "Khoa Minh Hoàng",
    "Nguyễn Hữu Hiệp",
    "Nguyễn Mạnh Hùng",
    "Nguyễn Vũ Gia",
    "Trần Tuấn Hưng",
]


def generate_password(length=16):
    """สร้าง password แบบ random ที่ผ่าน requirement ของ Microsoft"""
    password = ""
    for _ in range(length // 4):
        password += random.choice(string.ascii_lowercase)
        password += str(random.randint(0, 9))
        password += random.choice(string.ascii_uppercase)
        password += random.choice("~!#$%^&*()<>?./|")
    return password


def generate_username(length=12):
    """สร้าง username แบบ random"""
    username = ""
    for _ in range(length // 3):
        username += random.choice(string.ascii_lowercase)
        username += str(random.randint(0, 9))
        username += random.choice(string.ascii_uppercase)
    return username.lower()


def get_random_name(name_type="thai"):
    """สุ่มชื่อ"""
    names = THAI_NAMES if name_type == "thai" else VIET_NAMES
    full_name = random.choice(names)
    parts = full_name.split()
    
    if len(parts) >= 2:
        first_name = parts[0]
        last_name = " ".join(parts[1:])
    else:
        first_name = full_name
        last_name = "User"
    
    return first_name, last_name


def get_random_birthdate():
    """สุ่มวันเกิด"""
    from config import BIRTH_YEAR_MIN, BIRTH_YEAR_MAX
    
    day = random.randint(1, 28)
    month = random.randint(1, 12)
    year = random.randint(BIRTH_YEAR_MIN, BIRTH_YEAR_MAX)
    
    return day, month, year
