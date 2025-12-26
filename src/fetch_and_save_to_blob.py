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


def save_subsidy_to_blob(blob_service_client, container_name, subsidy_id, detail_data):
    """
    補助金詳細データをBlobに保存
    application_guidelines, outline_of_grant, application_formフィールドは除外する
    
    Args:
        blob_service_client: BlobServiceClient
        container_name: コンテナ名
        subsidy_id: 補助金ID
        detail_data: 補助金詳細データ
    """
    # 除外するフィールドのリスト
    exclude_fields = ['application_guidelines', 'outline_of_grant', 'application_form']
    
    # 除外フィールドを削除したデータを作成
    filtered_data = {k: v for k, v in detail_data.items() if k not in exclude_fields}
    
    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=f"{subsidy_id}.json"
    )
    
    json_data = json.dumps(filtered_data, ensure_ascii=False, indent=2)
    blob_client.upload_blob(json_data, overwrite=True)


def main():
    """メイン処理"""
    # 環境変数から設定を取得
    container_name = os.environ.get("BLOB_CONTAINER_NAME", "subsidies")
    
    print("補助金データ取得・保存処理を開始します")
    
    # 1. Blob Storageクライアントを取得
    blob_service_client = get_blob_service_client()
    
    # 2. 既存の補助金IDを取得
    existing_ids = get_existing_subsidy_ids(blob_service_client, container_name)
    
    # 3. 補助金一覧を取得
    subsidies_data = fetch_subsidies_list()
    if not subsidies_data:
        print("補助金一覧の取得に失敗しました")
        return
    
    subsidies = subsidies_data.get("result", [])
    
    # 4. 新規の補助金のみをフィルタリング
    new_subsidies = [s for s in subsidies if s.get("id") not in existing_ids]
    
    if len(new_subsidies) == 0:
        print("新規の補助金はありません")
        return
    
    # 5. 各補助金の詳細を取得してBlobに保存
    saved_count = 0
    failed_count = 0
    
    for subsidy in new_subsidies:
        subsidy_id = subsidy.get("id")
        title = subsidy.get("title", "不明")
        
        # 詳細情報を取得
        detail_data = fetch_subsidy_detail(subsidy_id)
        
        if not detail_data:
            print(f"詳細情報の取得に失敗: {subsidy_id} - {title[:50]}...")
            failed_count += 1
            continue
        
        # Blobに保存
        try:
            save_subsidy_to_blob(blob_service_client, container_name, subsidy_id, detail_data)
            saved_count += 1
        except Exception as e:
            print(f"保存エラー: {subsidy_id} - {title[:50]}... - {e}")
            failed_count += 1
    
    # 6. 結果サマリー
    print(f"\n{'='*60}")
    print(f"処理完了")
    print(f"   新規補助金: {len(new_subsidies)}件")
    print(f"   保存成功: {saved_count}件")
    if failed_count > 0:
        print(f"   失敗: {failed_count}件")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
