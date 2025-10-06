import requests
import json
import os
from datetime import datetime, timedelta

# ========================
# Zoho API Credentials
# ========================
client_id = "1000.A3WYEEJWFJYUZUXWENEPG8WSCK5J3L"
client_secret = "ba9a512df0141f214d828e9a3bfb9ffe9fa95db299"
refresh_token = "1000.e6943f399b78c7d5894de9908b25b732.fbaaefccaa134cabf75915033033d0f8"   # ← ضع التوكين هنا
org_id = "877151597"

# Token cache file
TOKEN_FILE = "zoho_token_cache.json"

def get_zoho_token():
    # 1️⃣ إذا فيه توكن محفوظ ولسه صالح
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
            if datetime.now() < datetime.fromisoformat(data["expiry"]):
                print("✅ Using cached Zoho access token")
                return data["access_token"]

    # 2️⃣ طلب توكن جديد
    print("🔄 Requesting new Zoho access token...")
    url = "https://accounts.zoho.com/oauth/v2/token"
    params = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }

    response = requests.post(url, data=params)
    print("📥 Raw response:", response.text)  # ← نطبع الرد الأصلي

    if response.status_code != 200:
        raise Exception(f"❌ Failed to refresh Zoho token (HTTP {response.status_code}): {response.text}")

    token_data = response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        raise Exception(f"❌ No access_token found in response: {token_data}")

    # حفظ التوكين لمدة 50 دقيقة
    expiry_time = datetime.now() + timedelta(minutes=50)
    with open(TOKEN_FILE, "w") as f:
        json.dump({"access_token": access_token, "expiry": expiry_time.isoformat()}, f)

    print("✅ New Zoho access token saved.")
    return access_token

# ==================================
# اختبار
# ==================================
token = get_zoho_token()
print("✅ Access token:", token)
