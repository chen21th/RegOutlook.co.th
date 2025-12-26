"""
GPMLogin + mProxy Vietnam - Outlook.co.th Registration
"""
import requests
import time
import random
import string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ============== CONFIG ==============
GPM_API = "http://127.0.0.1:19995/api/v3"
MPROXY_API_KEY = "8R5UzvmVYS0CWTLra1uqamdcz0EWkTt661QROumurgg"
MPROXY_API = f"https://mproxy.vn/capi/{MPROXY_API_KEY}"

# GPMLogin Profile ID
PROFILE_ID = "35aa3eaa-2d3b-4f04-a91e-a593de252d07"

# 2Captcha API
CAPTCHA_API_KEY = "f5cb74cff21d8caef0af74e953124f12"

# Thai names for registration
THAI_NAMES = [
    ("สมชาย", "ใจดี"), ("สมหญิง", "รักเรียน"), ("วิชัย", "มั่นคง"),
    ("สุดา", "งามตา"), ("ประเสริฐ", "ศรีสุข"), ("นภา", "พรหมมา"),
    ("อนันต์", "ทองดี"), ("พิมพ์", "สุขใจ"), ("ชัยวัฒน์", "เจริญ"),
    ("รัตนา", "วงศ์ไทย"), ("กิตติ", "สว่าง"), ("มาลี", "ดอกไม้"),
]


class MProxyManager:
    """Manage mProxy Vietnam API"""
    
    def __init__(self):
        self.current_key = None
    
    def get_keys(self):
        """Get all proxy keys"""
        resp = requests.get(f"{MPROXY_API}/keys")
        data = resp.json()
        if data.get("status") == 1:
            return data.get("data", [])
        return []
    
    def get_balance(self):
        """Get account balance"""
        resp = requests.get(f"{MPROXY_API}/balance")
        data = resp.json()
        if data.get("status") == 1:
            return data["data"]["balance"]
        return 0
    
    def buy_key(self, package_id=2):
        """Buy new proxy key (default: 1 day package)"""
        resp = requests.get(f"{MPROXY_API}/buy/{package_id}")
        data = resp.json()
        if data.get("status") == 1:
            self.current_key = data["data"]
            return self.current_key
        return None
    
    def reset_ip(self, key_code):
        """Reset IP (get new IP)"""
        resp = requests.get(f"{MPROXY_API}/key/{key_code}/resetIp")
        data = resp.json()
        if data.get("status") == 1:
            return data["data"]
        return None
    
    def get_proxy_string(self, key_data):
        """Get proxy string from key data"""
        return key_data.get("proxy")  # format: user:pass@host:port


class GPMLoginManager:
    """Manage GPMLogin profiles"""
    
    def __init__(self):
        self.driver = None
        self.profile_data = None
    
    def list_profiles(self):
        """List all profiles"""
        resp = requests.get(f"{GPM_API}/profiles")
        if resp.json().get("success"):
            return resp.json().get("data", [])
        return []
    
    def update_proxy(self, profile_id, proxy_string):
        """Update profile with new proxy
        proxy_string format: user:pass@host:port
        GPMLogin format: host:port:user:pass
        """
        # Parse proxy string (user:pass@host:port -> host:port:user:pass)
        if "@" in proxy_string:
            auth, hostport = proxy_string.split("@")
            user, passwd = auth.split(":")
            host, port = hostport.split(":")
            proxy_string = f"{host}:{port}:{user}:{passwd}"
        
        data = {
            "proxy_type": "http",
            "raw_proxy": proxy_string  # Use raw_proxy instead of proxy
        }
        resp = requests.post(f"{GPM_API}/profiles/update/{profile_id}", json=data)
        return resp.json().get("success", False)
    
    def start_profile(self, profile_id):
        """Start a profile and return browser connection info"""
        resp = requests.get(f"{GPM_API}/profiles/start/{profile_id}")
        data = resp.json()
        if data.get("success"):
            self.profile_data = data["data"]
            return self.profile_data
        return None
    
    def close_profile(self, profile_id):
        """Close a running profile"""
        resp = requests.get(f"{GPM_API}/profiles/close/{profile_id}")
        return resp.json().get("success", False)
    
    def connect_selenium(self):
        """Connect Selenium to running GPMLogin browser"""
        if not self.profile_data:
            raise Exception("Profile not started")
        
        debug_address = self.profile_data["remote_debugging_address"]
        driver_path = self.profile_data["driver_path"]
        
        options = Options()
        options.add_experimental_option("debuggerAddress", debug_address)
        
        service = Service(executable_path=driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        return self.driver


class OutlookRegistrator:
    """Register Outlook.co.th accounts"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)
    
    def generate_email(self):
        """Generate random email"""
        chars = string.ascii_lowercase + string.digits
        username = ''.join(random.choices(chars, k=random.randint(8, 12)))
        return f"{username}@outlook.co.th"
    
    def generate_password(self):
        """Generate random password"""
        chars = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(random.choices(chars, k=14))
    
    def register(self):
        """Main registration flow"""
        email = self.generate_email()
        password = self.generate_password()
        first_name, last_name = random.choice(THAI_NAMES)
        
        print(f"[INFO] Registering: {email}")
        print(f"[INFO] Name: {first_name} {last_name}")
        
        # Go to signup page
        self.driver.get("https://signup.live.com/signup?mkt=th-th&lic=1")
        time.sleep(3)
        
        try:
            # Step 1: Enter email
            print("[INFO] Step 1: Entering email...")
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "usernameInput"))
            )
            email_input.clear()
            email_input.send_keys(email.split("@")[0])  # Just username part
            time.sleep(1)
            
            # Click Next
            next_btn = self.driver.find_element(By.ID, "nextButton")
            next_btn.click()
            time.sleep(2)
            
            # Step 2: Enter password
            print("[INFO] Step 2: Entering password...")
            pwd_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "Password"))
            )
            pwd_input.send_keys(password)
            time.sleep(1)
            
            next_btn = self.driver.find_element(By.ID, "nextButton")
            next_btn.click()
            time.sleep(2)
            
            # Step 3: Enter name
            print("[INFO] Step 3: Entering name...")
            first_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "firstNameInput"))
            )
            first_input.send_keys(first_name)
            
            last_input = self.driver.find_element(By.ID, "lastNameInput")
            last_input.send_keys(last_name)
            time.sleep(1)
            
            next_btn = self.driver.find_element(By.ID, "nextButton")
            next_btn.click()
            time.sleep(2)
            
            # Step 4: Birthday
            print("[INFO] Step 4: Entering birthday...")
            # Select country (Thailand)
            country_select = self.wait.until(
                EC.presence_of_element_located((By.ID, "countryRegion"))
            )
            country_select.click()
            time.sleep(0.5)
            
            # Select TH
            th_option = self.driver.find_element(By.CSS_SELECTOR, "option[value='TH']")
            th_option.click()
            time.sleep(0.5)
            
            # Birth month
            month_select = self.driver.find_element(By.ID, "birthMonth")
            month_select.click()
            month_option = self.driver.find_element(By.CSS_SELECTOR, f"#birthMonth option[value='{random.randint(1,12)}']")
            month_option.click()
            
            # Birth day
            day_select = self.driver.find_element(By.ID, "birthDay")
            day_select.click()
            day_option = self.driver.find_element(By.CSS_SELECTOR, f"#birthDay option[value='{random.randint(1,28)}']")
            day_option.click()
            
            # Birth year
            year_select = self.driver.find_element(By.ID, "birthYear")
            year_select.click()
            year_option = self.driver.find_element(By.CSS_SELECTOR, f"#birthYear option[value='{random.randint(1985,2000)}']")
            year_option.click()
            time.sleep(1)
            
            next_btn = self.driver.find_element(By.ID, "nextButton")
            next_btn.click()
            time.sleep(3)
            
            # Step 5: Captcha
            print("[INFO] Step 5: Waiting for captcha...")
            print("[INFO] >>> Please solve captcha manually or wait for auto-solve <<<")
            
            # Wait for captcha to appear and be solved
            # After captcha, should redirect to success page
            time.sleep(60)  # Wait for manual solving
            
            # Check if registration successful
            if "outlook.live.com" in self.driver.current_url:
                print(f"[SUCCESS] Account created: {email}|{password}|{first_name} {last_name}")
                return {
                    "success": True,
                    "email": email,
                    "password": password,
                    "name": f"{first_name} {last_name}"
                }
            else:
                print(f"[FAIL] Registration failed")
                return {"success": False, "error": "Unknown error"}
                
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            return {"success": False, "error": str(e)}


def main():
    print("=" * 50)
    print("GPMLogin + mProxy Vietnam - Outlook Registration")
    print("=" * 50)
    
    # Initialize managers
    mproxy = MProxyManager()
    gpm = GPMLoginManager()
    
    # Check mProxy balance
    balance = mproxy.get_balance()
    print(f"[INFO] mProxy Balance: {balance:,} VND")
    
    # Get current keys
    keys = mproxy.get_keys()
    if keys:
        print(f"[INFO] Found {len(keys)} proxy key(s)")
        current_key = keys[0]  # Use first key
        proxy_str = current_key.get("proxy")
        print(f"[INFO] Using proxy: {proxy_str}")
        
        # Reset IP for fresh start
        print("[INFO] Resetting IP...")
        reset_result = mproxy.reset_ip(current_key["key_code"])
        if reset_result:
            proxy_str = reset_result.get("proxy")
            print(f"[INFO] New IP assigned")
    else:
        print("[WARN] No proxy keys found!")
        proxy_str = None
    
    # Update GPMLogin profile with proxy
    if proxy_str:
        print(f"[INFO] Updating GPMLogin profile with proxy...")
        gpm.update_proxy(PROFILE_ID, proxy_str)
    
    # Start GPMLogin profile
    print("[INFO] Starting GPMLogin profile...")
    profile_data = gpm.start_profile(PROFILE_ID)
    
    if not profile_data:
        print("[ERROR] Failed to start profile")
        return
    
    print(f"[INFO] Browser started at: {profile_data['remote_debugging_address']}")
    
    # Connect Selenium
    print("[INFO] Connecting Selenium...")
    driver = gpm.connect_selenium()
    
    # Check IP
    driver.get("http://ip-api.com/json")
    time.sleep(2)
    print(f"[INFO] Current IP info: {driver.find_element(By.TAG_NAME, 'body').text[:200]}")
    
    # Start registration
    registrator = OutlookRegistrator(driver)
    result = registrator.register()
    
    if result["success"]:
        # Save to file
        with open("accounts.txt", "a", encoding="utf-8") as f:
            f.write(f"{result['email']}|{result['password']}|{result['name']}\n")
        print(f"[SUCCESS] Saved to accounts.txt")
    
    # Ask to close
    input("\nPress Enter to close browser...")
    gpm.close_profile(PROFILE_ID)
    print("[INFO] Done!")


if __name__ == "__main__":
    main()
