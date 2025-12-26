"""
ทดสอบ Appium + Browser Mode (ให้ Appium จัดการ ChromeDriver เอง)
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

# ============ DRIVER ============
def create_browser_driver():
    """สร้าง Appium driver แบบ Browser mode"""
    options = AppiumOptions()
    options.set_capability("platformName", "Android")
    options.set_capability("automationName", "UiAutomator2")
    options.set_capability("deviceName", DEVICE_UDID)
    options.set_capability("udid", DEVICE_UDID)
    
    # ใช้ Browser mode - Appium จะเปิด browser และจัดการ WebView ให้
    options.set_capability("browserName", "Browser")
    
    # ChromeDriver
    options.set_capability("chromedriverExecutable", "c:\\Users\\ChenFB\\Desktop\\RegOutlookTH\\chromedriver.exe")
    options.set_capability("chromedriverAutodownload", True)
    
    options.set_capability("noReset", True)
    options.set_capability("newCommandTimeout", 300)
    
    print(f"[INFO] Connecting to Appium (Browser mode)...")
    driver = webdriver.Remote(APPIUM_SERVER, options=options)
    print("[SUCCESS] Connected!")
    return driver

def create_kiwi_webview_driver():
    """สร้าง Appium driver สำหรับ Kiwi พร้อม WebView"""
    options = AppiumOptions()
    options.set_capability("platformName", "Android")
    options.set_capability("automationName", "UiAutomator2")
    options.set_capability("deviceName", DEVICE_UDID)
    options.set_capability("udid", DEVICE_UDID)
    
    # Kiwi Browser
    options.set_capability("appPackage", "com.kiwibrowser.browser")
    options.set_capability("appActivity", "org.chromium.chrome.browser.ChromeTabbedActivity")
    
    # ChromeDriver สำหรับ WebView
    options.set_capability("chromedriverExecutable", "c:\\Users\\ChenFB\\Desktop\\RegOutlookTH\\chromedriver.exe")
    
    # ให้ switch ไป WebView อัตโนมัติ
    options.set_capability("autoWebview", True)
    options.set_capability("autoWebviewTimeout", 20000)
    
    options.set_capability("noReset", True)
    options.set_capability("newCommandTimeout", 300)
    
    print(f"[INFO] Connecting to Kiwi with WebView...")
    driver = webdriver.Remote(APPIUM_SERVER, options=options)
    print("[SUCCESS] Connected!")
    return driver

# ============ HELPER ============
def take_screenshot(driver, name):
    """ถ่ายภาพหน้าจอ"""
    filename = f"{name}_{int(time.time())}.png"
    driver.save_screenshot(filename)
    print(f"[SCREENSHOT] {filename}")
    return filename

def wait_and_find(driver, by, value, timeout=15):
    """รอจนกว่าจะเจอ element"""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, value)))

def safe_click(driver, by, value, timeout=10):
    """คลิก element อย่างปลอดภัย"""
    try:
        el = wait_and_find(driver, by, value, timeout)
        el.click()
        return True
    except Exception as e:
        print(f"[ERROR] Click failed: {e}")
        return False

def safe_type(driver, by, value, text, timeout=10):
    """พิมพ์ข้อความอย่างปลอดภัย"""
    try:
        el = wait_and_find(driver, by, value, timeout)
        el.clear()
        time.sleep(0.3)
        el.send_keys(text)
        return True
    except Exception as e:
        print(f"[ERROR] Type failed: {e}")
        return False

# ============ REGISTRATION STEPS ============
def step_enter_email(driver, email):
    """กรอก email"""
    print(f"\n[STEP] Entering email: {email}@outlook.co.th")
    
    # หา input email (ID หรือ Name)
    selectors = [
        (By.ID, "MemberName"),
        (By.NAME, "MemberName"),
        (By.CSS_SELECTOR, "input[type='email']"),
        (By.XPATH, "//input[@id='MemberName']")
    ]
    
    for by, value in selectors:
        try:
            el = wait_and_find(driver, by, value, timeout=5)
            el.clear()
            el.send_keys(email)
            print(f"[SUCCESS] Email entered using {by}:{value}")
            return True
        except:
            continue
    
    print("[ERROR] Could not find email input")
    return False

def step_click_next(driver):
    """กดปุ่มถัดไป"""
    print("\n[STEP] Clicking Next...")
    
    selectors = [
        (By.ID, "iSignupAction"),
        (By.XPATH, "//input[@id='iSignupAction']"),
        (By.CSS_SELECTOR, "input[type='submit']")
    ]
    
    for by, value in selectors:
        try:
            el = wait_and_find(driver, by, value, timeout=5)
            el.click()
            print(f"[SUCCESS] Next clicked using {by}:{value}")
            time.sleep(2)
            return True
        except:
            continue
    
    print("[ERROR] Could not find Next button")
    return False

def step_enter_password(driver, password):
    """กรอก password"""
    print(f"\n[STEP] Entering password...")
    
    selectors = [
        (By.ID, "PasswordInput"),
        (By.NAME, "Password"),
        (By.CSS_SELECTOR, "input[type='password']")
    ]
    
    for by, value in selectors:
        try:
            el = wait_and_find(driver, by, value, timeout=5)
            el.clear()
            el.send_keys(password)
            print(f"[SUCCESS] Password entered")
            return True
        except:
            continue
    
    print("[ERROR] Could not find password input")
    return False

# ============ MAIN TEST ============
def test_registration():
    """ทดสอบ flow การสมัคร"""
    driver = None
    
    # สร้างข้อมูลทดสอบ
    email = "test" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    password = "Test@" + ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    print("\n" + "="*60)
    print(" OUTLOOK REGISTRATION TEST (Appium Browser Mode)")
    print("="*60)
    print(f"Email: {email}@outlook.co.th")
    print(f"Password: {password}")
    print("="*60 + "\n")
    
    try:
        # ลอง Browser mode ก่อน
        try:
            driver = create_browser_driver()
        except Exception as e:
            print(f"[WARN] Browser mode failed: {e}")
            print("[INFO] Trying Kiwi WebView mode...")
            driver = create_kiwi_webview_driver()
        
        # ไปหน้า signup
        print(f"\n[STEP] Navigating to: {SIGNUP_URL}")
        driver.get(SIGNUP_URL)
        
        # รอหน้าโหลด
        time.sleep(5)
        print(f"[INFO] Current URL: {driver.current_url}")
        print(f"[INFO] Title: {driver.title}")
        
        take_screenshot(driver, "01_signup_page")
        
        # Step 1: Email
        if not step_enter_email(driver, email):
            take_screenshot(driver, "error_email")
            return False
        
        take_screenshot(driver, "02_email_entered")
        
        # Click Next
        if not step_click_next(driver):
            take_screenshot(driver, "error_next1")
            return False
        
        take_screenshot(driver, "03_after_email")
        
        # Step 2: Password
        if not step_enter_password(driver, password):
            take_screenshot(driver, "error_password")
            return False
        
        take_screenshot(driver, "04_password_entered")
        
        # Click Next
        if not step_click_next(driver):
            take_screenshot(driver, "error_next2")
            return False
        
        take_screenshot(driver, "05_after_password")
        
        # รอดูผล
        print("\n[INFO] Check the phone screen...")
        input("กด Enter เพื่อทำต่อ...")
        
        take_screenshot(driver, "06_current_state")
        print(f"[INFO] Current URL: {driver.current_url}")
        
        return True
        
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        if driver:
            take_screenshot(driver, "fatal_error")
        return False
        
    finally:
        if driver:
            print("\n[INFO] Session ended")
            input("กด Enter เพื่อปิด driver...")
            # driver.quit()

if __name__ == "__main__":
    test_registration()
