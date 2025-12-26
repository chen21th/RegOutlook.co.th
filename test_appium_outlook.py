"""
Test Outlook Thailand Registration with Appium + Kiwi Browser
เป็นตัวทดสอบ debug ว่าสามารถสมัคร + แก้ captcha ได้ไหม
"""
import time
import random
import string
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ============ CONFIG ============
APPIUM_SERVER = "http://127.0.0.1:4723/wd/hub"  # Appium 1.x uses /wd/hub
DEVICE_UDID = "ce0617164481141b0d7e"
KIWI_PACKAGE = "com.kiwibrowser.browser"
KIWI_ACTIVITY = "org.chromium.chrome.browser.ChromeTabbedActivity"

SIGNUP_URL = "https://signup.live.com/signup?mkt=th-th&lic=1"

# 2Captcha API
CAPTCHA_API_KEY = "f5cb74cff21d8caef0af74e953124f12"
FUNCAPTCHA_PUBLIC_KEY = "B7D8911C-5CC8-A9A3-35B0-554ACEE604DA"

# Thai months mapping
THAI_MONTHS = {
    1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
    5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม", 8: "สิงหาคม",
    9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
}

# ============ DATA GENERATOR ============
def generate_email():
    """สร้าง email แบบสุ่ม"""
    prefix = ''.join(random.choices(string.ascii_lowercase, k=6))
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{suffix}"

def generate_password():
    """สร้าง password ที่ปลอดภัย"""
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choices(chars, k=12))

def generate_birthday():
    """สร้างวันเกิดสุ่ม (อายุ 18-50 ปี)"""
    year = random.randint(1975, 2006)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return day, month, year

# ============ APPIUM DRIVER ============
def create_driver():
    """สร้าง Appium driver สำหรับ Kiwi Browser"""
    options = AppiumOptions()
    options.set_capability("platformName", "Android")
    options.set_capability("automationName", "UiAutomator2")
    options.set_capability("deviceName", DEVICE_UDID)
    options.set_capability("udid", DEVICE_UDID)
    
    # เปิด Kiwi Browser
    options.set_capability("appPackage", KIWI_PACKAGE)
    options.set_capability("appActivity", KIWI_ACTIVITY)
    
    # ตั้งค่าเพิ่มเติม
    options.set_capability("noReset", True)
    options.set_capability("autoGrantPermissions", True)
    options.set_capability("newCommandTimeout", 300)
    
    # ไม่ใช้ autoWebview - จะ switch เอง
    options.set_capability("autoWebview", False)
    
    # กำหนด chromedriver สำหรับ WebView
    options.set_capability("chromedriverExecutable", "c:\\Users\\ChenFB\\Desktop\\RegOutlookTH\\chromedriver.exe")
    
    print(f"[INFO] Connecting to Appium server: {APPIUM_SERVER}")
    print(f"[INFO] Device: {DEVICE_UDID}")
    print(f"[INFO] Browser: Kiwi ({KIWI_PACKAGE})")
    
    driver = webdriver.Remote(APPIUM_SERVER, options=options)
    return driver

def handle_kiwi_welcome(driver):
    """กดปุ่ม Continue ถ้ามีหน้า Welcome"""
    print("[INFO] Checking for Kiwi Welcome screen...")
    try:
        # รอสักครู่ให้หน้าโหลด
        time.sleep(2)
        
        # หาปุ่ม Continue ด้วย text หรือ resource-id
        continue_btn = None
        
        # ลองหาด้วย text
        try:
            continue_btn = driver.find_element(AppiumBy.XPATH, "//*[@text='Continue']")
        except:
            pass
        
        # ลองหาด้วย resource-id (ถ้าเจอปุ่ม)
        if not continue_btn:
            try:
                continue_btn = driver.find_element(AppiumBy.XPATH, "//android.widget.Button[contains(@text,'Continue')]")
            except:
                pass
        
        if continue_btn:
            print("[INFO] Found Continue button, clicking...")
            continue_btn.click()
            time.sleep(2)
            print("[SUCCESS] Clicked Continue!")
            return True
        else:
            print("[INFO] No Welcome screen detected")
            return True
            
    except Exception as e:
        print(f"[WARN] Welcome screen handling: {e}")
        return True  # ไม่ถือว่า error

def switch_to_webview(driver):
    """Switch ไปยัง WebView context"""
    print("[INFO] Switching to WebView context...")
    try:
        time.sleep(2)
        
        # ดู contexts ที่มี
        contexts = driver.contexts
        print(f"[INFO] Available contexts: {contexts}")
        
        # หา WEBVIEW context ของ Kiwi
        webview_context = None
        for ctx in contexts:
            if "WEBVIEW_com.kiwibrowser" in ctx:
                webview_context = ctx
                break
        
        if not webview_context:
            # ลอง WEBVIEW_chrome
            for ctx in contexts:
                if "WEBVIEW" in ctx:
                    webview_context = ctx
                    break
        
        if webview_context:
            driver.switch_to.context(webview_context)
            print(f"[SUCCESS] Switched to: {webview_context}")
            return True
        else:
            print("[WARN] No WebView context found, staying in NATIVE_APP")
            return False
            
    except Exception as e:
        print(f"[ERROR] Context switch failed: {e}")
        # ไม่ต้อง switch ก็ได้ ใช้ native mode แทน
        return False

def navigate_native(driver, url):
    """ไปที่ URL โดยใช้ Native mode (พิมพ์ใน search box)"""
    print(f"[INFO] Navigating to: {url}")
    
    try:
        # หา search box ของ Kiwi
        search_box = driver.find_element(AppiumBy.ID, "com.kiwibrowser.browser:id/search_box_text")
        search_box.click()
        time.sleep(0.5)
        
        # Clear แล้วพิมพ์ URL
        search_box.clear()
        time.sleep(0.3)
        search_box.send_keys(url)
        time.sleep(0.5)
        
        # กด Enter
        driver.press_keycode(66)  # KEYCODE_ENTER
        print("[SUCCESS] URL entered and submitted!")
        
        time.sleep(3)  # รอหน้าโหลด
        return True
        
    except Exception as e:
        print(f"[ERROR] Navigation failed: {e}")
        return False

# ============ HELPER FUNCTIONS ============
def wait_and_find(driver, by, value, timeout=15):
    """รอจนกว่าจะเจอ element"""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, value)))

def wait_and_click(driver, by, value, timeout=15):
    """รอจนกว่าจะเจอแล้วกด"""
    element = wait_and_find(driver, by, value, timeout)
    element.click()
    return element

def safe_send_keys(driver, by, value, text, timeout=15):
    """พิมพ์ข้อความอย่างปลอดภัย"""
    element = wait_and_find(driver, by, value, timeout)
    element.clear()
    time.sleep(0.3)
    element.send_keys(text)
    return element

def take_screenshot(driver, name="screenshot"):
    """ถ่ายภาพหน้าจอ"""
    filename = f"{name}_{int(time.time())}.png"
    driver.save_screenshot(filename)
    print(f"[SCREENSHOT] Saved: {filename}")
    return filename

# ============ REGISTRATION STEPS ============
def step_navigate(driver):
    """Step 1: ไปที่หน้าสมัคร"""
    print("\n[Step 1] Navigating to signup page...")
    driver.get(SIGNUP_URL)
    time.sleep(3)
    print(f"[INFO] Current URL: {driver.current_url}")
    take_screenshot(driver, "01_signup_page")

def step_enter_email(driver, email):
    """Step 2: กรอก Email"""
    print(f"\n[Step 2] Entering email: {email}@outlook.co.th")
    
    try:
        # หา input field สำหรับ email
        email_input = wait_and_find(driver, AppiumBy.ID, "MemberName", timeout=20)
        email_input.clear()
        time.sleep(0.5)
        email_input.send_keys(email)
        print(f"[SUCCESS] Email entered: {email}")
        
        time.sleep(1)
        take_screenshot(driver, "02_email_entered")
        
        # กดปุ่มถัดไป
        next_btn = wait_and_find(driver, AppiumBy.ID, "iSignupAction")
        next_btn.click()
        print("[SUCCESS] Clicked Next button")
        
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"[ERROR] Email step failed: {e}")
        take_screenshot(driver, "02_email_error")
        return False

def step_enter_password(driver, password):
    """Step 3: กรอก Password"""
    print(f"\n[Step 3] Entering password...")
    
    try:
        # หา password input
        pwd_input = wait_and_find(driver, AppiumBy.ID, "PasswordInput", timeout=15)
        pwd_input.clear()
        time.sleep(0.5)
        pwd_input.send_keys(password)
        print(f"[SUCCESS] Password entered: {password[:4]}****")
        
        time.sleep(1)
        take_screenshot(driver, "03_password_entered")
        
        # กดปุ่มถัดไป
        next_btn = wait_and_find(driver, AppiumBy.ID, "iSignupAction")
        next_btn.click()
        print("[SUCCESS] Clicked Next button")
        
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"[ERROR] Password step failed: {e}")
        take_screenshot(driver, "03_password_error")
        return False

def step_enter_name(driver, first_name="สมชาย", last_name="ใจดี"):
    """Step 4: กรอกชื่อ"""
    print(f"\n[Step 4] Entering name: {first_name} {last_name}")
    
    try:
        # หา FirstName input
        first_input = wait_and_find(driver, AppiumBy.ID, "FirstName", timeout=15)
        first_input.clear()
        time.sleep(0.3)
        first_input.send_keys(first_name)
        print(f"[SUCCESS] First name entered: {first_name}")
        
        # หา LastName input  
        last_input = wait_and_find(driver, AppiumBy.ID, "LastName")
        last_input.clear()
        time.sleep(0.3)
        last_input.send_keys(last_name)
        print(f"[SUCCESS] Last name entered: {last_name}")
        
        time.sleep(1)
        take_screenshot(driver, "04_name_entered")
        
        # กดปุ่มถัดไป
        next_btn = wait_and_find(driver, AppiumBy.ID, "iSignupAction")
        next_btn.click()
        print("[SUCCESS] Clicked Next button")
        
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"[ERROR] Name step failed: {e}")
        take_screenshot(driver, "04_name_error")
        return False

def step_enter_birthday(driver, day, month, year):
    """Step 5: เลือกวันเกิด"""
    print(f"\n[Step 5] Entering birthday: {day}/{month}/{year}")
    
    try:
        # เลือกวัน
        day_dropdown = wait_and_find(driver, AppiumBy.ID, "BirthDay", timeout=15)
        day_dropdown.click()
        time.sleep(0.5)
        
        # เลือกตัวเลือกวัน (ใช้ XPATH หรือ accessibility)
        day_option = wait_and_find(driver, AppiumBy.XPATH, f"//option[@value='{day}']")
        day_option.click()
        print(f"[SUCCESS] Day selected: {day}")
        
        time.sleep(0.5)
        
        # เลือกเดือน
        month_dropdown = wait_and_find(driver, AppiumBy.ID, "BirthMonth")
        month_dropdown.click()
        time.sleep(0.5)
        
        month_option = wait_and_find(driver, AppiumBy.XPATH, f"//option[@value='{month}']")
        month_option.click()
        print(f"[SUCCESS] Month selected: {THAI_MONTHS.get(month, month)}")
        
        time.sleep(0.5)
        
        # เลือกปี
        year_dropdown = wait_and_find(driver, AppiumBy.ID, "BirthYear")
        year_dropdown.click()
        time.sleep(0.5)
        
        year_option = wait_and_find(driver, AppiumBy.XPATH, f"//option[@value='{year}']")
        year_option.click()
        print(f"[SUCCESS] Year selected: {year}")
        
        time.sleep(1)
        take_screenshot(driver, "05_birthday_entered")
        
        # กดปุ่มถัดไป
        next_btn = wait_and_find(driver, AppiumBy.ID, "iSignupAction")
        next_btn.click()
        print("[SUCCESS] Clicked Next button")
        
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"[ERROR] Birthday step failed: {e}")
        take_screenshot(driver, "05_birthday_error")
        return False

def step_handle_captcha(driver):
    """Step 6: จัดการ Captcha (FunCaptcha)"""
    print("\n[Step 6] Handling Captcha...")
    
    try:
        # รอให้ captcha iframe โหลด
        time.sleep(3)
        take_screenshot(driver, "06_captcha_page")
        
        # ดูว่ามี captcha frame ไหม
        page_source = driver.page_source
        
        if "enforcementFrame" in page_source or "arkose" in page_source.lower():
            print("[INFO] FunCaptcha detected!")
            
            # TODO: ใช้ 2Captcha API แก้ captcha
            # ตอนนี้ให้ user แก้เอง
            print("\n" + "="*50)
            print("[MANUAL] กรุณาแก้ Captcha ในมือถือ")
            print("[MANUAL] กดปุ่มยืนยันเมื่อแก้เสร็จ")
            print("="*50 + "\n")
            
            input("กด Enter เมื่อแก้ Captcha เสร็จแล้ว...")
            
            time.sleep(2)
            take_screenshot(driver, "06_captcha_solved")
            return True
            
        else:
            print("[INFO] No captcha detected, continuing...")
            return True
            
    except Exception as e:
        print(f"[ERROR] Captcha step failed: {e}")
        take_screenshot(driver, "06_captcha_error")
        return False

def step_verify_success(driver):
    """Step 7: ตรวจสอบว่าสมัครสำเร็จ"""
    print("\n[Step 7] Verifying registration success...")
    
    try:
        time.sleep(3)
        current_url = driver.current_url
        page_source = driver.page_source
        
        take_screenshot(driver, "07_final_page")
        
        # ตรวจสอบว่าสำเร็จหรือไม่
        if "outlook.live.com" in current_url or "login.live.com" in current_url:
            print("[SUCCESS] Registration completed!")
            return True
        elif "error" in page_source.lower() or "ผิดพลาด" in page_source:
            print("[FAIL] Registration failed - error detected")
            return False
        else:
            print(f"[INFO] Current URL: {current_url}")
            print("[INFO] Status unknown - please verify manually")
            return None
            
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        return False

# ============ MAIN REGISTRATION FLOW ============
def run_registration():
    """รัน registration flow ทั้งหมด"""
    driver = None
    
    # สร้างข้อมูล
    email = generate_email()
    password = generate_password()
    day, month, year = generate_birthday()
    
    print("\n" + "="*60)
    print(" OUTLOOK THAILAND REGISTRATION TEST (Appium + Kiwi)")
    print("="*60)
    print(f"Email: {email}@outlook.co.th")
    print(f"Password: {password}")
    print(f"Birthday: {day}/{month}/{year}")
    print("="*60 + "\n")
    
    try:
        # สร้าง driver
        driver = create_driver()
        print("[SUCCESS] Connected to Appium!")
        
        # Step 1: Navigate
        step_navigate(driver)
        
        # Step 2: Email
        if not step_enter_email(driver, email):
            return False
            
        # Step 3: Password
        if not step_enter_password(driver, password):
            return False
            
        # Step 4: Name
        if not step_enter_name(driver):
            return False
            
        # Step 5: Birthday
        if not step_enter_birthday(driver, day, month, year):
            return False
            
        # Step 6: Captcha
        if not step_handle_captcha(driver):
            return False
            
        # Step 7: Verify
        result = step_verify_success(driver)
        
        if result:
            print("\n" + "="*60)
            print(" REGISTRATION SUCCESSFUL!")
            print("="*60)
            print(f"Email: {email}@outlook.co.th")
            print(f"Password: {password}")
            print("="*60 + "\n")
            return True
        else:
            print("\n[FAIL] Registration did not complete successfully")
            return False
            
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        if driver:
            take_screenshot(driver, "fatal_error")
        return False
        
    finally:
        if driver:
            print("\n[INFO] Closing driver...")
            # ไม่ปิด browser เพื่อให้ debug ได้
            # driver.quit()
            print("[INFO] Driver session ended (browser still open)")

# ============ DEBUG MODE ============
def debug_elements(driver):
    """Debug: ดู elements ในหน้าปัจจุบัน"""
    print("\n[DEBUG] Analyzing page elements...")
    
    # หา elements ด้วย XPATH (สำหรับ native mode)
    try:
        elements = driver.find_elements(AppiumBy.XPATH, "//*[@resource-id]")
        print(f"\n[DEBUG] Found {len(elements)} elements with resource-id:")
        for el in elements[:15]:
            try:
                el_id = el.get_attribute("resource-id")
                el_class = el.get_attribute("class")
                el_text = el.get_attribute("text") or ""
                print(f"  - ID: {el_id} | Class: {el_class} | Text: {el_text[:30]}")
            except:
                pass
    except Exception as e:
        print(f"[DEBUG] Native element search failed: {e}")
    
    # หา clickable elements
    try:
        clickables = driver.find_elements(AppiumBy.XPATH, "//*[@clickable='true']")
        print(f"\n[DEBUG] Found {len(clickables)} clickable elements:")
        for el in clickables[:10]:
            try:
                el_class = el.get_attribute("class")
                el_text = el.get_attribute("text") or el.get_attribute("content-desc") or ""
                print(f"  - Class: {el_class} | Text: {el_text[:30]}")
            except:
                pass
    except Exception as e:
        print(f"[DEBUG] Clickable search failed: {e}")

def debug_connect_only():
    """เชื่อมต่อ Appium เฉยๆ ไม่ทำอะไร (สำหรับ debug)"""
    print("[DEBUG] Connecting to existing browser session...")
    
    driver = create_driver()
    print("[SUCCESS] Connected!")
    
    # กด Continue ถ้ามีหน้า Welcome
    handle_kiwi_welcome(driver)
    
    # แสดง contexts
    print(f"\n[DEBUG] Available contexts: {driver.contexts}")
    print(f"[DEBUG] Current context: {driver.current_context}")
    
    # แสดง elements
    debug_elements(driver)
    
    # ถามว่าจะไป signup page ไหม
    choice = input("\n[?] Navigate to Outlook signup page? (y/n): ")
    if choice.lower() == 'y':
        navigate_native(driver, SIGNUP_URL)
        time.sleep(5)
        
        # ลอง switch ไป WebView
        switch_to_webview(driver)
        
        take_screenshot(driver, "signup_page")
        debug_elements(driver)
    
    take_screenshot(driver, "debug_page")
    
    print("\n[INFO] Debug session ready. Driver object available.")
    return driver

# ============ ENTRY POINT ============
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        # Debug mode: แค่เชื่อมต่อและวิเคราะห์หน้า
        driver = debug_connect_only()
        input("\nกด Enter เพื่อปิด...")
    else:
        # Normal mode: รัน registration
        run_registration()
