import azure.functions as func
import logging
from fetch_and_save_to_blob import main as fetch_and_save_main


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Functions HTTPトリガー
    補助金データを取得してBlobに保存する
    """
    logging.info('補助金データ取得・保存処理を開始します')
    
    try:
        # メイン処理を実行
        fetch_and_save_main()
        
        return func.HttpResponse(
            "補助金データの取得・保存が完了しました",
            status_code=200
        )
    except Exception as e:
        logging.error(f"エラーが発生しました: {e}")
        return func.HttpResponse(
            f"エラーが発生しました: {str(e)}",
            status_code=500
        )
