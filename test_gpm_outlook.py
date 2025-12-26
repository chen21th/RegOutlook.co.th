"""
Test GPMLogin Browser with Outlook.co.th Registration
"""
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

GPM_API = "http://127.0.0.1:19995/api/v3"

def get_profiles():
    """Get list of profiles"""
    resp = requests.get(f"{GPM_API}/profiles")
    return resp.json()

def start_profile(profile_id):
    """Start a profile and get connection info"""
    resp = requests.get(f"{GPM_API}/profiles/start/{profile_id}")
    return resp.json()

def close_profile(profile_id):
    """Close a profile"""
    resp = requests.get(f"{GPM_API}/profiles/close/{profile_id}")
    return resp.json()

def connect_selenium(debug_address, driver_path):
    """Connect Selenium to GPMLogin browser"""
    options = Options()
    options.debugger_address = debug_address
    
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def main():
    # Get profiles
    print("[INFO] Getting profiles...")
    profiles = get_profiles()
    
    if not profiles['success'] or not profiles['data']:
        print("[ERROR] No profiles found!")
        return
    
    profile = profiles['data'][0]
    profile_id = profile['id']
    print(f"[INFO] Found profile: {profile['name']} ({profile_id})")
    
    # Start profile
    print("[INFO] Starting profile...")
    result = start_profile(profile_id)
    
    if not result['success']:
        print(f"[ERROR] Failed to start: {result.get('message')}")
        return
    
    data = result['data']
    debug_address = data['remote_debugging_address']
    driver_path = data['driver_path']
    
    print(f"[INFO] Browser started!")
    print(f"[INFO] Debug address: {debug_address}")
    print(f"[INFO] Driver path: {driver_path}")
    
    # Connect Selenium
    print("[INFO] Connecting Selenium...")
    driver = connect_selenium(debug_address, driver_path)
    
    try:
        # Navigate to Outlook signup
        print("[INFO] Opening Outlook Thailand signup...")
        driver.get("https://signup.live.com/signup?mkt=th-th&lic=1")
        
        time.sleep(3)
        
        # Wait for email input
        print("[INFO] Waiting for email field...")
        wait = WebDriverWait(driver, 30)
        
        email_input = wait.until(
            EC.presence_of_element_located((By.ID, "usernameInput"))
        )
        
        # Generate test email
        import random
        import string
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"testgpm{random_str}"
        
        print(f"[INFO] Entering email: {test_email}@outlook.co.th")
        email_input.clear()
        email_input.send_keys(test_email)
        
        time.sleep(1)
        
        # Click Next
        print("[INFO] Clicking Next...")
        next_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "iSignupAction"))
        )
        next_btn.click()
        
        time.sleep(3)
        
        # Check if we passed or got blocked
        current_url = driver.current_url
        page_source = driver.page_source
        
        if "password" in page_source.lower() or "รหัสผ่าน" in page_source:
            print("[SUCCESS] Reached password page! GPMLogin is working!")
        elif "captcha" in page_source.lower() or "ยืนยัน" in page_source:
            print("[INFO] Captcha page - but we got past email!")
        else:
            print(f"[INFO] Current URL: {current_url}")
            print("[INFO] Checking page status...")
        
        # Keep browser open for manual check
        print("\n[INFO] Browser is open. Check manually if needed.")
        print("[INFO] Press Enter to close...")
        input()
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
        print("[INFO] Closing profile...")
        close_profile(profile_id)
        print("[INFO] Done!")

if __name__ == "__main__":
    main()
