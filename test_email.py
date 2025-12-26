"""
กรอก email แล้วกด ถัดไป
"""
import time
import random
import string
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy

options = AppiumOptions()
options.set_capability('platformName', 'Android')
options.set_capability('automationName', 'UiAutomator2')
options.set_capability('deviceName', 'ce0617164481141b0d7e')
options.set_capability('noReset', True)

print('[*] Connecting...')
driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
print('[+] Connected!')

email = ''.join(random.choices(string.ascii_lowercase, k=6)) + str(random.randint(100,999))
print(f'[*] Email: {email}')

# หา EditText
inputs = driver.find_elements(AppiumBy.CLASS_NAME, 'android.widget.EditText')
print(f'[*] Found {len(inputs)} EditText')

for inp in inputs:
    rid = inp.get_attribute('resource-id') or ''
    if 'url_bar' not in rid:
        inp.click()
        time.sleep(0.3)
        inp.send_keys(email)
        print(f'[+] Typed: {email}')
        break

time.sleep(1)
driver.save_screenshot('email_typed.png')
print('[+] Screenshot: email_typed.png')

# กดปุ่มถัดไป
btn = driver.find_element(AppiumBy.XPATH, "//*[@text='ถัดไป']")
btn.click()
print('[+] Clicked ถัดไป')

time.sleep(3)
driver.save_screenshot('step2.png')

xml = driver.page_source
with open('step2.xml', 'w', encoding='utf-8') as f:
    f.write(xml)
print('[+] Saved step2.png & step2.xml')
