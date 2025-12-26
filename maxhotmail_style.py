"""
MaxHotmail Style - Outlook.co.th Registration
Based on MaxHotmailPro_v25.03.09 flow
"""
import os
import sys
import time
import random
import string
import shutil
import subprocess
import requests
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

# ============== CONFIG ==============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILES_DIR = os.path.join(BASE_DIR, "chrome_profiles")
OUTPUT_FILE = os.path.join(BASE_DIR, "accounts.txt")

# OAuth2 Config (Custom Azure App)
OAUTH_CLIENT_ID = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
OAUTH_REDIRECT_URI = "https://login.live.com/oauth20_desktop.srf"
OAUTH_SCOPE = "offline_access https://outlook.office.com/Mail.ReadWrite"
FUNCAPTCHA_PUBLIC_KEY = "B7D8911C-5CC8-A9A3-35B0-554ACEE604DA"

# 2Captcha API
CAPTCHA_API_KEY = "f5cb74cff21d8caef0af74e953124f12"

# mProxy Vietnam
MPROXY_API_KEY = "8R5UzvmVYS0CWTLra1uqamdcz0EWkTt661QROumurgg"

# Thai Names
THAI_FIRST_NAMES = [
    "สมชาย", "สมหญิง", "วิชัย", "สุดา", "ประเสริฐ", "นภา", "อนันต์", "พิมพ์",
    "ชัยวัฒน์", "รัตนา", "กิตติ", "มาลี", "วีระ", "สุภา", "ธนา", "จันทร์",
    "พงศ์", "แก้ว", "บุญ", "ทอง", "เพชร", "ดาว", "นาค", "สิงห์",
    "วรรณ", "ศรี", "สุข", "ชัย", "พร", "มณี", "รุ่ง", "แสง"
]
THAI_LAST_NAMES = [
    "ใจดี", "รักเรียน", "มั่นคง", "งามตา", "ศรีสุข", "พรหมมา", "ทองดี", "สุขใจ",
    "เจริญ", "วงศ์ไทย", "สว่าง", "ดอกไม้", "แสงทอง", "มีชัย", "ศรีวิชัย", "พันธ์ดี",
    "สมบูรณ์", "รุ่งเรือง", "พิทักษ์", "สุขสันต์", "ทองคำ", "เพชรดี", "มณีรัตน์", "ศิริ"
]


class CaptchaSolver:
    """2Captcha FunCaptcha Solver"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://2captcha.com"
    
    def solve_funcaptcha(self, public_key, page_url, surl=None, data_blob=None, timeout=180):
        """Solve FunCaptcha and return token
        
        Args:
            public_key: FunCaptcha site key (e.g. B7D8911C-5CC8-A9A3-35B0-554ACEE604DA)
            page_url: Page URL where captcha appears
            surl: Optional service URL (e.g. https://client-api.arkoselabs.com)
            data_blob: Optional data[blob] value from page
            timeout: Max wait time in seconds (default 180)
        """
        print(f"[CAPTCHA] Sending to 2Captcha...")
        print(f"[CAPTCHA] Public Key: {public_key}")
        print(f"[CAPTCHA] Page URL: {page_url}")
        if surl:
            print(f"[CAPTCHA] Service URL: {surl}")
        
        # Submit task
        submit_url = f"{self.base_url}/in.php"
        params = {
            "key": self.api_key,
            "method": "funcaptcha",
            "publickey": public_key,
            "pageurl": page_url,
            "json": 1
        }
        
        # Add optional parameters
        if surl:
            params["surl"] = surl
        if data_blob:
            params["data[blob]"] = data_blob
        
        try:
            resp = requests.get(submit_url, params=params, timeout=30)
            data = resp.json()
            
            if data.get("status") != 1:
                print(f"[CAPTCHA] Submit error: {data.get('request')}")
                return None
            
            task_id = data.get("request")
            print(f"[CAPTCHA] Task ID: {task_id}")
            
            # Poll for result
            result_url = f"{self.base_url}/res.php"
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                time.sleep(5)
                
                resp = requests.get(result_url, params={
                    "key": self.api_key,
                    "action": "get",
                    "id": task_id,
                    "json": 1
                }, timeout=30)
                
                data = resp.json()
                
                if data.get("status") == 1:
                    token = data.get("request")
                    print(f"[CAPTCHA] Solved! Token: {token[:50]}...")
                    return token
                elif data.get("request") == "CAPCHA_NOT_READY":
                    print(f"[CAPTCHA] Waiting... ({int(time.time() - start_time)}s)")
                else:
                    print(f"[CAPTCHA] Error: {data.get('request')}")
                    return None
            
            print(f"[CAPTCHA] Timeout!")
            return None
            
        except Exception as e:
            print(f"[CAPTCHA] Exception: {e}")
            return None


class OutlookRegistrator:
    """MaxHotmail style Outlook registration"""
    
    def __init__(self, driver, captcha_solver=None):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.captcha_solver = captcha_solver
    
    def delay(self, seconds=1.0):
        """Wait for specified seconds"""
        time.sleep(seconds)
    
    def get_refresh_token(self):
        """Get OAuth2 Refresh Token (MaxHotmailPro style)"""
        print("[OAUTH] Getting Refresh Token...")
        
        try:
            # Build OAuth2 authorize URL
            auth_url = (
                f"https://login.live.com/oauth20_authorize.srf"
                f"?client_id={OAUTH_CLIENT_ID}"
                f"&response_type=code"
                f"&redirect_uri={OAUTH_REDIRECT_URI}"
                f"&scope={OAUTH_SCOPE.replace(' ', '%20')}"
            )
            
            print(f"[OAUTH] Going to authorize URL...")
            self.driver.get(auth_url)
            self.delay(5)
            
            # Wait for redirect with code (up to 30 seconds)
            for i in range(30):
                current_url = self.driver.current_url
                
                # Check if we got redirected with code
                if "code=" in current_url:
                    print(f"[OAUTH] Got authorization code!")
                    
                    # Extract code from URL
                    code_match = re.search(r'code=([^&]+)', current_url)
                    if code_match:
                        auth_code = code_match.group(1)
                        print(f"[OAUTH] Code: {auth_code[:30]}...")
                        
                        # Exchange code for refresh token
                        token_url = "https://login.live.com/oauth20_token.srf"
                        data = {
                            "client_id": OAUTH_CLIENT_ID,
                            "code": auth_code,
                            "redirect_uri": OAUTH_REDIRECT_URI,
                            "grant_type": "authorization_code"
                        }
                        
                        resp = requests.post(token_url, data=data, timeout=30)
                        token_data = resp.json()
                        
                        if "refresh_token" in token_data:
                            refresh_token = token_data["refresh_token"]
                            print(f"[OAUTH] Refresh Token: {refresh_token[:50]}...")
                            return refresh_token, OAUTH_CLIENT_ID
                        else:
                            print(f"[OAUTH] Error: {token_data}")
                            return None, None
                    break
                
                # Check if need to click "Yes" to authorize
                try:
                    yes_btn = self.driver.find_element(By.XPATH, "//*[text()='Yes' or text()='ใช่']")
                    yes_btn.click()
                    print("[OAUTH] Clicked Yes to authorize")
                except:
                    pass
                
                time.sleep(1)
            
            print("[OAUTH] Timeout waiting for code")
            return None, None
            
        except Exception as e:
            print(f"[OAUTH] Error: {e}")
            return None, None
    
    def check_element(self, selector, timeout=0):
        """Check if element exists (supports multi-selector with comma)"""
        try:
            # Special case: check by text content
            if selector.startswith("text="):
                text = selector[5:]
                try:
                    elem = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
                    return elem.is_displayed()
                except:
                    return False
            
            # Split multi-selectors and check each
            selectors = [s.strip() for s in selector.split(',')]
            for sel in selectors:
                try:
                    if timeout > 0:
                        WebDriverWait(self.driver, timeout).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, sel))
                        )
                    elem = self.driver.find_element(By.CSS_SELECTOR, sel)
                    if elem.is_displayed():
                        return True
                except:
                    continue
            return False
        except:
            return False
    
    def check_elements(self, selectors, timeout=0):
        """Check which element exists from list, returns first matching selector"""
        for selector in selectors:
            if self.check_element(selector, timeout):
                return selector
        return ""
    
    def find_element_multi(self, selector):
        """Find element using multi-selector (comma separated)"""
        selectors = [s.strip() for s in selector.split(',')]
        for sel in selectors:
            try:
                elem = self.driver.find_element(By.CSS_SELECTOR, sel)
                if elem.is_displayed():
                    return elem
            except:
                continue
        return None
    
    def send_keys(self, selector, text):
        """Type text into element (supports multi-selector)"""
        try:
            elem = self.find_element_multi(selector)
            if elem:
                elem.clear()
                elem.send_keys(text)
                return True
            return False
        except:
            return False
    
    def click(self, selector):
        """Click element (supports multi-selector)"""
        try:
            elem = self.find_element_multi(selector)
            if elem:
                elem.click()
                return True
            return False
        except:
            return False
    
    def get_text(self, selector):
        """Get text from element (supports multi-selector)"""
        try:
            elem = self.find_element_multi(selector)
            return elem.text if elem else ""
        except:
            return ""
    
    def get_value(self, selector):
        """Get value attribute from element (supports multi-selector)"""
        try:
            elem = self.find_element_multi(selector)
            return elem.get_attribute("value") if elem else ""
        except:
            return ""
    
    def select_option(self, selector, value):
        """Select dropdown option by value"""
        try:
            from selenium.webdriver.support.ui import Select
            elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            select = Select(elem)
            select.select_by_value(str(value))
            return True
        except:
            return False
    
    def execute_script(self, script):
        """Execute JavaScript"""
        try:
            return self.driver.execute_script(script)
        except:
            return None
    
    def inject_captcha_token(self, token):
        """Inject FunCaptcha token (multiple methods)"""
        print(f"[CAPTCHA] Injecting token...")
        
        # Method 1: postMessage (MaxHotmail style)
        script1 = f'''
        try {{
            parent.postMessage(JSON.stringify({{
                eventId: "challenge-complete",
                payload: {{sessionToken: "{token}"}}
            }}), "*");
            console.log("[INJECT] postMessage sent");
        }} catch(e) {{ console.log("[INJECT] postMessage failed:", e); }}
        '''
        self.execute_script(script1)
        
        # Method 2: fc-token element (2Captcha recommended)
        script2 = f'''
        try {{
            var fcToken = document.getElementById("fc-token");
            if (fcToken) {{
                fcToken.value = "{token}";
                console.log("[INJECT] fc-token set");
                return true;
            }}
            // Also try in iframes
            var iframes = document.querySelectorAll("iframe");
            for (var i = 0; i < iframes.length; i++) {{
                try {{
                    var fcInFrame = iframes[i].contentDocument.getElementById("fc-token");
                    if (fcInFrame) {{
                        fcInFrame.value = "{token}";
                        console.log("[INJECT] fc-token in iframe set");
                        return true;
                    }}
                }} catch(e) {{}}
            }}
        }} catch(e) {{ console.log("[INJECT] fc-token failed:", e); }}
        return false;
        '''
        self.execute_script(script2)
        
        # Method 3: ArkoseEnforcement callback
        script3 = f'''
        try {{
            if (typeof window.ArkoseEnforcement !== 'undefined' && window.ArkoseEnforcement.setConfig) {{
                window.ArkoseEnforcement.setConfig({{solved: true, token: "{token}"}});
                console.log("[INJECT] ArkoseEnforcement set");
            }}
        }} catch(e) {{ console.log("[INJECT] ArkoseEnforcement failed:", e); }}
        '''
        self.execute_script(script3)
        
        # Method 4: Find and call verifyCallback 
        script4 = f'''
        try {{
            // Common callback names
            var callbacks = ['verifyCallback', 'funcaptchaCallback', 'arkoseCallback', 'onCaptchaSuccess'];
            for (var i = 0; i < callbacks.length; i++) {{
                if (typeof window[callbacks[i]] === 'function') {{
                    window[callbacks[i]]("{token}");
                    console.log("[INJECT] Called " + callbacks[i]);
                    return true;
                }}
            }}
        }} catch(e) {{ console.log("[INJECT] callback failed:", e); }}
        return false;
        '''
        self.execute_script(script4)
        
        print(f"[CAPTCHA] Token injection completed")
    
    def register(self, email_prefix, password, first_name, last_name, 
                 birth_month, birth_day, birth_year, timeout=300):
        """
        Main registration flow (based on MaxHotmailPro method_50)
        """
        result = {
            "success": False,
            "error": "",
            "email": f"{email_prefix}@outlook.co.th",
            "password": password,
            "name": f"{first_name} {last_name}",
            "refresh_token": "",
            "client_id": ""
        }
        
        print(f"[REG] Starting registration for {result['email']}")
        
        # Go to signup page
        self.driver.get("https://signup.live.com/signup?mkt=th-th&lic=1")
        self.delay(3)
        
        # Wait for page to load
        print("[DEBUG] Waiting for page to load...")
        for i in range(15):
            # New Microsoft signup uses input[type='email'] or name='อีเมล'
            if self.check_element("input[type='email']") or self.check_element("input#MemberName"):
                print("[DEBUG] Email input found!")
                break
            print(f"[DEBUG] Waiting... ({i+1}/15)")
            self.delay(1)
        
        # Debug: Dump all input elements on page
        try:
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"[DEBUG] Found {len(inputs)} input elements:")
            for inp in inputs[:10]:
                inp_id = inp.get_attribute("id")
                inp_name = inp.get_attribute("name")
                inp_type = inp.get_attribute("type")
                inp_placeholder = inp.get_attribute("placeholder")
                print(f"  - id='{inp_id}' name='{inp_name}' type='{inp_type}' placeholder='{inp_placeholder}'")
            
            # Also check select/dropdown elements
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            print(f"[DEBUG] Found {len(selects)} select elements:")
            for sel in selects[:5]:
                sel_id = sel.get_attribute("id")
                sel_name = sel.get_attribute("name")
                print(f"  - id='{sel_id}' name='{sel_name}'")
            
            # Check buttons
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"[DEBUG] Found {len(buttons)} buttons:")
            for btn in buttons[:5]:
                btn_id = btn.get_attribute("id")
                btn_type = btn.get_attribute("type")
                btn_text = btn.text[:30] if btn.text else ""
                print(f"  - id='{btn_id}' type='{btn_type}' text='{btn_text}'")
                
        except Exception as e:
            print(f"[DEBUG] Error getting inputs: {e}")
        
        start_time = time.time()
        captcha_attempts = 0
        max_captcha_attempts = 5
        email_entered = False
        
        while time.time() - start_time < timeout:
            # Debug: Print current URL and page state
            current_url = self.driver.current_url
            print(f"[DEBUG] URL: {current_url[:80]}...")
            
            # Check which step we're on (MaxHotmail style multi-selector check)
            # NOTE: Microsoft changed their selectors! New ones use type/name instead of id
            current_step = self.check_elements([
                "input[type='email']",                        # Email step (new style)
                "input#MemberName",                           # Email step (old)
                "input[type='password']",                     # Password step (new style)
                "input#PasswordInput",                        # Password step (old)
                "#firstNameInput",                            # First name (new)
                "#lastNameInput",                             # Last name (new)
                "input[name='ชื่อ']",                          # First name (Thai)
                "#FirstName",                                 # Name step (old)
                "#BirthDayDropdown",                          # Birthday dropdown (new)
                "input[name='BirthYear']",                    # Birthday year input (new)
                "#BirthMonth",                                # Birthday step (old)
                "text=กดค้าง",                                 # Press and Hold (by text)
                "#HipEnforcementForm",                        # Captcha (old)
                "[data-testid='enforcement-frame']",          # Captcha (new)
                "#enforcementFrame",                          # Captcha iframe
                "iframe[title*='arkose']",                    # Captcha iframe alt
                "[name='DontShowAgain']",                     # Success popup
                "#O365_MainLink_Me",                          # Already logged in
                "#riskApiBlockedViewTitle",                   # Blocked
                "#suggLink",                                  # Email exists
                "#error"                                      # Error message
            ])
            
            print(f"[DEBUG] Current step detected: '{current_step}'")
            
            # ===== EMPTY STEP - SPACE > Wait 20s > SPACE > Click ตกลง > Cancel Passkeys =====
            if current_step == "":
                print("[DEBUG] Captcha step - pressing SPACE BAR...")
                
                from selenium.webdriver.common.keys import Keys
                from selenium.webdriver.common.action_chains import ActionChains
                
                # Check if we're on Passkeys page first
                current_url = self.driver.current_url
                if "fido" in current_url or "passkey" in current_url.lower():
                    print("[DEBUG] On Passkeys page - clicking Cancel...")
                    try:
                        cancel_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
                        cancel_btn.click()
                        print("[SUCCESS] Clicked Cancel on Passkeys!")
                    except:
                        try:
                            cancel_btn = self.driver.find_element(By.XPATH, "//*[text()='ยกเลิก']")
                            cancel_btn.click()
                            print("[SUCCESS] Clicked ยกเลิก!")
                        except:
                            print("[DEBUG] Cancel button not found")
                    self.delay(3)
                    continue
                
                # Step 1: Press SPACE BAR
                ActionChains(self.driver).send_keys(Keys.SPACE).perform()
                print("[DEBUG] SPACE pressed! Waiting 20 seconds...")
                
                # Step 2: Wait 20 seconds
                time.sleep(20)
                
                # Step 3: Press SPACE BAR again
                ActionChains(self.driver).send_keys(Keys.SPACE).perform()
                print("[SUCCESS] SPACE pressed again!")
                
                self.delay(3)
                
                # Step 4: Click "ตกลง" button if it appears
                print("[DEBUG] Looking for 'ตกลง' button...")
                try:
                    ok_btn = self.driver.find_element(By.XPATH, "//*[text()='ตกลง']")
                    ok_btn.click()
                    print("[SUCCESS] Clicked 'ตกลง' button!")
                except:
                    try:
                        ok_btn = self.driver.find_element(By.XPATH, "//span[text()='ตกลง']/ancestor::button")
                        ok_btn.click()
                        print("[SUCCESS] Clicked 'ตกลง' button!")
                    except:
                        print("[DEBUG] 'ตกลง' button not found yet")
                
                self.delay(3)
                
                # Step 5: Check for Passkeys page and click Cancel
                current_url = self.driver.current_url
                if "fido" in current_url or "passkey" in current_url.lower():
                    print("[DEBUG] On Passkeys page - clicking Cancel...")
                    try:
                        cancel_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
                        cancel_btn.click()
                        print("[SUCCESS] Clicked Cancel!")
                    except:
                        try:
                            cancel_btn = self.driver.find_element(By.XPATH, "//*[text()='ยกเลิก']")
                            cancel_btn.click()
                            print("[SUCCESS] Clicked ยกเลิก!")
                        except:
                            pass
                    
                    self.delay(3)
                    
                    # Step 6: Get Refresh Token
                    print("[DEBUG] Getting Refresh Token...")
                    refresh_token, client_id = self.get_refresh_token()
                    if refresh_token:
                        result["refresh_token"] = refresh_token
                        result["client_id"] = client_id
                        result["success"] = True
                        print(f"[SUCCESS] Registration complete with Refresh Token!")
                        break
                
                self.delay(3)
                continue
            
            # ===== EMAIL STEP =====
            if current_step in ["input[type='email']", "input#MemberName"]:
                if result["success"]:
                    self.driver.get("https://outlook.live.com/mail/0/")
                    break
                
                # Check if email already exists
                if self.check_element("#suggLink"):
                    result["error"] = "Email already exists"
                    break
                
                if not email_entered:
                    # Full email with domain
                    full_email = f"{email_prefix}@outlook.co.th"
                    print(f"[REG] Step 1: Entering email '{full_email}'...")
                    
                    # Try new style first, then old
                    typed = False
                    for sel in ["input[type='email']", "input#MemberName", "input#usernameInput"]:
                        if self.send_keys(sel, full_email):
                            print(f"[DEBUG] Typed in {sel}")
                            typed = True
                            break
                    
                    if not typed:
                        print("[DEBUG] Could not find email input!")
                        self.delay(2)
                        continue
                    
                    self.delay(1)
                    
                    # Click next button - try multiple selectors
                    clicked = False
                    for sel in ["button[type='submit']", "#iSignupAction", "#nextButton", "button.primary"]:
                        if self.click(sel):
                            print(f"[DEBUG] Clicked {sel}")
                            clicked = True
                            break
                    
                    if not clicked:
                        print("[DEBUG] Could not find next button, trying Enter key...")
                        # Try pressing Enter on the input field
                        try:
                            elem = self.find_element_multi("input[type='email']")
                            if elem:
                                from selenium.webdriver.common.keys import Keys
                                elem.send_keys(Keys.ENTER)
                                print("[DEBUG] Pressed Enter")
                        except:
                            pass
                    
                    email_entered = True
                    self.delay(3)
                else:
                    # Already entered email, waiting for next step
                    print("[DEBUG] Email entered, waiting for next step...")
                    self.delay(2)
            
            # ===== PASSWORD STEP =====
            elif current_step in ["input[type='password']", "input#PasswordInput", "input#Password"]:
                # Check password error
                error_text = self.get_text("#PasswordError")
                if error_text:
                    result["error"] = f"Password error: {error_text}"
                    break
                
                print(f"[REG] Step 2: Entering password...")
                typed = False
                for sel in ["input[type='password']", "input#PasswordInput", "input#Password"]:
                    if self.send_keys(sel, password):
                        print(f"[DEBUG] Typed password in {sel}")
                        typed = True
                        break
                
                self.delay(1)
                
                # Click next
                for sel in ["button[type='submit']", "#iSignupAction", "#nextButton", "button.primary"]:
                    if self.click(sel):
                        print(f"[DEBUG] Clicked {sel}")
                        break
                
                self.delay(3)
            
            # ===== NAME STEP =====
            elif current_step in ["input[name='ชื่อ']", "input[name='นามสกุล']", "#FirstName", "#firstNameInput", "input#firstNameInput"]:
                print(f"[REG] Step 3: Entering name '{first_name} {last_name}'...")
                
                # First name
                for sel in ["#firstNameInput", "input[name='firstNameInput']", "input[name='ชื่อ']", "#FirstName"]:
                    if self.send_keys(sel, first_name):
                        print(f"[DEBUG] Typed first name in {sel}")
                        break
                
                self.delay(0.5)
                
                # Last name
                for sel in ["#lastNameInput", "input[name='lastNameInput']", "input[name='นามสกุล']", "#LastName"]:
                    if self.send_keys(sel, last_name):
                        print(f"[DEBUG] Typed last name in {sel}")
                        break
                
                self.delay(1)
                
                # Click next
                for sel in ["button[type='submit']", "#iSignupAction", "#nextButton", "button.primary"]:
                    if self.click(sel):
                        print(f"[DEBUG] Clicked {sel}")
                        break
                
                self.delay(3)
            
            # ===== BIRTHDAY STEP (with Country) =====
            elif current_step in ["select[name='ประเทศ/ภูมิภาค']", "select[name='เดือนเกิด']", "#BirthMonth", "#BirthDayDropdown", "input[name='BirthYear']"]:
                print(f"[REG] Step 4: Entering birthday {birth_day}/{birth_month}/{birth_year}...")
                
                # Thai month names
                THAI_MONTHS = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", 
                              "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", 
                              "พฤศจิกายน", "ธันวาคม"]
                
                # ===== วัน (Day) - Custom Combobox =====
                try:
                    day_btn = self.driver.find_element(By.CSS_SELECTOR, "#BirthDayDropdown, button[name='BirthDay']")
                    day_btn.click()
                    print("[DEBUG] Clicked day dropdown")
                    self.delay(0.5)
                    
                    # Find option by text (just the number)
                    options = self.driver.find_elements(By.CSS_SELECTOR, "[role='option']")
                    for opt in options:
                        if opt.text.strip() == str(birth_day):
                            opt.click()
                            print(f"[DEBUG] Selected day: {birth_day}")
                            break
                except Exception as e:
                    print(f"[DEBUG] Day selection error: {e}")
                
                self.delay(0.5)
                
                # ===== เดือน (Month) - Custom Combobox =====
                try:
                    month_btn = self.driver.find_element(By.CSS_SELECTOR, "#BirthMonthDropdown, button[name='BirthMonth']")
                    month_btn.click()
                    print("[DEBUG] Clicked month dropdown")
                    self.delay(0.5)
                    
                    # Find option by Thai month name
                    month_name = THAI_MONTHS[birth_month]
                    options = self.driver.find_elements(By.CSS_SELECTOR, "[role='option']")
                    for opt in options:
                        if opt.text.strip() == month_name:
                            opt.click()
                            print(f"[DEBUG] Selected month: {month_name}")
                            break
                except Exception as e:
                    print(f"[DEBUG] Month selection error: {e}")
                
                self.delay(0.5)
                
                # ===== ปี (Year) - Input field =====
                try:
                    year_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='BirthYear']")
                    year_input.clear()
                    year_input.send_keys(str(birth_year))
                    print(f"[DEBUG] Typed year: {birth_year}")
                except Exception as e:
                    print(f"[DEBUG] Year input error: {e}")
                
                self.delay(1)
                
                # Click next
                for sel in ["button[type='submit']", "#iSignupAction", "#nextButton"]:
                    if self.click(sel):
                        print(f"[DEBUG] Clicked {sel}")
                        break
                
                self.delay(3)
            
            # ===== PRESS AND HOLD STEP (Captcha) =====
            elif current_step == "text=กดค้าง":
                print(f"[REG] Step 5: Captcha (Press and Hold) detected!")
                print("[REG] Using accessibility bypass (Enter key method)...")
                
                try:
                    from selenium.webdriver.common.keys import Keys
                    
                    # Step 1: Find accessibility button (wheelchair icon)
                    access_btn = None
                    for method in [
                        ("SVG path", "//path[contains(@d, 'M45 24C45 12.997')]/ancestor::a"),
                        ("SVG ancestor", "//svg[contains(@aria-hidden, 'true')]//path[contains(@d, 'M45 24C45')]/ancestor::*[@role='button']"),
                        ("viewBox", "//svg[@viewBox='0 0 50 50']/ancestor::a[@role='button']"),
                    ]:
                        try:
                            access_btn = self.driver.find_element(By.XPATH, method[1])
                            print(f"[DEBUG] Found accessibility button by {method[0]}!")
                            break
                        except:
                            pass
                    
                    if not access_btn:
                        # Try aria-label
                        try:
                            access_btn = self.driver.find_element(By.CSS_SELECTOR, 
                                "[aria-label*='ความท้าทาย'], [aria-label*='accessibility'], [aria-label*='Accessibility']")
                            print("[DEBUG] Found by aria-label!")
                        except:
                            pass
                    
                    if access_btn:
                        print("[DEBUG] Found accessibility button!")
                        
                        # Step 2: Focus on button and press ENTER (not click!)
                        print("[DEBUG] Pressing ENTER on accessibility button...")
                        access_btn.send_keys(Keys.ENTER)
                        print("[DEBUG] ENTER pressed! Waiting for 'Try again' button...")
                        
                        # Step 3: Wait for "กดอีกครั้ง" / "Try again" button
                        retry_found = False
                        for i in range(120):  # Wait up to 2 minutes
                            if i % 10 == 0:
                                print(f"[DEBUG] Waiting... ({i}/120 sec)")
                            
                            # Look for retry button
                            try:
                                retry_btn = self.driver.find_element(By.XPATH, 
                                    "//*[contains(text(), 'กดอีกครั้ง') or contains(text(), 'Try again') or contains(text(), 'ลองอีกครั้ง')]")
                                if retry_btn.is_displayed():
                                    print("[DEBUG] Found 'Try again' button!")
                                    retry_found = True
                                    
                                    # Step 4: Press ENTER on retry button
                                    print("[DEBUG] Pressing ENTER on retry button...")
                                    retry_btn.send_keys(Keys.ENTER)
                                    print("[SUCCESS] Challenge bypassed!")
                                    break
                            except:
                                pass
                            
                            # Also check if captcha already passed
                            if not self.check_element("text=กดค้าง"):
                                print("[DEBUG] Captcha step seems to be done!")
                                retry_found = True
                                break
                            
                            time.sleep(1)
                        
                        if not retry_found:
                            print("[DEBUG] Timeout waiting for retry button")
                            input("Please solve manually, press Enter when done...")
                    else:
                        print("[DEBUG] Could not find accessibility button")
                        input("Please solve manually, press Enter when done...")
                        
                except Exception as e:
                    print(f"[ERROR] Captcha error: {e}")
                    input("Please solve manually, press Enter when done...")
                
                self.delay(3)
            
            # ===== CAPTCHA STEP =====
            elif current_step in ["#HipEnforcementForm", "[data-testid='enforcement-frame']", "#enforcementFrame"]:
                print(f"[REG] Step 5: Captcha detected!")
                
                if self.captcha_solver:
                    # Wait for captcha iframe to load
                    for _ in range(30):
                        if self.check_element("[data-theme='home.verifyButton']"):
                            break
                        self.delay(1)
                    
                    if not self.check_element("[data-theme='home.verifyButton']"):
                        result["error"] = "Captcha frame not loaded"
                        break
                    
                    captcha_attempts += 1
                    if captcha_attempts > max_captcha_attempts:
                        result["error"] = "Too many captcha attempts"
                        break
                    
                    # Click verify button to start captcha
                    self.click("[data-theme='home.verifyButton']")
                    self.delay(2)
                    
                    # Solve captcha
                    token = self.captcha_solver.solve_funcaptcha(
                        FUNCAPTCHA_PUBLIC_KEY,
                        "https://signup.live.com"
                    )
                    
                    if not token:
                        # Try restart
                        self.click("button.restart-button")
                        self.delay(2)
                        continue
                    
                    # Inject token
                    self.inject_captcha_token(token)
                    self.delay(10)
                    
                    # Wait for captcha to complete
                    for _ in range(30):
                        if not self.check_element("[role='progressbar']"):
                            break
                        self.delay(1)
                else:
                    # Manual captcha solving
                    print("[REG] >>> Please solve captcha manually <<<")
                    # Wait for user to solve
                    for _ in range(300):  # 5 minutes
                        if not self.check_element("#HipEnforcementForm,[data-testid='switch-arkose']"):
                            break
                        self.delay(1)
            
            # ===== SUCCESS POPUP =====
            elif current_step == "[name='DontShowAgain']":
                result["success"] = True
                self.click(current_step)
                self.delay(1)
                self.click("#idSIButton9,#acceptButton")
                print(f"[REG] Registration successful!")
                break
            
            # ===== ALREADY LOGGED IN =====
            elif current_step == "#O365_MainLink_Me":
                result["success"] = True
                print(f"[REG] Already logged in!")
                break
            
            # ===== BLOCKED =====
            elif current_step == "#riskApiBlockedViewTitle":
                result["error"] = "Blocked by Microsoft"
                break
            
            # ===== EMAIL EXISTS =====
            elif current_step == "#suggLink":
                result["error"] = "Email already exists"
                break
            
            # ===== HANDLE OTHER PAGES =====
            else:
                current_url = self.driver.current_url
                
                # Privacy notice
                if "privacynotice.account.microsoft.com" in current_url:
                    self.click("button")
                    self.delay(2)
                
                # Error pages
                elif any(x in current_url for x in [
                    "complete-client-signin-oauth-silent",
                    "error.aspx?errcode=",
                    "chrome-error://chromewebdata/"
                ]):
                    if email_entered:
                        self.driver.get("https://outlook.live.com/mail/0/")
                    else:
                        self.driver.get("https://signup.live.com/signup")
                    self.delay(2)
            
            self.delay(1)
        
        if not result["success"] and not result["error"]:
            result["error"] = "Timeout"
        
        return result
    
    def get_refresh_token(self):
        """Get OAuth2 refresh token after registration"""
        print("[OAUTH] Getting refresh token...")
        
        scopes = "offline_access https://outlook.office.com/IMAP.AccessAsUser.All https://outlook.office.com/POP.AccessAsUser.All https://outlook.office.com/EWS.AccessAsUser.All https://outlook.office.com/SMTP.Send"
        
        auth_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={OAUTH_CLIENT_ID}&response_type=code&redirect_uri=https%3A%2F%2Flocalhost%2F&response_mode=query&scope={requests.utils.quote(scopes)}&state=PythonOAuth"
        
        self.driver.get(auth_url)
        self.delay(3)
        
        code = None
        for i in range(60):
            current_url = self.driver.current_url
            
            # Check if redirected to localhost with code
            if "localhost" in current_url and "code=" in current_url:
                match = re.search(r'code=([^&]+)', current_url)
                if match:
                    code = match.group(1)
                    print("[OAUTH] Got authorization code!")
                    break
            
            # Click accept buttons
            for sel in ["#idBtn_Accept", "#iLandingViewAction", "[data-testid='appConsentPrimaryButton']"]:
                if self.check_element(sel):
                    self.click(sel)
                    self.delay(2)
                    break
            
            self.delay(1)
        
        if not code:
            print("[OAUTH] Could not get authorization code")
            return None, None
        
        # Exchange code for tokens
        print("[OAUTH] Exchanging code for tokens...")
        resp = requests.post(
            "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            data={
                "client_id": OAUTH_CLIENT_ID,
                "code": code,
                "redirect_uri": "https://localhost/",
                "grant_type": "authorization_code"
            }
        )
        
        if resp.status_code == 200:
            data = resp.json()
            refresh_token = data.get("refresh_token", "")
            if refresh_token:
                print(f"[OAUTH] Got refresh token!")
                return refresh_token, OAUTH_CLIENT_ID
        
        print("[OAUTH] Failed to get refresh token")
        return None, None


def generate_account_info():
    """Generate random account information"""
    # Email prefix - MUST start with letter, then 7-11 more chars
    first_char = random.choice(string.ascii_lowercase)  # ขึ้นต้นด้วยตัวอักษรเสมอ
    rest_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(7, 11)))
    email_prefix = first_char + rest_chars
    
    # Password (14 chars with mixed case, digits, symbols)
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$%"),
    ]
    password.extend(random.choices(string.ascii_letters + string.digits + "!@#$%", k=10))
    random.shuffle(password)
    password = ''.join(password)
    
    # Thai name
    first_name = random.choice(THAI_FIRST_NAMES)
    last_name = random.choice(THAI_LAST_NAMES)
    
    # Birthday (1990-1999)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    birth_year = random.randint(1990, 1999)
    
    return {
        "email_prefix": email_prefix,
        "email": f"{email_prefix}@outlook.co.th",
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "birth_month": birth_month,
        "birth_day": birth_day,
        "birth_year": birth_year
    }


def create_chrome_profile():
    """Create fresh Chrome profile"""
    if not os.path.exists(PROFILES_DIR):
        os.makedirs(PROFILES_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    profile_name = f"profile_{timestamp}_{random.randint(1000, 9999)}"
    profile_path = os.path.join(PROFILES_DIR, profile_name)
    os.makedirs(profile_path)
    
    return profile_path


def start_chrome(profile_path, debug_port=9222):
    """Start Chrome with fresh profile and remote debugging"""
    args = [
        CHROME_PATH,
        f'--user-data-dir={profile_path}',
        f'--remote-debugging-port={debug_port}',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-default-apps',
        'https://signup.live.com/signup?mkt=th-th&lic=1'
    ]
    
    process = subprocess.Popen(args)
    return process, debug_port


def connect_selenium(debug_port):
    """Connect Selenium to running Chrome"""
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
    driver = webdriver.Chrome(options=options)
    return driver


def main():
    print("=" * 60)
    print("  MaxHotmail Style - Outlook.co.th Registration")
    print("=" * 60)
    print()
    
    # Ask mode
    print("Mode:")
    print("  1. AUTO - Bot fills the form automatically")
    print("  2. MANUAL - Fill the form yourself")
    print("  3. HYBRID - You enter email/password, bot continues")
    mode = input("Choose mode (1/2/3): ").strip()
    auto_mode = mode == "1"
    hybrid_mode = mode == "3"
    print()
    
    # Generate account info
    account = generate_account_info()
    
    print(f"[INFO] Email: {account['email']}")
    print(f"[INFO] Password: {account['password']}")
    print(f"[INFO] Name: {account['first_name']} {account['last_name']}")
    print(f"[INFO] Birthday: {account['birth_day']}/{account['birth_month']}/{account['birth_year']}")
    print()
    
    # For HYBRID mode, ask for email and password
    if hybrid_mode:
        print("=" * 60)
        print("  HYBRID MODE - Input email & password, bot continues")
        print("=" * 60)
        custom_email = input("Enter email (without @outlook.co.th): ").strip()
        custom_password = input("Enter password: ").strip()
        
        if custom_email:
            account['email_prefix'] = custom_email.split('@')[0]  # Remove domain if user typed it
            account['email'] = f"{account['email_prefix']}@outlook.co.th"
        
        if custom_password:
            account['password'] = custom_password
        
        print()
        print(f"[INFO] Email: {account['email']}")
        print(f"[INFO] Password: {account['password']}")
        print(f"[INFO] Name: {account['first_name']} {account['last_name']}")
        print(f"[INFO] Birthday: {account['birth_day']}/{account['birth_month']}/{account['birth_year']}")
        print()
    
    
    # Create profile and start Chrome
    profile_path = create_chrome_profile()
    debug_port = 9222 + random.randint(0, 1000)
    
    print(f"[INFO] Starting Chrome (port {debug_port})...")
    process, debug_port = start_chrome(profile_path, debug_port)
    
    time.sleep(3)  # Wait for Chrome to start
    
    # Connect Selenium
    print("[INFO] Connecting Selenium...")
    driver = connect_selenium(debug_port)
    
    # Initialize captcha solver (optional)
    captcha_solver = None
    if CAPTCHA_API_KEY:
        captcha_solver = CaptchaSolver(CAPTCHA_API_KEY)
    
    # Create registrator
    reg = OutlookRegistrator(driver, captcha_solver)
    
    if auto_mode:
        # ===== AUTO MODE =====
        print()
        print("=" * 60)
        print("  AUTO MODE - Bot will fill the form")
        print("=" * 60)
        print()
        
        result = reg.register(
            email_prefix=account['email_prefix'],
            password=account['password'],
            first_name=account['first_name'],
            last_name=account['last_name'],
            birth_month=account['birth_month'],
            birth_day=account['birth_day'],
            birth_year=account['birth_year']
        )
        
        success = result["success"]
        refresh_token = result.get("refresh_token", "")
        client_id = result.get("client_id", "")
        
        if success:
            print(f"\n[SUCCESS] Registration completed!")
            # Get refresh token
            get_token = input("Get Refresh Token? (y/n): ").strip().lower()
            if get_token == 'y':
                refresh_token, client_id = reg.get_refresh_token()
                if refresh_token:
                    print(f"[SUCCESS] Got Refresh Token!")
                else:
                    print(f"[WARN] Could not get Refresh Token")
        else:
            print(f"\n[FAIL] Registration failed: {result['error']}")
    elif hybrid_mode:
        # ===== HYBRID MODE =====
        print()
        print("=" * 60)
        print("  HYBRID MODE - Bot continues from here")
        print("=" * 60)
        print()
        
        result = reg.register(
            email_prefix=account['email_prefix'],
            password=account['password'],
            first_name=account['first_name'],
            last_name=account['last_name'],
            birth_month=account['birth_month'],
            birth_day=account['birth_day'],
            birth_year=account['birth_year']
        )
        
        success = result["success"]
        refresh_token = result.get("refresh_token", "")
        client_id = result.get("client_id", "")
        
        if success:
            print(f"\n[SUCCESS] Registration completed!")
            print(f"[INFO] Ready to extract Refresh Token...")
            extract = input("Extract Refresh Token? (y/n): ").strip().lower()
            if extract == 'y':
                refresh_token, client_id = reg.get_refresh_token()
                if refresh_token:
                    print(f"[SUCCESS] Got Refresh Token!")
                else:
                    print(f"[WARN] Could not get Refresh Token")
        else:
            print(f"\n[FAIL] Registration failed: {result['error']}")
    else:
        # ===== MANUAL MODE =====
        print()
        print("=" * 60)
        print("  MANUAL MODE - Fill the form yourself")
        print("=" * 60)
        print(f"  Email:    {account['email_prefix']}")
        print(f"  Password: {account['password']}")
        print(f"  Name:     {account['first_name']} {account['last_name']}")
        print(f"  Birthday: Day={account['birth_day']}, Month={account['birth_month']}, Year={account['birth_year']}")
        print("=" * 60)
        print()
        
        input("Press Enter after registration is complete...")
        
        # Ask result
        success = input("Registration successful? (y/n): ").strip().lower() == 'y'
        
        refresh_token = ""
        client_id = ""
        
        if success:
            # Get refresh token
            get_token = input("Get Refresh Token? (y/n): ").strip().lower()
            if get_token == 'y':
                refresh_token, client_id = reg.get_refresh_token()
                if refresh_token:
                    print(f"[SUCCESS] Got Refresh Token!")
                else:
                    print(f"[WARN] Could not get Refresh Token")
    
    if success:
        # Save to file
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            line = f"{account['email']}|{account['password']}"
            if refresh_token:
                line += f"|{refresh_token}|{client_id}"
            line += "\n"
            f.write(line)
        
        print(f"[SUCCESS] Saved to {OUTPUT_FILE}")
    
    # Ask to continue
    again = input("\nCreate another account? (y/n): ").strip().lower()
    if again == 'y':
        driver.quit()
        main()
    else:
        print("[INFO] Done!")


if __name__ == "__main__":
    main()
