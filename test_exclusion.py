#!/usr/bin/env python3
"""
fetch_subsidy_detail.pyの除外機能をテストするスクリプト
"""
import sys
import os
import json

# srcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fetch_subsidy_detail import fetch_subsidy_detail

def test_fetch_with_exclusion():
    """不要フィールドが除外されているかテスト"""
    # テスト用の補助金ID（実際のID）
    test_id = "a0W5h00000RcFx6EAF"
    
    print(f"補助金ID: {test_id} の詳細を取得中...")
    print("=" * 60)
    
    # 詳細情報を取得（デフォルトで除外）
    data = fetch_subsidy_detail(test_id)
    
    if not data:
        print("❌ データ取得に失敗しました")
        return False
    
    # resultフィールドをチェック
    if 'result' not in data or len(data['result']) == 0:
        print("❌ resultフィールドが見つかりません")
        return False
    
    result = data['result'][0]
    
    # 除外すべきフィールドがないことを確認
    excluded_fields = ['application_guidelines', 'outline_of_grant', 'application_form']
    found_excluded = []
    
    for field in excluded_fields:
        if field in result:
            found_excluded.append(field)
    
    # 結果表示
    print(f"取得したフィールド数: {len(result)}")
    print(f"\n主要フィールド:")
    for key in ['id', 'name', 'title', 'subsidy_max_limit']:
        if key in result:
            value = result[key]
            if isinstance(value, str) and len(value) > 50:
                value = value[:50] + "..."
            print(f"  - {key}: {value}")
    
    print(f"\n除外フィールドチェック:")
    for field in excluded_fields:
        status = "❌ 存在する" if field in result else "✅ 除外済み"
        print(f"  - {field}: {status}")
    
    # データサイズを表示
    json_str = json.dumps(data, ensure_ascii=False)
    size_kb = len(json_str.encode('utf-8')) / 1024
    print(f"\nデータサイズ: {size_kb:.2f} KB")
    
    print("=" * 60)
    
    if found_excluded:
        print(f"❌ テスト失敗: 以下のフィールドが除外されていません: {', '.join(found_excluded)}")
        return False
    else:
        print("✅ テスト成功: すべての不要フィールドが除外されています")
        return True

if __name__ == "__main__":
    success = test_fetch_with_exclusion()
    sys.exit(0 if success else 1)
