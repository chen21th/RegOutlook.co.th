# ===== PROXY MANAGER =====

import requests
import time
from config import ABC_PROXY_URL, PROXY_CHECK_URL


class ABCProxyManager:
    """
    Class สำหรับจัดการ ABC Proxy (Rotating Proxy)
    ทุกครั้งที่ request จะได้ IP ใหม่อัตโนมัติ
    """
    
    def __init__(self):
        self.proxy_url = ABC_PROXY_URL
        self.check_url = PROXY_CHECK_URL
    
    def get_proxy(self):
        """
        ดึง proxy URL สำหรับใช้งาน
        ABC Proxy เป็นแบบ rotating - ทุก request จะได้ IP ใหม่
        """
        return self.proxy_url
    
    def check_current_ip(self):
        """เช็ค IP ปัจจุบันผ่าน proxy"""
        try:
            proxies = {
                "http": self.proxy_url,
                "https": self.proxy_url
            }
            response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=30)
            result = response.json()
            current_ip = result.get("origin", "Unknown")
            print(f"[PROXY] Current IP: {current_ip}")
            return current_ip
        except Exception as e:
            print(f"[PROXY ERROR] Cannot check IP: {e}")
            return None
    
    def test_proxy(self):
        """ทดสอบว่า proxy ใช้งานได้"""
        try:
            proxies = {
                "http": self.proxy_url,
                "https": self.proxy_url
            }
            response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=30)
            if response.status_code == 200:
                print(f"[PROXY] Test OK - IP: {response.json().get('origin')}")
                return True
            return False
        except Exception as e:
            print(f"[PROXY ERROR] Test failed: {e}")
            return False


class ProxyManager:
    """Class wrapper สำหรับ backward compatibility"""
    
    def __init__(self):
        self.abc_proxy = ABCProxyManager()
        self.current_proxy = self.abc_proxy.get_proxy()
    
    def get_new_proxy(self):
        """
        สำหรับ ABC Proxy rotating - ไม่ต้องขอใหม่
        แต่ละ request จะได้ IP ใหม่อัตโนมัติ
        """
        # Test proxy ก่อน
        if self.abc_proxy.test_proxy():
            return {
                "success": True,
                "proxy": self.current_proxy,
                "next_change": 0  # rotating = ไม่ต้องรอ
            }
        else:
            return {
                "success": False,
                "error": "Proxy test failed"
            }


class StaticProxyManager:
    """Class สำหรับใช้ proxy แบบ static list"""
    
    def __init__(self, proxy_file="proxies.txt"):
        self.proxies = []
        self.current_index = 0
        self.load_proxies(proxy_file)
    
    def load_proxies(self, proxy_file):
        """โหลด proxy จากไฟล์"""
        try:
            with open(proxy_file, "r") as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            print(f"[PROXY] Loaded {len(self.proxies)} proxies")
        except FileNotFoundError:
            print(f"[PROXY] File {proxy_file} not found, using no proxy")
            self.proxies = []
    
    def get_next(self):
        """ดึง proxy ถัดไป (round-robin)"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def get_random(self):
        """ดึง proxy แบบ random"""
        import random
        if not self.proxies:
            return None
        return random.choice(self.proxies)
