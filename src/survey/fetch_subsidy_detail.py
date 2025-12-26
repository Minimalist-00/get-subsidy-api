import requests
import json

def fetch_subsidy_detail(subsidy_id):
    """
    J-Grants APIから特定の補助金の詳細情報を取得する
    
    Args:
        subsidy_id (str): 補助金のID
    
    Returns:
        dict: 補助金の詳細情報（取得失敗時はNone）
    """
    url = f"https://api.jgrants-portal.go.jp/exp/v1/public/subsidies/id/{subsidy_id}"
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API取得エラー (ID: {subsidy_id}): {e}")
        return None


if __name__ == "__main__":
    # テスト用
    test_id = "a0WJ200000CDRBGMA5"
    data = fetch_subsidy_detail(test_id)
    
    if data:
        print(json.dumps(data, ensure_ascii=False, indent=2))

