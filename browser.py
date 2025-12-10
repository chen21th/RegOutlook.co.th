# ===== BROWSER MANAGER =====

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import CHROME_DRIVER_PATH, WINDOW_WIDTH, WINDOW_HEIGHT, BASE_DIR


class BrowserManager:
    """Class สำหรับจัดการ Chrome Browser"""
    
    # ต้องใช้ mkt=th-th เพื่อรองรับ @outlook.co.th
    SIGNUP_URL = "https://signup.live.com/signup?mkt=th-th&lic=1"
    
    def __init__(self, proxy=None, position_x=0, position_y=0):
        self.proxy = proxy
        self.position_x = position_x
        self.position_y = position_y
        self.driver = None
    
    def create_options(self):
        """สร้าง Chrome options"""
        import zipfile
        import os
        
        options = Options()
        
        # Proxy (รองรับ format http://user:pass@host:port)
        if self.proxy:
            # สำหรับ authenticated proxy ต้องใช้ extension
            if "@" in self.proxy:
                # ABC Proxy format: http://user:pass@host:port
                
                # Parse proxy
                proxy_parts = self.proxy.replace("http://", "").split("@")
                user_pass = proxy_parts[0].split(":")
                host_port = proxy_parts[1].split(":")
                
                PROXY_HOST = host_port[0]
                PROXY_PORT = host_port[1]
                PROXY_USER = user_pass[0]
                PROXY_PASS = user_pass[1]
                
                # สร้าง extension สำหรับ authenticated proxy
                manifest_json = """
                {
                    "version": "1.0.0",
                    "manifest_version": 2,
                    "name": "Chrome Proxy",
                    "permissions": [
                        "proxy",
                        "tabs",
                        "unlimitedStorage",
                        "storage",
                        "<all_urls>",
                        "webRequest",
                        "webRequestBlocking"
                    ],
                    "background": {
                        "scripts": ["background.js"]
                    },
                    "minimum_chrome_version":"22.0.0"
                }
                """
                
                background_js = """
                var config = {
                        mode: "fixed_servers",
                        rules: {
                        singleProxy: {
                            scheme: "http",
                            host: "%s",
                            port: parseInt(%s)
                        },
                        bypassList: ["localhost"]
                        }
                    };

                chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

                function callbackFn(details) {
                    return {
                        authCredentials: {
                            username: "%s",
                            password: "%s"
                        }
                    };
                }

                chrome.webRequest.onAuthRequired.addListener(
                            callbackFn,
                            {urls: ["<all_urls>"]},
                            ['blocking']
                );
                """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
                
                # สร้าง extension zip
                plugin_file = os.path.join(BASE_DIR, 'proxy_auth_plugin.zip')
                with zipfile.ZipFile(plugin_file, 'w') as zp:
                    zp.writestr("manifest.json", manifest_json)
                    zp.writestr("background.js", background_js)
                
                options.add_extension(plugin_file)
            else:
                # Simple proxy format: host:port
                options.add_argument(f"--proxy-server={self.proxy}")
        
        # Window size
        options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
        
        # Anti-detection
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-site-isolation-trials")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # หน้าเริ่มต้น
        options.add_argument("--app=https://httpbin.org/ip")
        
        return options
    
    def start(self):
        """เริ่ม browser"""
        options = self.create_options()
        service = Service(CHROME_DRIVER_PATH)
        
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_window_position(self.position_x, self.position_y)
        self.driver.implicitly_wait(10)
        
        # Remove webdriver flag
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return self.driver
    
    def go_to_signup(self):
        """ไปหน้า signup"""
        self.driver.get(self.SIGNUP_URL)
    
    def wait_for_element(self, element_id, timeout=10):
        """รอ element by ID"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, element_id))
            )
            return element
        except TimeoutException:
            return None
    
    def wait_for_element_by_name(self, name, timeout=10):
        """รอ element by name"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.NAME, name))
            )
            return element
        except TimeoutException:
            return None
    
    def wait_for_element_by_type(self, input_type, timeout=10):
        """รอ element by type (e.g., password, email)"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"input[type='{input_type}']"))
            )
            return element
        except TimeoutException:
            return None
    
    def fill_input_by_type(self, input_type, value, timeout=10):
        """กรอกข้อมูล by input type"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"input[type='{input_type}']"))
            )
            element.clear()
            element.send_keys(value)
            return True
        except TimeoutException:
            return False
    
    def click_element(self, element_id, timeout=10):
        """คลิก element by ID"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.ID, element_id))
            )
            element.click()
            return True
        except TimeoutException:
            return False
    
    def click_button_by_text(self, text, timeout=10):
        """คลิก button ตาม text"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{text}')]"))
            )
            element.click()
            return True
        except TimeoutException:
            return False
    
    def click_primary_button(self, timeout=10):
        """คลิกปุ่มหลัก (ถัดไป/Next) โดยใช้ data-testid"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='primaryButton']"))
            )
            element.click()
            return True
        except TimeoutException:
            # Fallback to text search
            return self.click_button_by_text("ถัดไป") or self.click_button_by_text("Next")
    
    def fill_input(self, element_id, value, timeout=10):
        """กรอกข้อมูล by ID"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, element_id))
            )
            element.clear()
            element.send_keys(value)
            return True
        except TimeoutException:
            return False
    
    def fill_input_by_name(self, name, value, timeout=10):
        """กรอกข้อมูล by name"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.NAME, name))
            )
            element.clear()
            element.send_keys(value)
            return True
        except TimeoutException:
            return False
    
    def select_dropdown(self, element_id, value, timeout=10):
        """เลือก dropdown by ID"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, element_id))
            )
            select = Select(element)
            select.select_by_value(str(value))
            return True
        except TimeoutException:
            return False
    
    def select_dropdown_by_name(self, name, value, timeout=10):
        """เลือก dropdown by name"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.NAME, name))
            )
            select = Select(element)
            select.select_by_value(str(value))
            return True
        except TimeoutException:
            return False
    
    def check_page_contains(self, text):
        """เช็คว่าหน้ามีข้อความนี้ไหม"""
        return text in self.driver.page_source
    
    def close(self):
        """ปิด browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
