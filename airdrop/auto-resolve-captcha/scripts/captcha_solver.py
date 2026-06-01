#!/usr/bin/env python3
"""
CAPTCHA Solver - Solve various CAPTCHA types using 2captcha/CapSolver
Usage: python captcha_solver.py <site_key> <page_url> [type]
"""

import sys
import time
import requests

# Configure your API keys
TWOCAPTCHA_API_KEY="YOUR_2CAPTCHA_KEY"
CAPSOLVER_API_KEY="YOUR_CAPSOLVER_KEY"

def solve_recaptcha_v2(site_key, page_url, service="2captcha"):
    """Solve reCAPTCHA v2"""
    
    if service == "2captcha":
        return solve_2captcha("userrecaptcha", site_key, page_url)
    elif service == "capsolver":
        return solve_capsolver("ReCaptchaV2Task", site_key, page_url)
    else:
        raise ValueError(f"Unknown service: {service}")

def solve_hcaptcha(site_key, page_url, service="2captcha"):
    """Solve hCaptcha"""
    
    if service == "2captcha":
        return solve_2captcha("hcaptcha", site_key, page_url)
    elif service == "capsolver":
        return solve_capsolver("HCaptchaTask", site_key, page_url)
    else:
        raise ValueError(f"Unknown service: {service}")

def solve_2captcha(method, site_key, page_url):
    """Submit to 2captcha"""
    
    base_url = "https://2captcha.com"
    
    # Submit
    data = {
        "key": TWOCAPTCHA_API_KEY,
        "method": method,
        "googlekey" if "recaptcha" in method else "sitekey": site_key,
        "pageurl": page_url,
        "json": 1
    }
    
    resp = requests.post(f"{base_url}/in.php", data=data).json()
    if resp["status"] != 1:
        raise Exception(f"Submit failed: {resp}")
    
    task_id = resp["request"]
    
    # Poll
    for _ in range(60):
        time.sleep(2)
        result = requests.get(f"{base_url}/res.php", params={
            "key": TWOCAPTCHA_API_KEY,
            "action": "get",
            "id": task_id,
            "json": 1
        }).json()
        
        if result["status"] == 1:
            return result["request"]
        
        if result["request"] != "CAPCHA_NOT_READY":
            raise Exception(f"Solve failed: {result}")
    
    raise Exception("Timeout")

def solve_capsolver(task_type, site_key, page_url):
    """Submit to CapSolver"""
    
    # Create task
    resp = requests.post("https://api.capsolver.com/createTask", json={
        "clientKey": CAPSOLVER_API_KEY,
        "task": {
            "type": task_type,
            "websiteURL": page_url,
            "websiteKey": site_key,
        }
    }).json()
    
    if resp["errorId"] != 0:
        raise Exception(f"Error: {resp}")
    
    task_id = resp["taskId"]
    
    # Poll
    for _ in range(60):
        time.sleep(2)
        result = requests.post("https://api.capsolver.com/getTaskResult", json={
            "clientKey": CAPSOLVER_API_KEY,
            "taskId": task_id
        }).json()
        
        if result["status"] == "ready":
            return result["solution"]["gRecaptchaResponse"]
        
        if result["errorId"] != 0:
            raise Exception(f"Error: {result}")
    
    raise Exception("Timeout")

def main():
    if len(sys.argv) < 3:
        print("Usage: python captcha_solver.py <site_key> <page_url> [type]")
        print("Types: recaptcha_v2 (default), hcaptcha")
        sys.exit(1)
    
    site_key = sys.argv[1]
    page_url = sys.argv[2]
    captcha_type = sys.argv[3] if len(sys.argv) > 3 else "recaptcha_v2"
    
    print(f"Solving {captcha_type}...")
    print(f"Site: {page_url}")
    
    try:
        if captcha_type == "recaptcha_v2":
            token = solve_recaptcha_v2(site_key, page_url)
        elif captcha_type == "hcaptcha":
            token = solve_hcaptcha(site_key, page_url)
        else:
            print(f"Unknown type: {captcha_type}")
            sys.exit(1)
        
        print(f"\nToken: {token[:50]}...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
