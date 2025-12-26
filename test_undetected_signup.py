#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test with undetected-chromedriver - bypass bot detection
ใช้ undetected-chromedriver ที่ bypass anti-bot ได้ดีกว่า selenium ปกติ
"""

import undetected_chromedriver as uc
import time
import random
import string
import os

# Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNUP_URL = "https://signup.live.com/signup?mkt=th-th&lic=1"

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def main():
    print("=" * 60)
    print("  Outlook Registration - Undetected Chrome")
    print("=" * 60)
    
    # Generate data
    username = generate_random_string(12)
    email = f"{username}@outlook.co.th"
    password = "Test@" + generate_random_string(8) + "!"
    
    print(f"\n📧 Email: {email}")
    print(f"🔑 Password: {password}")
    
    # Chrome options
    options = uc.ChromeOptions()
    options.add_argument("--window-size=500,700")
    options.add_argument("--lang=th-TH")
    
    # ใช้ profile แยก (เหมือนสร้าง profile ใหม่ใน Chrome)
    profile_dir = os.path.join(BASE_DIR, "chrome_profile")
    options.add_argument(f"--user-data-dir={profile_dir}")
    
    print("\n🌐 Starting undetected Chrome...")
    
    # undetected-chromedriver จะ bypass bot detection อัตโนมัติ
    driver = uc.Chrome(options=options, version_main=None)  # auto-detect version
    
    try:
        print(f"🔗 Going to: {SIGNUP_URL}")
        driver.get(SIGNUP_URL)
        time.sleep(5)  # รอหน้าโหลดนานขึ้น
        
        # Step 1: Enter email
        print("\n📝 Step 1: Enter email...")
        
        # รอจนกว่า element จะพร้อม
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        email_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "MemberName"))
        )
        email_input.clear()
        
        # พิมพ์ทีละตัวเหมือนคนพิมพ์
        for char in email:
            email_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        print(f"   ✓ Entered: {email}")
        time.sleep(1)
        
        # Click Next
        next_btn = driver.find_element("id", "iSignupAction")
        next_btn.click()
        print("   ✓ Clicked Next")
        time.sleep(3)
        
        # Check for errors
        page_source = driver.page_source
        if "ชื่อนี้ถูกใช้แล้ว" in page_source or "already taken" in page_source.lower():
            print("   ⚠️ Username taken, try again with different name")
        
        # Step 2: Password
        print("\n🔐 Step 2: Enter password...")
        try:
            pwd_input = driver.find_element("id", "PasswordInput")
            for char in password:
                pwd_input.send_keys(char)
                time.sleep(random.uniform(0.03, 0.1))
            print(f"   ✓ Entered password")
            time.sleep(1)
            
            next_btn = driver.find_element("id", "iSignupAction")
            next_btn.click()
            print("   ✓ Clicked Next")
            time.sleep(3)
        except Exception as e:
            print(f"   ⚠️ Password step: {e}")
        
        # Step 3: Name
        print("\n👤 Step 3: Enter name...")
        try:
            first_name = driver.find_element("id", "FirstName")
            last_name = driver.find_element("id", "LastName")
            
            for char in "สมชาย":
                first_name.send_keys(char)
                time.sleep(random.uniform(0.05, 0.1))
            
            for char in "ใจดี":
                last_name.send_keys(char)
                time.sleep(random.uniform(0.05, 0.1))
            
            print("   ✓ Entered name: สมชาย ใจดี")
            time.sleep(1)
            
            next_btn = driver.find_element("id", "iSignupAction")
            next_btn.click()
            print("   ✓ Clicked Next")
            time.sleep(3)
        except Exception as e:
            print(f"   ⚠️ Name step: {e}")
        
        # Step 4: Birthday
        print("\n🎂 Step 4: Enter birthday...")
        try:
            from selenium.webdriver.support.ui import Select
            
            # Country (should be Thailand already)
            country = Select(driver.find_element("id", "Country"))
            country.select_by_value("TH")
            
            # Day
            day = Select(driver.find_element("id", "BirthDay"))
            day.select_by_value(str(random.randint(1, 28)))
            
            # Month
            month = Select(driver.find_element("id", "BirthMonth"))
            month.select_by_value(str(random.randint(1, 12)))
            
            # Year
            year_input = driver.find_element("id", "BirthYear")
            year_input.clear()
            year_input.send_keys(str(random.randint(1985, 2000)))
            
            print("   ✓ Entered birthday")
            time.sleep(1)
            
            next_btn = driver.find_element("id", "iSignupAction")
            next_btn.click()
            print("   ✓ Clicked Next")
            time.sleep(5)
        except Exception as e:
            print(f"   ⚠️ Birthday step: {e}")
        
        # Check current state
        print("\n📋 Current page state:")
        current_url = driver.current_url
        print(f"   URL: {current_url}")
        
        page_source = driver.page_source
        if "มาเริ่มกัน" in page_source or "กดค้าง" in page_source:
            print("   🎯 CAPTCHA page detected!")
            print("\n" + "=" * 60)
            print("   กรุณาแก้ captcha ด้วยตัวเอง แล้วดูว่าผ่านได้ไหม")
            print("=" * 60)
            
            # รอให้ user แก้ captcha
            input("\n   กด Enter เมื่อแก้ captcha เสร็จแล้ว...")
            
        elif "Stay signed in" in page_source or "ลงชื่อเข้าใช้ค้างไว้" in page_source:
            print("   ✅ SUCCESS! Account created!")
            print(f"\n   📧 Email: {email}")
            print(f"   🔑 Password: {password}")
            
            # Save to file
            with open(os.path.join(BASE_DIR, "accounts.txt"), "a", encoding="utf-8") as f:
                f.write(f"{email}|{password}\n")
            print("   💾 Saved to accounts.txt")
        else:
            print("   ❓ Unknown state")
            driver.save_screenshot("current_state.png")
            print("   📸 Screenshot saved: current_state.png")
        
        print("\n⏳ Waiting... (press Ctrl+C to exit)")
        time.sleep(300)
        
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("🔒 Browser closed")

if __name__ == "__main__":
    main()
