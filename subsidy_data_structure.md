# 補助金データ構造

## 概要

J-Grants APIから取得される補助金詳細情報(`result`)の構造を説明します。

## データ構造

| カテゴリ | キー | データ型 | 説明 |
|---------|------|---------|------|
| **基本情報** | `id` | 文字列 | 補助金の一意識別子 |
| | `name` | 文字列 | 補助金の管理番号 |
| | `title` | 文字列 | 補助金のタイトル |
| | `subsidy_catch_phrase` | 文字列 | 補助金のキャッチフレーズ |
| **詳細情報** | `detail` | 文字列(HTML) | 補助金の詳細説明(目的・概要、根拠法令、応募資格、問合せ先等を含む) |
| **対象・条件** | `use_purpose` | 文字列 | 補助金の利用目的 |
| | `industry` | 文字列 | 対象となる業種 |
| | `target_area_search` | 文字列 | 対象地域(検索用) |
| | `target_area_detail` | 文字列 | 対象地域の詳細説明 |
| | `target_number_of_employees` | 文字列 | 対象となる従業員数の条件 |
| **金額・補助率** | `subsidy_rate` | 文字列 | 補助率(例: "3/4以内") |
| | `subsidy_max_limit` | 数値 | 補助金の上限額 |
| **期間・期限** | `acceptance_start_datetime` | 文字列(ISO 8601) | 受付開始日時 |
| | `acceptance_end_datetime` | 文字列(ISO 8601) | 受付終了日時 |
| | `project_end_deadline` | 文字列(ISO 8601) | 事業完了期限 |
| **申請条件** | `request_reception_presence` | 文字列 | 事前相談の有無 |
| | `is_enable_multiple_request` | 真偽値 | 複数申請の可否 |
| **リンク・添付資料** | `front_subsidy_detail_page_url` | 文字列(URL) | 補助金詳細ページのURL |
| | `application_guidelines` | 配列 | 申請要領のリスト |
| | `application_guidelines[].name` | 文字列 | 申請要領ファイル名 |
| | `application_guidelines[].data` | 文字列(Base64) | Base64エンコードされたPDFデータ |

## 注意事項

- 日時フィールドはISO 8601形式(例: `2025-06-25T05:00Z`)で提供されます
- `detail`フィールドはHTML形式のため、表示時にはHTMLパーサーが必要です
- `application_guidelines[].data`は大容量のBase64エンコードデータを含むため、処理時には注意が必要です
