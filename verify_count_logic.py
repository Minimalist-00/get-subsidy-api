import requests

def verify_counts():
    base_url = "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies"
    headers = {"Accept": "application/json"}
    
    def get_ids(acceptance_val):
        params = {
            "keyword": "補助金",
            "sort": "created_date",
            "order": "DESC",
            "acceptance": acceptance_val
        }
        res = requests.get(base_url, params=params, headers=headers)
        data = res.json()
        ids = {item["id"] for item in data.get("result", [])}
        return ids

    ids_active = get_ids("1")
    ids_zero = get_ids("0")
    
    print(f"\nFetched {len(ids_active)} IDs for Active (first page)")
    print(f"Fetched {len(ids_zero)} IDs for Zero (first page)")
    
    intersection = ids_active.intersection(ids_zero)
    print(f"Intersection count: {len(intersection)}")
    
    if len(intersection) == len(ids_active):
        print("CONCLUSION: acceptance=0 INCLUDES acceptance=1 items. (acceptance=0 is likely ALL)")
    elif len(intersection) > 0:
        print("CONCLUSION: Partial Overlap. acceptance=0 likely includes everything but sort order might have pushed some out of first page.")
    else:
        print("CONCLUSION: NO Overlap on first page. They might be disjoint OR the sort order obscures it.")

if __name__ == "__main__":
    verify_counts()
