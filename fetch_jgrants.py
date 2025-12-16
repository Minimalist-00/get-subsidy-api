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

    # =================================================================
    #  富山県の補助金集計
    # =================================================================
    try:
        print("\n" + "="*30)
        print("Fetching Toyama specific data...")
        
        # 富山県・全件（acceptance=0 で全期間と仮定）
        params_toyama_all = {
            "keyword": "補助金",
            "sort": "created_date",
            "order": "DESC",
            "acceptance": "0",
            "target_area_search": "富山県"
        }
        res_toyama_all = requests.get(base_url, params=params_toyama_all, headers=headers)
        res_toyama_all.raise_for_status()
        count_toyama_all = res_toyama_all.json().get("metadata", {}).get("resultset", {}).get("count", 0)

        # 富山県・受付中（acceptance=1）
        params_toyama_active = {
            "keyword": "補助金",
            "sort": "created_date",
            "order": "DESC",
            "acceptance": "1",
            "target_area_search": "富山県"
        }
        res_toyama_active = requests.get(base_url, params=params_toyama_active, headers=headers)
        res_toyama_active.raise_for_status()
        count_toyama_active = res_toyama_active.json().get("metadata", {}).get("resultset", {}).get("count", 0)

        print(f"富山県の補助金 全件: {count_toyama_all}件")
        print(f"富山県の補助金 受付中: {count_toyama_active}件")
        print("="*30)

    except Exception as e:
        print(f"富山県データの取得中にエラーが発生しました: {e}")
    # =================================================================


if __name__ == "__main__":
    fetch_subsidies()
