# ═══════════════════════════════════════════════════════════════════════════════
# JioTV PRO Bot Configuration Template
# 
# Copy this file to config.py and fill in your credentials
# Then update bot.py to import from config.py
# ═══════════════════════════════════════════════════════════════════════════════

# ══ TELEGRAM BOT CREDENTIALS ══════════════════════════════════════════════════════
# Get these from https://my.telegram.org/apps
API_ID = 20093900                                          # Your API ID
API_HASH = "314286d8af54eda517ff6f3974fd3aad"            # Your API Hash

# Get Bot Token from @BotFather (https://t.me/botfather)
BOT_TOKEN = "8516486280:AAHi3kgQ75gvJYJDUpSv_E8Q5DfNVK58fPs"

# Your Telegram User ID (for admin commands)
# Get it with: https://t.me/userinfobot
ADMIN_ID = 5009476236

# ══ DATABASE ══════════════════════════════════════════════════════════════════════
# MongoDB Connection String (optional, for user tracking)
# Leave empty to skip database features
DB_URL = "mongodb+srv://hdmovie7080:Q3EHYt3z5oc1Af76@cluster0.yrkrelc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "Cluster0"

# ══ DOWNLOAD SETTINGS ═════════════════════════════════════════════════════════════
DOWNLOAD_DIR = "./downloads"  # Where to save recordings
TEMP_DIR = "./temp"           # Temporary files location
MAX_REC_SEC = 4 * 3600        # Maximum recording duration (4 hours)
PROGRESS_SEC = 4              # Progress update interval (seconds)
PAGE_SIZE = 10                # Items per page in paginated lists

# ══ BOT BRANDING ══════════════════════════════════════════════════════════════════
RELEASE_TAG = "『𝗠𝗔𝗗𝗔𝗥𝗔』"  # Release tag for file names

# ══ JIOTV CREDENTIALS ═════════════════════════════════════════════════════════════
# These are PRE-CONFIGURED from TS-JioTV project
# Auto-refresh happens every ~1.9 hours
# No login required!

JIOTV_CREDS = {
    "authToken": (
        "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImF1dGhUb2tlbklkIjoiYjM2YjZjMmYtODA2Ny00NDI4LWEyNWUtZTE3NDc2YmRmY2I1IiwidXNlcklkIjoiZThkZjYxOTEtOTE1ZC00MDE0LTljOTEtN2I0ZmRjNzI2NzYwIiwidXNlclR5cGUiOiJKSU8iLCJvcyI6ImFuZHJvaWQiLCJkZXZpY2VUeXBlIjoicGhvbmUiLCJhY2Nlc3NMZXZlbCI6IjkiLCJkZXZpY2VJZCI6ImFmNDExN2IzYjM0MjNiZTQiLCJleHRyYSI6IntcIm51bWJlclwiOlwiSldaSDg4Y1hXWjRnMzdHU1BqVjdNVjVQY0tGV2dmYldvcGVMK081eHhXU0VjOFEweGMzSXQ6az1cIixcInBsYW5kZXRhaWxzXCI6e1wiUGFja2FnZUluZm9cIjpbe1wicGxhbmlkXCI6XCIxXCIsXCJzdWJzY3JpcHRpb25zdGFydFwiOjE2OTM3MzI5ODcsXCJzdWJzY3JpcHRpb25lbmRcIjoxODA3MDk5OTQ3LFwicGxhbnR5cGVcIjpcIlwiLFwiYnVzaW5lc3NUeXBlXCI6XCJqaW9cIixcIm5vdGVzXCI6XCJcIn1dfSxcImpUb2tlblwiOlwiNWM2NTQzOGRmNGJmZWMxMWZhNWViMGIxZDkzZTgyM2QuNjI3YWE5Yjk5ZWNkNjdkY2FhY2M1MWRhYjMyMzU2YmE2MDNlNmU0ZDI1NTZiYmI0MjdiYmUyN2U3NjZmNTJhMWVlMTE5ZjY3ZmZiODNkMjQzMzAwMjRlOTc0NTI2YTEyNTdjNjAxNTBjMGRiMzI0NTk2YTI3MmQzNTNlYzU1N2NhODZkZjAyYTc0NTYxMDQ5N2RmMDAzNzg0NGU5MDUzOWY2NzUwOGZhZTdmYWZlYmM4Mzk4MTY5ZDJkZWEyOTgzNjVjYTQwNTM1M2VhODFmOGRjYjU0MjQ1ZDFkNTM0ZDQxYmM1M2UxY2M5ZWYzNTk3NWFjNzUwZmVkYTcwMjNkNmYxNTQxYmFlMjExMDgzMzJkMjBlMjMxNGIxYTBkYTM3NzA4NDA0MWFlYWE2YTk2ZDkzMDYyNTU4ODQ3ZGU3ZjExN2NkZGIyZWNjYThkOTVhYjM2ODhiMzRlMGMxNDkwZDg3YTc2NWE1OGQwNzc4YWZkMWY1YzI0ZWRkODk3YmFjNmI2MTM0NWFlM2JmOWE5Zjk1MDY0Y2FkOWNmYmFlN2Y5NDMwYWQ3Y2U0OWJmMzgyNmY2NjhkN2VjNDAyMWQ2NjZhNTU0OGM4ZGVjYTA2MWM4OTA4MDUwOWViYTBlZWNkYzJhM2IwY2M1OGZmODcxZDliNTc4MGY5ZjZiYzA4MGIyMzk4NjAyN2JkMzZkODUzMzQ5YWNjNzg1Yzc2N2VmM2YwODhiZGNhNmY0NTk4NmFiMzMxMzA3MjAwNWVlNzY4NDFjM2IwM2Q2NmQ1MTFhZTIzZWIyMTFkZWNiYjNkZTA2MmFlN2FlODVjYjAyNWNiMGNjZjZkYTE4MmFmYTQxMjlhOWIxNDU2NWI5NDkyYzNlNDY4OTcyOTRjYTllMDIzMDI5MjM4OTQ0MTMxOWZiNjJjMmQyOTQ4NjY3NWFkYWRcIixcInVzZXJEZXRhaWxzXCI6XCJJay9VVTZnZTdZVEoxZjZTTTR2bHZuOGVsRlhVSUh4KzNvcDArUkluWU9FT0ZxS2draFYzY25ycVd3aTQyd0V0TFR3bGZSaFVUa0Z0YW1mRFhqdE1HMmxtS01EY0h0WGo0V0xSZzhsaVcyWmdVdXhDNmYvRmNPM3kxcktMUjdEWjhwdjFmNmx0V1ZvNlYxYU5WWXZPYjZubTYwQzBXaE44NDFWYVRsc1FzRGhiT2pkb1d1a21pZ0xjVjVEb1dBT25Kekt0UVhTQlJtaDNmeUNOZ0xFOC96YU5nb3AwU0tmd3JmTnQ4dVpiZUxEOWRqUjdmUW44Y0VHajg2TnFJS0pDb1g4eUxSYy82N1V5RjdRMjBCSU5NeEtvaTlaS3VreTI1YVYycXhuXCJ9Iiwic3Vic2NyaWJlcklkIjoiMzEyNjcwNzgxNiIsImFwcE5hbWUiOiJSSklMX0ppb1RWIiwidmVyc2lvbiI6InYxLjEiLCJwbGF0Zm9ybSI6IiJ9LCJleHAiOjE3NzY0Mjc5NDcsImlhdCI6MTc3NTU2Mzk0N30.3-BcLoz9RoXD26pLWi9SGd79PuLParvd6yeXo9SX8zKDOwUa1dY8PWoUTJR7xg-Mpqf0FTkQFMGIdoJJ_iP7QQ"
    ),
    "ssoToken": (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkRm9yIjoiSmlvVFYiLCJkZXZpY2VJZCI6ImFmNDExN2IzYjM0MjNiZTQiLCJpYXQiOjE3NzU1NjM5NDcsInNJZCI6IlUyRnNkR1ZrWDErZ2Y0UmU0cXJ2c0M2TVNiNWhkOFBDRUtUcHFmYkkwZjg5IiwidW5pcXVlIjoiZThkZjYxOTEtOTE1ZC00MDE0LTljOTEtN2I0ZmRjNzI2NzYwIiwidXNlclR5cGUiOiJKSU8ifQ.0uqDBWxHcvJD-iqtjSBOCNLv9RZJcKxgtY3XwBCml1s"
    ),
    "refreshToken": "af939ca6-3b0c-4f5a-933f-2c24399db1f0",
    "deviceId": "af4117b3b3423be4",
    "subscriberId": "3126707816",
    "uniqueId": "e8df6191-915d-4014-9c91-7b4fdc726760",
    "lbCookie": "1",
    "name": "Md. Hasen Ali",
    "mobile": "+916295958622",
    "refreshed_at": 0.0,
}

# ══ LANGUAGE MAPPINGS ═════════════════════════════════════════════════════════════
# These map language codes to scene-style abbreviations
LANG_MAP = {
    "hin": "HIN", "hi": "HIN", "hindi": "HIN",
    "asm": "ASM", "as": "ASM", "assamese": "ASM",
    "ben": "BEN", "bn": "BEN", "bengali": "BEN",
    "bod": "BOD", "bodo": "BOD",
    "doi": "DOG", "dogri": "DOG", "dog": "DOG",
    "guj": "GUJ", "gu": "GUJ", "gujarati": "GUJ",
    "kan": "KAN", "kn": "KAN", "kannada": "KAN",
    "kas": "KAS", "ks": "KAS", "kashmiri": "KAS",
    "kok": "KON", "konkani": "KON", "kon": "KON",
    "mai": "MAI", "maithili": "MAI",
    "mal": "MAL", "ml": "MAL", "malayalam": "MAL",
    "mni": "MAN", "manipuri": "MAN", "man": "MAN",
    "mar": "MAR", "mr": "MAR", "marathi": "MAR",
    "nep": "NEP", "ne": "NEP", "nepali": "NEP",
    "ori": "ODI", "or": "ODI", "odia": "ODI", "odi": "ODI",
    "pan": "PUN", "pa": "PUN", "punjabi": "PUN", "pun": "PUN",
    "san": "SAN", "sa": "SAN", "sanskrit": "SAN",
    "sat": "SANL", "santali": "SANL", "sanl": "SANL",
    "snd": "SIN", "sindhi": "SIN", "sin": "SIN",
    "tam": "TAM", "ta": "TAM", "tamil": "TAM",
    "tel": "TEL", "te": "TEL", "telugu": "TEL",
    "urd": "URD", "ur": "URD", "urdu": "URD",
    "eng": "ENG", "en": "ENG", "english": "ENG",
    "und": "UND", "unknown": "UND", "": "UND",
}
