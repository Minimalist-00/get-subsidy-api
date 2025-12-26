import os
import json
from azure.storage.blob import BlobServiceClient
from fetch_jgrants import fetch_subsidies_list
from fetch_subsidy_detail import fetch_subsidy_detail


def get_blob_service_client():
    """Azure Blob Storageのクライアントを取得"""
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("環境変数 AZURE_STORAGE_CONNECTION_STRING が設定されていません")
    return BlobServiceClient.from_connection_string(connection_string)


def get_existing_subsidy_ids(blob_service_client, container_name):
    """
    Blobに既に保存されている補助金IDのセットを取得
    
    Args:
        blob_service_client: BlobServiceClient
        container_name: コンテナ名
    
    Returns:
        set: 既存の補助金IDのセット
    """
    container_client = blob_service_client.get_container_client(container_name)
    
    # コンテナが存在しない場合は作成
    try:
        container_client.get_container_properties()
    except Exception:
        container_client.create_container()
        return set()
    
    # Blob一覧から補助金IDを抽出（ファイル名がID.jsonの形式を想定）
    existing_ids = set()
    for blob in container_client.list_blobs():
        blob_name = blob.name
        if blob_name.endswith('.json'):
            subsidy_id = blob_name[:-5]  # .jsonを除去
            existing_ids.add(subsidy_id)
    
    return existing_ids


def is_empty_detail(detail_data):
    """
    詳細データが空かどうかを判定
    application_guidelines, outline_of_grant, application_formが全て空配列の場合はTrue
    
    Args:
        detail_data: 補助金詳細データ
    
    Returns:
        bool: 空の場合True
    """
    if not detail_data:
        return True
    
    guidelines = detail_data.get('application_guidelines', [])
    outline = detail_data.get('outline_of_grant', [])
    form = detail_data.get('application_form', [])
    
    return len(guidelines) == 0 and len(outline) == 0 and len(form) == 0


def save_subsidy_to_blob(blob_service_client, container_name, subsidy_id, detail_data):
    """
    補助金詳細データをBlobに保存
    
    Args:
        blob_service_client: BlobServiceClient
        container_name: コンテナ名
        subsidy_id: 補助金ID
        detail_data: 補助金詳細データ
    """
    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=f"{subsidy_id}.json"
    )
    
    json_data = json.dumps(detail_data, ensure_ascii=False, indent=2)
    blob_client.upload_blob(json_data, overwrite=True)


def main():
    """メイン処理"""
    # 環境変数から設定を取得
    container_name = os.environ.get("BLOB_CONTAINER_NAME", "subsidies")
    
    print("補助金データ取得・保存処理を開始します")
    
    # 1. Blob Storageクライアントを取得
    blob_service_client = get_blob_service_client()
    print(f"Blob Storageに接続しました (コンテナ: {container_name})")
    
    # 2. 既存の補助金IDを取得
    existing_ids = get_existing_subsidy_ids(blob_service_client, container_name)
    print(f"既存の補助金データ: {len(existing_ids)}件")
    
    # 3. 補助金一覧を取得
    subsidies_data = fetch_subsidies_list()
    if not subsidies_data:
        print("補助金一覧の取得に失敗しました")
        return
    
    subsidies = subsidies_data.get("result", [])
    print(f"補助金一覧を取得しました: {len(subsidies)}件")
    
    # 4. 新規の補助金のみをフィルタリング
    new_subsidies = [s for s in subsidies if s.get("id") not in existing_ids]
    print(f"新規補助金: {len(new_subsidies)}件")
    
    if len(new_subsidies) == 0:
        print("新規の補助金はありません")
        return
    
    # 5. 各補助金の詳細を取得してBlobに保存
    saved_count = 0
    skipped_count = 0
    
    for subsidy in new_subsidies:
        subsidy_id = subsidy.get("id")
        title = subsidy.get("title", "不明")
        
        print(f"\n処理中: {subsidy_id} - {title[:50]}...")
        
        # 詳細情報を取得
        detail_data = fetch_subsidy_detail(subsidy_id)
        
        if not detail_data:
            print(f"  詳細情報の取得に失敗しました")
            continue
        
        # 空のデータはスキップ
        if is_empty_detail(detail_data):
            print(f"  空のデータのためスキップしました")
            skipped_count += 1
            continue
        
        # Blobに保存
        try:
            save_subsidy_to_blob(blob_service_client, container_name, subsidy_id, detail_data)
            print(f"  Blobに保存しました")
            saved_count += 1
        except Exception as e:
            print(f"  保存エラー: {e}")
    
    # 6. 結果サマリー
    print(f"\n{'='*60}")
    print(f"処理完了")
    print(f"   新規補助金: {len(new_subsidies)}件")
    print(f"   保存成功: {saved_count}件")
    print(f"   スキップ: {skipped_count}件")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
