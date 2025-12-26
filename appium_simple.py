"""
Simple Appium - ดู XML แล้ว tap ไปเรื่อยๆ
ไม่ใช้ WebView - ใช้ Native mode อย่างเดียว
"""
import time
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy

# ============ CONFIG ============
APPIUM_SERVER = "http://127.0.0.1:4723"  # Appium 2.x ไม่ใช้ /wd/hub
DEVICE_UDID = "ce0617164481141b0d7e"

# ============ DRIVER ============
def connect():
    """เชื่อมต่อ Appium"""
    options = AppiumOptions()
    options.set_capability("platformName", "Android")
    options.set_capability("automationName", "UiAutomator2")
    options.set_capability("deviceName", DEVICE_UDID)
    options.set_capability("udid", DEVICE_UDID)
    options.set_capability("noReset", True)
    options.set_capability("newCommandTimeout", 600)
    
    # ไม่ระบุ app - ใช้หน้าจอปัจจุบัน
    
    print("[*] Connecting...")
    driver = webdriver.Remote(APPIUM_SERVER, options=options)
    print("[+] Connected!")
    return driver

# ============ ACTIONS ============
def dump(driver):
    """แสดง XML ของหน้าจอ"""
    xml = driver.page_source
    print("\n" + "="*60)
    print(xml[:5000])  # แสดงแค่ 5000 ตัวอักษรแรก
    print("="*60)
    
    # บันทึกไฟล์
    with open("page_dump.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    print("[+] Saved to page_dump.xml")

def tap(driver, x, y):
    """Tap ที่ตำแหน่ง x, y"""
    driver.tap([(x, y)])
    print(f"[+] Tapped ({x}, {y})")

def tap_text(driver, text):
    """Tap element ที่มี text"""
    try:
        el = driver.find_element(AppiumBy.XPATH, f"//*[@text='{text}']")
        el.click()
        print(f"[+] Tapped: {text}")
        return True
    except:
        print(f"[-] Not found: {text}")
        return False

def tap_id(driver, resource_id):
    """Tap element ที่มี resource-id"""
    try:
        # ถ้าไม่มี package prefix ให้เพิ่ม
        if ":" not in resource_id:
            resource_id = f"com.android.chrome:id/{resource_id}"
        el = driver.find_element(AppiumBy.ID, resource_id)
        el.click()
        print(f"[+] Tapped ID: {resource_id}")
        return True
    except:
        print(f"[-] Not found ID: {resource_id}")
        return False

def type_text(driver, text):
    """พิมพ์ข้อความลง element ที่ focused"""
    driver.press_keycode(0)  # wake
    for char in text:
        driver.press_keycode(ord(char))
    print(f"[+] Typed: {text}")

def input_text(driver, resource_id, text):
    """พิมพ์ข้อความลง element"""
    try:
        if ":" not in resource_id:
            resource_id = f"com.android.chrome:id/{resource_id}"
        el = driver.find_element(AppiumBy.ID, resource_id)
        el.clear()
        el.send_keys(text)
        print(f"[+] Input: {text}")
        return True
    except:
        print(f"[-] Input failed: {resource_id}")
        return False

def enter(driver):
    """กด Enter"""
    driver.press_keycode(66)
    print("[+] Pressed Enter")

def back(driver):
    """กด Back"""
    driver.press_keycode(4)
    print("[+] Pressed Back")

def screenshot(driver, name="screen"):
    """ถ่ายภาพหน้าจอ"""
    filename = f"{name}_{int(time.time())}.png"
    driver.save_screenshot(filename)
    print(f"[+] Screenshot: {filename}")

def swipe_up(driver):
    """Swipe ขึ้น"""
    size = driver.get_window_size()
    x = size['width'] // 2
    driver.swipe(x, size['height']*0.7, x, size['height']*0.3, 500)
    print("[+] Swiped up")

def swipe_down(driver):
    """Swipe ลง"""
    size = driver.get_window_size()
    x = size['width'] // 2
    driver.swipe(x, size['height']*0.3, x, size['height']*0.7, 500)
    print("[+] Swiped down")

def find_all(driver, text_contains=""):
    """หา elements ทั้งหมด"""
    if text_contains:
        els = driver.find_elements(AppiumBy.XPATH, f"//*[contains(@text,'{text_contains}')]")
    else:
        els = driver.find_elements(AppiumBy.XPATH, "//*[@clickable='true']")
    
    print(f"\n[*] Found {len(els)} elements:")
    for i, el in enumerate(els[:20]):
        try:
            text = el.get_attribute("text") or ""
            cls = el.get_attribute("class").split(".")[-1]
            bounds = el.get_attribute("bounds")
            print(f"  {i}: [{cls}] {text[:30]} {bounds}")
        except:
            pass
    return els

# ============ INTERACTIVE MODE ============
def interactive(driver):
    """โหมด Interactive - พิมพ์คำสั่งเอง"""
    print("\n" + "="*60)
    print(" INTERACTIVE MODE")
    print("="*60)
    print(" Commands:")
    print("   dump          - แสดง XML")
    print("   tap X Y       - Tap ที่ตำแหน่ง")
    print("   tap_text TEXT - Tap ที่ text")
    print("   tap_id ID     - Tap ที่ resource-id")
    print("   input ID TEXT - พิมพ์ข้อความ")
    print("   enter         - กด Enter")
    print("   back          - กด Back")
    print("   up/down       - Swipe")
    print("   find TEXT     - หา elements")
    print("   shot          - Screenshot")
    print("   url URL       - เปิด URL ใน Chrome")
    print("   q             - ออก")
    print("="*60)
    
    while True:
        try:
            cmd = input("\n> ").strip()
            
            if not cmd:
                continue
            elif cmd == "q":
                break
            elif cmd == "dump":
                dump(driver)
            elif cmd.startswith("tap "):
                parts = cmd.split()
                if len(parts) == 3:
                    tap(driver, int(parts[1]), int(parts[2]))
                else:
                    print("Usage: tap X Y")
            elif cmd.startswith("tap_text "):
                tap_text(driver, cmd[9:])
            elif cmd.startswith("tap_id "):
                tap_id(driver, cmd[7:])
            elif cmd.startswith("input "):
                parts = cmd.split(" ", 2)
                if len(parts) == 3:
                    input_text(driver, parts[1], parts[2])
                else:
                    print("Usage: input ID TEXT")
            elif cmd == "enter":
                enter(driver)
            elif cmd == "back":
                back(driver)
            elif cmd == "up":
                swipe_up(driver)
            elif cmd == "down":
                swipe_down(driver)
            elif cmd.startswith("find"):
                text = cmd[5:].strip() if len(cmd) > 5 else ""
                find_all(driver, text)
            elif cmd == "shot":
                screenshot(driver)
            elif cmd.startswith("url "):
                url = cmd[4:]
                # เปิด Chrome กับ URL
                driver.execute_script("mobile: shell", {
                    "command": "am",
                    "args": ["start", "-a", "android.intent.action.VIEW", "-d", url]
                })
                print(f"[+] Opening: {url}")
            else:
                print(f"Unknown: {cmd}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[-] Error: {e}")

# ============ MAIN ============
if __name__ == "__main__":
    driver = connect()
    
    try:
        # เริ่ม interactive mode
        interactive(driver)
    finally:
        print("\n[*] Done")
