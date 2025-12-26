"""
Solve current captcha on open browser
"""
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# 2Captcha API
CAPTCHA_API_KEY = "f5cb74cff21d8caef0af74e953124f12"
FUNCAPTCHA_PUBLIC_KEY = "B7D8911C-5CC8-A9A3-35B0-554ACEE604DA"

def solve_funcaptcha(api_key, public_key, page_url, timeout=120):
    """Solve FunCaptcha via 2Captcha"""
    print(f"[CAPTCHA] Sending to 2Captcha...")
    print(f"[CAPTCHA] Public Key: {public_key}")
    print(f"[CAPTCHA] Page URL: {page_url}")
    
    # Submit task
    submit_url = "http://2captcha.com/in.php"
    params = {
        "key": api_key,
        "method": "funcaptcha",
        "publickey": public_key,
        "pageurl": page_url,
        "json": 1
    }
    
    try:
        resp = requests.get(submit_url, params=params, timeout=30)
        data = resp.json()
        print(f"[CAPTCHA] Submit response: {data}")
        
        if data.get("status") != 1:
            print(f"[CAPTCHA] Submit error: {data.get('request')}")
            return None
        
        task_id = data.get("request")
        print(f"[CAPTCHA] Task ID: {task_id}")
        
        # Poll for result
        result_url = "http://2captcha.com/res.php"
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            time.sleep(5)
            
            resp = requests.get(result_url, params={
                "key": api_key,
                "action": "get",
                "id": task_id,
                "json": 1
            }, timeout=30)
            
            data = resp.json()
            print(f"[CAPTCHA] Poll response: {data}")
            
            if data.get("status") == 1:
                token = data.get("request")
                print(f"[CAPTCHA] Solved! Token length: {len(token)}")
                return token
            elif data.get("request") == "CAPCHA_NOT_READY":
                elapsed = int(time.time() - start_time)
                print(f"[CAPTCHA] Waiting... ({elapsed}s)")
            else:
                print(f"[CAPTCHA] Error: {data.get('request')}")
                return None
        
        print(f"[CAPTCHA] Timeout!")
        return None
        
    except Exception as e:
        print(f"[CAPTCHA] Exception: {e}")
        return None


def inject_token(driver, token):
    """Inject FunCaptcha token"""
    print("[INJECT] Injecting token...")
    
    # Method 1: PostMessage
    script1 = f'''
    var msg = JSON.stringify({{
        eventId: "challenge-complete",
        payload: {{sessionToken: "{token}"}}
    }});
    window.postMessage(msg, "*");
    parent.postMessage(msg, "*");
    console.log("Token injected via postMessage");
    return "postMessage sent";
    '''
    result1 = driver.execute_script(script1)
    print(f"[INJECT] PostMessage result: {result1}")
    
    time.sleep(2)
    
    # Method 2: Find and fill hidden input
    script2 = f'''
    var inputs = document.querySelectorAll('input[type="hidden"]');
    for (var i = 0; i < inputs.length; i++) {{
        if (inputs[i].name && inputs[i].name.toLowerCase().includes('token')) {{
            inputs[i].value = "{token}";
            console.log("Set token in hidden input:", inputs[i].name);
        }}
    }}
    return inputs.length;
    '''
    result2 = driver.execute_script(script2)
    print(f"[INJECT] Hidden inputs found: {result2}")
    
    # Method 3: Direct callback
    script3 = f'''
    try {{
        if (typeof ArkoseEnforcement !== 'undefined') {{
            ArkoseEnforcement.setConfig({{ onCompleted: function() {{ }} }});
        }}
    }} catch(e) {{}}
    
    try {{
        var event = new CustomEvent('arkose-complete', {{ detail: {{ token: "{token}" }} }});
        document.dispatchEvent(event);
    }} catch(e) {{}}
    
    return "callbacks attempted";
    '''
    result3 = driver.execute_script(script3)
    print(f"[INJECT] Callback result: {result3}")


def main():
    print("=" * 60)
    print("  Solve Current Captcha")
    print("=" * 60)
    
    # Connect to existing Chrome
    debug_port = input("Enter Chrome debug port (check maxhotmail output): ").strip()
    if not debug_port:
        debug_port = "9222"
    
    print(f"[INFO] Connecting to Chrome on port {debug_port}...")
    
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
    
    try:
        driver = webdriver.Chrome(options=options)
        print(f"[INFO] Connected! Current URL: {driver.current_url}")
        
        # Solve captcha
        page_url = driver.current_url
        token = solve_funcaptcha(CAPTCHA_API_KEY, FUNCAPTCHA_PUBLIC_KEY, page_url)
        
        if token:
            print(f"\n[SUCCESS] Got token!")
            print(f"Token (first 100 chars): {token[:100]}...")
            
            # Inject
            inject_token(driver, token)
            
            print("\n[INFO] Token injected! Check if captcha passed.")
            print("[INFO] If not, the token might need different injection method.")
        else:
            print("[FAIL] Could not solve captcha")
            
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
