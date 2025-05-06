import requests
from bs4 import BeautifulSoup
import time
import json
import os

# === Configuration ===
API_KEY = "fvgfbmJ3IT7ksiMm"  # Torn API key
REQUEST_DELAY = 1             # seconds between requests

# Path setup: generate data.json in this folder
BASE_DIR = os.path.dirname(__file__)
OUTPUT_PATH = os.path.join(BASE_DIR, "data.json")

def scrape_company_ids():
    """
    Scrapes Torn's public company listings to collect all player-run company IDs.
    Iterates through each of the 40 company types with pagination.
    """
    session = requests.Session()
    all_ids = set()

    for type_id in range(1, 41):  # company types 1..40
        offset = 0
        while True:
            url = f"https://www.torn.com/companies.php?type={type_id}&offset={offset}"
            resp = session.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            table = soup.find("table", class_="table-hover")
            rows = table.find_all("tr")[1:] if table else []  # skip header
            if not rows:
                break

            for row in rows:
                link = row.find("a", href=True)
                if link:
                    cid = link["href"].split("company/")[-1]
                    all_ids.add(cid)

            offset += len(rows)
            time.sleep(REQUEST_DELAY)

    return list(all_ids)

def fetch_company_data(company_id):
    """
    Fetches basic and performance data for one company via Torn API.
    """
    url = (
        f"https://api.torn.com/company/{company_id}"
        f"?selections=basic,performance&key={API_KEY}"
    )
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    basic = data.get("basic", {})
    perf = data.get("performance", {})

    return {
        "company_id": company_id,
        "company_name": basic.get("name", ""),
        "company_url": f"https://www.torn.com/company/{company_id}",
        "company_type": basic.get("company_type", ""),
        "employees": basic.get("employees", 0),
        "today_income": perf.get("today_income", 0),
        "average_income": perf.get("average_income", 0),
    }

def main():
    # 1) Scrape all company IDs
    print("Scraping company IDs...")
    company_ids = scrape_company_ids()
    print(f"Found {len(company_ids)} companies.")

    # 2) Fetch data for each company
    results = []
    for idx, cid in enumerate(company_ids, start=1):
        try:
            entry = fetch_company_data(cid)
            results.append(entry)
            print(f"{idx}. {entry['company_name']} (ID: {cid}) processed")
        except Exception as e:
            print(f"Error fetching {cid}: {e}")
        time.sleep(REQUEST_DELAY)

    # 3) Save to data.json
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote {len(results)} entries to data.json")

if __name__ == "__main__":
    main()