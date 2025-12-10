#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ทดสอบ Proxy แบบละเอียด"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

print("=" * 50)
print("  Proxy Debug Test")
print("=" * 50)

# Test 1: ไม่ใช้ proxy
print("\n[1] Testing without proxy...")
try:
    r = requests.get("https://httpbin.org/ip", timeout=10)
    print(f"    Your real IP: {r.json().get('origin')}")
except Exception as e:
    print(f"    Error: {e}")

# Test 2: ABC Proxy
from config import ABC_PROXY_URL, ABC_PROXY_HOST, ABC_PROXY_PORT, ABC_PROXY_USER, ABC_PROXY_PASS

print(f"\n[2] ABC Proxy config:")
print(f"    Host: {ABC_PROXY_HOST}")
print(f"    Port: {ABC_PROXY_PORT}")
print(f"    User: {ABC_PROXY_USER}")
print(f"    Pass: {ABC_PROXY_PASS}")
print(f"    Full URL: {ABC_PROXY_URL}")

print("\n[3] Testing ABC Proxy...")
try:
    proxies = {
        "http": ABC_PROXY_URL,
        "https": ABC_PROXY_URL
    }
    r = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=30)
    print(f"    ✓ Proxy IP: {r.json().get('origin')}")
except requests.exceptions.ProxyError as e:
    print(f"    ✗ Proxy Error: {e}")
except requests.exceptions.ConnectTimeout as e:
    print(f"    ✗ Connection Timeout: {e}")
except Exception as e:
    print(f"    ✗ Error: {type(e).__name__}: {e}")

# Test 3: ลองใช้ format อื่น
print("\n[4] Testing alternative proxy formats...")

# Format 1: http://host:port (ไม่มี auth)
proxy_no_auth = f"http://{ABC_PROXY_HOST}:{ABC_PROXY_PORT}"
print(f"    Format 1 (no auth): {proxy_no_auth}")
try:
    proxies = {"http": proxy_no_auth, "https": proxy_no_auth}
    r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=10)
    print(f"      ✓ IP: {r.json().get('origin')}")
except Exception as e:
    print(f"      ✗ {type(e).__name__}")

# Format 2: socks5
proxy_socks = f"socks5://{ABC_PROXY_USER}:{ABC_PROXY_PASS}@{ABC_PROXY_HOST}:{ABC_PROXY_PORT}"
print(f"    Format 2 (socks5): socks5://...@{ABC_PROXY_HOST}:{ABC_PROXY_PORT}")
try:
    proxies = {"http": proxy_socks, "https": proxy_socks}
    r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=10)
    print(f"      ✓ IP: {r.json().get('origin')}")
except Exception as e:
    print(f"      ✗ {type(e).__name__}")

print("\n" + "=" * 50)
