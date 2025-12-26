"""
Quick script to get Refresh Token from logged-in Chrome
"""
import requests
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# OAuth2 Config (from MaxHotmailPro)
CLIENT_ID = '9e5f94bc-e8a4-4e73-b8be-63364c29d753'
REDIRECT_URI = 'https://localhost/'
SCOPES = 'offline_access https://outlook.office.com/IMAP.AccessAsUser.All https://outlook.office.com/POP.AccessAsUser.All https://outlook.office.com/EWS.AccessAsUser.All https://outlook.office.com/SMTP.Send'

# Build auth URL
auth_url = f'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri=https%3A%2F%2Flocalhost%2F&response_mode=query&scope={requests.utils.quote(SCOPES)}&state=PythonOAuth'

print('[INFO] Connecting to Chrome...')

# Find Chrome debug port
driver = None
for port in range(9222, 10300):
    try:
        options = Options()
        options.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')
        driver = webdriver.Chrome(options=options)
        print(f'[INFO] Connected on port {port}')
        break
    except:
        continue

if not driver:
    print('[ERROR] Could not connect to Chrome')
    print('[INFO] Make sure Chrome was opened with --remote-debugging-port')
    exit(1)

print('[INFO] Going to OAuth2 authorization page...')
driver.get(auth_url)
time.sleep(3)

code = None
for i in range(60):
    url = driver.current_url
    
    # Check if redirected to localhost with code
    if 'localhost' in url and 'code=' in url:
        match = re.search(r'code=([^&]+)', url)
        if match:
            code = match.group(1)
            print('[SUCCESS] Got authorization code!')
            break
    
    # Try clicking accept button
    selectors = ['#idBtn_Accept', '#iLandingViewAction', '[data-testid="appConsentPrimaryButton"]', 'input[type="submit"]']
    for sel in selectors:
        try:
            btn = driver.find_element(By.CSS_SELECTOR, sel)
            if btn.is_displayed():
                btn.click()
                print(f'[INFO] Clicked consent button')
                time.sleep(2)
                break
        except:
            pass
    
    print(f'[INFO] Waiting for consent... ({i+1}/60)')
    time.sleep(1)

if not code:
    print('[ERROR] Could not get authorization code')
    print('[INFO] Current URL:', driver.current_url)
    exit(1)

# Exchange code for tokens
print('[INFO] Exchanging code for tokens...')
resp = requests.post('https://login.microsoftonline.com/common/oauth2/v2.0/token', data={
    'client_id': CLIENT_ID,
    'code': code,
    'redirect_uri': REDIRECT_URI,
    'grant_type': 'authorization_code'
})

if resp.status_code == 200:
    data = resp.json()
    refresh_token = data.get('refresh_token', '')
    access_token = data.get('access_token', '')
    
    print()
    print('=' * 60)
    print('  SUCCESS! Got Refresh Token')
    print('=' * 60)
    print(f'Refresh Token: {refresh_token[:80]}...')
    print(f'Client ID: {CLIENT_ID}')
    print()
    print('Full format (for accounts.txt):')
    print(f'{refresh_token}|{CLIENT_ID}')
    print()
    
    # Save to file
    with open('last_refresh_token.txt', 'w') as f:
        f.write(f'refresh_token={refresh_token}\n')
        f.write(f'client_id={CLIENT_ID}\n')
        f.write(f'access_token={access_token}\n')
    print('[INFO] Saved to last_refresh_token.txt')
    
else:
    print(f'[ERROR] Token exchange failed: {resp.status_code}')
    print(resp.text)
