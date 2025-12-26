import requests
import json

def fetch_subsidy_detail(subsidy_id, exclude_fields=None):
    """
    J-Grants APIから特定の補助金の詳細情報を取得する
    
    Args:
        subsidy_id (str): 補助金のID
        exclude_fields (list): 除外するフィールド名のリスト
    
    Returns:
        dict: 補助金の詳細情報（取得失敗時はNone）
    """
    url = f"https://api.jgrants-portal.go.jp/exp/v1/public/subsidies/id/{subsidy_id}"
    headers = {"Accept": "application/json"}
    
    # デフォルトで除外するフィールド
    if exclude_fields is None:
        exclude_fields = ['application_guidelines', 'outline_of_grant', 'application_form']
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # resultフィールドが存在する場合、その中の最初の要素から不要なフィールドを削除
        if data and 'result' in data and len(data['result']) > 0:
            for field in exclude_fields:
                if field in data['result'][0]:
                    del data['result'][0][field]
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"API取得エラー (ID: {subsidy_id}): {e}")
        return None


if __name__ == "__main__":
    # テスト用
    test_id = "a0WJ200000CDRBGMA5"
    data = fetch_subsidy_detail(test_id)
    
    if data:
        print(json.dumps(data, ensure_ascii=False, indent=2))

