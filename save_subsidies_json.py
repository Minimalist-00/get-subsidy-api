import requests
import json
from datetime import datetime

def fetch_and_save_subsidies():
    """
    J-Grants APIから補助金データを取得してJSON形式で保存する
    """
    base_url = "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies"
    
    headers = {
        "Accept": "application/json"
    }
    
    # 全件取得（acceptance=0で全期間）
    params = {
        "keyword": "補助金",
        "sort": "created_date",
        "order": "DESC",
        "acceptance": "0"  # 0: 全件, 1: 募集中のみ
    }
    
    try:
        print("J-Grants APIから補助金データを取得中...")
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # 取得件数を表示
        count = data.get("metadata", {}).get("resultset", {}).get("count", 0)
        print(f"取得件数: {count}件")
        
        # ファイル名にタイムスタンプを含める
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"subsidies_{timestamp}.json"
        
        # JSON形式で保存（日本語を読みやすく、インデント付き）
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ データを保存しました: {filename}")
        print(f"   - 総件数: {count}件")
        print(f"   - ファイルサイズ: {len(json.dumps(data, ensure_ascii=False)) / 1000} KB")
        
        return filename
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API取得エラー: {e}")
        return None
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return None


if __name__ == "__main__":
    fetch_and_save_subsidies()
