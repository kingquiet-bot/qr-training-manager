#!/usr/bin/env python3
"""
Keep-Alive Script for Render Free Tier
=======================================
This script pings your Render app every 10 minutes to prevent it from sleeping.

Usage:
  1. Deploy this script to a free cron job service
  2. Or run locally with: python3 keep_alive.py
  3. Or add to GitHub Actions as a scheduled workflow

Free Cron Job Services:
  - https://cron-job.org (free)
  - https://www.setcronjob.com (free)
  - https://github.com/RenderExamples/keep-alive-example (GitHub Actions)
"""

import requests
import time
import sys
from datetime import datetime

# Configuration
RENDER_URL = "https://qr-training-manager.onrender.com"  # Your Render URL
PING_INTERVAL = 600  # 10 minutes in seconds
HEALTH_ENDPOINT = "/"  # Endpoint to ping

def ping_app():
    """Ping the Render app to keep it alive."""
    try:
        start_time = time.time()
        response = requests.get(
            f"{RENDER_URL}{HEALTH_ENDPOINT}",
            timeout=30,
            headers={
                "User-Agent": "KeepAlive/1.0",
                "Cache-Control": "no-cache"
            }
        )
        elapsed = time.time() - start_time

        if response.status_code == 200:
            print(f"✅ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"Ping successful - Status: {response.status_code} - "
                  f"Response time: {elapsed:.2f}s")
            return True
        else:
            print(f"⚠️ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"Ping returned status: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
              f"Ping failed: {str(e)}")
        return False

def main():
    """Main function to run the keep-alive script."""
    # Check for --once flag (used by GitHub Actions)
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        success = ping_app()
        sys.exit(0 if success else 1)

    print("=" * 60)
    print("Render Keep-Alive Script")
    print("=" * 60)
    print(f"Target: {RENDER_URL}")
    print(f"Interval: {PING_INTERVAL} seconds ({PING_INTERVAL // 60} minutes)")
    print("=" * 60)
    print("\nPress Ctrl+C to stop\n")

    try:
        while True:
            ping_app()
            time.sleep(PING_INTERVAL)
    except KeyboardInterrupt:
        print("\n\nKeep-alive script stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
