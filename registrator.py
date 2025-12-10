# ===== MAIN REGISTRATOR =====

import threading
import time
from datetime import datetime

from browser import BrowserManager
from captcha_solver import CaptchaSolver, inject_captcha_token
from data import generate_password, generate_username, get_random_name, get_random_birthdate
from config import (
    EMAIL_DOMAIN, OUTPUT_FILE, WAIT_BETWEEN_ACTIONS, 
    WAIT_FOR_CAPTCHA
)


class AccountRegistrator(threading.Thread):
    """Class หลักสำหรับสร้างบัญชี"""
    
    def __init__(self, proxy=None, position_x=0, position_y=0, name_type="thai"):
        threading.Thread.__init__(self)
        self.proxy = proxy
        self.position_x = position_x
        self.position_y = position_y
        self.name_type = name_type
        
        # Account data
        self.username = None
        self.email = None
        self.password = None
        self.first_name = None
        self.last_name = None
        self.birth_day = None
        self.birth_month = None
        self.birth_year = None
        
        # Status
        self.success = False
        self.error_message = None
    
    def generate_account_data(self):
        """สร้างข้อมูลบัญชี"""
        self.username = generate_username()
        self.email = self.username + EMAIL_DOMAIN
        self.password = generate_password()
        self.first_name, self.last_name = get_random_name(self.name_type)
        self.birth_day, self.birth_month, self.birth_year = get_random_birthdate()
        
        print(f"[NEW] {self.email}")
    
    def save_account(self):
        """บันทึกบัญชีที่สร้างสำเร็จ"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{self.email}|{self.password}|{self.first_name} {self.last_name}|{timestamp}\n"
        
        with open(OUTPUT_FILE, "a+", encoding="utf-8") as f:
            f.write(line)
        
        print(f"[SAVED] {self.email}")
    
    def run(self):
        """Main process"""
        browser = None
        
        try:
            # Generate data
            self.generate_account_data()
            
            # Start browser
            browser = BrowserManager(
                proxy=self.proxy,
                position_x=self.position_x,
                position_y=self.position_y
            )
            driver = browser.start()
            
            # Go to signup page
            browser.go_to_signup()
            time.sleep(WAIT_BETWEEN_ACTIONS)
            
            # Step 1: Enter email
            print(f"[STEP 1] Entering email: {self.email}")
            browser.fill_input("MemberName", self.email)
            time.sleep(WAIT_BETWEEN_ACTIONS)
            browser.click_element("iSignupAction")
            time.sleep(3)
            
            # Step 2: Enter password  
            print(f"[STEP 2] Entering password")
            browser.fill_input("PasswordInput", self.password)
            time.sleep(WAIT_BETWEEN_ACTIONS)
            browser.click_element("iSignupAction")
            time.sleep(3)
            
            # Step 3: Enter name
            print(f"[STEP 3] Entering name: {self.first_name} {self.last_name}")
            browser.fill_input("FirstName", self.first_name)
            time.sleep(WAIT_BETWEEN_ACTIONS)
            browser.fill_input("LastName", self.last_name)
            time.sleep(WAIT_BETWEEN_ACTIONS)
            browser.click_element("iSignupAction")
            time.sleep(3)
            
            # Step 4: Enter birthdate
            print(f"[STEP 4] Entering birthdate: {self.birth_day}/{self.birth_month}/{self.birth_year}")
            browser.select_dropdown("BirthMonth", self.birth_month)
            time.sleep(WAIT_BETWEEN_ACTIONS)
            browser.select_dropdown("BirthDay", self.birth_day)
            time.sleep(WAIT_BETWEEN_ACTIONS)
            browser.fill_input("BirthYear", str(self.birth_year))
            time.sleep(WAIT_BETWEEN_ACTIONS)
            browser.click_element("iSignupAction")
            time.sleep(3)
            
            # Check for phone verification (fail case)
            if browser.check_page_contains("We'll text you the code"):
                print(f"[FAIL] Phone verification required - {self.email}")
                self.error_message = "Phone verification required"
                return
            
            # Step 5: Solve captcha
            print(f"[STEP 5] Waiting for captcha...")
            time.sleep(WAIT_FOR_CAPTCHA)
            
            solver = CaptchaSolver()
            token = solver.solve()
            
            if not token:
                print(f"[FAIL] Captcha solve failed - {self.email}")
                self.error_message = "Captcha failed"
                return
            
            # Inject token
            inject_captcha_token(driver, token)
            time.sleep(10)
            
            # Check success
            if browser.check_page_contains("Stay signed in?"):
                print(f"[SUCCESS] Account created: {self.email}")
                self.success = True
                self.save_account()
                
                browser.click_element("idSIButton9")
                time.sleep(3)
            else:
                print(f"[FAIL] Unknown error - {self.email}")
                self.error_message = "Unknown error after captcha"
                
        except Exception as e:
            print(f"[ERROR] {self.email}: {e}")
            self.error_message = str(e)
            
        finally:
            if browser:
                browser.close()


def run_batch(proxy, num_accounts=3, name_type="thai"):
    """รัน batch สร้างหลายบัญชีพร้อมกัน"""
    threads = []
    
    for i in range(num_accounts):
        position_x = i * 280  # จัด window ไม่ให้ทับกัน
        
        registrator = AccountRegistrator(
            proxy=proxy,
            position_x=position_x,
            position_y=0,
            name_type=name_type
        )
        registrator.start()
        threads.append(registrator)
    
    # รอทุก thread เสร็จ
    for t in threads:
        t.join()
    
    # สรุปผล
    success_count = sum(1 for t in threads if t.success)
    print(f"\n[BATCH DONE] Success: {success_count}/{num_accounts}")
    
    return success_count
