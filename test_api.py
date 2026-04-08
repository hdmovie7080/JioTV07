#!/usr/bin/env python3
"""
Direct JioTV API test script - Debug the 400 errors
"""

import json
import requests
import gzip
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Credentials from bot.py
CREDS = {
    "authToken": (
        "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImF1dGhUb2tlbklkIjoi"
        "YjM2YjZjMmYtODA2Ny00NDI4LWEyNWUtZTE3NDc2YmRmY2I1IiwidXNlcklkIjoiZThkZjY"
        "xOTEtOTE1ZC00MDE0LTljOTEtN2I0ZmRjNzI2NzYwIiwidXNlclR5cGUiOiJKSU8iLCJvc"
        "yI6ImFuZHJvaWQiLCJkZXZpY2VUeXBlIjoicGhvbmUiLCJhY2Nlc3NMZXZlbCI6IjkiLCJ"
        "kZXZpY2VJZCI6ImFmNDExN2IzYjM0MjNiZTQiLCJleHRyYSI6IntcIm51bWJlclwiOlwia"
        "VdaSDg4Y1hXWjRnMzdHU1BqVjdNVjVQY0tGV2dmYldvcGVMK081eHhXU0VjOFEweGMzSXR"
        "6az1cIixcInBsYW5kZXRhaWxzXCI6e1wiUGFja2FnZUluZm9cIjpbe1wicGxhbmlkXCI6XC"
        "IxXCIsXCJzdWJzY3JpcHRpb25zdGFydFwiOjE2OTM3MzI5ODcsXCJzdWJzY3JpcHRpb25l"
        "bmRcIjoxODA3MDk5OTQ3LFwicGxhbnR5cGVcIjpcIlwiLFwiYnVzaW5lc3NUeXBlXCI6XC"
        "JqaW9cIixcIm5vdGVzXCI6XCJcIn1dfSxcImpUb2tlblwiOlwiNWM2NTQzOGRmNGJmZWMx"
        "MWZhNWViMGIxZDkzZTgyM2QuNjI3YWE5Yjk5ZWNkNjdkY2FhY2M1MWRhYjMyMzU2YmE2MD"
        "NlNmU0ZDI1NTZiYmI0MjdiYmUyN2U3NjZmNTJhMWVlMTE5ZjY3ZmZiODNkMjQzMzAwMjRl"
        "OTc0NTI2YTEyNTdjNjAxNTBjMGRiMzI0NTk2YTI3MmQzNTNlYzU1N2NhODZkZjAyYTc0NT"
        "YxMDQ5N2RmMDAzNzg0NGU5MDUzOWY2NzUwOGZhZTdmYWZlYmM4Mzk4MTY5ZDJkZWEyOTgz"
        "NjVjYTQwNTM1M2VhODFmOGRjYjU0MjQ1ZDFkNTM0ZDQxYmM1M2UxY2M5ZWYzNTk3NWFjNz"
        "UwZmVkYTcwMjNkNmYxNTQxYmFlMjExMDgzMzJkMjBlMjMxNGIxYTBkYTM3NzA4NDA0MWFl"
        "YWE2YTk2ZDkzMDYyNTU4ODQ3ZGU3ZjExN2NkZGIyZWNjYThkOTVhYjM2ODhiMzRlMGMxND"
        "kwZDg3YTc2NWE1OGQwNzc4YWZkMWY1YzI0ZWRkODk3YmFjNmI2MTM0NWFlM2JmOWE5Zjk1"
        "MDY0Y2FkOWNmYmFlN2Y5NDMwYWQ3Y2U0OWJmMzgyNmY2NjhkN2VjNDAyMWQ2NjZhNTU0OG"
        "M4ZGVjYTA2MWM4OTA4MDUwOWViYTBlZWNkYzJhM2IwY2M1OGZmODcxZDliNTc4MGY5ZjZi"
        "YzA4MGIyMzk4NjAyN2JkMzZkODUzMzQ5YWNjNzg1Yzc2N2VmM2YwODhiZGNhNmY0NTk4Nm"
        "FiMzMxMzA3MjAwNWVlNzY4NDFjM2IwM2Q2NmQ1MTFhZTIzZWIyMTFkZWNiYjNkZTA2MmFl"
        "N2FlODVjYjAyNWNiMGNjZjZkYTE4MmFmYTQxMjlhOWIxNDU2NWI5NDkyYzNlNDY4OTcyOT"
        "RjYTllMDIzMDI5MjM4OTQ0MTMxOWZiNjJjMmQyOTQ4NjY3NWFkYWRcIixcInVzZXJEZXRh"
        "aWxzXCI6XCJJay9VVTZnZTdZVEoxZjZTTTR2bHZuOGVsRlhVSUh4KzNvcDArUkluWU9FT2"
        "FxS2draFYzY25ycVd3aTQyd0V0TFR3bGZSaFVUa0Z0YW1mRFhqdE1HMmxtS01EY0h0WGo0"
        "V0xSZzhsaVcyWmdVdXhDNmYvRmNPM3kxcktMUjdEWjhwdjFmNmx0V1ZvNlYxYU5WWXZPYj"
        "ZubTYwQzBXaE44NDFWYVRsc1FzRGhiT2pkb1d1a21pZ0xjVjVEb1dBT25Kemt0UVhTQlJt"
        "aDNmeUNOZ0xFOC96YU5nb3AwU0tmd3JmTnQ4dVpiZUxEOWRqUjdmUW44Y0VHajg2TnFJS1"
        "JDb1g4eUxSYy82N1V5RjdRMjBCSU5NeEtvaTlaS3VreTI1YVYycXhuXCJ9Iiwic3Vic2Ny"
        "aWJlcklkIjoiMzEyNjcwNzgxNiIsImFwcE5hbWUiOiJSSklMX0ppb1RWIiwidmVyc2lvbi"
        "I6InYxLjEiLCJwbGF0Zm9ybSI6IiJ9LCJleHAiOjE3NzY0Mjc5NDcsImlhdCI6MTc3NTU2"
        "Mzk0N30.3-BcLoz9RoXD26pLWi9SGd79PuLParvd6yeXo9SX8zKDOwUa1dY8PWoUTJR7xg"
        "-Mpqf0FTkQFMGIdoJJ_iP7QQ"
    ),
    "ssoToken": (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkRm9yIjoiSmlvVFYiLCJk"
        "ZXZpY2VJZCI6ImFmNDExN2IzYjM0MjNiZTQiLCJpYXQiOjE3NzU1NjM5NDcsInNJZCI6Il"
        "UyRnNkR1ZrWDErZ2Y0UmU0cXJ2c0M2TVNiNWhkOFBDRUtUcHFmYkkwZjg5IiwidW5pcXVl"
        "IjoiZThkZjYxOTEtOTE1ZC00MDE0LTljOTEtN2I0ZmRjNzI2NzYwIiwidXNlclR5cGUiOi"
        "KKSU8ifQ.0uqDBWxHcvJD-iqtjSBOCNLv9RZJcKxgtY3XwBCml1s"
    ),
    "deviceId": "af4117b3b3423be4",
    "subscriberId": "3126707816",
    "uniqueId": "e8df6191-915d-4014-9c91-7b4fdc726760",
}

def make_session():
    s = requests.Session()
    r = Retry(total=3, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
    a = HTTPAdapter(max_retries=r, pool_connections=20, pool_maxsize=20)
    s.mount("http://", a)
    s.mount("https://", a)
    return s

def get_headers():
    return {
        "Host": "jiotvapi.cdn.jio.com",
        "Connection": "keep-alive",
        "User-Agent": "okhttp/4.12.13",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "accesstoken": CREDS["authToken"],
        "ssotoken": CREDS["ssoToken"],
        "subscriberid": CREDS["subscriberId"],
        "deviceid": CREDS["deviceId"],
        "uniqueid": CREDS["uniqueId"],
        "versioncode": "331",
        "os": "android",
        "devicetype": "phone",
        "appname": "RJIL_JioTV",
    }

def test_channels():
    print("\n" + "="*60)
    print("TEST 1: Fetching Channels List")
    print("="*60)
    
    url = "https://jiotvapi.cdn.jio.com/apis/v1.3/getepg/get?offset=-1&channel_id=all&langId=6"
    headers = get_headers()
    session = make_session()
    
    print(f"\nURL: {url}")
    print(f"\nHeaders being sent:")
    for k, v in headers.items():
        if "token" in k.lower():
            print(f"  {k}: {v[:50]}...")
        else:
            print(f"  {k}: {v}")
    
    try:
        print("\nMaking request...")
        r = session.get(url, headers=headers, timeout=30, allow_redirects=True)
        
        print(f"\nResponse Status: {r.status_code}")
        print(f"Response Headers: {dict(r.headers)}")
        
        if r.status_code == 200:
            try:
                raw = gzip.decompress(r.content)
            except:
                raw = r.content
            
            data = json.loads(raw.decode("utf-8", errors="ignore"))
            print(f"\nResponse Data Keys: {list(data.keys())}")
            
            channels = data.get("result") or data.get("channels") or data.get("epg") or []
            print(f"Channels found: {len(channels)}")
            
            if channels:
                print(f"\nFirst channel: {channels[0]}")
                return True
        else:
            print(f"\nError Response Body: {r.text[:500]}")
            return False
            
    except Exception as e:
        print(f"\nException: {type(e).__name__}: {e}")
        return False

def test_epg_single():
    print("\n" + "="*60)
    print("TEST 2: Fetching EPG for Single Channel (816)")
    print("="*60)
    
    url = "https://jiotvapi.cdn.jio.com/apis/v1.3/getepg/get?offset=-1&channel_id=816&langId=6"
    headers = get_headers()
    session = make_session()
    
    print(f"\nURL: {url}")
    
    try:
        print("\nMaking request...")
        r = session.get(url, headers=headers, timeout=30, allow_redirects=True)
        
        print(f"Response Status: {r.status_code}")
        
        if r.status_code == 200:
            try:
                raw = gzip.decompress(r.content)
            except:
                raw = r.content
            
            data = json.loads(raw.decode("utf-8", errors="ignore"))
            epg = data.get("epg", [])
            print(f"EPG shows found: {len(epg)}")
            
            if epg:
                print(f"\nFirst show: {epg[0]['showname']}")
                return True
        else:
            print(f"Error: {r.status_code}")
            print(f"Body: {r.text[:500]}")
            return False
            
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("JioTV API Debug Script")
    print("="*60)
    print(f"Auth Token (first 50 chars): {CREDS['authToken'][:50]}...")
    print(f"Device ID: {CREDS['deviceId']}")
    
    result1 = test_channels()
    time.sleep(1)
    result2 = test_epg_single()
    
    print("\n" + "="*60)
    print("Results:")
    print(f"  Channels test: {'PASS' if result1 else 'FAIL'}")
    print(f"  EPG test: {'PASS' if result2 else 'FAIL'}")
    print("="*60 + "\n")
