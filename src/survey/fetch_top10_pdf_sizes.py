import requests
import base64
import json
import os
from datetime import datetime

def load_subsidy_ids(json_path, limit=10):
    """JSONファイルから補助金IDを取得"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data.get("result", [])
    return [item["id"] for item in results[:limit]]

def get_subsidy_detail(subsidy_id):
    """補助金詳細を取得"""
    url = f"https://api.jgrants-portal.go.jp/exp/v1/public/subsidies/id/{subsidy_id}"
    
    headers = {
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    return data.get("result", [{}])[0]

def calculate_pdf_size(base64_data):
    """Base64エンコードされたPDFデータのサイズを計算（MB単位）"""
    pdf_bytes = base64.b64decode(base64_data)
    size_mb = len(pdf_bytes) / (1024 * 1024)
    return size_mb, pdf_bytes

def save_pdf_file(pdf_bytes, output_dir, rank, subsidy_id, filename):
    """PDFファイルを保存"""
    # ファイル名を整形（順位_ID_元のファイル名）
    safe_filename = f"{rank:02d}_{subsidy_id}_{filename}"
    filepath = os.path.join(output_dir, safe_filename)
    
    with open(filepath, "wb") as f:
        f.write(pdf_bytes)
    
    return filepath

def main():
    # JSONファイルのパス
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    json_path = os.path.join(project_root, "output", "subsidies_20251216_111354.json")
    
    # output/top10ディレクトリを作成
    output_dir = os.path.join(project_root, "output", "top10")
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("補助金詳細情報とPDFファイル取得")
    print("=" * 80)
    print(f"保存先: {output_dir}\n")
    
    # 上位10件のIDを取得
    subsidy_ids = load_subsidy_ids(json_path, limit=10)
    print(f"取得対象: {len(subsidy_ids)}件\n")
    
    results = []
    
    for i, subsidy_id in enumerate(subsidy_ids, 1):
        print(f"[{i}/10] ID: {subsidy_id}")
        
        try:
            # 詳細情報を取得
            detail = get_subsidy_detail(subsidy_id)
            
            title = detail.get("title", "タイトル不明")
            print(f"  タイトル: {title[:60]}...")
            
            # 詳細JSONを保存
            detail_filename = f"{i:02d}_{subsidy_id}_detail.json"
            detail_filepath = os.path.join(output_dir, detail_filename)
            with open(detail_filepath, "w", encoding="utf-8") as f:
                json.dump(detail, f, ensure_ascii=False, indent=2)
            print(f"  → 詳細JSON保存: {detail_filename}")
            
            # application_guidelinesを確認
            guidelines = detail.get("application_guidelines", [])
            
            if not guidelines:
                print("  → PDFファイルなし\n")
                results.append({
                    "rank": i,
                    "id": subsidy_id,
                    "title": title,
                    "pdf_count": 0,
                    "total_size_mb": 0,
                    "pdfs": [],
                    "detail_json": detail_filename
                })
            else:
                total_size = 0
                pdf_info = []
                
                print(f"  → PDFファイル数: {len(guidelines)}件")
                
                for j, guideline in enumerate(guidelines, 1):
                    pdf_name = guideline.get("name", "名前不明")
                    pdf_data = guideline.get("data", "")
                    
                    if pdf_data:
                        size_mb, pdf_bytes = calculate_pdf_size(pdf_data)
                        total_size += size_mb
                        
                        # PDFファイルを保存
                        saved_path = save_pdf_file(pdf_bytes, output_dir, i, subsidy_id, pdf_name)
                        
                        print(f"     [{j}] {pdf_name}")
                        print(f"         サイズ: {size_mb:.2f} MB")
                        print(f"         保存: {os.path.basename(saved_path)}")
                        
                        pdf_info.append({
                            "name": pdf_name,
                            "size_mb": round(size_mb, 2),
                            "saved_filename": os.path.basename(saved_path)
                        })
                    else:
                        print(f"     [{j}] {pdf_name}: データなし")
                
                results.append({
                    "rank": i,
                    "id": subsidy_id,
                    "title": title,
                    "pdf_count": len(guidelines),
                    "total_size_mb": round(total_size, 2),
                    "pdfs": pdf_info,
                    "detail_json": detail_filename
                })
                
                print(f"  → 合計サイズ: {total_size:.2f} MB\n")
        
        except Exception as e:
            print(f"  → エラー: {e}\n")
            results.append({
                "rank": i,
                "id": subsidy_id,
                "title": "取得失敗",
                "error": str(e)
            })
    
    # サマリー表示
    print("\n" + "=" * 80)
    print("【サマリー】")
    print("=" * 80)
    
    total_pdfs = sum(r.get("pdf_count", 0) for r in results)
    total_size = sum(r.get("total_size_mb", 0) for r in results)
    
    print(f"\n総PDFファイル数: {total_pdfs}件")
    print(f"総サイズ: {total_size:.2f} MB")
    if total_pdfs > 0:
        print(f"平均サイズ: {total_size / total_pdfs:.2f} MB/ファイル")
    
    # 一覧表示
    print("\n" + "-" * 80)
    print("【PDFサイズ一覧】")
    print("-" * 80)
    print(f"{'順位':<4} {'ID':<25} {'PDF数':<6} {'合計サイズ(MB)':<15}")
    print("-" * 80)
    
    for r in results:
        if "error" not in r:
            print(f"{r['rank']:<4} {r['id']:<25} {r['pdf_count']:<6} {r['total_size_mb']:<15.2f}")
    
    # 結果をJSONファイルに保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"summary_{timestamp}.json")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ サマリーを保存しました: {output_file}")
    print(f"✅ PDFファイル保存先: {output_dir}")

if __name__ == "__main__":
    main()
