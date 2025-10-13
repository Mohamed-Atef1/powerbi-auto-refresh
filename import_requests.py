import os
import requests
import json
import pandas as pd

# ✅ قراءة بيانات الدخول من GitHub Secrets
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
refresh_token = os.getenv("REFRESH_TOKEN")
org_id = os.getenv("ORG_ID")

TOKEN_FILE = "zoho_token.json"

def get_access_token():
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        with open(TOKEN_FILE, "w") as f:
            json.dump({"access_token": access_token}, f)
        return access_token
    else:
        raise Exception(f"❌ Failed to refresh token: {response.text}")

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f).get("access_token")
    return None

def get_reporting_tags(token):
    url = f"https://www.zohoapis.com/books/v3/settings/reportingtags?organization_id={org_id}"
    headers = {"Authorization": f"Zoho-oauthtoken {token}"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json().get("reporting_tags", [])
    else:
        raise Exception(f"❌ Failed to fetch tags: {res.text}")

def get_profit_and_loss(token, tag_id, tag_name):
    url = f"https://www.zohoapis.com/books/v3/reports/profitandloss"
    headers = {"Authorization": f"Zoho-oauthtoken {token}"}
    params = {
        "organization_id": org_id,
        "from_date": "2025-01-01",
        "to_date": "2025-12-31",
        "reporting_tag_id": tag_id
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        data = res.json()
        data["tag_name"] = tag_name
        return data
    else:
        print(f"⚠️ Failed for tag {tag_name}: {res.text}")
        return None

if __name__ == "__main__":
    token = load_token() or get_access_token()
    tags = get_reporting_tags(token)

    all_reports = []
    for tag in tags:
        tag_id = tag["reporting_tag_id"]
        tag_name = tag["name"]
        print(f"📊 Fetching P&L for: {tag_name}")
        report = get_profit_and_loss(token, tag_id, tag_name)
        if report:
            all_reports.append(report)

    # حفظ كل التقارير في ملف JSON واحد
    with open("profit_loss_by_tag.json", "w", encoding="utf-8") as f:
        json.dump(all_reports, f, ensure_ascii=False, indent=2)

    print("✅ Saved all P&L reports by Reporting Tag → profit_loss_by_tag.json")
