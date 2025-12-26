"""
ทดสอบ Appium แบบง่ายๆ - ใช้ Native mode ควบคุม Kiwi Browser
ไม่ต้อง switch WebView - ใช้ accessibility/UiAutomator2 ในการหา elements
"""
import time
import random
import string
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ============ CONFIG ============
APPIUM_SERVER = "http://127.0.0.1:4723/wd/hub"
DEVICE_UDID = "ce0617164481141b0d7e"
KIWI_PACKAGE = "com.kiwibrowser.browser"
KIWI_ACTIVITY = "org.chromium.chrome.browser.ChromeTabbedActivity"

SIGNUP_URL = "https://signup.live.com/signup?mkt=th-th&lic=1"

# ============ DRIVER ============
def create_driver():
    """สร้าง Appium driver"""
    options = AppiumOptions()
    options.set_capability("platformName", "Android")
    options.set_capability("automationName", "UiAutomator2")
    options.set_capability("deviceName", DEVICE_UDID)
    options.set_capability("udid", DEVICE_UDID)
    options.set_capability("appPackage", KIWI_PACKAGE)
    options.set_capability("appActivity", KIWI_ACTIVITY)
    options.set_capability("noReset", True)
    options.set_capability("autoGrantPermissions", True)
    options.set_capability("newCommandTimeout", 300)
    
    print(f"[INFO] Connecting to Appium: {APPIUM_SERVER}")
    driver = webdriver.Remote(APPIUM_SERVER, options=options)
    print("[SUCCESS] Connected!")
    return driver

# ============ HELPER ============
def click_if_exists(driver, xpath, timeout=3):
    """กด element ถ้าเจอ"""
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.XPATH, xpath))
        )
        el.click()
        return True
    except:
        return False

def type_text(driver, xpath, text, timeout=10):
    """พิมพ์ข้อความลงใน element"""
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.XPATH, xpath))
        )
        el.clear()
        time.sleep(0.3)
        el.send_keys(text)
        return True
    except Exception as e:
        print(f"[ERROR] Type failed: {e}")
        return False

def find_and_click_text(driver, text, timeout=10):
    """หา element ที่มี text แล้วกด"""
    try:
        xpath = f"//*[@text='{text}']"
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.XPATH, xpath))
        )
        el.click()
        return True
    except:
        # ลอง content-desc
        try:
            xpath = f"//*[@content-desc='{text}']"
            el = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((AppiumBy.XPATH, xpath))
            )
            el.click()
            return True
        except:
            return False

def scroll_down(driver):
    """Scroll ลง"""
    size = driver.get_window_size()
    start_x = size['width'] // 2
    start_y = size['height'] * 0.8
    end_y = size['height'] * 0.2
    driver.swipe(start_x, int(start_y), start_x, int(end_y), 500)

def take_screenshot(driver, name):
    """ถ่ายภาพหน้าจอ"""
    filename = f"{name}_{int(time.time())}.png"
    driver.save_screenshot(filename)
    print(f"[SCREENSHOT] {filename}")
    return filename

def dump_page(driver):
    """แสดง elements ในหน้าปัจจุบัน"""
    print("\n[PAGE DUMP]")
    
    # หา elements ที่มี text
    try:
        elements = driver.find_elements(AppiumBy.XPATH, "//*[@text!='']")
        print(f"Elements with text ({len(elements)}):")
        for el in elements[:20]:
            try:
                text = el.get_attribute("text")
                cls = el.get_attribute("class").split(".")[-1]
                print(f"  [{cls}] {text[:50]}")
            except:
                pass
    except:
        pass
    
    # หา EditText
    try:
        inputs = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
        print(f"\nEditText fields ({len(inputs)}):")
        for inp in inputs:
            try:
                text = inp.get_attribute("text") or inp.get_attribute("hint") or "(empty)"
                rid = inp.get_attribute("resource-id") or "no-id"
                print(f"  ID: {rid.split('/')[-1]} | Text: {text[:30]}")
            except:
                pass
    except:
        pass

# ============ MAIN TEST ============
def test_navigate_to_signup():
    """ทดสอบไปหน้า signup"""
    driver = create_driver()
    
    try:
        # กด Continue ถ้ามีหน้า Welcome
        time.sleep(2)
        if click_if_exists(driver, "//*[@text='Continue']"):
            print("[INFO] Clicked Continue button")
            time.sleep(2)
        
        # ไปหน้า signup
        print(f"\n[STEP] Navigating to: {SIGNUP_URL}")
        
        # กด search box
        search_box = driver.find_element(AppiumBy.ID, "com.kiwibrowser.browser:id/search_box_text")
        search_box.click()
        time.sleep(0.5)
        
        # หา URL bar (หลังกด search box จะเปลี่ยนเป็น URL bar)
        try:
            url_bar = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((AppiumBy.ID, "com.kiwibrowser.browser:id/url_bar"))
            )
            url_bar.clear()
            url_bar.send_keys(SIGNUP_URL)
        except:
            # ถ้าหาไม่เจอ ใช้ search_box_text เลย
            search_box.send_keys(SIGNUP_URL)
        
        time.sleep(0.5)
        driver.press_keycode(66)  # Enter
        
        print("[SUCCESS] URL submitted!")
        
        # รอหน้าโหลด
        print("[INFO] Waiting for page to load...")
        time.sleep(8)
        
        take_screenshot(driver, "01_signup_loaded")
        dump_page(driver)
        
        # รอให้ user ดู
        input("\n[PAUSE] กด Enter เพื่อทำต่อ...")
        
        # ลองกรอก email
        print("\n[STEP] Looking for email input...")
        dump_page(driver)
        
        # หา EditText สำหรับ email
        inputs = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
        print(f"Found {len(inputs)} EditText fields")
        
        if len(inputs) > 1:  # ข้ามอันแรก (URL bar)
            email_input = inputs[1]
            test_email = "test" + str(random.randint(1000, 9999))
            print(f"[INFO] Trying to type: {test_email}")
            email_input.click()
            time.sleep(0.3)
            email_input.send_keys(test_email)
            print("[SUCCESS] Email entered!")
            
            take_screenshot(driver, "02_email_entered")
        
        input("\n[END] กด Enter เพื่อปิด...")
        
    finally:
        print("[INFO] Session ended")
        # driver.quit()

if __name__ == "__main__":
    test_navigate_to_signup()
