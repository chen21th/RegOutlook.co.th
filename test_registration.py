#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ทดสอบ Registration Flow แบบ step-by-step (Updated for new MS UI)"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("  RegOutlookTH - Single Registration Test (New UI)")
print("=" * 60)

from config import ABC_PROXY_URL, EMAIL_DOMAIN
from browser import BrowserManager
from data import generate_username, generate_password, get_random_name, get_random_birthdate

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

try:
    driver = browser.start()
    print("   ✓ Browser started")
    
    # Go to signup
    print("\n[STEP 1] Going to signup page...")
    browser.go_to_signup()
    time.sleep(5)
    print(f"   URL: {driver.current_url}")
    
    # Enter email (Thai UI uses name='อีเมล', English uses name='Email')
    print(f"\n[STEP 2] Entering email: {email}")
    email_entered = (
        browser.fill_input_by_name("อีเมล", email) or  # Thai
        browser.fill_input_by_name("Email", email) or  # English
        browser.fill_input("MemberName", email) or     # Old UI
        browser.fill_input("floatingLabelInput4", email)  # ID fallback
    )
    if email_entered:
        print("   ✓ Email entered")
    else:
        print("   ✗ Failed to enter email")
    time.sleep(2)
    
    # Click Next button using primaryButton
    print("\n[STEP 3] Clicking Next...")
    if browser.click_primary_button():
        print("   ✓ Clicked")
    else:
        print("   ✗ Failed to click")
    time.sleep(5)
    
    # Check current page
    page_source = driver.page_source
    if "already" in page_source.lower() or "taken" in page_source.lower():
        print("   ⚠️ Email might be taken!")
    
    # Enter password (Thai UI: type='password', no name attribute)
    print(f"\n[STEP 4] Entering password...")
    success = False
    # Try by type first (most reliable for new UI)
    if browser.fill_input_by_type("password", password):
        print("   ✓ Password entered (by type)")
        success = True
    else:
        # Try different name selectors
        for selector in ["รหัสผ่าน", "Password", "PasswordInput", "passwd"]:
            if browser.fill_input_by_name(selector, password):
                print(f"   ✓ Password entered (name={selector})")
                success = True
                break
            if browser.fill_input(selector, password):
                print(f"   ✓ Password entered (id={selector})")
                success = True
                break
    if not success:
        print("   ✗ Failed to find password field")
    time.sleep(2)
    
    # Click Next
    print("\n[STEP 5] Clicking Next...")
    if browser.click_primary_button():
        print("   ✓ Clicked")
    else:
        print("   ✗ Failed to click")
    time.sleep(5)
    
    # Enter name (Thai: ชื่อ/นามสกุล, English: FirstName/LastName)
    print(f"\n[STEP 6] Entering name: {first_name} {last_name}")
    # Try Thai names first, then English, then by type
    first_name_entered = (
        browser.fill_input_by_name("ชื่อ", first_name) or  # Thai
        browser.fill_input_by_name("FirstName", first_name) or
        browser.fill_input("FirstName", first_name) or
        browser.fill_input_by_type("text", first_name)  # First text input
    )
    time.sleep(1)
    last_name_entered = (
        browser.fill_input_by_name("นามสกุล", last_name) or  # Thai
        browser.fill_input_by_name("LastName", last_name) or
        browser.fill_input("LastName", last_name)
    )
    print(f"   First name: {'✓' if first_name_entered else '✗'}")
    print(f"   Last name: {'✓' if last_name_entered else '✗'}")
    time.sleep(2)
    
    # Click Next
    print("\n[STEP 7] Clicking Next...")
    if browser.click_primary_button():
        print("   ✓ Clicked")
    else:
        print("   ✗ Failed to click")
    time.sleep(5)
    
    # Enter birthday
    print(f"\n[STEP 8] Entering birthday: {birth_day}/{birth_month}/{birth_year}")
    # Try dropdown or input (Thai names: เดือน, วัน, ปี)
    month_entered = (
        browser.select_dropdown_by_name("เดือน", birth_month) or  # Thai
        browser.select_dropdown("BirthMonth", birth_month) or
        browser.select_dropdown_by_name("BirthMonth", birth_month)
    )
    day_entered = (
        browser.select_dropdown_by_name("วัน", birth_day) or  # Thai
        browser.select_dropdown("BirthDay", birth_day) or
        browser.select_dropdown_by_name("BirthDay", birth_day)
    )
    year_entered = (
        browser.fill_input_by_name("ปี", str(birth_year)) or  # Thai
        browser.fill_input("BirthYear", str(birth_year)) or
        browser.fill_input_by_name("BirthYear", str(birth_year))
    )
    print(f"   Month: {'✓' if month_entered else '✗'}")
    print(f"   Day: {'✓' if day_entered else '✗'}")
    print(f"   Year: {'✓' if year_entered else '✗'}")
    time.sleep(2)
    
    # Click Next
    print("\n[STEP 9] Clicking Next...")
    if browser.click_primary_button():
        print("   ✓ Clicked")
    else:
        print("   ✗ Failed to click")
    time.sleep(5)
    
    # Check current state
    print(f"\n📍 Current state:")
    print(f"   URL: {driver.current_url}")
    
    page_source = driver.page_source
    if "phone" in page_source.lower() and ("verify" in page_source.lower() or "text" in page_source.lower()):
        print("   ⚠️ Phone verification required!")
        print("   This IP might be flagged.")
    elif "captcha" in page_source.lower() or "enforcement" in page_source.lower() or "puzzle" in page_source.lower():
        print("   🔐 CAPTCHA appeared! Ready for captcha solving...")
    elif "Stay signed in" in page_source or "stay signed" in page_source.lower():
        print("   🎉 SUCCESS! Account created!")
    else:
        print("   ❓ Unknown state - check browser window")
    
    print("\n⏳ Waiting 60 seconds to observe...")
    print("   Press Ctrl+C to exit early")
    time.sleep(60)
    
except KeyboardInterrupt:
    print("\n\n⚠️ Interrupted by user")
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("\n🔒 Closing browser...")
    browser.close()
    print("   Done!")
