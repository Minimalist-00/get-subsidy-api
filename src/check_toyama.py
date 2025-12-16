import requests
import json

base_url = "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies"
headers = {"Accept": "application/json"}
params = {
    "keyword": "補助金",
    "sort": "created_date",
    "order": "DESC",
    "acceptance": "0",
    "target_area_search": "富山県"
}

try:
    res = requests.get(base_url, params=params, headers=headers)
    res.raise_for_status()
    data = res.json()
    items = data.get("result", [])
    
    print(f"Count: {len(items)}")
    for item in items[:5]:  # Check first 5 items
        print(f"Title: {item.get('title')}")
        print(f"Target Area: {item.get('target_area_search')}")
        print("-" * 20)

except Exception as e:
    print(e)
