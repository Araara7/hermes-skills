# xvfb Usage for Anti-Detect Browsers

## What is xvfb?

xvfb (X Virtual Framebuffer) creates a virtual display for running GUI applications without a physical screen. Required for non-headless browser automation on servers.

## Why Use xvfb?

- **Headless mode**: `navigator.webdriver` may be detected, popup support limited
- **xvfb mode**: Full browser behavior, popup support, more natural fingerprint

## Installation

```bash
apt-get install -y xvfb
```

## Usage

### Basic Usage

```bash
xvfb-run -a python3 script.py
```

### With Custom Screen Size

```bash
xvfb-run -a -s "-screen 0 1920x1080x24" python3 script.py
```

### In Python Script

```python
import subprocess
import sys

# Run script with xvfb
subprocess.run([
    "xvfb-run", "-a", 
    "-s", "-screen 0 1920x1080x24",
    sys.executable, "script.py"
])
```

## Camoufox with xvfb

```python
from camoufox.sync_api import Camoufox

# Must run script with: xvfb-run -a -s "-screen 0 1920x1080x24" python3 script.py
with Camoufox(headless=False) as browser:
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
    )
    page = context.new_page()
    page.goto("https://example.com")
```

## Popup Handling

### Problem: Google Sign-In Popup

Google Sign-In uses GSI (Google Sign-In Identity) API which opens a popup. In headless mode, popups may not work.

### Solution: Use xvfb

```bash
xvfb-run -a -s "-screen 0 1920x1080x24" python3 script.py
```

### Popup Detection

```python
# Method 1: Event listener (unreliable for Google GSI)
page.on("popup", lambda popup: print(f"Popup: {popup.url}"))

# Method 2: Check all pages (more reliable)
time.sleep(5)  # Wait for popup
all_pages = context.pages
for p in all_pages:
    if "accounts.google.com" in p.url:
        print(f"Google popup found: {p.url}")

# Method 3: expect_popup (best for regular popups)
with page.expect_popup() as popup_info:
    page.click("button")
popup = popup_info.value
```

## Troubleshooting

### Error: "no DISPLAY environment variable specified"

**Solution**: Use xvfb-run

```bash
xvfb-run -a python3 script.py
```

### Error: "Cannot open display"

**Solution**: Set display variable

```bash
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
python3 script.py
```

### Popup Not Detected

**Problem**: Google GSI popup doesn't trigger popup event

**Solution**: 
1. Use xvfb (not headless)
2. Check all pages in context
3. Use coordinate-based clicking as fallback

```python
# Get iframe position and click
js_code = """
() => {
    const iframe = document.querySelector('iframe[src*="google"]');
    if (iframe) {
        const rect = iframe.getBoundingClientRect();
        return {x: rect.x + rect.width/2, y: rect.y + rect.height/2};
    }
    return null;
}
"""
coords = page.evaluate(js_code)
if coords:
    page.mouse.click(coords['x'], coords['y'])
```

## Performance Notes

- xvfb uses more memory than headless mode
- Each xvfb instance uses ~50-100MB RAM
- Use `-a` flag to auto-select display number
- Clean up with `killall Xvfb` when done

## Best Practices

1. **Use headless for simple tasks** (scraping, API calls)
2. **Use xvfb for complex tasks** (OAuth, popups, CAPTCHA)
3. **Set consistent screen size** for reliable element positioning
4. **Take screenshots** for debugging
5. **Close browser properly** to free resources
