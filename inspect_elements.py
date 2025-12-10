#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ตรวจสอบ element IDs บนหน้า signup"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ABC_PROXY_URL
from browser import BrowserManager
from selenium.webdriver.common.by import By

print("=" * 60)
print("  Element Inspector - Outlook Signup")
print("=" * 60)

browser = BrowserManager(proxy=ABC_PROXY_URL, position_x=100, position_y=50)

try:
    driver = browser.start()
    print("\n[1] Going to signup page...")
    browser.go_to_signup()
    time.sleep(5)
    
    print(f"\n[2] Current URL: {driver.current_url}")
    print(f"    Title: {driver.title}")
    
    # Find all input elements
    print("\n[3] Looking for input elements...")
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"    Found {len(inputs)} input elements:")
    for inp in inputs:
        inp_id = inp.get_attribute("id")
        inp_name = inp.get_attribute("name")
        inp_type = inp.get_attribute("type")
        inp_placeholder = inp.get_attribute("placeholder")
        if inp_id or inp_name:
            print(f"      - id='{inp_id}' name='{inp_name}' type='{inp_type}' placeholder='{inp_placeholder}'")
    
    # Find all buttons
    print("\n[4] Looking for buttons...")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"    Found {len(buttons)} buttons:")
    for btn in buttons:
        btn_id = btn.get_attribute("id")
        btn_text = btn.text[:50] if btn.text else ""
        print(f"      - id='{btn_id}' text='{btn_text}'")
    
    # Look for specific known elements
    print("\n[5] Checking specific elements...")
    test_ids = ["MemberName", "iSignupAction", "liveSwitch", "usernameInput", "nextButton", "memberName"]
    for test_id in test_ids:
        try:
            elem = driver.find_element(By.ID, test_id)
            print(f"    ✓ Found: #{test_id}")
        except:
            print(f"    ✗ Not found: #{test_id}")
    
    # Also check by name
    print("\n[6] Checking by name attribute...")
    test_names = ["MemberName", "loginfmt", "passwd"]
    for test_name in test_names:
        try:
            elem = driver.find_element(By.NAME, test_name)
            print(f"    ✓ Found: name='{test_name}'")
        except:
            print(f"    ✗ Not found: name='{test_name}'")
    
    print("\n⏳ Waiting 60 seconds - check the browser window...")
    time.sleep(60)
    
except KeyboardInterrupt:
    print("\n⚠️ Interrupted")
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    browser.close()
    print("\n✓ Browser closed")
