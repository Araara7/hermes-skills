#!/usr/bin/env python3
"""
Quick Register - Registrasi cepat untuk website airdrop
Digunakan langsung dari agent tanpa config file
"""

import asyncio
import json
import sys
from pathlib import Path

try:
    from camoufox.async_api import AsyncCamoufox
except ImportError:
    print("❌ Camoufox belum terinstall. Jalankan: pip install camoufox")
    sys.exit(1)

# Data default
DEFAULT_DATA = {
    "email": "otamaagent7@gmail.com",
    "wallet": "0x000C0e48DC08987954631249Cffba71B5EfaD263",
    "twitter": "@otama777A",
    "name": "Otama",
    "age": "25",
    "country": "Indonesia",
    "timezone": "UTC+7"
}

# Field mapping
FIELD_KEYWORDS = {
    "email": ["email", "e-mail", "mail"],
    "wallet": ["wallet", "address", "ethereum", "0x", "evm"],
    "twitter": ["twitter", "handle", "x.com"],
    "name": ["name", "username", "full name"],
    "age": ["age", "umur"],
    "country": ["country", "nation", "location"],
    "timezone": ["timezone", "time zone", "gmt"]
}

async def quick_register(url, data=None, screenshot=True):
    """Registrasi cepat"""
    if data is None:
        data = DEFAULT_DATA
    
    print(f"🚀 Quick Register: {url}")
    print("=" * 50)
    
    async with AsyncCamoufox(headless=True) as browser:
        page = await browser.new_page()
        
        try:
            # Buka halaman
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(2)
            
            # Cari dan isi semua input
            filled = 0
            inputs = await page.query_selector_all('input, textarea, select')
            
            for inp in inputs:
                try:
                    info = await page.evaluate('''(el) => {
                        return {
                            tag: el.tagName.toLowerCase(),
                            type: el.type || 'text',
                            name: (el.name || '').toLowerCase(),
                            id: (el.id || '').toLowerCase(),
                            placeholder: (el.placeholder || '').toLowerCase(),
                            label: el.labels && el.labels[0] ? el.labels[0].textContent.toLowerCase() : ''
                        }
                    }''', inp)
                    
                    # Skip jika sudah terisi
                    value = await inp.get_attribute('value')
                    if value:
                        continue
                    
                    # Cari field type
                    check_text = f"{info['name']} {info['id']} {info['placeholder']} {info['label']}"
                    
                    field_type = None
                    for ftype, keywords in FIELD_KEYWORDS.items():
                        for kw in keywords:
                            if kw in check_text:
                                field_type = ftype
                                break
                        if field_type:
                            break
                    
                    if field_type and field_type in data:
                        if info['tag'] == 'select':
                            # Dropdown
                            options = await inp.query_selector_all('option')
                            for opt in options:
                                text = await opt.text_content()
                                if data[field_type].lower() in text.lower():
                                    await opt.click()
                                    break
                        else:
                            # Text input
                            await inp.click()
                            await asyncio.sleep(0.2)
                            await inp.fill(data[field_type])
                        
                        filled += 1
                        print(f"  ✓ {field_type}: {data[field_type][:20]}...")
                        await asyncio.sleep(0.3)
                        
                except Exception as e:
                    continue
            
            print(f"\n📝 {filled} field berhasil diisi")
            
            # Cari tombol submit
            submit_buttons = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Register")',
                'button:has-text("Sign Up")',
                'button:has-text("Join")',
                'button:has-text("Continue")',
                'button:has-text("Next")'
            ]
            
            submitted = False
            for selector in submit_buttons:
                try:
                    btn = await page.query_selector(selector)
                    if btn:
                        await btn.click()
                        print(f"📤 Form dikirim!")
                        submitted = True
                        break
                except:
                    continue
            
            if not submitted:
                print("⚠️  Tombol submit tidak ditemukan")
            
            # Tunggu response
            await asyncio.sleep(3)
            
            # Screenshot
            if screenshot:
                screenshots_dir = Path.home() / "airdrop-agent" / "data" / "screenshots"
                screenshots_dir.mkdir(parents=True, exist_ok=True)
                filename = f"quick_register_{int(time.time())}.png"
                await page.screenshot(path=str(screenshots_dir / filename))
                print(f"📸 Screenshot: {screenshots_dir / filename}")
            
            # Cek hasil
            body = await page.text_content('body')
            success_words = ["success", "berhasil", "registered", "welcome", "thank", "congratulations"]
            
            if any(w in body.lower() for w in success_words):
                print("\n✅ Registrasi BERHASIL!")
                return True
            else:
                print("\n⚠️  Status tidak diketahui - cek screenshot")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False
        
        finally:
            await page.close()

if __name__ == "__main__":
    import time
    
    if len(sys.argv) < 2:
        print("Usage: python3 quick_register.py <URL> [data_json]")
        print("Example: python3 quick_register.py https://example.com/register '{\"email\":\"test@test.com\"}'")
        sys.exit(1)
    
    url = sys.argv[1]
    data = None
    
    if len(sys.argv) > 2:
        try:
            data = json.loads(sys.argv[2])
            # Merge dengan default
            merged = DEFAULT_DATA.copy()
            merged.update(data)
            data = merged
        except:
            print("❌ Format data tidak valid")
            sys.exit(1)
    
    success = asyncio.run(quick_register(url, data))
    sys.exit(0 if success else 1)
