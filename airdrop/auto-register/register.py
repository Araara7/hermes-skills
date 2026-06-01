#!/usr/bin/env python3
"""
Auto-Register Script untuk Website Airdrop
Menggunakan Camoufox untuk anti-detection
"""

import asyncio
import json
import os
import sys
import time
import random
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from camoufox.async_api import AsyncCamoufox
except ImportError:
    print("❌ Camoufox belum terinstall. Jalankan: pip install camoufox")
    sys.exit(1)

class AutoRegister:
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path)
        self.data_dir = Path.home() / "airdrop-agent" / "data" / "registrations"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir = Path.home() / "airdrop-agent" / "data" / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path):
        """Load config dari file atau gunakan default"""
        default_config = {
            "default_data": {
                "email": "otamaagent7@gmail.com",
                "wallet": "0x000C0e48DC08987954631249Cffba71B5EfaD263",
                "twitter": "@otama777A",
                "discord": "",
                "telegram": "",
                "name": "Otama",
                "age": "25",
                "country": "Indonesia",
                "timezone": "UTC+7"
            },
            "field_mapping": {
                "email": ["email", "e-mail", "correo", "メール"],
                "wallet": ["wallet", "address", "ethereum", "0x"],
                "twitter": ["twitter", "handle", "@"],
                "discord": ["discord", "discord username"],
                "telegram": ["telegram", "tg"],
                "name": ["name", "full name", "username"],
                "age": ["age", "how old"],
                "country": ["country", "nation", "location"],
                "timezone": ["timezone", "time zone", "gmt"]
            },
            "captcha": {
                "enabled": True,
                "service": "2captcha",
                "api_key": ""
            },
            "anti_detection": {
                "use_camoufox": True,
                "random_delay": True,
                "min_delay": 1,
                "max_delay": 3
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                # Merge dengan default
                for key in user_config:
                    if isinstance(user_config[key], dict) and key in default_config:
                        default_config[key].update(user_config[key])
                    else:
                        default_config[key] = user_config[key]
        
        return default_config
    
    def _random_delay(self, min_sec=None, max_sec=None):
        """Random delay untuk hindari deteksi"""
        if not self.config["anti_detection"]["random_delay"]:
            return
        min_sec = min_sec or self.config["anti_detection"]["min_delay"]
        max_sec = max_sec or self.config["anti_detection"]["max_delay"]
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def _detect_field_type(self, element_info):
        """Deteksi jenis field berdasarkan atribut"""
        text_to_check = " ".join([
            element_info.get("label", ""),
            element_info.get("placeholder", ""),
            element_info.get("name", ""),
            element_info.get("id", ""),
            element_info.get("aria-label", "")
        ]).lower()
        
        for field_type, keywords in self.config["field_mapping"].items():
            for keyword in keywords:
                if keyword.lower() in text_to_check:
                    return field_type
        
        return None
    
    async def _solve_captcha(self, page):
        """Handle CAPTCHA jika ada"""
        if not self.config["captcha"]["enabled"]:
            return False
        
        # Cek reCAPTCHA
        recaptcha = await page.query_selector('iframe[src*="recaptcha"]')
        if recaptcha:
            print("🔒 reCAPTCHA terdeteksi, mencoba solve...")
            # Integrasi dengan skill auto-resolve-captcha
            # TODO: Implementasi solver
            return True
        
        # Cek hCaptcha
        hcaptcha = await page.query_selector('iframe[src*="hcaptcha"]')
        if hcaptcha:
            print("🔒 hCaptcha terdeteksi, mencoba solve...")
            # TODO: Implementasi solver
            return True
        
        # Cek Turnstile
        turnstile = await page.query_selector('iframe[src*="turnstile"]')
        if turnstile:
            print("🔒 Turnstile terdeteksi, mencoba solve...")
            # TODO: Implementasi solver
            return True
        
        return False
    
    async def _fill_form(self, page, custom_data=None):
        """Isi form dengan data yang sesuai"""
        data = {**self.config["default_data"]}
        if custom_data:
            data.update(custom_data)
        
        filled_fields = []
        
        # Cari semua input field
        inputs = await page.query_selector_all('input, textarea, select')
        
        for input_elem in inputs:
            try:
                # Ambil info element
                elem_info = await page.evaluate('''(el) => {
                    return {
                        tag: el.tagName.toLowerCase(),
                        type: el.type || 'text',
                        name: el.name || '',
                        id: el.id || '',
                        placeholder: el.placeholder || '',
                        ariaLabel: el.getAttribute('aria-label') || '',
                        label: el.labels && el.labels[0] ? el.labels[0].textContent : '',
                        value: el.value || ''
                    }
                }''', input_elem)
                
                # Skip jika sudah terisi
                if elem_info.get("value"):
                    continue
                
                # Deteksi jenis field
                field_type = self._detect_field_type(elem_info)
                
                if field_type and field_type in data:
                    value = data[field_type]
                    
                    # Handle berdasarkan tag
                    if elem_info["tag"] == "select":
                        # Dropdown select
                        options = await input_elem.query_selector_all('option')
                        for option in options:
                            option_text = await option.text_content()
                            if value.lower() in option_text.lower():
                                await option.click()
                                break
                    elif elem_info["type"] == "checkbox":
                        # Checkbox
                        if value.lower() in ["true", "1", "yes", "on"]:
                            await input_elem.check()
                    elif elem_info["type"] == "radio":
                        # Radio button
                        if value.lower() in ["true", "1", "yes", "on"]:
                            await input_elem.check()
                    else:
                        # Text input
                        await input_elem.click()
                        self._random_delay(0.1, 0.3)
                        await input_elem.fill(value)
                    
                    filled_fields.append({
                        "field_type": field_type,
                        "detected_from": elem_info,
                        "value": value
                    })
                    
                    self._random_delay(0.2, 0.5)
                    
            except Exception as e:
                print(f"⚠️  Error filling field: {e}")
                continue
        
        return filled_fields
    
    async def _submit_form(self, page):
        """Submit form"""
        # Cari tombol submit
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Submit")',
            'button:has-text("Register")',
            'button:has-text("Sign Up")',
            'button:has-text("Join")',
            'button:has-text("Continue")',
            'button:has-text("Next")',
            'a:has-text("Submit")',
            'a:has-text("Register")'
        ]
        
        for selector in submit_selectors:
            try:
                button = await page.query_selector(selector)
                if button:
                    await button.click()
                    print(f"✅ Tombol submit diklik: {selector}")
                    return True
            except:
                continue
        
        print("⚠️  Tombol submit tidak ditemukan")
        return False
    
    async def _take_screenshot(self, page, filename):
        """Ambil screenshot"""
        filepath = self.screenshots_dir / filename
        await page.screenshot(path=str(filepath))
        print(f"📸 Screenshot disimpan: {filepath}")
        return filepath
    
    async def _save_registration(self, url, filled_fields, success, screenshot_path=None):
        """Simpan data registrasi"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        website_name = url.split("//")[-1].split("/")[0].replace(".", "_")
        
        registration_data = {
            "url": url,
            "timestamp": timestamp,
            "success": success,
            "filled_fields": filled_fields,
            "screenshot": str(screenshot_path) if screenshot_path else None
        }
        
        # Simpan ke file
        filename = f"{website_name}_{timestamp}.json"
        filepath = self.data_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(registration_data, f, indent=2)
        
        print(f"💾 Data registrasi disimpan: {filepath}")
        
        # Update log
        log_file = self.data_dir / "registrations_log.json"
        log_data = []
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        
        log_data.append(registration_data)
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        return filepath
    
    async def register(self, url, custom_data=None, take_screenshot=True):
        """Proses registrasi utama"""
        print(f"\n🚀 Memulai registrasi di: {url}")
        print("=" * 50)
        
        async with AsyncCamoufox(headless=True) as browser:
            page = await browser.new_page()
            
            try:
                # Buka halaman
                print(f"🌐 Membuka halaman...")
                await page.goto(url, wait_until="networkidle", timeout=60000)
                self._random_delay(2, 4)
                
                # Ambil screenshot awal
                if take_screenshot:
                    await self._take_screenshot(page, "initial_page.png")
                
                # Isi form
                print("📝 Mengisi form...")
                filled_fields = await self._fill_form(page, custom_data)
                
                if not filled_fields:
                    print("⚠️  Tidak ada field yang terisi")
                    return False
                
                print(f"✅ {len(filled_fields)} field berhasil diisi:")
                for field in filled_fields:
                    print(f"   - {field['field_type']}: {field['value'][:20]}...")
                
                # Handle CAPTCHA
                captcha_detected = await self._solve_captcha(page)
                if captcha_detected:
                    print("🔒 CAPTCHA sedang diproses...")
                    self._random_delay(3, 5)
                
                # Ambil screenshot setelah isi form
                if take_screenshot:
                    await self._take_screenshot(page, "after_fill.png")
                
                # Submit form
                print("📤 Mengirim form...")
                submitted = await self._submit_form(page)
                
                if submitted:
                    self._random_delay(3, 5)
                    
                    # Ambil screenshot setelah submit
                    if take_screenshot:
                        screenshot_path = await self._take_screenshot(page, "after_submit.png")
                    
                    # Cek hasil
                    page_text = await page.text_content('body')
                    
                    if any(keyword in page_text.lower() for keyword in ["success", "berhasil", "registered", "welcome", "thank"]):
                        print("✅ Registrasi BERHASIL!")
                        
                        # Simpan data
                        await self._save_registration(
                            url, 
                            filled_fields, 
                            True, 
                            screenshot_path if take_screenshot else None
                        )
                        
                        return True
                    else:
                        print("⚠️  Status registrasi tidak diketahui")
                        print(f"   Cek screenshot untuk detail")
                        
                        await self._save_registration(
                            url, 
                            filled_fields, 
                            False, 
                            screenshot_path if take_screenshot else None
                        )
                        
                        return False
                else:
                    print("❌ Gagal submit form")
                    return False
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
                # Ambil screenshot error
                if take_screenshot:
                    await self._take_screenshot(page, "error.png")
                
                return False
            
            finally:
                await page.close()

def main():
    parser = argparse.ArgumentParser(description='Auto-Register Website Airdrop')
    parser.add_argument('--url', required=True, help='URL website registrasi')
    parser.add_argument('--config', help='Path ke config file')
    parser.add_argument('--data', help='Custom data (JSON string)')
    parser.add_argument('--screenshot', action='store_true', help='Ambil screenshot')
    parser.add_argument('--no-screenshot', action='store_true', help='Tidak ambil screenshot')
    
    args = parser.parse_args()
    
    # Parse custom data
    custom_data = None
    if args.data:
        try:
            custom_data = json.loads(args.data)
        except json.JSONDecodeError:
            print("❌ Format data tidak valid. Gunakan JSON string.")
            sys.exit(1)
    
    # Tentukan screenshot
    take_screenshot = True
    if args.no_screenshot:
        take_screenshot = False
    elif args.screenshot:
        take_screenshot = True
    
    # Jalankan registrasi
    registerer = AutoRegister(config_path=args.config)
    
    success = asyncio.run(
        registerer.register(
            url=args.url,
            custom_data=custom_data,
            take_screenshot=take_screenshot
        )
    )
    
    if success:
        print("\n🎉 Registrasi selesai!")
        sys.exit(0)
    else:
        print("\n💥 Registrasi gagal!")
        sys.exit(1)

if __name__ == "__main__":
    main()
