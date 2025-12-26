"""
Outlook Thailand Registration - Appium + Chrome Browser
ใช้ Chrome บน Android เพื่อควบคุม WebView โดยตรง
"""
import time
import random
import string
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# ============ CONFIG ============
APPIUM_SERVER = "http://127.0.0.1:4723/wd/hub"
DEVICE_UDID = "ce0617164481141b0d7e"

SIGNUP_URL = "https://signup.live.com/signup?mkt=th-th&lic=1"

# 2Captcha
CAPTCHA_API_KEY = "f5cb74cff21d8caef0af74e953124f12"
FUNCAPTCHA_PUBLIC_KEY = "B7D8911C-5CC8-A9A3-35B0-554ACEE604DA"

# Thai months
THAI_MONTHS = {
    1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
    5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม", 8: "สิงหาคม",
    9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
}

# ============ DATA GENERATOR ============
def generate_email():
    prefix = ''.join(random.choices(string.ascii_lowercase, k=6))
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{suffix}"

def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$"
    return ''.join(random.choices(chars, k=12))

def generate_birthday():
    year = random.randint(1975, 2000)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return day, month, year

# ============ DRIVER ============
def create_chrome_driver():
    """สร้าง Appium driver สำหรับ Chrome Browser"""
    options = AppiumOptions()
    options.set_capability("platformName", "Android")
    options.set_capability("automationName", "UiAutomator2")
    options.set_capability("deviceName", DEVICE_UDID)
    options.set_capability("udid", DEVICE_UDID)
    
    # ใช้ Chrome Browser
    options.set_capability("browserName", "Chrome")
    
    # ChromeDriver
    options.set_capability("chromedriverExecutable", "c:\\Users\\ChenFB\\Desktop\\RegOutlookTH\\chromedriver.exe")
    
    # Settings
    options.set_capability("noReset", True)
    options.set_capability("newCommandTimeout", 300)
    
    print(f"[INFO] Connecting to Appium: {APPIUM_SERVER}")
    print(f"[INFO] Device: {DEVICE_UDID}")
    print(f"[INFO] Browser: Chrome")
    
    driver = webdriver.Remote(APPIUM_SERVER, options=options)
    return driver

# ============ HELPERS ============
def wait_and_find(driver, by, value, timeout=15):
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, value)))

def wait_and_click(driver, by, value, timeout=15):
    el = wait_and_find(driver, by, value, timeout)
    el.click()
    return el

def safe_send_keys(driver, by, value, text, timeout=15):
    el = wait_and_find(driver, by, value, timeout)
    el.clear()
    time.sleep(0.3)
    el.send_keys(text)
    return el

def take_screenshot(driver, name):
    filename = f"{name}_{int(time.time())}.png"
    driver.save_screenshot(filename)
    print(f"[SCREENSHOT] {filename}")
    return filename

# ============ REGISTRATION STEPS ============
def step_navigate(driver):
    """ไปหน้า signup"""
    print(f"\n[Step 1] Navigating to: {SIGNUP_URL}")
    driver.get(SIGNUP_URL)
    time.sleep(3)
    print(f"[INFO] URL: {driver.current_url}")
    take_screenshot(driver, "01_signup")

def step_email(driver, email):
    """กรอก email"""
    print(f"\n[Step 2] Entering email: {email}@outlook.co.th")
    
    try:
        # หา input field
        email_input = wait_and_find(driver, By.ID, "MemberName", timeout=20)
        email_input.clear()
        time.sleep(0.3)
        email_input.send_keys(email)
        print(f"[SUCCESS] Email entered")
        
        time.sleep(1)
        
        # กด Next
        next_btn = wait_and_find(driver, By.ID, "iSignupAction")
        next_btn.click()
        print("[SUCCESS] Clicked Next")
        
        time.sleep(2)
        take_screenshot(driver, "02_email")
        return True
        
    except Exception as e:
        print(f"[ERROR] Email step: {e}")
        take_screenshot(driver, "02_email_error")
        return False

def step_password(driver, password):
    """กรอก password"""
    print(f"\n[Step 3] Entering password")
    
    try:
        pwd_input = wait_and_find(driver, By.ID, "PasswordInput", timeout=15)
        pwd_input.clear()
        time.sleep(0.3)
        pwd_input.send_keys(password)
        print(f"[SUCCESS] Password entered: {password[:4]}****")
        
        time.sleep(1)
        
        next_btn = wait_and_find(driver, By.ID, "iSignupAction")
        next_btn.click()
        print("[SUCCESS] Clicked Next")
        
        time.sleep(2)
        take_screenshot(driver, "03_password")
        return True
        
    except Exception as e:
        print(f"[ERROR] Password step: {e}")
        take_screenshot(driver, "03_password_error")
        return False

def step_name(driver, first_name="สมชาย", last_name="ใจดี"):
    """กรอกชื่อ"""
    print(f"\n[Step 4] Entering name: {first_name} {last_name}")
    
    try:
        first_input = wait_and_find(driver, By.ID, "FirstName", timeout=15)
        first_input.clear()
        time.sleep(0.3)
        first_input.send_keys(first_name)
        
        last_input = wait_and_find(driver, By.ID, "LastName")
        last_input.clear()
        time.sleep(0.3)
        last_input.send_keys(last_name)
        
        print(f"[SUCCESS] Name entered")
        
        time.sleep(1)
        
        next_btn = wait_and_find(driver, By.ID, "iSignupAction")
        next_btn.click()
        print("[SUCCESS] Clicked Next")
        
        time.sleep(2)
        take_screenshot(driver, "04_name")
        return True
        
    except Exception as e:
        print(f"[ERROR] Name step: {e}")
        take_screenshot(driver, "04_name_error")
        return False

def step_birthday(driver, day, month, year):
    """เลือกวันเกิด"""
    print(f"\n[Step 5] Entering birthday: {day}/{month}/{year}")
    
    try:
        # เลือกวัน
        day_select = wait_and_find(driver, By.ID, "BirthDay", timeout=15)
        day_select.click()
        time.sleep(0.5)
        day_option = wait_and_find(driver, By.XPATH, f"//option[@value='{day}']")
        day_option.click()
        print(f"[SUCCESS] Day: {day}")
        
        time.sleep(0.5)
        
        # เลือกเดือน
        month_select = wait_and_find(driver, By.ID, "BirthMonth")
        month_select.click()
        time.sleep(0.5)
        month_option = wait_and_find(driver, By.XPATH, f"//option[@value='{month}']")
        month_option.click()
        print(f"[SUCCESS] Month: {THAI_MONTHS.get(month)}")
        
        time.sleep(0.5)
        
        # เลือกปี
        year_select = wait_and_find(driver, By.ID, "BirthYear")
        year_select.click()
        time.sleep(0.5)
        year_option = wait_and_find(driver, By.XPATH, f"//option[@value='{year}']")
        year_option.click()
        print(f"[SUCCESS] Year: {year}")
        
        time.sleep(1)
        
        next_btn = wait_and_find(driver, By.ID, "iSignupAction")
        next_btn.click()
        print("[SUCCESS] Clicked Next")
        
        time.sleep(2)
        take_screenshot(driver, "05_birthday")
        return True
        
    except Exception as e:
        print(f"[ERROR] Birthday step: {e}")
        take_screenshot(driver, "05_birthday_error")
        return False

def step_captcha(driver):
    """จัดการ Captcha"""
    print("\n[Step 6] Handling Captcha...")
    
    time.sleep(3)
    take_screenshot(driver, "06_captcha")
    
    # ตรวจสอบว่ามี captcha หรือไม่
    page_source = driver.page_source
    
    if "enforcementFrame" in page_source or "arkose" in page_source.lower() or "FunCaptcha" in page_source:
        print("[INFO] FunCaptcha detected!")
        print("\n" + "="*50)
        print("[MANUAL] กรุณาแก้ Captcha ในมือถือ")
        print("[MANUAL] แล้วกด Enter เมื่อเสร็จ")
        print("="*50)
        
        input("\nกด Enter หลังแก้ Captcha...")
        
        time.sleep(2)
        take_screenshot(driver, "06_captcha_done")
        return True
    else:
        print("[INFO] No captcha detected")
        return True

def step_verify(driver, email, password):
    """ตรวจสอบผลลัพธ์"""
    print("\n[Step 7] Verifying result...")
    
    time.sleep(3)
    url = driver.current_url
    take_screenshot(driver, "07_result")
    
    print(f"[INFO] Final URL: {url}")
    
    if "outlook" in url or "live.com" in url:
        print("\n" + "="*60)
        print(" ✓ REGISTRATION SUCCESS!")
        print("="*60)
        print(f" Email: {email}@outlook.co.th")
        print(f" Password: {password}")
        print("="*60)
        return True
    else:
        print("[INFO] Please verify manually")
        return None

# ============ MAIN ============
def run_registration():
    """รัน registration flow"""
    driver = None
    
    # Generate data
    email = generate_email()
    password = generate_password()
    day, month, year = generate_birthday()
    
    print("\n" + "="*60)
    print(" OUTLOOK THAILAND REGISTRATION (Chrome + Appium)")
    print("="*60)
    print(f" Email: {email}@outlook.co.th")
    print(f" Password: {password}")
    print(f" Birthday: {day}/{month}/{year}")
    print("="*60)
    
    try:
        driver = create_chrome_driver()
        print("[SUCCESS] Chrome connected!")
        
        # Run steps
        step_navigate(driver)
        
        if not step_email(driver, email):
            return False
            
        if not step_password(driver, password):
            return False
            
        if not step_name(driver):
            return False
            
        if not step_birthday(driver, day, month, year):
            return False
            
        if not step_captcha(driver):
            return False
            
        step_verify(driver, email, password)
        
        input("\n[END] กด Enter เพื่อปิด...")
        return True
        
    except Exception as e:
        print(f"\n[FATAL] {e}")
        if driver:
            take_screenshot(driver, "fatal_error")
        return False
        
    finally:
        if driver:
            print("[INFO] Session ended")

def test_connection():
    """ทดสอบการเชื่อมต่อ Chrome"""
    print("[TEST] Testing Chrome connection...")
    
    try:
        driver = create_chrome_driver()
        print("[SUCCESS] Connected!")
        
        driver.get("https://www.google.com")
        time.sleep(2)
        
        print(f"[INFO] URL: {driver.current_url}")
        print(f"[INFO] Title: {driver.title}")
        
        take_screenshot(driver, "test_chrome")
        
        input("\n[OK] Chrome working! กด Enter เพื่อปิด...")
        
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_connection()
    else:
        run_registration()
