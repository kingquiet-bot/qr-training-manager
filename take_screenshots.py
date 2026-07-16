#!/usr/bin/env python3
"""
Screenshot Helper Script
========================
This script helps you take screenshots of the QR Training Manager application.
It uses Selenium to automate Chrome and take screenshots at specific resolutions.

Prerequisites:
  pip install selenium webdriver-manager

Usage:
  python3 take_screenshots.py
"""

import os
import sys
import time
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("Selenium not installed. Installing...")
    os.system("pip install selenium webdriver-manager")
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("webdriver-manager not installed. Installing...")
    os.system("pip install webdriver-manager")
    from webdriver_manager.chrome import ChromeDriverManager


def take_screenshots():
    """Take screenshots of the QR Training Manager application."""

    # Create screenshots directory
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)

    # Base URL
    base_url = "http://localhost:5000"

    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    # Initialize Chrome driver
    print("Initializing Chrome driver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Desktop screenshots (1280×800)
        print("\n=== Taking Desktop Screenshots (1280×800) ===")
        driver.set_window_size(1280, 800)

        # 1. Dashboard Desktop
        print("1. Taking dashboard screenshot...")
        driver.get(base_url)
        time.sleep(3)  # Wait for page to load
        driver.save_screenshot(str(screenshots_dir / "01-dashboard-desktop.png"))
        print("   ✓ Saved: 01-dashboard-desktop.png")

        # 2. Create Event Form Desktop
        print("2. Taking create event form screenshot...")
        try:
            create_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "btn-show-form"))
            )
            create_btn.click()
            time.sleep(1)
            driver.save_screenshot(str(screenshots_dir / "02-create-event-desktop.png"))
            print("   ✓ Saved: 02-create-event-desktop.png")
        except Exception as e:
            print(f"   ⚠ Could not capture create event form: {e}")

        # 3. Event Detail Desktop (if events exist)
        print("3. Taking event detail screenshot...")
        try:
            # Try to click on first event
            event_card = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[onclick*='_viewEvent']"))
            )
            event_card.click()
            time.sleep(2)
            driver.save_screenshot(str(screenshots_dir / "03-event-detail-desktop.png"))
            print("   ✓ Saved: 03-event-detail-desktop.png")
        except Exception as e:
            print(f"   ⚠ Could not capture event detail (no events?): {e}")

        # 4. Self Check-in Page Desktop
        print("4. Taking self-check-in page screenshot...")
        # Get event ID from URL or use a sample
        try:
            driver.get(f"{base_url}/self-checkin?event_id=sample")
            time.sleep(2)
            driver.save_screenshot(str(screenshots_dir / "04-self-checkin-desktop.png"))
            print("   ✓ Saved: 04-self-checkin-desktop.png")
        except Exception as e:
            print(f"   ⚠ Could not capture self-check-in page: {e}")

        # Mobile screenshots (390×844)
        print("\n=== Taking Mobile Screenshots (390×844) ===")
        driver.set_window_size(390, 844)

        # 5. Dashboard Mobile
        print("5. Taking mobile dashboard screenshot...")
        driver.get(base_url)
        time.sleep(3)
        driver.save_screenshot(str(screenshots_dir / "05-dashboard-mobile.png"))
        print("   ✓ Saved: 05-dashboard-mobile.png")

        # 6. QR Scanner Mobile
        print("6. Taking QR scanner screenshot...")
        try:
            scanner_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-tab='scanner']"))
            )
            scanner_btn.click()
            time.sleep(2)
            driver.save_screenshot(str(screenshots_dir / "06-scanner-mobile.png"))
            print("   ✓ Saved: 06-scanner-mobile.png")
        except Exception as e:
            print(f"   ⚠ Could not capture scanner: {e}")

        # 7. Self Check-in Mobile
        print("7. Taking mobile self-check-in screenshot...")
        try:
            driver.get(f"{base_url}/self-checkin?event_id=sample")
            time.sleep(2)
            driver.save_screenshot(str(screenshots_dir / "07-self-checkin-mobile.png"))
            print("   ✓ Saved: 07-self-checkin-mobile.png")
        except Exception as e:
            print(f"   ⚠ Could not capture mobile self-check-in: {e}")

        print("\n=== Screenshots Complete! ===")
        print(f"Screenshots saved to: {screenshots_dir.absolute()}")

    finally:
        driver.quit()
        print("Chrome driver closed.")


if __name__ == "__main__":
    print("QR Training Manager - Screenshot Helper")
    print("=" * 50)
    print("\nThis script will take screenshots of the application.")
    print("Make sure the app is running on http://localhost:5000\n")

    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

    take_screenshots()
