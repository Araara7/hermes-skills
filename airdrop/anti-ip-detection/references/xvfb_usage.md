# xvfb Usage Guide

## Install
```bash
apt-get install -y xvfb
```

## Basic Usage
```bash
xvfb-run -a python3 script.py
```

## With Screen Size
```bash
xvfb-run -a -s "-screen 0 1920x1080x24" python3 script.py
```

## With Camoufox
```python
from camoufox.sync_api import Camoufox

# Non-headless dengan xvfb
with Camoufox(headless=False) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

## Troubleshooting

### Error: "no DISPLAY environment variable"
```bash
# Solution: pakai xvfb-run
xvfb-run -a python3 script.py
```

### Error: "cannot open display"
```bash
# Solution: set display manually
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
python3 script.py
```

### Popup Tidak Muncul
- Google GSI popup **TIDAK BISA** di-automate
- Solusi: Export cookies manual dari browser user

## Best Practices

1. Always use `-a` flag (auto-select display)
2. Set screen size untuk screenshot quality
3. Cleanup zombie processes: `pkill Xvfb`
4. Use `/tmp/.X99-lock` check sebelum start
