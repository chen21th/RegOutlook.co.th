# RegOutlookTH - Copilot Instructions

## Project Overview
Python Portable automation tool for Outlook Thailand (@outlook.co.th) account registration using Selenium WebDriver with ABC Rotating Proxy.

## Architecture
```
main.py              → Entry point, CLI args parsing (portable support)
├── registrator.py       → Main registration flow (threading)
│   ├── browser.py           → Selenium Chrome + authenticated proxy
│   ├── captcha_solver.py    → FunCaptcha solving via AnyCaptcha API
│   └── data.py              → Thai names (40+) & generators
├── proxy_manager.py     → ABC Proxy rotation (new IP each request)
└── config.py            → All config (uses BASE_DIR for portable)
```

## Key Patterns

### Portable Python Support
All paths use `BASE_DIR` from `config.py`:
```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROME_DRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")
```

### ABC Proxy (Authenticated Rotating)
In `browser.py`, creates Chrome extension for authenticated proxy:
```python
# Format: http://user:pass@host:port
# Creates proxy_auth_plugin.zip extension automatically
```

### Threading Pattern
Each registration runs in `AccountRegistrator` thread. Use `run_batch()` to spawn multiple threads.

### Browser Anti-Detection
```python
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
```

### Captcha Flow
1. Wait for captcha iframe (`enforcementFrame`)
2. Call `CaptchaSolver.solve()` to get token
3. Use `inject_captcha_token()` to submit

## Conventions

### Configuration
All constants in `config.py`. ABC Proxy credentials:
```python
ABC_PROXY_HOST = "as.7ca2c8ca73824063.abcproxy.vip"
ABC_PROXY_PORT = "4950"
ABC_PROXY_USER = "CJPq9PbdU3-zone-star-region-TH"
ABC_PROXY_PASS = "27606332"
```

### Error Handling
- Print `[STATUS]` prefix: `[SUCCESS]`, `[FAIL]`, `[ERROR]`, `[INFO]`, `[PROXY]`
- Set `self.error_message` on failure
- Always close browser in `finally` block

### Output Format
```
email@outlook.co.th|password|full_name|timestamp
```

## Common Tasks

### Add New Thai Name
Edit `data.py` → `THAI_NAMES` list (currently 40+ names)

### Change Proxy Credentials
Edit `config.py`: `ABC_PROXY_USER`, `ABC_PROXY_PASS`, etc.

### Add New Captcha Service
Create class in `captcha_solver.py` with `solve()` method returning token.

## Dependencies
- `selenium>=4.0.0` - Browser automation
- `requests>=2.28.0` - HTTP calls for APIs
- ChromeDriver matching Chrome version
