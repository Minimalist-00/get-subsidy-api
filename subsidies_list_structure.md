# 補助金一覧データ構造

## 概要

J-Grants APIから取得される補助金一覧情報(`result`)の構造を説明します。
これは補助金の基本情報のみを含む簡易版のデータです。

## データ構造

| キー | データ型 | 説明 |
|------|---------|------|
| `id` | 文字列 | 補助金の一意識別子 |
| `name` | 文字列 | 補助金の管理番号 |
| `title` | 文字列 | 補助金のタイトル |
| `target_area_search` | 文字列 | 対象地域(検索用) |
| `subsidy_max_limit` | 数値 | 補助金の上限額 |
| `acceptance_start_datetime` | 文字列(ISO 8601) | 受付開始日時 |
| `acceptance_end_datetime` | 文字列(ISO 8601) | 受付終了日時 |
| `target_number_of_employees` | 文字列 | 対象となる従業員数の条件 |

## 詳細データとの違い

一覧データには以下の情報が**含まれません**：
- `subsidy_catch_phrase`（キャッチフレーズ）
- `detail`（詳細説明HTML）
- `use_purpose`（利用目的）
- `industry`（対象業種）
- `target_area_detail`（対象地域詳細）
- `subsidy_rate`（補助率）
- `project_end_deadline`（事業完了期限）
- `request_reception_presence`（事前相談の有無）
- `is_enable_multiple_request`（複数申請可否）
- `front_subsidy_detail_page_url`（詳細ページURL）
- `application_guidelines`（申請要領PDF）

詳細情報が必要な場合は、`id`を使用して個別の補助金詳細APIを呼び出す必要があります。

## 注意事項

- 日時フィールドはISO 8601形式(例: `2025-06-25T05:00:00.000Z`)で提供されます
- `subsidy_max_limit`が`0`の場合、上限額が設定されていないか、別途確認が必要です
- 一覧データは検索・絞り込み用の基本情報のみを提供します
