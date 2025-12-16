import requests

def fetch_subsidies():
    base_url = "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies"
    
    headers = {
        "Accept": "application/json"
    }
    
    params_active = {
        "keyword": "補助金",
        "sort": "created_date",
        "order": "DESC",
        "acceptance": "1"
    }
    
    try:
        print("Fetching active subsidies (acceptance=1)...")
        res_active = requests.get(base_url, params=params_active, headers=headers)
        res_active.raise_for_status()
        data_active = res_active.json()
        count_active = data_active.get("metadata", {}).get("resultset", {}).get("count", 0)
    except Exception as e:
        print(f"Error fetching active subsidies: {e}")
        return

    params_zero = {
        "keyword": "補助金",
        "sort": "created_date",
        "order": "DESC",
        "acceptance": "0"
    }

    try:
        print("Fetching query with acceptance=0...")
        res_zero = requests.get(base_url, params=params_zero, headers=headers)
        res_zero.raise_for_status()
        data_zero = res_zero.json()
        count_zero = data_zero.get("metadata", {}).get("resultset", {}).get("count", 0)
    except Exception as e:
        print(f"Error fetching acceptance=0: {e}")
        return

    if count_zero > count_active:
         total_count = count_zero
    else:
         total_count = count_zero

    print("-" * 30)
    print(f"Result for acceptance=1 (Active?): {count_active}")
    print(f"Result for acceptance=0: {count_zero}")
    print("-" * 30)
    print("【集計結果】")
    print(f"全件取得数: {total_count}件 (推定)")
    print(f"受付中件数: {count_active}件")

if __name__ == "__main__":
    fetch_subsidies()
