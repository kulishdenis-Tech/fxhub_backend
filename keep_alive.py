"""
Keep-alive script to prevent Render free tier service from sleeping.
Sends a GET request to /health endpoint every 5 minutes.
"""
import threading
import time
import requests
import logging

logger = logging.getLogger(__name__)

def keep_alive():
    """
    Background thread function that pings the health endpoint every 5 minutes
    to keep the Render service awake.
    """
    url = "https://fxhub-backend.onrender.com/health"
    
    # Wait a bit before first ping to let the app start
    time.sleep(10)
    
    while True:
        try:
            r = requests.get(url, timeout=30)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"[keep_alive] ✅ Ping OK {r.status_code} at {timestamp}")
            print(f"[keep_alive] ✅ Ping OK {r.status_code} at {timestamp}")
        except requests.exceptions.Timeout:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            logger.warning(f"[keep_alive] ⏱️  Timeout at {timestamp} (service may be sleeping)")
            print(f"[keep_alive] ⏱️  Timeout at {timestamp} (service may be sleeping)")
        except Exception as e:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            logger.error(f"[keep_alive] ❌ Error at {timestamp}: {e}")
            print(f"[keep_alive] ❌ Error at {timestamp}: {e}")
        
        # Sleep for 5 minutes (300 seconds)
        time.sleep(300)

