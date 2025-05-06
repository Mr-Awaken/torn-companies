import requests
import json
import os
from datetime import datetime

API_KEY = os.getenv("TORN_API_KEY")
OUTPUT_FILE = "static/daily_companies.json"

def fetch_all_companies():
    print("Fetching all companies from Torn API...")
    url = f"https://api.torn.com/torn/?selections=companies&key={API_KEY}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()["companies"]

def fetch_company_data(companies):
    print("Processing company data...")
    result = []
    for cid, info in companies.items():
        company = {
            "id": cid,
            "name": info.get("company_name"),
            "type": info.get("company_type"),
            "employees": info.get("employees", 0),
            "daily_income": info.get("daily_income", 0),
            "average_income": info.get("weekly_income", 0) // 7 if info.get("weekly_income") else 0
        }
        result.append(company)
    return result

def save_to_file(data):
    print(f"Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w") as f:
        json.dump({
            "updated": datetime.utcnow().isoformat(),
            "companies": data
        }, f, indent=2)

def main():
    companies_raw = fetch_all_companies()
    processed = fetch_company_data(companies_raw)
    save_to_file(processed)
    print("Done.")

if __name__ == "__main__":
    main()
