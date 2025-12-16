import json
import sys

def analyze_target_area(json_file):
    """
    JSONファイルから全国と富山が対象の補助金件数を集計
    """
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        subsidies = data.get("result", [])
        total_count = len(subsidies)
        
        # 全国対象の件数
        zenkoku_count = 0
        # 富山県対象の件数
        toyama_count = 0
        # 両方に該当する件数
        both_count = 0
        
        for subsidy in subsidies:
            target_area = subsidy.get("target_area_search", "")
            
            # target_area_searchがNoneの場合は空文字列に変換
            if target_area is None:
                target_area = ""
            
            is_zenkoku = "全国" in target_area
            is_toyama = "富山" in target_area
            
            if is_zenkoku:
                zenkoku_count += 1
            if is_toyama:
                toyama_count += 1
            if is_zenkoku and is_toyama:
                both_count += 1
        
        print("=" * 50)
        print(f"📊 対象地域の集計結果（ファイル: {json_file}）")
        print("=" * 50)
        print(f"総件数: {total_count}件")
        print(f"")
        print(f"🌏 全国が対象: {zenkoku_count}件")
        print(f"🏔️  富山が対象: {toyama_count}件")
        print(f"🔄 両方に該当: {both_count}件")
        print("=" * 50)
        
        # サンプル表示（富山が対象のもの）
        print(f"\n【富山が対象の補助金サンプル（最初の5件）】")
        toyama_samples = [s for s in subsidies if s.get("target_area_search") and "富山" in s.get("target_area_search", "")]
        for i, subsidy in enumerate(toyama_samples[:5], 1):
            print(f"{i}. {subsidy.get('title', 'タイトルなし')}")
            print(f"   対象地域: {subsidy.get('target_area_search', 'N/A')}")
            print()
        
    except FileNotFoundError:
        print(f"❌ ファイルが見つかりません: {json_file}")
    except json.JSONDecodeError:
        print(f"❌ JSONファイルの読み込みに失敗しました: {json_file}")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")


if __name__ == "__main__":
    # コマンドライン引数でファイル名を指定、なければ最新のファイルを使用
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = "subsidies_20251216_111354.json"
    
    analyze_target_area(json_file)
