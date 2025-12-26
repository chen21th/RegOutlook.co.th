"""
Outlook Registration - tap ไปเรื่อยๆ
ดู XML แล้ว tap ตาม bounds/resource-id
"""
import time
import random
import string
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy

# ============ CONFIG ============
APPIUM_SERVER = "http://127.0.0.1:4723"
DEVICE_UDID = "ce0617164481141b0d7e"
SIGNUP_URL = "https://signup.live.com/signup?mkt=th-th&lic=1"

# ============ CONNECT ============
def connect():
    options = AppiumOptions()
    options.set_capability("platformName", "Android")
    options.set_capability("automationName", "UiAutomator2")
    options.set_capability("deviceName", DEVICE_UDID)
    options.set_capability("noReset", True)
    options.set_capability("newCommandTimeout", 600)
    
    print("[*] Connecting...")
    driver = webdriver.Remote(APPIUM_SERVER, options=options)
    print("[+] Connected!")
    return driver

# ============ HELPERS ============
def tap(driver, x, y):
    driver.tap([(x, y)])
    print(f"[TAP] ({x}, {y})")

def type_in(driver, rid, text):
    """พิมพ์ลง element ด้วย resource-id"""
    try:
        el = driver.find_element(AppiumBy.XPATH, f"//*[@resource-id='{rid}']")
        el.clear()
        time.sleep(0.2)
        el.send_keys(text)
        print(f"[TYPE] {rid} = {text}")
        return True
    except Exception as e:
        print(f"[FAIL] {rid}: {e}")
        return False

def tap_text(driver, text):
    """tap element ที่มี text"""
    try:
        el = driver.find_element(AppiumBy.XPATH, f"//*[@text='{text}']")
        el.click()
        print(f"[TAP] text='{text}'")
        return True
    except:
        print(f"[FAIL] text='{text}' not found")
        return False

def tap_id(driver, rid):
    """tap element ด้วย resource-id"""
    try:
        el = driver.find_element(AppiumBy.XPATH, f"//*[@resource-id='{rid}']")
        el.click()
        print(f"[TAP] id='{rid}'")
        return True
    except:
        print(f"[FAIL] id='{rid}' not found")
        return False

def wait_for(driver, text, timeout=15):
    """รอจนกว่าจะเจอ text"""
    for i in range(timeout):
        try:
            driver.find_element(AppiumBy.XPATH, f"//*[contains(@text,'{text}')]")
            print(f"[FOUND] '{text}'")
            return True
        except:
            time.sleep(1)
    print(f"[TIMEOUT] '{text}'")
    return False

def dump(driver, filename="dump.xml"):
    xml = driver.page_source
    with open(filename, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"[DUMP] {filename}")

def shot(driver, name="screen"):
    fn = f"{name}_{int(time.time())}.png"
    driver.save_screenshot(fn)
    print(f"[SHOT] {fn}")

# ============ GENERATE DATA ============
def gen_email():
    return ''.join(random.choices(string.ascii_lowercase, k=6)) + str(random.randint(100,999))

def gen_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + "!@"

def gen_birthday():
    return random.randint(1,28), random.randint(1,12), random.randint(1980, 2000)

# ============ REGISTRATION FLOW ============
def register(driver):
    email = gen_email()
    password = gen_password()
    day, month, year = gen_birthday()
    
    print("\n" + "="*50)
    print(f" Email: {email}@outlook.co.th")
    print(f" Password: {password}")
    print(f" Birthday: {day}/{month}/{year}")
    print("="*50 + "\n")
    
    # Step 1: เปิด Chrome โดยตรง (ไม่ถาม browser)
    print("\n[STEP 1] Opening Chrome directly...")
    import subprocess
    # ใช้ -n เพื่อระบุ component โดยตรง ไม่ถาม browser chooser
    subprocess.run([
        "adb", "shell", "am", "start", 
        "-n", "com.android.chrome/com.google.android.apps.chrome.Main",
        "-a", "android.intent.action.VIEW",
        "-d", SIGNUP_URL
    ], capture_output=True)
    
    print("[*] Waiting for page to load...")
    time.sleep(6)
    dump(driver, "step1.xml")
    shot(driver, "step1")
    
    # Step 2: กรอก Email
    print("\n[STEP 2] Entering email...")
    # รอหน้าโหลด
    wait_for(driver, "อีเมล", 15)
    
    # หา input field (อาจเป็น floatingLabelInput4 หรืออื่นๆ)
    try:
        inputs = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
        # หา input ที่ไม่ใช่ URL bar
        for inp in inputs:
            rid = inp.get_attribute("resource-id") or ""
            if "floatingLabel" in rid or "url_bar" not in rid:
                if "url_bar" not in rid:
                    inp.clear()
                    inp.send_keys(email)
                    print(f"[TYPE] email = {email}")
                    break
    except Exception as e:
        print(f"[ERROR] {e}")
    
    time.sleep(1)
    shot(driver, "step2_email")
    
    # กดปุ่มถัดไป
    tap_text(driver, "ถัดไป")
    time.sleep(3)
    dump(driver, "step2.xml")
    shot(driver, "step2_next")
    
    # Step 3: กรอก Password
    print("\n[STEP 3] Entering password...")
    wait_for(driver, "รหัสผ่าน", 10)
    
    try:
        inputs = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
        for inp in inputs:
            rid = inp.get_attribute("resource-id") or ""
            if "url_bar" not in rid:
                inp.clear()
                inp.send_keys(password)
                print(f"[TYPE] password = {password}")
                break
    except Exception as e:
        print(f"[ERROR] {e}")
    
    time.sleep(1)
    shot(driver, "step3_password")
    
    tap_text(driver, "ถัดไป")
    time.sleep(3)
    dump(driver, "step3.xml")
    shot(driver, "step3_next")
    
    # Step 4: กรอกชื่อ
    print("\n[STEP 4] Entering name...")
    wait_for(driver, "ชื่อ", 10)
    
    try:
        inputs = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
        # กรอก FirstName, LastName
        filled = 0
        for inp in inputs:
            rid = inp.get_attribute("resource-id") or ""
            if "url_bar" not in rid and filled < 2:
                inp.clear()
                if filled == 0:
                    inp.send_keys("สมชาย")
                    print("[TYPE] FirstName = สมชาย")
                else:
                    inp.send_keys("ใจดี")
                    print("[TYPE] LastName = ใจดี")
                filled += 1
    except Exception as e:
        print(f"[ERROR] {e}")
    
    time.sleep(1)
    shot(driver, "step4_name")
    
    tap_text(driver, "ถัดไป")
    time.sleep(3)
    dump(driver, "step4.xml")
    shot(driver, "step4_next")
    
    # Step 5: วันเกิด
    print("\n[STEP 5] Entering birthday...")
    wait_for(driver, "วัน", 10)
    dump(driver, "step5_before.xml")
    
    # ต้องดู XML ก่อนว่า dropdown เป็นยังไง
    # อาจต้อง tap ที่ dropdown แล้วเลือก
    shot(driver, "step5_birthday")
    
    print("\n[!] ถึง Birthday แล้ว - ต้องดู XML ก่อน")
    print("[!] ดูไฟล์ step5_before.xml แล้วแก้ script")
    
    return email, password

# ============ MAIN ============
if __name__ == "__main__":
    driver = connect()
    
    try:
        email, password = register(driver)
        
        print("\n" + "="*50)
        print(" สรุป:")
        print(f" Email: {email}@outlook.co.th")
        print(f" Password: {password}")
        print("="*50)
        
        input("\n[DONE] กด Enter เพื่อปิด...")
        
    except Exception as e:
        print(f"\n[FATAL] {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[*] Done")
