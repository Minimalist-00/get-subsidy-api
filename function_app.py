import azure.functions as func
import logging
import sys
import os
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from fetch_and_save_to_blob import main as fetch_and_save_main

app = func.FunctionApp()

@app.timer_trigger(schedule="0 0 2 * * *", arg_name="myTimer", run_on_startup=False,
                   use_monitor=False) 
def fetch_subsidy_timer(myTimer: func.TimerRequest) -> None:
    """
    タイマートリガーで補助金データを取得してBlobに保存
    スケジュール: 毎日午前2時（JST）に実行
    Cron形式: "秒 分 時 日 月 曜日"
    """
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('補助金データ取得処理を開始します')
    
    try:
        # 全件処理を実行
        fetch_and_save_main()
        logging.info('補助金データ取得処理が正常に完了しました')
    except Exception as e:
        logging.error(f'補助金データ取得処理でエラーが発生しました: {e}')
        raise


@app.route(route="fetch_subsidy_manual", auth_level=func.AuthLevel.FUNCTION)
def fetch_subsidy_manual(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP トリガーで補助金データを手動取得
    URL: https://<your-function-app>.azurewebsites.net/api/fetch_subsidy_manual?code=<function-key>
    """
    logging.info('手動で補助金データ取得処理を開始します')

    try:
        # 全件処理を実行
        fetch_and_save_main()
        logging.info('補助金データ取得処理が正常に完了しました')
        
        return func.HttpResponse(
            "補助金データの取得と保存が正常に完了しました",
            status_code=200
        )
    except Exception as e:
        logging.error(f'補助金データ取得処理でエラーが発生しました: {e}')
        return func.HttpResponse(
            f"エラーが発生しました: {str(e)}",
            status_code=500
        )
