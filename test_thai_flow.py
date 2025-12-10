#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RegOutlookTH - Registration Test (Thai UI Flow)
Flow: Email -> Password -> Birthday -> Name -> Captcha
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("  RegOutlookTH - Registration Test (Thai Flow)")
print("  Email -> Password -> Birthday -> Name -> Captcha")
print("=" * 60)

from config import ABC_PROXY_URL, EMAIL_DOMAIN
from browser import BrowserManager
from data import generate_username, generate_password, get_random_name, get_random_birthdate
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Generate account data
username = generate_username()
email = username + EMAIL_DOMAIN
password = generate_password()
first_name, last_name = get_random_name("thai")
birth_day, birth_month, birth_year = get_random_birthdate()

print(f"\n📧 Account Info:")
print(f"   Email: {email}")
print(f"   Password: {password}")
print(f"   Name: {first_name} {last_name}")
print(f"   Birthday: {birth_day}/{birth_month}/{birth_year}")

# Start browser
print(f"\n🌐 Starting browser with proxy...")
browser = BrowserManager(proxy=ABC_PROXY_URL, position_x=100, position_y=50)

def click_dropdown_option(driver, dropdown_id, value):
    """คลิก dropdown แล้วเลือก option"""
    try:
        # คลิกปุ่ม dropdown
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, dropdown_id))
        )
        dropdown.click()
        time.sleep(0.5)
        
        # หา option ที่ต้องการ (ใช้ data-value หรือ text)
        option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[@data-value='{value}'] | //div[contains(@class, 'option') and text()='{value}']"))
        )
        option.click()
        return True
    except Exception as e:
        print(f"      Dropdown error: {e}")
        return False

try:
    driver = browser.start()
    print("   ✓ Browser started")
    
    # ===== STEP 1: Email =====
    print("\n[STEP 1] Going to signup page...")
    browser.go_to_signup()
    time.sleep(4)
    print(f"   URL: {driver.current_url}")
    
    print(f"\n[STEP 2] Entering email: {email}")
    if browser.fill_input_by_name("อีเมล", email) or browser.fill_input("floatingLabelInput4", email):
        print("   ✓ Email entered")
    time.sleep(1)
    
    print("\n[STEP 3] Clicking Next...")
    browser.click_primary_button()
    time.sleep(4)
    
    # ===== STEP 2: Password =====
    print(f"\n[STEP 4] Entering password...")
    if browser.fill_input_by_type("password", password):
        print("   ✓ Password entered")
    time.sleep(1)
    
    print("\n[STEP 5] Clicking Next...")
    browser.click_primary_button()
    time.sleep(4)
    
    # ===== STEP 3: Birthday (ประเทศ/วันเกิด) =====
    print(f"\n[STEP 6] Entering birthday: {birth_day}/{birth_month}/{birth_year}")
    
    # Thai month names
    THAI_MONTHS = {
        1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
        5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม", 8: "สิงหาคม",
        9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
    }
    
    # วัน - BirthDayDropdown
    print("   Selecting day...")
    try:
        day_dropdown = driver.find_element(By.ID, "BirthDayDropdown")
        day_dropdown.click()
        time.sleep(0.5)
        # คลิก option โดยใช้ text (ตัวเลข)
        day_option = driver.find_element(By.XPATH, f"//div[@role='option' and contains(text(), '{birth_day}')]")
        day_option.click()
        print(f"   ✓ Day: {birth_day}")
    except Exception as e:
        print(f"   ✗ Day failed: {type(e).__name__}")
    time.sleep(0.5)
    
    # เดือน - BirthMonthDropdown (ใช้ชื่อเดือนภาษาไทย)
    print("   Selecting month...")
    try:
        month_dropdown = driver.find_element(By.ID, "BirthMonthDropdown")
        month_dropdown.click()
        time.sleep(0.5)
        thai_month = THAI_MONTHS.get(birth_month, str(birth_month))
        month_option = driver.find_element(By.XPATH, f"//div[@role='option' and contains(text(), '{thai_month}')]")
        month_option.click()
        print(f"   ✓ Month: {thai_month}")
    except Exception as e:
        print(f"   ✗ Month failed: {type(e).__name__}")
    time.sleep(0.5)
    
    # ปี - BirthYear input
    print("   Entering year...")
    if browser.fill_input("floatingLabelInput23", str(birth_year)) or browser.fill_input_by_name("BirthYear", str(birth_year)):
        print(f"   ✓ Year: {birth_year}")
    else:
        print("   ✗ Year failed")
    time.sleep(1)
    
    print("\n[STEP 7] Clicking Next...")
    browser.click_primary_button()
    time.sleep(4)
    
    # ===== STEP 4: Name (ชื่อ/นามสกุล) =====
    print(f"\n[STEP 8] Entering name: {first_name} {last_name}")
    
    # หา input fields ทั้งหมดบนหน้านี้
    inputs = driver.find_elements(By.TAG_NAME, "input")
    text_inputs = [inp for inp in inputs if inp.get_attribute("type") in ["text", ""]]
    
    if len(text_inputs) >= 2:
        # First input = First name, Second = Last name
        text_inputs[0].clear()
        text_inputs[0].send_keys(first_name)
        print(f"   ✓ First name: {first_name}")
        time.sleep(0.5)
        
        text_inputs[1].clear()
        text_inputs[1].send_keys(last_name)
        print(f"   ✓ Last name: {last_name}")
    elif len(text_inputs) == 1:
        # อาจจะเป็น full name
        text_inputs[0].send_keys(f"{first_name} {last_name}")
        print(f"   ✓ Full name: {first_name} {last_name}")
    else:
        # Try by name attribute
        browser.fill_input_by_name("ชื่อ", first_name) or browser.fill_input_by_name("FirstName", first_name)
        browser.fill_input_by_name("นามสกุล", last_name) or browser.fill_input_by_name("LastName", last_name)
        print("   Tried by name attribute")
    
    time.sleep(1)
    
    print("\n[STEP 9] Clicking Next...")
    browser.click_primary_button()
    time.sleep(5)
    
    # ===== Check Result =====
    print(f"\n📍 Current state:")
    print(f"   URL: {driver.current_url}")
    
    page_source = driver.page_source
    
    # Debug: หาว่า "กดค้าง" อยู่ตรงไหนใน HTML
    if "กดค้าง" in page_source:
        import re
        # หา context รอบๆ คำว่า "กดค้าง"
        matches = list(re.finditer(r'.{0,100}กดค้าง.{0,100}', page_source))
        print(f"\n   🔍 Found 'กดค้าง' {len(matches)} times in HTML:")
        for i, m in enumerate(matches[:5]):  # แสดง 5 อันแรก
            snippet = m.group().replace('\n', ' ').replace('  ', ' ')
            print(f"   [{i+1}] ...{snippet}...")
    
    # Check for captcha - กดค้าง
    if "กดค้าง" in page_source or "กดปุ่มค้างไว้" in page_source or "มาพิสูจน์" in page_source:
        print("   🔐 Hold Captcha detected!")
        time.sleep(2)
        
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            
            # หาปุ่ม "กดค้าง" - ง่ายๆ ตรงๆ
            hold_button = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[2]/p")
            print(f"   ✓ Found: {hold_button.text}")
            
            # กดค้าง 30 วินาที
            print("   🖱️ Holding for 30 seconds...")
            actions = ActionChains(driver)
            actions.click_and_hold(hold_button).perform()
            
            for i in range(30):
                time.sleep(1)
                print(f"      Holding... {i+1}s", end="\r")
                try:
                    driver.find_element(By.XPATH, "//p[text()='กดค้าง']")
                except:
                    print(f"\n   ✓ Passed after {i+1}s!")
                    break
            
            actions.release().perform()
            print("\n   ✓ Released!")
            time.sleep(5)
            
            # เช็คผลลัพธ์
            result_page = driver.page_source
            if "stay signed" in result_page.lower() or "ลงชื่อเข้าใช้ค้างไว้" in result_page:
                print("\n   🎉 SUCCESS! Account created!")
                with open("accounts.txt", "a", encoding="utf-8") as f:
                    f.write(f"{email}|{password}|{first_name} {last_name}\n")
                print("   💾 Saved to accounts.txt")
            elif "phone" in result_page.lower() or "เบอร์" in result_page:
                print("   ⚠️ Phone verification required")
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    elif "phone" in page_source.lower() or "เบอร์" in page_source:
        print("   ⚠️ Phone verification required!")
    elif "stay signed" in page_source.lower() or "ลงชื่อเข้าใช้ค้างไว้" in page_source:
        print("   🎉 SUCCESS!")
    else:
        print("   ❓ Unknown state")
    
    print("\n⏳ Waiting 120 seconds...")
    time.sleep(120)
    
except KeyboardInterrupt:
    print("\n\n⚠️ Interrupted")
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    print("\n🔒 Closing browser...")
    browser.close()
    print("   Done!")
