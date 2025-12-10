#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ทดสอบเปิด Browser พร้อม Proxy"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("  Browser Test with ABC Proxy")
print("=" * 50)

from config import ABC_PROXY_URL, CHROME_DRIVER_PATH
from browser import BrowserManager

print(f"\n[1] Creating browser with proxy...")
print(f"    Proxy: {ABC_PROXY_URL[:50]}...")
print(f"    Driver: {CHROME_DRIVER_PATH}")

browser = BrowserManager(proxy=ABC_PROXY_URL, position_x=100, position_y=100)

try:
    print("\n[2] Starting Chrome...")
    driver = browser.start()
    
    print("\n[3] Going to httpbin to check IP...")
    driver.get("https://httpbin.org/ip")
    time.sleep(3)
    
    # Get page content
    body = driver.find_element("tag name", "body").text
    print(f"    Response: {body}")
    
    print("\n[4] Going to Outlook signup page...")
    browser.go_to_signup()
    time.sleep(5)
    
    print(f"    Current URL: {driver.current_url}")
    print(f"    Title: {driver.title}")
    
    print("\n[5] Browser test successful!")
    print("    Press Enter to close browser...")
    input()
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    print("\n[6] Closing browser...")
    browser.close()
    print("    Done!")
