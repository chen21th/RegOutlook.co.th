"""
Outlook OAuth2 Refresh Token Getter
ดึง Refresh Token หลังจาก register สำเร็จแล้ว
"""
import os
import re
import time
import requests
from urllib.parse import urlparse, parse_qs

# Microsoft OAuth2 Config (จาก MaxHotmailPro)
CLIENT_ID = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
REDIRECT_URI = "https://localhost/"
SCOPES = "offline_access https://outlook.office.com/IMAP.AccessAsUser.All https://outlook.office.com/POP.AccessAsUser.All https://outlook.office.com/EWS.AccessAsUser.All https://outlook.office.com/SMTP.Send"

# URLs
AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"


def get_auth_url():
    """สร้าง Authorization URL"""
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "response_mode": "query",
        "scope": SCOPES,
        "state": "PythonOAuth"
    }
    param_str = "&".join([f"{k}={requests.utils.quote(v)}" for k, v in params.items()])
    return f"{AUTH_URL}?{param_str}"


def extract_code_from_url(url):
    """ดึง authorization code จาก redirect URL"""
    # URL format: https://localhost/?code=XXXXX&state=...
    match = re.search(r'code=([^&]+)', url)
    if match:
        return match.group(1)
    return None


def exchange_code_for_token(code):
    """แลก code เป็น tokens"""
    data = {
        "client_id": CLIENT_ID,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(TOKEN_URL, data=data, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[ERROR] Token exchange failed: {response.status_code}")
        print(response.text)
        return None


def get_refresh_token_selenium(driver):
    """ดึง refresh token โดยใช้ Selenium driver ที่ login แล้ว"""
    
    auth_url = get_auth_url()
    print(f"[INFO] Going to OAuth2 authorization page...")
    
    driver.get(auth_url)
    
    # รอให้ user กด Accept หรือ redirect อัตโนมัติ
    code = None
    for i in range(60):  # Wait max 60 seconds
        current_url = driver.current_url
        
        # Check if redirected to localhost
        if "localhost" in current_url and "code=" in current_url:
            code = extract_code_from_url(current_url)
            if code:
                print(f"[INFO] Got authorization code!")
                break
        
        # Try to click Accept button if exists
        try:
            accept_buttons = [
                "#idBtn_Accept",
                "#iLandingViewAction", 
                "[data-testid='appConsentPrimaryButton']"
            ]
            for btn_selector in accept_buttons:
                try:
                    btn = driver.find_element("css selector", btn_selector)
                    if btn.is_displayed():
                        btn.click()
                        print(f"[INFO] Clicked accept button")
                        time.sleep(2)
                        break
                except:
                    pass
        except:
            pass
        
        time.sleep(1)
    
    if not code:
        print("[ERROR] Could not get authorization code")
        return None
    
    # Exchange code for tokens
    print(f"[INFO] Exchanging code for tokens...")
    tokens = exchange_code_for_token(code)
    
    if tokens and "refresh_token" in tokens:
        refresh_token = tokens["refresh_token"]
        print(f"[SUCCESS] Got refresh token!")
        return {
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "access_token": tokens.get("access_token", ""),
            "expires_in": tokens.get("expires_in", 0)
        }
    
    return None


def get_refresh_token_manual():
    """ดึง refresh token แบบ manual (copy URL จาก browser)"""
    print("=" * 60)
    print("  Outlook OAuth2 Refresh Token - Manual Mode")
    print("=" * 60)
    print()
    
    auth_url = get_auth_url()
    print("[1] Copy this URL and open in browser where you're logged in:")
    print()
    print(auth_url)
    print()
    print("[2] After clicking 'Accept', browser will redirect to localhost")
    print("[3] Copy the FULL URL from address bar (even if page shows error)")
    print()
    
    redirect_url = input("Paste the redirect URL here: ").strip()
    
    code = extract_code_from_url(redirect_url)
    
    if not code:
        print("[ERROR] Could not extract code from URL")
        return None
    
    print(f"[INFO] Got authorization code, exchanging for tokens...")
    
    tokens = exchange_code_for_token(code)
    
    if tokens and "refresh_token" in tokens:
        refresh_token = tokens["refresh_token"]
        print()
        print("=" * 60)
        print("  SUCCESS! Here's your data:")
        print("=" * 60)
        print(f"Refresh Token: {refresh_token}")
        print(f"Client ID: {CLIENT_ID}")
        print()
        return {
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID
        }
    else:
        print("[ERROR] Failed to get refresh token")
        return None


def use_refresh_token(refresh_token, client_id=CLIENT_ID):
    """ใช้ refresh token เพื่อดึง access token ใหม่"""
    data = {
        "client_id": client_id,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "scope": SCOPES
    }
    
    response = requests.post(TOKEN_URL, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[ERROR] Refresh failed: {response.status_code}")
        return None


if __name__ == "__main__":
    result = get_refresh_token_manual()
    
    if result:
        print("\n[TEST] Testing refresh token...")
        new_tokens = use_refresh_token(result["refresh_token"])
        if new_tokens:
            print("[SUCCESS] Refresh token works! Can get new access token.")
        else:
            print("[WARN] Refresh token test failed")
