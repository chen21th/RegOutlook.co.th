#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RegOutlookTH - Undetected Chrome Test
ใช้ undetected-chromedriver เพื่อ bypass AI detection
"""

import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data import generate_username, generate_password, get_random_name, get_random_birthdate
from config import EMAIL_DOMAIN

print("=" * 60)
print("  RegOutlookTH - Undetected Chrome Test")
print("=" * 60)

# Generate account data
username = generate_username()
email = username + EMAIL_DOMAIN
password = generate_password()
first_name, last_name = get_random_name("thai")
birth_day, birth_month, birth_year = get_random_birthdate()

# Thai month names
THAI_MONTHS = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
               "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

print(f"\n📧 Account Info:")
print(f"   Email: {email}")
print(f"   Password: {password}")
print(f"   Name: {first_name} {last_name}")
print(f"   Birthday: {birth_day}/{birth_month}/{birth_year}")

# Setup undetected Chrome
print(f"\n🌐 Starting Undetected Chrome...")

options = uc.ChromeOptions()
options.add_argument("--lang=th-TH")
options.add_argument("--window-size=450,800")
options.add_argument("--window-position=100,50")

# ใช้ undetected_chromedriver
driver = uc.Chrome(options=options, use_subprocess=True)

print("   ✓ Browser started (Undetected mode)")

try:
    # Step 1: Go to signup
    print("\n[STEP 1] Going to signup page...")
    driver.get("https://signup.live.com/signup?mkt=th-th&lic=1")
    time.sleep(3)
    
    # Step 2: Enter email
    print(f"\n[STEP 2] Entering email: {email}")
    email_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "อีเมล"))
    )
    email_input.send_keys(email)
    print("   ✓ Email entered")
    time.sleep(1)
    
    # Step 3: Click Next
    print("\n[STEP 3] Clicking Next...")
    time.sleep(2)
    next_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], #iSignupAction, #idSIButton9"))
    )
    next_btn.click()
    time.sleep(3)
    
    # Step 4: Enter password
    print("\n[STEP 4] Entering password...")
    password_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
    )
    password_input.send_keys(password)
    print("   ✓ Password entered")
    time.sleep(1)
    
    # Step 5: Click Next
    print("\n[STEP 5] Clicking Next...")
    time.sleep(1)
    next_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], #iSignupAction, #idSIButton9"))
    )
    next_btn.click()
    time.sleep(3)
    
    # Step 6: Birthday
    print(f"\n[STEP 6] Entering birthday: {birth_day}/{birth_month}/{birth_year}")
    
    # รอ dropdown โหลด
    time.sleep(2)
    
    # Day dropdown - หาทั้งหมดที่เป็น dropdown/select
    print("   Finding birthday elements...")
    
    # หา day element
    try:
        # วิธี 1: Custom dropdown
        day_btn = driver.find_element(By.ID, "BirthDayDropdown")
        day_btn.click()
        time.sleep(1)
        
        # หา option จาก listbox
        day_option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[@role='listbox']//div[@data-value='{birth_day}'] | //div[@role='option' and text()='{birth_day}'] | //div[contains(@class,'option') and text()='{birth_day}']"))
        )
        day_option.click()
        print(f"   ✓ Day: {birth_day}")
    except Exception as e:
        print(f"   Day error: {e}")
        # Debug: แสดง HTML ของ dropdown
        try:
            dropdown_html = driver.find_element(By.ID, "BirthDayDropdown").get_attribute("outerHTML")
            print(f"   Day dropdown: {dropdown_html[:200]}...")
        except:
            pass
    time.sleep(1)
    
    # Month dropdown
    month_name = THAI_MONTHS[int(birth_month)]
    print(f"   Selecting month: {month_name}")
    try:
        month_btn = driver.find_element(By.ID, "BirthMonthDropdown")
        month_btn.click()
        time.sleep(1)
        
        # หา option ด้วยชื่อเดือนไทย
        month_option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[@role='listbox']//div[contains(text(),'{month_name}')] | //div[@role='option' and contains(text(),'{month_name}')] | //div[contains(@class,'option') and contains(text(),'{month_name}')]"))
        )
        month_option.click()
        print(f"   ✓ Month: {month_name}")
    except Exception as e:
        print(f"   Month error: {e}")
        try:
            dropdown_html = driver.find_element(By.ID, "BirthMonthDropdown").get_attribute("outerHTML")
            print(f"   Month dropdown: {dropdown_html[:200]}...")
        except:
            pass
    time.sleep(1)
    
    # Year input
    print(f"   Entering year: {birth_year}")
    year_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='number']")
    for inp in year_inputs:
        placeholder = inp.get_attribute("placeholder") or ""
        name = inp.get_attribute("name") or ""
        id_attr = inp.get_attribute("id") or ""
        if "year" in id_attr.lower() or "year" in name.lower() or "ปี" in placeholder:
            inp.clear()
            inp.send_keys(str(birth_year))
            print(f"   ✓ Year: {birth_year} (found: {id_attr or name})")
            break
    time.sleep(1)
    
    # Step 7: Click Next
    print("\n[STEP 7] Clicking Next...")
    time.sleep(1)
    next_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], #iSignupAction, #idSIButton9"))
    )
    next_btn.click()
    time.sleep(3)
    
    # Step 8: Enter name
    print(f"\n[STEP 8] Entering name: {first_name} {last_name}")
    
    # หา text input ทั้งหมดที่มองเห็น
    time.sleep(2)
    text_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']:not([readonly])")
    visible_inputs = [inp for inp in text_inputs if inp.is_displayed()]
    
    print(f"   Found {len(visible_inputs)} visible text inputs")
    
    if len(visible_inputs) >= 2:
        # First = First name, Second = Last name
        visible_inputs[0].clear()
        visible_inputs[0].send_keys(first_name)
        print(f"   ✓ First name: {first_name}")
        time.sleep(0.5)
        
        visible_inputs[1].clear()
        visible_inputs[1].send_keys(last_name)
        print(f"   ✓ Last name: {last_name}")
    elif len(visible_inputs) == 1:
        # อาจเป็น Full name
        visible_inputs[0].send_keys(f"{first_name} {last_name}")
        print(f"   ✓ Full name: {first_name} {last_name}")
    else:
        # ลองหาด้วย ID เดิม
        try:
            first_input = driver.find_element(By.ID, "FirstName")
            first_input.send_keys(first_name)
            print(f"   ✓ First name: {first_name}")
            
            last_input = driver.find_element(By.ID, "LastName")
            last_input.send_keys(last_name)
            print(f"   ✓ Last name: {last_name}")
        except Exception as e:
            print(f"   Name input error: {e}")
    
    time.sleep(1)
    
    # Step 9: Click Next
    print("\n[STEP 9] Clicking Next...")
    time.sleep(1)
    next_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], #iSignupAction, #idSIButton9"))
    )
    next_btn.click()
    time.sleep(5)
    
    # Check result
    print(f"\n📍 Current state:")
    print(f"   URL: {driver.current_url}")
    
    page_source = driver.page_source
    
    # Check for captcha
    if "มาพิสูจน์" in page_source or "แก้ปริศนา" in page_source or "แก้ไขปริศนา" in page_source:
        print("   🔐 FunCaptcha detected! Using 2Captcha...")
        
        solver = TwoCaptcha("f5cb74cff21d8caef0af74e953124f12")
        print("   [2Captcha] Sending to solve (30-60 sec)...")
        
        try:
            result = solver.funcaptcha(
                sitekey="B7D8911C-5CC8-A9A3-35B0-554ACEE604DA",
                url="https://signup.live.com/signup?mkt=th-th&lic=1",
                surl="https://client-api.arkoselabs.com"
            )
            
            token = result['code']
            print(f"   [2Captcha] ✓ Solved! Token: {token[:50]}...")
            
            # Inject token
            driver.execute_script(f"""
                window.postMessage({{eventId:'challenge-complete', payload:{{sessionToken:'{token}'}}}}, '*');
            """)
            print("   [Inject] Token sent!")
            time.sleep(5)
            
        except Exception as e:
            print(f"   [2Captcha] Error: {e}")
    
    elif "กดค้าง" in page_source:
        print("   🔐 Hold captcha - need manual solve or different approach")
    
    elif "stay signed" in page_source.lower() or "ลงชื่อเข้าใช้" in page_source:
        print("   🎉 SUCCESS! Account may be created!")
        with open("accounts.txt", "a", encoding="utf-8") as f:
            f.write(f"{email}|{password}|{first_name} {last_name}\n")
        print("   💾 Saved to accounts.txt")
    
    else:
        print("   ❓ Unknown state")
    
    print("\n⏳ Waiting 120 seconds...")
    time.sleep(120)

except KeyboardInterrupt:
    print("\n\n⚠️ Interrupted")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("\n🔒 Closing browser...")
    driver.quit()
    print("   Done!")
