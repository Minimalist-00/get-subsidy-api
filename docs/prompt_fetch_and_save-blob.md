## 前提

デジタル庁の補助金一覧 API から補助金の一覧を取得して、それぞれの補助金の詳細を取得して、それぞれを blob に格納するというタスクを行う

## やること

1. Fucntions で手動実行する
2. 補助金 API を叩いて、補助金の一覧を取得
3. 補助金の一覧 API を叩い時に取得できたそれぞれの id を参照して詳細情報を取得し、それぞれを blob に格納する

一覧と詳細取得のコードは[fetch_jgrants.py](../src/fetch_jgrants.py)と[fetch_subsidy_detail.py](../src/fetch_subsidy_detail.py)である

## 留意点

- 2 回目以降実行した時に、取得するものが重複しないよう、一覧を取得した後に blob に格納されているものの id と比較をしてほしい
  - その結果、blob に含まれていないもののみ詳細を取得し、blob に新しく格納する
- 以下の フィールドは除いた状態で全件を blob に格納してほしい
  ```json
  {
    "application_guidelines": [],
    "outline_of_grant": [],
    "application_form": []
  }
  ```
- 格納するときの形式は json なので、blob には json 形式のまま格納してほしい

## 補助金一覧 API の構造

| キー                         | データ型         | 説明                     |
| ---------------------------- | ---------------- | ------------------------ |
| `id`                         | 文字列           | 補助金の一意識別子       |
| `name`                       | 文字列           | 補助金の管理番号         |
| `title`                      | 文字列           | 補助金のタイトル         |
| `target_area_search`         | 文字列           | 対象地域(検索用)         |
| `subsidy_max_limit`          | 数値             | 補助金の上限額           |
| `acceptance_start_datetime`  | 文字列(ISO 8601) | 受付開始日時             |
| `acceptance_end_datetime`    | 文字列(ISO 8601) | 受付終了日時             |
| `target_number_of_employees` | 文字列           | 対象となる従業員数の条件 |

### 注意事項

- 日時フィールドは ISO 8601 形式(例: `2025-06-25T05:00:00.000Z`)で提供されます
- `subsidy_max_limit`が`0`の場合、上限額が設定されていないか、別途確認が必要です
- 一覧データは検索・絞り込み用の基本情報のみを提供します

## 補助金詳細 API の構造

| カテゴリ             | キー                            | データ型         | 説明                                                               |
| -------------------- | ------------------------------- | ---------------- | ------------------------------------------------------------------ |
| **基本情報**         | `id`                            | 文字列           | 補助金の一意識別子                                                 |
|                      | `name`                          | 文字列           | 補助金の管理番号                                                   |
|                      | `title`                         | 文字列           | 補助金のタイトル                                                   |
|                      | `subsidy_catch_phrase`          | 文字列           | 補助金のキャッチフレーズ                                           |
| **詳細情報**         | `detail`                        | 文字列(HTML)     | 補助金の詳細説明(目的・概要、根拠法令、応募資格、問合せ先等を含む) |
| **対象・条件**       | `use_purpose`                   | 文字列           | 補助金の利用目的                                                   |
|                      | `industry`                      | 文字列           | 対象となる業種                                                     |
|                      | `target_area_search`            | 文字列           | 対象地域(検索用)                                                   |
|                      | `target_area_detail`            | 文字列           | 対象地域の詳細説明                                                 |
|                      | `target_number_of_employees`    | 文字列           | 対象となる従業員数の条件                                           |
| **金額・補助率**     | `subsidy_rate`                  | 文字列           | 補助率(例: "3/4 以内")                                             |
|                      | `subsidy_max_limit`             | 数値             | 補助金の上限額                                                     |
| **期間・期限**       | `acceptance_start_datetime`     | 文字列(ISO 8601) | 受付開始日時                                                       |
|                      | `acceptance_end_datetime`       | 文字列(ISO 8601) | 受付終了日時                                                       |
|                      | `project_end_deadline`          | 文字列(ISO 8601) | 事業完了期限                                                       |
| **申請条件**         | `request_reception_presence`    | 文字列           | 事前相談の有無                                                     |
|                      | `is_enable_multiple_request`    | 真偽値           | 複数申請の可否                                                     |
| **リンク・添付資料** | `front_subsidy_detail_page_url` | 文字列(URL)      | 補助金詳細ページの URL                                             |
|                      | `application_guidelines`        | 配列             | 申請要領のリスト                                                   |
|                      | `application_guidelines[].name` | 文字列           | 申請要領ファイル名                                                 |
|                      | `application_guidelines[].data` | 文字列(Base64)   | Base64 エンコードされた PDF データ                                 |

### 注意事項

- 日時フィールドは ISO 8601 形式(例: `2025-06-25T05:00Z`)で提供されます
- `detail`フィールドは HTML 形式のため、表示時には HTML パーサーが必要です
- `application_guidelines[].data`は大容量の Base64 エンコードデータを含むため、処理時には注意が必要です
