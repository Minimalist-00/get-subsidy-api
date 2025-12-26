# 補助金データ取得・保存システム

デジタル庁の補助金一覧 API から補助金データを取得し、Azure Blob Storage に保存するシステムです。

## 機能

- J-Grants API から補助金一覧を取得
- 各補助金の詳細情報を取得
- Azure Blob Storage に自動保存
- 重複データのスキップ（2 回目以降の実行時）
- 空データのフィルタリング

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`local.env.template` をコピーして `local.env` を作成し、必要な情報を記入してください。

```bash
cp local.env.template local.env
```

`local.env` に以下の情報を設定:

```env
# Azure Blob Storage接続文字列
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT_NAME;AccountKey=YOUR_ACCOUNT_KEY;EndpointSuffix=core.windows.net

# Blobコンテナ名
BLOB_CONTAINER_NAME=subsidies
```

#### Azure Storage 接続文字列の取得方法

1. Azure Portal にログイン
2. ストレージアカウントを選択
3. 「アクセスキー」メニューを開く
4. 「接続文字列」をコピー

## ローカルでの実行

環境変数を読み込んで実行:

```bash
# Bashの場合
export $(cat local.env | xargs)
python src/fetch_and_save_to_blob.py

# または直接指定
AZURE_STORAGE_CONNECTION_STRING="..." BLOB_CONTAINER_NAME="subsidies" python src/fetch_and_save_to_blob.py
```

## Azure Functions での実行

### デプロイ

```bash
func azure functionapp publish <YOUR_FUNCTION_APP_NAME>
```

### 環境変数の設定

Azure Portal または Azure CLI で以下の環境変数を設定:

- `AZURE_STORAGE_CONNECTION_STRING`
- `BLOB_CONTAINER_NAME`

### 手動実行

Azure Portal から Functions を開き、HTTP トリガーの URL にアクセスするか、「テスト/実行」ボタンをクリック。

## データ構造

### Blob 保存形式

- ファイル名: `{補助金ID}.json`
- 形式: JSON
- コンテナ: `subsidies` (デフォルト)

### スキップされるデータ

以下の条件を満たすデータは保存されません:

```json
{
  "application_guidelines": [],
  "outline_of_grant": [],
  "application_form": []
}
```

## ファイル構成

```
.
├── src/
│   ├── fetch_jgrants.py           # 補助金一覧取得
│   ├── fetch_subsidy_detail.py    # 補助金詳細取得
│   ├── fetch_and_save_to_blob.py  # メイン処理
│   ├── function_app.py            # Azure Functions エントリーポイント
│   └── function.json              # Azure Functions 設定
├── requirements.txt               # 依存パッケージ
├── local.env.template            # 環境変数テンプレート
└── README.md                     # このファイル
```

## トラブルシューティング

### 環境変数が読み込まれない

- `local.env` ファイルが正しい場所にあるか確認
- 環境変数が正しくエクスポートされているか確認: `echo $AZURE_STORAGE_CONNECTION_STRING`

### Blob 接続エラー

- 接続文字列が正しいか確認
- ストレージアカウントへのアクセス権限があるか確認
- ネットワーク接続を確認

### API 取得エラー

- インターネット接続を確認
- J-Grants API が稼働しているか確認
