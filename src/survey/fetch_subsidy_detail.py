import requests
import json
import os
import argparse
from datetime import datetime

def fetch_subsidy_detail(subsidy_id):
    """
    J-Grants APIから特定の補助金の詳細情報を取得する
    
    Args:
        subsidy_id (str): 補助金のID
    
    Returns:
        dict: 補助金の詳細情報
    """
    base_url = f"https://api.jgrants-portal.go.jp/exp/v1/public/subsidies/id/{subsidy_id}"
    
    headers = {
        "Accept": "application/json"
    }
    
    try:
        print(f"補助金ID: {subsidy_id} の詳細情報を取得中...")
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # 基本情報を表示
        print("\n" + "="*80)
        print("📋 補助金詳細情報")
        print("="*80)
        
        result = data.get("result", {})
        
        # タイトル
        if "title" in result:
            print(f"\n【タイトル】\n{result['title']}")
        
        # キャッチフレーズ
        if "catch_phrase" in result:
            print(f"\n【キャッチフレーズ】\n{result['catch_phrase']}")
        
        # 詳細説明
        if "detail" in result:
            detail_text = result['detail'][:200] + "..." if len(result.get('detail', '')) > 200 else result.get('detail', '')
            print(f"\n【詳細説明】\n{detail_text}")
        
        # 補助金情報
        print(f"\n【補助金情報】")
        if "subsidy_max_limit" in result:
            print(f"  上限額: {result['subsidy_max_limit']:,}円")
        if "subsidy_rate" in result:
            print(f"  補助率: {result['subsidy_rate']}")
        
        # 対象情報
        print(f"\n【対象情報】")
        if "target_area_search" in result:
            print(f"  対象地域: {result['target_area_search']}")
        if "target_number_of_employees" in result:
            print(f"  従業員数: {result['target_number_of_employees']}")
        if "industry" in result:
            print(f"  業種: {result['industry']}")
        if "use_purpose" in result:
            print(f"  利用目的: {result['use_purpose']}")
        
        # 募集情報
        print(f"\n【募集情報】")
        if "acceptance_start_datetime" in result:
            print(f"  募集開始: {result['acceptance_start_datetime']}")
        if "acceptance_end_datetime" in result:
            print(f"  募集終了: {result['acceptance_end_datetime']}")
        if "project_end_datetime" in result:
            print(f"  事業期限: {result['project_end_datetime']}")
        
        # 添付ファイル情報（Base64データは表示しない）
        print(f"\n【添付ファイル】")
        if "public_offering_guidelines_file" in result and result["public_offering_guidelines_file"]:
            print(f"  ✓ 公募要領（PDF）")
        if "grant_guidelines_file" in result and result["grant_guidelines_file"]:
            print(f"  ✓ 交付要綱（PDF）")
        if "application_form_file" in result and result["application_form_file"]:
            print(f"  ✓ 申請様式（PDF）")
        
        # 問い合わせ先
        if "contact" in result:
            print(f"\n【問い合わせ先】\n{result['contact']}")
        
        print("\n" + "="*80)
        
        # ファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # スクリプトのディレクトリから2階層上がプロジェクトルート
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        output_dir = os.path.join(project_root, "output")
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"subsidy_detail_{subsidy_id}_{timestamp}.json")
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 詳細データを保存しました: {filename}")
        
        # データサイズを表示
        data_size = len(json.dumps(data, ensure_ascii=False))
        print(f"   ファイルサイズ: {data_size / 1024 / 1024:.2f} MB")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API取得エラー: {e}")
        return None
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="J-Grants APIから補助金の詳細情報を取得します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python fetch_subsidy_detail.py a0WJ200000CDRBGMA5
  python fetch_subsidy_detail.py --id a0WJ200000CDRBGMA5
        """
    )
    parser.add_argument(
        "subsidy_id",
        nargs="?",
        help="補助金のID（例: a0WJ200000CDRBGMA5）"
    )
    parser.add_argument(
        "--id",
        dest="subsidy_id_option",
        help="補助金のID（オプション形式）"
    )
    
    args = parser.parse_args()
    
    # 引数の優先順位: 位置引数 > --id オプション
    subsidy_id = args.subsidy_id or args.subsidy_id_option
    
    if not subsidy_id:
        parser.print_help()
        print("\n❌ エラー: 補助金IDを指定してください")
        exit(1)
    
    fetch_subsidy_detail(subsidy_id)

