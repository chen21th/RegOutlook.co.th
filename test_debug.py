#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script สำหรับทดสอบทีละส่วน"""

import sys
import os

# เพิ่ม current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("  RegOutlookTH - Debug Test")
print("=" * 50)

# Test 1: Import modules
print("\n[TEST 1] Importing modules...")
try:
    from config import ABC_PROXY_URL, EMAIL_DOMAIN, CHROME_DRIVER_PATH
    print(f"  ✓ config.py loaded")
    print(f"    - Email domain: {EMAIL_DOMAIN}")
    print(f"    - ChromeDriver: {CHROME_DRIVER_PATH}")
    print(f"    - Proxy URL: {ABC_PROXY_URL[:60]}...")
except Exception as e:
    print(f"  ✗ config.py error: {e}")

try:
    from data import THAI_NAMES, generate_password, generate_username, get_random_name
    print(f"  ✓ data.py loaded")
    print(f"    - Thai names count: {len(THAI_NAMES)}")
except Exception as e:
    print(f"  ✗ data.py error: {e}")

try:
    from proxy_manager import ABCProxyManager
    print(f"  ✓ proxy_manager.py loaded")
except Exception as e:
    print(f"  ✗ proxy_manager.py error: {e}")

try:
    from captcha_solver import CaptchaSolver
    print(f"  ✓ captcha_solver.py loaded")
except Exception as e:
    print(f"  ✗ captcha_solver.py error: {e}")

try:
    from browser import BrowserManager
    print(f"  ✓ browser.py loaded")
except Exception as e:
    print(f"  ✗ browser.py error: {e}")

# Test 2: Data generation
print("\n[TEST 2] Data generation...")
try:
    username = generate_username()
    password = generate_password()
    first_name, last_name = get_random_name("thai")
    print(f"  ✓ Username: {username}")
    print(f"  ✓ Password: {password}")
    print(f"  ✓ Name: {first_name} {last_name}")
except Exception as e:
    print(f"  ✗ Data generation error: {e}")

# Test 3: Proxy test
print("\n[TEST 3] Testing ABC Proxy...")
try:
    proxy_manager = ABCProxyManager()
    result = proxy_manager.test_proxy()
    if result:
        print(f"  ✓ Proxy working!")
        ip = proxy_manager.check_current_ip()
    else:
        print(f"  ✗ Proxy not working")
except Exception as e:
    print(f"  ✗ Proxy error: {e}")

# Test 4: ChromeDriver check
print("\n[TEST 4] Checking ChromeDriver...")
if os.path.exists(CHROME_DRIVER_PATH):
    print(f"  ✓ ChromeDriver found: {CHROME_DRIVER_PATH}")
else:
    print(f"  ✗ ChromeDriver NOT found: {CHROME_DRIVER_PATH}")
    print(f"    Download from: https://chromedriver.chromium.org/downloads")

# Test 5: Selenium import
print("\n[TEST 5] Testing Selenium...")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    print(f"  ✓ Selenium imported successfully")
except Exception as e:
    print(f"  ✗ Selenium error: {e}")

print("\n" + "=" * 50)
print("  Test complete!")
print("=" * 50)
