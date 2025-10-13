import os
import requests
import json

# ====== 🔐 المتغيرات (من GitHub Secrets أو البيئة المحلية) ======
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
refresh_token = os.getenv("REFRESH_TOKEN")
org_id = os.getenv("ORG_ID")

# ====== 📦 دوال المساعدة ======
def get_access_token():
    """يُجدد التوكن من Zoho"""
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }
    res = requests.post(url, data=data)
    if res.status_code == 200:
        print("✅ Access token generated")
        return res.json().get("access_token")
    else:
        raise Exception(f"❌ Failed to refresh token: {res.text}")

def get_reporting_tags(token):
    """يجلب جميع الـ Reporting Tags"""
    url = f"https://www.zohoapis.com/books/v3/settings/reportingtags?organization_id={org_id}"
    headers = {"Authorization": f"Zoho-oauthtoken {token}"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        tags = res.json().get("reporting_tags", [])
        return tags
    else:
        raise Exception(f"❌ Failed to fetch tags: {res.text}")

def get_profit_and_loss(token, tag_option_id):
    """يجلب تقرير P&L لعلامة معينة"""
    url = "https://www.zohoapis.com/books/v3/reports/profitandloss"
    headers = {"Authorization": f"Zoho-oauthtoken {token}"}
    params = {
        "organization_id": org_id,
        "from_date": "2025-01-01",
        "to_date": "2025-12-31",
        "filter_by": "ThisYear",
        "tag_option_id1": tag_option_id
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json().get("profit_and_loss", [])
    else:
        print(f"⚠️ Skipped tag {tag_option_id}: {res.text}")
        return []

# ====== 🚀 التشغيل الرئيسي ======
if __name__ == "__main__":
    token = get_access_token()
    tags = get_reporting_tags(token)

    all_data = {}
    for tag in tags:
        tag_name = tag.get("tag_name")
        tag_options = tag.get("tag_options", [])
        for option in tag_options:
            option_name = option.get("tag_option_name")
            option_id = option.get("tag_option_id")
            print(f"📊 Fetching P&L for {tag_name} → {option_name}")
            pl_data = get_profit_and_loss(token, option_id)
            all_data[f"{tag_name} - {option_name}"] = pl_data

    # ====== 💾 حفظ النتائج ======
    with open("profit_loss_by_tag.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print("✅ All reports saved to profit_loss_by_tag.json")
