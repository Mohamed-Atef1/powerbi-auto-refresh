import os
import requests
import json

# ✅ قراءة المتغيرات من GitHub Secrets
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
refresh_token = os.getenv("REFRESH_TOKEN")
org_id = os.getenv("ORG_ID")

# ✅ ملفات التخزين (token cache)
TOKEN_FILE = "zoho_token.json"

def get_access_token():
    """يحصل على Access Token جديد من Zoho"""
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        print("✅ New Zoho access token received.")
        save_token(access_token)
        return access_token
    else:
        print(f"❌ Failed to refresh Zoho token: {response.text}")
        return None

def save_token(token):
    """يحفظ الـ Access Token في ملف"""
    with open(TOKEN_FILE, "w") as f:
        json.dump({"access_token": token}, f)

def load_token():
    """يقرأ التوكن من الملف"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
            return data.get("access_token")
    return None

def get_profit_and_loss(access_token):
    """يطلب تقرير الأرباح والخسائر من Zoho"""
    url = "https://www.zohoapis.com/books/v3/reports/profitandloss"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    params = {
        "organization_id": org_id,
        "from_date": "2025-01-01",
        "to_date": "2025-12-31"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        print("✅ Profit & Loss data retrieved successfully!")
        return response.json()
    else:
        print(f"❌ Failed to fetch data: {response.text}")
        return None

if __name__ == "__main__":
    token = load_token()
    if not token:
        print("🔄 Requesting new Zoho access token...")
        token = get_access_token()
    else:
        print("✅ Using cached Zoho access token")

    if token:
        data = get_profit_and_loss(token)
