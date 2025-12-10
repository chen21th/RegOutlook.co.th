#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick inspect - หา elements แต่ละหน้า"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ABC_PROXY_URL, EMAIL_DOMAIN
from browser import BrowserManager
from data import generate_username, generate_password
from selenium.webdriver.common.by import By

def inspect_inputs(driver):
    """แสดง input elements"""
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"\n  📝 Inputs ({len(inputs)}):")
    for inp in inputs[:15]:
        inp_id = inp.get_attribute("id") or ""
        inp_name = inp.get_attribute("name") or ""
        inp_type = inp.get_attribute("type") or ""
        inp_ph = inp.get_attribute("placeholder") or ""
        print(f"    id='{inp_id}' name='{inp_name}' type='{inp_type}' placeholder='{inp_ph[:20]}'")

def inspect_buttons(driver):
    """แสดง buttons"""
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"\n  🔘 Buttons ({len(buttons)}):")
    for btn in buttons[:10]:
        btn_id = btn.get_attribute("id") or ""
        btn_text = btn.text[:30] if btn.text else ""
        btn_testid = btn.get_attribute("data-testid") or ""
        print(f"    id='{btn_id}' testid='{btn_testid}' text='{btn_text}'")

def inspect_selects(driver):
    """แสดง select dropdowns"""
    selects = driver.find_elements(By.TAG_NAME, "select")
    print(f"\n  📋 Selects ({len(selects)}):")
    for sel in selects[:10]:
        sel_id = sel.get_attribute("id") or ""
        sel_name = sel.get_attribute("name") or ""
        print(f"    id='{sel_id}' name='{sel_name}'")

print("=" * 60)
browser = BrowserManager(proxy=ABC_PROXY_URL, position_x=100, position_y=50)

try:
    driver = browser.start()
    
    # Step 1: Email
    browser.go_to_signup()
    time.sleep(3)
    
    # Enter email
    email = generate_username() + EMAIL_DOMAIN
    password = generate_password()
    print(f"\n📧 Email: {email}")
    browser.fill_input_by_name("อีเมล", email)
    time.sleep(1)
    browser.click_primary_button()
    time.sleep(4)
    
    # Step 2: Password - inspect
    print("\n" + "="*50)
    print("  STEP 2: PASSWORD PAGE")
    print("="*50)
    inspect_inputs(driver)
    inspect_buttons(driver)
    
    browser.fill_input_by_type("password", password)
    time.sleep(1)
    browser.click_primary_button()
    time.sleep(4)
    
    # Step 3: Name - inspect
    print("\n" + "="*50)
    print("  STEP 3: NAME PAGE")
    print("="*50)
    print(f"  Title: {driver.title}")
    inspect_inputs(driver)
    inspect_buttons(driver)
    
    input("\n  >> Press Enter to continue to birthday...")
    
    # Try to fill name and continue
    # Look for first two text inputs
    text_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
    if len(text_inputs) >= 2:
        text_inputs[0].send_keys("ทดสอบ")
        time.sleep(0.5)
        text_inputs[1].send_keys("ระบบ")
    browser.click_primary_button()
    time.sleep(4)
    
    # Step 4: Birthday - inspect
    print("\n" + "="*50)
    print("  STEP 4: BIRTHDAY PAGE")
    print("="*50)
    print(f"  Title: {driver.title}")
    inspect_inputs(driver)
    inspect_buttons(driver)
    inspect_selects(driver)
    
    # Look for combobox buttons
    combos = driver.find_elements(By.CSS_SELECTOR, "button[role='combobox']")
    print(f"\n  🎯 Combobox buttons ({len(combos)}):")
    for i, combo in enumerate(combos):
        combo_id = combo.get_attribute("id") or ""
        combo_name = combo.get_attribute("name") or ""
        combo_text = combo.text[:30] if combo.text else ""
        print(f"    [{i}] id='{combo_id}' name='{combo_name}' text='{combo_text}'")
    
    input("\n  >> Press Enter to close...")

except KeyboardInterrupt:
    print("\n⚠️ Interrupted")
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    browser.close()
