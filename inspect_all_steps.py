#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Inspect ทุก step ของ signup"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ABC_PROXY_URL, EMAIL_DOMAIN
from browser import BrowserManager
from data import generate_username
from selenium.webdriver.common.by import By

print("=" * 60)
print("  Step-by-Step Element Inspector")
print("=" * 60)

browser = BrowserManager(proxy=ABC_PROXY_URL, position_x=100, position_y=50)

def inspect_page(driver, step_name):
    """Inspect current page elements"""
    print(f"\n{'='*40}")
    print(f"  {step_name}")
    print(f"{'='*40}")
    print(f"  URL: {driver.current_url[:60]}...")
    print(f"  Title: {driver.title}")
    
    # Find inputs
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"\n  Inputs ({len(inputs)}):")
    for inp in inputs[:10]:  # limit to 10
        inp_id = inp.get_attribute("id") or ""
        inp_name = inp.get_attribute("name") or ""
        inp_type = inp.get_attribute("type") or ""
        if inp_id or inp_name:
            print(f"    - id='{inp_id}' name='{inp_name}' type='{inp_type}'")
    
    # Find buttons
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"\n  Buttons ({len(buttons)}):")
    for btn in buttons[:5]:
        btn_id = btn.get_attribute("id") or ""
        btn_text = btn.text[:30] if btn.text else ""
        print(f"    - id='{btn_id}' text='{btn_text}'")
    
    # Find selects (dropdowns)
    selects = driver.find_elements(By.TAG_NAME, "select")
    print(f"\n  Dropdowns ({len(selects)}):")
    for sel in selects[:5]:
        sel_id = sel.get_attribute("id") or ""
        sel_name = sel.get_attribute("name") or ""
        print(f"    - id='{sel_id}' name='{sel_name}'")

try:
    driver = browser.start()
    
    # Step 1: Signup page
    browser.go_to_signup()
    time.sleep(3)
    inspect_page(driver, "STEP 1: Email Page")
    
    # Enter email
    email = generate_username() + EMAIL_DOMAIN
    print(f"\n  >> Entering email: {email}")
    browser.fill_input_by_name("อีเมล", email) or browser.fill_input_by_name("Email", email)
    time.sleep(1)
    browser.click_button_by_text("ถัดไป") or browser.click_button_by_text("Next")
    time.sleep(5)
    
    # Step 2: Password page
    inspect_page(driver, "STEP 2: Password Page")
    input("\nPress Enter to continue to name step...")
    
    # Enter password and continue
    browser.fill_input_by_name("รหัสผ่าน", "Test123456!@") or browser.fill_input_by_name("Password", "Test123456!@")
    time.sleep(1)
    browser.click_button_by_text("ถัดไป") or browser.click_button_by_text("Next")
    time.sleep(5)
    
    # Step 3: Name page
    inspect_page(driver, "STEP 3: Name Page")
    input("\nPress Enter to continue to birthday step...")
    
    # Enter name
    browser.fill_input_by_name("ชื่อ", "ทดสอบ") or browser.fill_input_by_name("FirstName", "Test")
    browser.fill_input_by_name("นามสกุล", "ระบบ") or browser.fill_input_by_name("LastName", "User")
    time.sleep(1)
    browser.click_button_by_text("ถัดไป") or browser.click_button_by_text("Next")
    time.sleep(5)
    
    # Step 4: Birthday page
    inspect_page(driver, "STEP 4: Birthday Page")
    input("\nPress Enter to close...")
    
except KeyboardInterrupt:
    print("\n⚠️ Interrupted")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    browser.close()
