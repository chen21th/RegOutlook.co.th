# ===== CAPTCHA SOLVER =====

import requests
import time
from config import CAPTCHA_API_KEY, CAPTCHA_API_URL


class CaptchaSolver:
    """Class สำหรับแก้ FunCaptcha ของ Microsoft"""
    
    MICROSOFT_SITE_KEY = "B7D8911C-5CC8-A9A3-35B0-554ACEE604DA"
    SIGNUP_URL = "https://signup.live.com/signup?mkt=th-th&lic=1"
    
    def __init__(self, api_key=None):
        self.api_key = api_key or CAPTCHA_API_KEY
        self.base_url = CAPTCHA_API_URL
    
    def check_balance(self):
        """เช็คเงินคงเหลือ"""
        try:
            response = requests.post(
                f"{self.base_url}/getBalance",
                data={"clientKey": self.api_key}
            )
            result = response.json()
            return float(result.get("balance", 0))
        except Exception as e:
            print(f"[ERROR] Check balance failed: {e}")
            return 0
    
    def create_task(self):
        """สร้าง task สำหรับแก้ captcha"""
        data = {
            "clientKey": self.api_key,
            "task": {
                "type": "FunCaptchaTaskProxyless",
                "websiteURL": self.SIGNUP_URL,
                "websitePublicKey": self.MICROSOFT_SITE_KEY,
            },
            "softId": 847,
            "languagePool": "en"
        }
        
        try:
            response = requests.post(f"{self.base_url}/createTask", json=data)
            result = response.json()
            
            if result.get("errorId", 1) == 0:
                return result.get("taskId")
            else:
                print(f"[ERROR] Create task failed: {result}")
                return None
        except Exception as e:
            print(f"[ERROR] Create task exception: {e}")
            return None
    
    def get_result(self, task_id, max_wait=120):
        """รอผลลัพธ์ captcha"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.post(
                    f"{self.base_url}/getTaskResult",
                    data={"clientKey": self.api_key, "taskId": task_id}
                )
                result = response.json()
                
                if result.get("errorId") == 2:
                    print("[ERROR] Captcha task error")
                    return None
                
                if result.get("status") == "ready" and result.get("errorId") == 0:
                    return result.get("solution", {}).get("token")
                
                # ยังไม่เสร็จ รอต่อ
                time.sleep(3)
                
            except Exception as e:
                print(f"[ERROR] Get result exception: {e}")
                return None
        
        print("[ERROR] Captcha timeout")
        return None
    
    def solve(self):
        """แก้ captcha - main function"""
        # เช็คเงินก่อน
        balance = self.check_balance()
        if balance < 0.003:
            print(f"[ERROR] เงินไม่พอ! Balance: ${balance}")
            return None
        
        print(f"[INFO] Balance: ${balance}")
        
        # สร้าง task
        task_id = self.create_task()
        if not task_id:
            return None
        
        print(f"[INFO] Task created: {task_id}")
        
        # รอผลลัพธ์
        token = self.get_result(task_id)
        if token:
            print("[SUCCESS] Captcha solved!")
        
        return token


def inject_captcha_token(driver, token):
    """Inject captcha token เข้า iframe"""
    script = f"""
        var anyCaptchaToken = '{token}';
        var enc = document.getElementById('enforcementFrame');
        var encWin = enc.contentWindow || enc;
        var encDoc = enc.contentDocument || encWin.document;
        let script = encDoc.createElement('SCRIPT');
        script.append('function AnyCaptchaSubmit(token) {{ parent.postMessage(JSON.stringify({{ eventId: "challenge-complete", payload: {{ sessionToken: token }} }}), "*") }}');
        encDoc.documentElement.appendChild(script);
        encWin.AnyCaptchaSubmit(anyCaptchaToken);
    """
    driver.execute_script(script)
