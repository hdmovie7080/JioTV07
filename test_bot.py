#!/usr/bin/env python3
"""
Test bot functions without running full Telegram bot
Run with: python test_bot.py
"""

import sys
import json
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def test_fetch_channels():
    """Test the fetch_channels function from bot.py"""
    print("\n" + "="*60)
    print("Testing fetch_channels function")
    print("="*60)
    
    try:
        # Import from bot
        from bot import fetch_channels, refresh_token, ensure_token
        
        print("\n1. Ensuring token is valid...")
        ensure_token()
        
        print("\n2. Calling fetch_channels(force=True)...")
        channels = fetch_channels(force=True)
        
        print(f"\n✅ SUCCESS: Got {len(channels)} channels")
        
        if channels:
            print("\nFirst 3 channels:")
            for i, ch in enumerate(channels[:3]):
                ch_id = ch.get("channel_id") or ch.get("channelId")
                ch_name = ch.get("channel_name") or ch.get("channelName")
                print(f"  {i+1}. {ch_name} (ID: {ch_id})")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fetch_epg():
    """Test the fetch_epg function from bot.py"""
    print("\n" + "="*60)
    print("Testing fetch_epg function")
    print("="*60)
    
    try:
        from bot import fetch_epg, ensure_token
        
        print("\n1. Ensuring token is valid...")
        ensure_token()
        
        channel_id = "816"
        print(f"\n2. Calling fetch_epg('{channel_id}', offset=-1)...")
        epg_data = fetch_epg(channel_id, offset=-1)
        
        if epg_data:
            epg_shows = epg_data.get("epg", [])
            print(f"\n✅ SUCCESS: Got {len(epg_shows)} shows for channel {channel_id}")
            
            if epg_shows:
                print("\nFirst 2 shows:")
                for i, show in enumerate(epg_shows[:2]):
                    print(f"  {i+1}. {show.get('showname', 'Unknown')} at {show.get('showtime', '??:??:??')}")
            return True
        else:
            print(f"\n❌ No EPG data returned for channel {channel_id}")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("JioTV Bot Function Tests")
    print("="*60)
    
    result1 = test_fetch_channels()
    result2 = test_fetch_epg()
    
    print("\n" + "="*60)
    print("Test Summary:")
    print(f"  fetch_channels: {'PASS ✅' if result1 else 'FAIL ❌'}")
    print(f"  fetch_epg: {'PASS ✅' if result2 else 'FAIL ❌'}")
    print("="*60 + "\n")
    
    sys.exit(0 if (result1 and result2) else 1)
