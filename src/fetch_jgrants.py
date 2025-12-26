import requests

def fetch_subsidies_list(params=None):
    """
    J-Grants APIから補助金の一覧を取得する
    
    Args:
        params (dict, optional): APIリクエストパラメータ
            デフォルトは受付中の補助金を新しい順で取得
    
    Returns:
        dict: APIレスポンス全体（取得失敗時はNone）
    """
    url = "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies"
    headers = {"Accept": "application/json"}
    
    # デフォルトパラメータ
    if params is None:
        params = {
            "keyword": "補助金",
            "sort": "created_date",
            "order": "DESC",
            "acceptance": "1"  # 1: 受付中, 0: すべて
        }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API取得エラー: {e}")
        return None


if __name__ == "__main__":
    # テスト用
    data = fetch_subsidies_list()
    
    if data:
        count = data.get("metadata", {}).get("resultset", {}).get("count", 0)
        items = data.get("result", [])
        print(f"✅ 補助金一覧取得成功")
        print(f"   総件数: {count}件")
        print(f"   取得件数: {len(items)}件")
        
        if items:
            print(f"\n最初の補助金:")
            print(f"   ID: {items[0].get('id')}")
            print(f"   タイトル: {items[0].get('title')}")
