"""
Chrome Fresh Profile - Outlook.co.th Registration
ใช้ Chrome ปกติ + Profile ใหม่ทุกครั้ง + mProxy Vietnam
"""
import os
import sys
import time
import random
import string
import shutil
import subprocess
import requests
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# OAuth2 Config (from MaxHotmailPro)
OAUTH_CLIENT_ID = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
OAUTH_REDIRECT_URI = "https://localhost/"
OAUTH_SCOPES = "offline_access https://outlook.office.com/IMAP.AccessAsUser.All https://outlook.office.com/POP.AccessAsUser.All https://outlook.office.com/EWS.AccessAsUser.All https://outlook.office.com/SMTP.Send"
OAUTH_AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
OAUTH_TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

# ============== CONFIG ==============
# mProxy Vietnam API
MPROXY_API_KEY = "8R5UzvmVYS0CWTLra1uqamdcz0EWkTt661QROumurgg"
MPROXY_API = f"https://mproxy.vn/capi/{MPROXY_API_KEY}"

# Chrome path
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Profiles directory
PROFILES_DIR = os.path.join(BASE_DIR, "chrome_profiles")

# Output file
OUTPUT_FILE = os.path.join(BASE_DIR, "accounts.txt")

# Thai names
THAI_FIRST_NAMES = [
    "สมชาย", "สมหญิง", "วิชัย", "สุดา", "ประเสริฐ", "นภา", "อนันต์", "พิมพ์",
    "ชัยวัฒน์", "รัตนา", "กิตติ", "มาลี", "วีระ", "สุภา", "ธนา", "จันทร์",
    "พงศ์", "แก้ว", "บุญ", "ทอง", "เพชร", "ดาว", "นาค", "สิงห์"
]

THAI_LAST_NAMES = [
    "ใจดี", "รักเรียน", "มั่นคง", "งามตา", "ศรีสุข", "พรหมมา", "ทองดี", "สุขใจ",
    "เจริญ", "วงศ์ไทย", "สว่าง", "ดอกไม้", "แสงทอง", "มีชัย", "ศรีวิชัย", "พันธ์ดี",
    "สมบูรณ์", "รุ่งเรือง", "พิทักษ์", "สุขสันต์"
]


class MProxyManager:
    """Manage mProxy Vietnam"""
    
    @staticmethod
    def get_keys():
        """Get all proxy keys"""
        try:
            resp = requests.get(f"{MPROXY_API}/keys", timeout=10)
            data = resp.json()
            if data.get("status") == 1:
                return data.get("data", [])
        except:
            pass
        return []
    
    @staticmethod
    def get_balance():
        """Get account balance"""
        try:
            resp = requests.get(f"{MPROXY_API}/balance", timeout=10)
            data = resp.json()
            if data.get("status") == 1:
                return data["data"]["balance"]
        except:
            pass
        return 0
    
    @staticmethod
    def reset_ip(key_code):
        """Reset IP to get new one"""
        try:
            resp = requests.get(f"{MPROXY_API}/key/{key_code}/resetIp", timeout=10)
            data = resp.json()
            if data.get("status") == 1:
                return data["data"]
        except:
            pass
        return None
    
    @staticmethod
    def buy_key(package_id=2):
        """Buy new key (default: 1 day = 15K VND)"""
        try:
            resp = requests.get(f"{MPROXY_API}/buy/{package_id}", timeout=10)
            data = resp.json()
            if data.get("status") == 1:
                return data["data"]
        except:
            pass
        return None


def generate_username():
    """Generate random username for email"""
    # Mix of letters and numbers
    chars = string.ascii_lowercase + string.digits
    length = random.randint(8, 12)
    return ''.join(random.choices(chars, k=length))


def generate_password():
    """Generate strong password"""
    # At least 1 uppercase, 1 lowercase, 1 digit, 1 special
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$%"),
    ]
    # Fill the rest
    chars = string.ascii_letters + string.digits + "!@#$%"
    password.extend(random.choices(chars, k=10))
    random.shuffle(password)
    return ''.join(password)


def generate_thai_name():
    """Generate random Thai name"""
    first = random.choice(THAI_FIRST_NAMES)
    last = random.choice(THAI_LAST_NAMES)
    return first, last


def generate_birthday():
    """Generate random birthday (18-35 years old)"""
    year = random.randint(1990, 2005)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return day, month, year


def create_fresh_profile():
    """Create a new Chrome profile directory"""
    # Ensure profiles directory exists
    if not os.path.exists(PROFILES_DIR):
        os.makedirs(PROFILES_DIR)
    
    # Create unique profile name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    profile_name = f"profile_{timestamp}_{random.randint(1000, 9999)}"
    profile_path = os.path.join(PROFILES_DIR, profile_name)
    
    os.makedirs(profile_path)
    return profile_path


def create_proxy_extension(proxy_host, proxy_port, proxy_user, proxy_pass, profile_path):
    """Create Chrome extension for authenticated proxy"""
    import zipfile
    
    manifest_json = """{
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
}"""

    background_js = """var config = {
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
);""" % (proxy_host, proxy_port, proxy_user, proxy_pass)

    extension_path = os.path.join(profile_path, "proxy_extension")
    os.makedirs(extension_path, exist_ok=True)
    
    with open(os.path.join(extension_path, "manifest.json"), 'w') as f:
        f.write(manifest_json)
    
    with open(os.path.join(extension_path, "background.js"), 'w') as f:
        f.write(background_js)
    
    # Create zip
    zip_path = os.path.join(profile_path, "proxy_auth.zip")
    with zipfile.ZipFile(zip_path, 'w') as zp:
        zp.write(os.path.join(extension_path, "manifest.json"), "manifest.json")
        zp.write(os.path.join(extension_path, "background.js"), "background.js")
    
    return zip_path


def open_chrome_with_profile(profile_path, url, proxy_extension=None, debug_port=9222):
    """Open Chrome with fresh profile"""
    args = [
        CHROME_PATH,
        f'--user-data-dir={profile_path}',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-default-apps',
        f'--remote-debugging-port={debug_port}',
    ]
    
    if proxy_extension:
        args.append(f'--load-extension={os.path.dirname(proxy_extension)}')
    
    args.append(url)
    
    # Start Chrome
    process = subprocess.Popen(args)
    return process, debug_port


def cleanup_old_profiles(keep_last=5):
    """Delete old profiles to save space"""
    if not os.path.exists(PROFILES_DIR):
        return
    
    profiles = sorted(os.listdir(PROFILES_DIR))
    if len(profiles) > keep_last:
        for profile in profiles[:-keep_last]:
            profile_path = os.path.join(PROFILES_DIR, profile)
            try:
                shutil.rmtree(profile_path)
                print(f"[CLEANUP] Deleted old profile: {profile}")
            except:
                pass


def get_oauth_auth_url():
    """สร้าง OAuth2 Authorization URL"""
    params = {
        "client_id": OAUTH_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": OAUTH_REDIRECT_URI,
        "response_mode": "query",
        "scope": OAUTH_SCOPES,
        "state": "PythonOAuth"
    }
    param_str = "&".join([f"{k}={requests.utils.quote(v)}" for k, v in params.items()])
    return f"{OAUTH_AUTH_URL}?{param_str}"


def exchange_code_for_tokens(code):
    """แลก authorization code เป็น tokens"""
    data = {
        "client_id": OAUTH_CLIENT_ID,
        "code": code,
        "redirect_uri": OAUTH_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    response = requests.post(OAUTH_TOKEN_URL, data=data)
    
    if response.status_code == 200:
        return response.json()
    return None


def get_refresh_token_from_browser(driver):
    """ดึง Refresh Token จาก browser ที่ login แล้ว"""
    print("[INFO] Getting OAuth2 Refresh Token...")
    
    auth_url = get_oauth_auth_url()
    driver.get(auth_url)
    
    code = None
    for i in range(60):  # Wait max 60 seconds
        current_url = driver.current_url
        
        # Check if redirected to localhost with code
        if "localhost" in current_url and "code=" in current_url:
            match = re.search(r'code=([^&]+)', current_url)
            if match:
                code = match.group(1)
                print(f"[INFO] Got authorization code!")
                break
        
        # Try to click Accept button
        accept_selectors = [
            "#idBtn_Accept",
            "#iLandingViewAction", 
            "[data-testid='appConsentPrimaryButton']",
            "input[type='submit'][value='Yes']"
        ]
        
        for selector in accept_selectors:
            try:
                from selenium.webdriver.common.by import By
                btn = driver.find_element(By.CSS_SELECTOR, selector)
                if btn.is_displayed():
                    btn.click()
                    print(f"[INFO] Clicked consent button")
                    time.sleep(2)
                    break
            except:
                pass
        
        time.sleep(1)
    
    if not code:
        print("[WARN] Could not get authorization code")
        return None, None
    
    # Exchange code for tokens
    tokens = exchange_code_for_tokens(code)
    
    if tokens and "refresh_token" in tokens:
        return tokens["refresh_token"], OAUTH_CLIENT_ID
    
    return None, None


def main():
    print("=" * 60)
    print("  Chrome Fresh Profile - Outlook.co.th Registration")
    print("=" * 60)
    print()
    
    # Check mProxy
    print("[INFO] Checking mProxy Vietnam...")
    balance = MProxyManager.get_balance()
    print(f"[INFO] Balance: {balance:,} VND")
    
    keys = MProxyManager.get_keys()
    proxy_info = None
    
    if keys:
        key = keys[0]
        print(f"[INFO] Found proxy key: {key['key_code'][:10]}...")
        
        # Reset IP for fresh start
        print("[INFO] Resetting IP...")
        reset_result = MProxyManager.reset_ip(key['key_code'])
        if reset_result:
            proxy_info = {
                'host': reset_result['server_host'],
                'port': str(reset_result['server_port']),
                'user': reset_result['user'],
                'pass': reset_result['password']
            }
            print(f"[INFO] New proxy: {proxy_info['host']}:{proxy_info['port']}")
    else:
        print("[WARN] No proxy key found. Running without proxy.")
    
    # Generate account info
    print()
    print("[INFO] Generating account info...")
    username = generate_username()
    email = f"{username}@outlook.co.th"
    password = generate_password()
    first_name, last_name = generate_thai_name()
    day, month, year = generate_birthday()
    
    print(f"[INFO] Email: {email}")
    print(f"[INFO] Password: {password}")
    print(f"[INFO] Name: {first_name} {last_name}")
    print(f"[INFO] Birthday: {day}/{month}/{year}")
    print()
    
    # Create fresh profile
    print("[INFO] Creating fresh Chrome profile...")
    profile_path = create_fresh_profile()
    print(f"[INFO] Profile: {profile_path}")
    
    # Create proxy extension if proxy available
    proxy_ext = None
    if proxy_info:
        print("[INFO] Creating proxy extension...")
        proxy_ext = create_proxy_extension(
            proxy_info['host'],
            proxy_info['port'],
            proxy_info['user'],
            proxy_info['pass'],
            profile_path
        )
    
    # Open Chrome
    print()
    print("[INFO] Opening Chrome...")
    debug_port = 9222 + random.randint(0, 1000)  # Random port to avoid conflicts
    process, debug_port = open_chrome_with_profile(
        profile_path,
        "https://signup.live.com/signup?mkt=th-th&lic=1",
        proxy_ext,
        debug_port
    )
    
    print()
    print("=" * 60)
    print("  ACCOUNT INFO - Copy these values:")
    print("=" * 60)
    print(f"  Email:    {email}")
    print(f"  Password: {password}")
    print(f"  Name:     {first_name} {last_name}")
    print(f"  Birthday: Day={day}, Month={month}, Year={year}")
    print("=" * 60)
    print()
    print("[INFO] Fill in the form manually in Chrome.")
    print("[INFO] After successful registration, press Enter to save.")
    print()
    
    input("Press Enter after registration is complete (or 'q' to quit)...")
    
    # Ask if successful
    success = input("Was registration successful? (y/n): ").strip().lower()
    
    refresh_token = ""
    client_id = ""
    
    if success == 'y':
        # Ask if want to get refresh token
        get_token = input("Get Refresh Token? (y/n): ").strip().lower()
        
        if get_token == 'y':
            # Connect Selenium to the running Chrome
            print("[INFO] Connecting to Chrome to get Refresh Token...")
            try:
                options = Options()
                options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
                
                # Use system chromedriver
                driver = webdriver.Chrome(options=options)
                
                # Get refresh token
                refresh_token, client_id = get_refresh_token_from_browser(driver)
                
                if refresh_token:
                    print(f"[SUCCESS] Got Refresh Token!")
                else:
                    print(f"[WARN] Could not get Refresh Token")
                    
            except Exception as e:
                print(f"[ERROR] Failed to get refresh token: {e}")
        
        # Save to file
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            if refresh_token:
                f.write(f"{email}|{password}|{first_name} {last_name}|{refresh_token}|{client_id}|{timestamp}\n")
            else:
                f.write(f"{email}|{password}|{first_name} {last_name}|||{timestamp}\n")
        print(f"[SUCCESS] Account saved to {OUTPUT_FILE}")
    else:
        print("[INFO] Account not saved.")
    
    # Cleanup
    print()
    print("[INFO] Cleaning up old profiles...")
    cleanup_old_profiles(keep_last=3)
    
    # Ask to continue
    again = input("\nCreate another account? (y/n): ").strip().lower()
    if again == 'y':
        main()
    else:
        print("[INFO] Done! Goodbye.")


if __name__ == "__main__":
    main()
