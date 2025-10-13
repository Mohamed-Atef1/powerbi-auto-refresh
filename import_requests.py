import os
import requests
import json
import pandas as pd

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
refresh_token = os.getenv("REFRESH_TOKEN")
org_id = os.getenv("ORG_ID")

BASE_URL = "https://www.zohoapis.com/books/v3"
TOKEN_FILE = "zoho_token.json"

def get_access_token():
    url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }
    res = requests.post(url, data=data)
    return res.json().get("access_token")

def get_projects(token):
    """جلب قائمة المشاريع"""
    url = f"{BASE_URL}/projects"
    headers = {"Authorization": f"Zoho-oauthtoken {token}"}
    params = {"organization_id": org_id}
    res = requests.get(url, headers=headers, params=params)
    data = res.json()
    return data.get("projects", [])

def get_pnl_for_project(token, project_id, project_name):
    """جلب تقرير الأرباح والخسائر لكل مشروع"""
    url = f"{BASE_URL}/reports/profitandloss"
    headers = {"Authorization": f"Zoho-oauthtoken {token}"}
    params = {
        "organization_id": org_id,
        "project_id": project_id,
        "from_date": "2025-01-01",
        "to_date": "2025-12-31"
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        pnl = res.json().get("profit_and_loss", [])
        df = pd.json_normalize(pnl)
        df["project_name"] = project_name
        return df
    else:
        print(f"❌ Failed for project {project_name}: {res.text}")
        return pd.DataFrame()

if __name__ == "__main__":
    token = get_access_token()
    projects = get_projects(token)
    all_data = pd.DataFrame()

    for p in projects:
        pid = p.get("project_id")
        pname = p.get("project_name")
        print(f"📊 Fetching P&L for {pname} ...")
        df = get_pnl_for_project(token, pid, pname)
        all_data = pd.concat([all_data, df], ignore_index=True)

    # تصدير كل المشاريع إلى ملف JSON واحد
    all_data.to_json("projects_profit_loss.json", orient="records", force_ascii=False, indent=2)
    print("✅ Saved all project P&L data to projects_profit_loss.json")
