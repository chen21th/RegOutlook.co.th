# ===== MAIN ENTRY POINT =====
"""
RegOutlookTH - Outlook/Hotmail Registration Tool (Portable Version)
===================================================================

วิธีใช้:
1. แก้ไข config.py ใส่ API keys
2. วาง chromedriver.exe ไว้ในโฟลเดอร์เดียวกัน
3. รัน: python main.py

สำหรับ Portable Python:
- วาง Python portable ไว้ในโฟลเดอร์ python/
- รัน: python/python.exe main.py

Requirements:
- Python 3.8+
- selenium
- requests
"""

import time
import argparse
import sys
import os

# เพิ่ม current directory เข้า path (สำหรับ portable)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from proxy_manager import ProxyManager, ABCProxyManager, StaticProxyManager
from registrator import run_batch, AccountRegistrator
from config import MAX_THREADS, ABC_PROXY_URL


def main():
    parser = argparse.ArgumentParser(description="RegOutlookTH - Outlook Registration Tool (Portable)")
    parser.add_argument("--mode", choices=["abc", "static", "noproxy"], default="abc",
                       help="Proxy mode: abc=ABC Rotating Proxy, static=from file, noproxy=no proxy")
    parser.add_argument("--threads", type=int, default=MAX_THREADS,
                       help="Number of concurrent browsers")
    parser.add_argument("--names", choices=["thai", "viet"], default="thai",
                       help="Name type to use")
    parser.add_argument("--loop", action="store_true",
                       help="Run continuously")
    parser.add_argument("--count", type=int, default=0,
                       help="Total accounts to create (0 = unlimited)")
    
    args = parser.parse_args()
    
    print("=" * 55)
    print("  RegOutlookTH - Outlook Registration Tool (Portable)")
    print("  Domain: @outlook.co.th")
    print("=" * 55)
    print(f"Mode: {args.mode}")
    print(f"Threads: {args.threads}")
    print(f"Names: {args.names}")
    print(f"Loop: {args.loop}")
    print(f"Target count: {args.count if args.count > 0 else 'Unlimited'}")
    print("=" * 55)
    
    total_created = 0
    
    if args.mode == "abc":
        # ใช้ ABC Proxy (Rotating - ทุก request ได้ IP ใหม่)
        print("\n[INFO] Using ABC Proxy (Rotating)")
        print(f"[INFO] Proxy: {ABC_PROXY_URL[:50]}...")
        
        # Test proxy ก่อน
        proxy_manager = ABCProxyManager()
        if not proxy_manager.test_proxy():
            print("[ERROR] Proxy test failed! Check your ABC Proxy credentials.")
            return
        
        proxy = proxy_manager.get_proxy()
        
        while True:
            success = run_batch(proxy, args.threads, args.names)
            total_created += success
            
            print(f"\n[TOTAL] Accounts created: {total_created}")
            
            if args.count > 0 and total_created >= args.count:
                print(f"[DONE] Target reached: {total_created}/{args.count}")
                break
            
            if not args.loop:
                break
            
            # รอก่อนรอบถัดไป (rotating proxy ไม่ต้องรอนาน)
            print(f"\n[WAIT] Waiting 30s for next batch...")
            time.sleep(30)
            
    elif args.mode == "static":
        # ใช้ proxy จากไฟล์
        proxy_manager = StaticProxyManager("proxies.txt")
        
        while True:
            proxy = proxy_manager.get_next()
            success = run_batch(proxy, args.threads, args.names)
            total_created += success
            
            print(f"\n[TOTAL] Accounts created: {total_created}")
            
            if args.count > 0 and total_created >= args.count:
                break
            
            if not args.loop:
                break
                
            time.sleep(30)
            
    else:
        # ไม่ใช้ proxy (noproxy)
        while True:
            success = run_batch(None, args.threads, args.names)
            total_created += success
            
            print(f"\n[TOTAL] Accounts created: {total_created}")
            
            if args.count > 0 and total_created >= args.count:
                break
            
            if not args.loop:
                break
                
            time.sleep(30)
    
    print(f"\n[DONE] Program finished. Total accounts: {total_created}")


if __name__ == "__main__":
    main()
