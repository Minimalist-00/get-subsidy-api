import json
import sys
from datetime import datetime
from collections import Counter

def analyze_update_frequency(json_file):
    """
    JSONファイルから補助金の更新頻度を分析
    """
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        subsidies = data.get("result", [])
        total_count = len(subsidies)
        
        print("=" * 60)
        print(f"📅 補助金データの更新頻度分析（ファイル: {json_file}）")
        print("=" * 60)
        print(f"総件数: {total_count}件\n")
        
        # 日付フィールドを確認
        created_dates = []
        updated_dates = []
        acceptance_start_dates = []
        acceptance_end_dates = []
        
        # サンプルデータの構造を確認
        if subsidies:
            print("【データ構造サンプル（1件目）】")
            sample = subsidies[0]
            for key, value in sample.items():
                if isinstance(value, str) and len(value) < 100:
                    print(f"  {key}: {value}")
            print()
        
        # 日付データを収集
        for subsidy in subsidies:
            # created_date系のフィールドを探す
            if "created_date" in subsidy and subsidy["created_date"]:
                try:
                    dt = datetime.fromisoformat(subsidy["created_date"].replace("Z", "+00:00"))
                    created_dates.append(dt)
                except:
                    pass
            
            if "updated_date" in subsidy and subsidy["updated_date"]:
                try:
                    dt = datetime.fromisoformat(subsidy["updated_date"].replace("Z", "+00:00"))
                    updated_dates.append(dt)
                except:
                    pass
            
            if "acceptance_start_datetime" in subsidy and subsidy["acceptance_start_datetime"]:
                try:
                    dt = datetime.fromisoformat(subsidy["acceptance_start_datetime"].replace("Z", "+00:00"))
                    acceptance_start_dates.append(dt)
                except:
                    pass
            
            if "acceptance_end_datetime" in subsidy and subsidy["acceptance_end_datetime"]:
                try:
                    dt = datetime.fromisoformat(subsidy["acceptance_end_datetime"].replace("Z", "+00:00"))
                    acceptance_end_dates.append(dt)
                except:
                    pass
        
        # 作成日時の分析
        if created_dates:
            created_dates.sort()
            print(f"【作成日時（created_date）の分析】")
            print(f"  データ件数: {len(created_dates)}件")
            print(f"  最古: {created_dates[0].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  最新: {created_dates[-1].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 月別の作成件数
            monthly_counts = Counter([dt.strftime('%Y-%m') for dt in created_dates])
            print(f"\n  【月別作成件数（最近6ヶ月）】")
            for month, count in sorted(monthly_counts.items(), reverse=True)[:6]:
                print(f"    {month}: {count}件")
            print()
        
        # 更新日時の分析
        if updated_dates:
            updated_dates.sort()
            print(f"【更新日時（updated_date）の分析】")
            print(f"  データ件数: {len(updated_dates)}件")
            print(f"  最古: {updated_dates[0].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  最新: {updated_dates[-1].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 月別の更新件数
            monthly_counts = Counter([dt.strftime('%Y-%m') for dt in updated_dates])
            print(f"\n  【月別更新件数（最近6ヶ月）】")
            for month, count in sorted(monthly_counts.items(), reverse=True)[:6]:
                print(f"    {month}: {count}件")
            print()
        
        # 募集開始日時の分析
        if acceptance_start_dates:
            acceptance_start_dates.sort()
            print(f"【募集開始日時の分析】")
            print(f"  データ件数: {len(acceptance_start_dates)}件")
            print(f"  最古: {acceptance_start_dates[0].strftime('%Y-%m-%d')}")
            print(f"  最新: {acceptance_start_dates[-1].strftime('%Y-%m-%d')}")
            
            # 今後開始予定のもの
            now = datetime.now(acceptance_start_dates[0].tzinfo)
            future_starts = [dt for dt in acceptance_start_dates if dt > now]
            print(f"  今後開始予定: {len(future_starts)}件")
            print()
            
            # 新しいもの20件を表示
            print(f"【募集開始日時が新しい順 TOP 20】")
            # 補助金を募集開始日時でソート
            subsidies_with_dates = []
            for subsidy in subsidies:
                if "acceptance_start_datetime" in subsidy and subsidy["acceptance_start_datetime"]:
                    try:
                        dt = datetime.fromisoformat(subsidy["acceptance_start_datetime"].replace("Z", "+00:00"))
                        subsidies_with_dates.append((dt, subsidy))
                    except:
                        pass
            
            # 新しい順にソート
            subsidies_with_dates.sort(key=lambda x: x[0], reverse=True)
            
            # 上位20件を表示
            for i, (dt, subsidy) in enumerate(subsidies_with_dates[:20], 1):
                title = subsidy.get("title", "タイトルなし")
                # タイトルが長い場合は省略
                if len(title) > 60:
                    title = title[:60] + "..."
                print(f"  {i:2d}. {dt.strftime('%Y-%m-%d %H:%M')} | {title}")
            print()
        
        # 募集終了日時の分析
        if acceptance_end_dates:
            acceptance_end_dates.sort()
            print(f"【募集終了日時の分析】")
            print(f"  データ件数: {len(acceptance_end_dates)}件")
            print(f"  最古: {acceptance_end_dates[0].strftime('%Y-%m-%d')}")
            print(f"  最新: {acceptance_end_dates[-1].strftime('%Y-%m-%d')}")
            
            # 現在募集中のもの（終了日が未来）
            now = datetime.now(acceptance_end_dates[0].tzinfo)
            active_subsidies = [dt for dt in acceptance_end_dates if dt > now]
            print(f"  現在募集中（終了日が未来）: {len(active_subsidies)}件")
            
            # 月別の終了予定
            monthly_ends = Counter([dt.strftime('%Y-%m') for dt in active_subsidies])
            if monthly_ends:
                print(f"\n  【月別終了予定（募集中のもの）】")
                for month, count in sorted(monthly_ends.items())[:6]:
                    print(f"    {month}: {count}件")
            print()
        
        print("=" * 60)
        print("【結論】")
        if created_dates:
            days_span = (created_dates[-1] - created_dates[0]).days
            avg_per_day = len(created_dates) / max(days_span, 1)
            print(f"  データ期間: {days_span}日間")
            print(f"  平均作成頻度: 約{avg_per_day:.2f}件/日")
        
        if updated_dates:
            recent_updates = [dt for dt in updated_dates if (datetime.now(dt.tzinfo) - dt).days <= 30]
            print(f"  過去30日以内の更新: {len(recent_updates)}件")
        
        print("=" * 60)
        
    except FileNotFoundError:
        print(f"❌ ファイルが見つかりません: {json_file}")
    except json.JSONDecodeError:
        print(f"❌ JSONファイルの読み込みに失敗しました: {json_file}")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # コマンドライン引数でファイル名を指定、なければ最新のファイルを使用
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = "subsidies_20251216_111354.json"
    
    analyze_update_frequency(json_file)
