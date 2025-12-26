#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Method: Connect to existing Chrome via Remote Debugging
วิธีนี้จะเปิด Chrome ปกติ แล้ว Selenium connect เข้าไปควบคุม
ทำให้ Chrome ดูเหมือนคนใช้จริงๆ ไม่ใช่ automation
"""

import subprocess
import time
import os
import sys

# Chrome path - ปรับตามเครื่อง
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEBUG_PORT = 9222
PROFILE_DIR = os.path.join(os.path.dirname(__file__), "chrome_debug_profile")

print("=" * 60)
print("  Method: Remote Debugging Chrome")
print("=" * 60)
print("""
วิธีนี้จะ:
1. เปิด Chrome ปกติด้วย --remote-debugging-port
2. Selenium connect เข้าไปควบคุม Chrome ตัวนั้น
3. Chrome จะดูเหมือนคนใช้จริง ไม่ใช่ bot

หมายเหตุ: ต้องปิด Chrome ทุกตัวก่อนรัน!
""")

# Check if Chrome exists
if not os.path.exists(CHROME_PATH):
    # Try other paths
    alt_paths = [
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for p in alt_paths:
        if os.path.exists(p):
            CHROME_PATH = p
            break

print(f"Chrome path: {CHROME_PATH}")
print(f"Debug port: {DEBUG_PORT}")
print(f"Profile dir: {PROFILE_DIR}")

# Create profile dir
os.makedirs(PROFILE_DIR, exist_ok=True)

# Kill existing Chrome first
print("\n🔄 Closing existing Chrome...")
os.system("taskkill /f /im chrome.exe 2>nul")
time.sleep(2)

# Start Chrome with remote debugging
print("\n🌐 Starting Chrome with remote debugging...")
cmd = [
    CHROME_PATH,
    f"--remote-debugging-port={DEBUG_PORT}",
    f"--user-data-dir={PROFILE_DIR}",
    "--no-first-run",
    "--no-default-browser-check",
    "--window-size=600,800",
    "--window-position=100,50",
    "https://signup.live.com/signup?mkt=th-th&lic=1"
]

# Start Chrome as subprocess (non-blocking)
chrome_process = subprocess.Popen(cmd)
print(f"✓ Chrome started (PID: {chrome_process.pid})")

time.sleep(5)

# Connect with Selenium
print("\n🔗 Connecting Selenium to Chrome...")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import string

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Connect to existing Chrome
options = Options()
options.add_experimental_option("debuggerAddress", f"127.0.0.1:{DEBUG_PORT}")

# ใช้ chromedriver ที่มีอยู่
chromedriver_path = os.path.join(os.path.dirname(__file__), "chromedriver.exe")
service = Service(chromedriver_path)

try:
    driver = webdriver.Chrome(service=service, options=options)
    print("✓ Connected to Chrome!")
    
    # Generate account data
    username = generate_random_string(12)
    email = f"{username}@outlook.co.th"
    password = "Test@" + generate_random_string(8) + "!"
    
    print(f"\n📧 Email: {email}")
    print(f"🔑 Password: {password}")
    
    # Wait for page
    print("\n⏳ Waiting for page...")
    time.sleep(3)
    
    # Find and fill email
    print("\n📝 Step 1: Enter email...")
    try:
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_input.clear()
        for char in email:
            email_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.1))
        print(f"   ✓ Entered: {email}")
        
        time.sleep(1)
        
        # Click next
        next_btn = driver.find_element(By.ID, "iSignupAction")
        next_btn.click()
        print("   ✓ Clicked Next")
        
    except Exception as e:
        print(f"   ⚠️ Email step error: {e}")
    
    time.sleep(3)
    
    # Step 2: Password
    print("\n🔐 Step 2: Enter password...")
    try:
        pwd_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "PasswordInput"))
        )
        for char in password:
            pwd_input.send_keys(char)
            time.sleep(random.uniform(0.03, 0.08))
        print("   ✓ Entered password")
        
        time.sleep(1)
        next_btn = driver.find_element(By.ID, "iSignupAction")
        next_btn.click()
        print("   ✓ Clicked Next")
    except Exception as e:
        print(f"   ⚠️ Password step: {e}")
    
    time.sleep(3)
    
    # Step 3: Name
    print("\n👤 Step 3: Enter name...")
    try:
        first_name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "FirstName"))
        )
        last_name = driver.find_element(By.ID, "LastName")
        
        for char in "สมชาย":
            first_name.send_keys(char)
            time.sleep(0.08)
        for char in "ใจดี":
            last_name.send_keys(char)
            time.sleep(0.08)
        
        print("   ✓ Entered: สมชาย ใจดี")
        
        time.sleep(1)
        next_btn = driver.find_element(By.ID, "iSignupAction")
        next_btn.click()
        print("   ✓ Clicked Next")
    except Exception as e:
        print(f"   ⚠️ Name step: {e}")
    
    time.sleep(3)
    
    # Step 4: Birthday
    print("\n🎂 Step 4: Enter birthday...")
    try:
        from selenium.webdriver.support.ui import Select
        
        day = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "BirthDay"))
        ))
        day.select_by_value(str(random.randint(1, 28)))
        
        month = Select(driver.find_element(By.ID, "BirthMonth"))
        month.select_by_value(str(random.randint(1, 12)))
        
        year_input = driver.find_element(By.ID, "BirthYear")
        year_input.clear()
        year_input.send_keys(str(random.randint(1985, 2000)))
        
        print("   ✓ Entered birthday")
        
        time.sleep(1)
        next_btn = driver.find_element(By.ID, "iSignupAction")
        next_btn.click()
        print("   ✓ Clicked Next")
    except Exception as e:
        print(f"   ⚠️ Birthday step: {e}")
    
    print("\n" + "=" * 60)
    print("  ถึง Captcha แล้ว - ดูว่าผ่านได้ไหม")
    print("  Chrome ยังเปิดอยู่ ลองทำต่อด้วยมือได้")
    print("  กด Ctrl+C เมื่อเสร็จ")
    print("=" * 60)
    
    # Keep running
    while True:
        time.sleep(5)
        
except KeyboardInterrupt:
    print("\n\n👋 Done!")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n💡 Note: Chrome ยังเปิดอยู่ สามารถใช้ต่อได้")
