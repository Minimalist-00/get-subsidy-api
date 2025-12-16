# JグランツAPI 調査レポート

## 1. API概要

### 基本情報
- **提供元**: デジタル庁
- **サービス名**: jGrants（Jグランツ）
- **API種別**: パブリックAPI（認証不要）
- **エンドポイント**: `https://api.jgrants-portal.go.jp/exp/v1/public`
- **利用料**: 無料
- **ドキュメント**: https://developers.digital.go.jp/documents/jgrants/api/

### 提供されるAPI

#### 1. 補助金一覧取得API
```
GET /subsidies
```

**主要パラメータ**:
- `keyword` (必須): 検索キーワード（2文字以上、表記ゆれ対応）
- `sort` (必須): ソート項目
  - `created_date`: 作成日時
  - `acceptance_start_datetime`: 募集開始日時
  - `acceptance_end_datetime`: 募集終了日時
- `order` (必須): ソート順（ASC/DESC）
- `acceptance` (必須): 募集期間内絞込（0:否 / 1:要）
- `use_purpose` (任意): 利用目的（複数可、スペース+/+スペースで区切り）
- `industry` (任意): 業種（複数可）
- `target_number_of_employees` (任意): 従業員数
- `target_area_search` (任意): 補助対象地域

**レスポンス例**:
```json
{
  "metadata": {
    "type": "...",
    "resultset": {
      "count": 1
    }
  },
  "result": [
    {
      "id": "S0J0w00wer0wUgr77E",
      "name": "S-01100011",
      "title": "小規模事業者補助金",
      "target_area_search": "東京都 / 大阪府",
      "subsidy_max_limit": 10000000,
      "acceptance_start_datetime": "2020-02-28T16:41:41.090Z",
      "acceptance_end_datetime": "2021-02-28T16:41:41.090Z",
      "target_number_of_employees": "20名以下"
    }
  ]
}
```

#### 2. 補助金詳細取得API
```
GET /subsidies/id/{id}
```

**詳細情報に含まれる項目**:
- 基本情報（タイトル、キャッチフレーズ、詳細説明）
- 対象情報（利用目的、業種、地域、従業員数）
- 補助金情報（補助率、上限額）
- 募集情報（開始/終了日時、プロジェクト期限）
- **添付ファイル**（Base64エンコード）:
  - 公募要領（PDF）
  - 交付要綱（PDF）
  - 申請様式（PDF）

---

## 2. データ量と更新頻度

### データ規模
- **2021年時点**: 14省庁30自治体の410補助金
- **2021年（8月時点）**: 約800以上の補助金
- **申請件数**: 年間約9万件（2021年1-11月）

### 推定データ量
- 1件あたりの一覧データ: 約0.5-1KB
- 1件あたりの詳細データ（PDF含む）: 数MB〜数十MB
- **全件一覧取得**: 800件 × 1KB = 約800KB（軽量）
- **全件詳細取得**: PDFを含めると数GB規模

### 更新頻度
- 補助金情報は随時更新（新規追加、募集期間変更など）
- 日次〜週次での更新が想定される

---

## 3. 利用規約とデータ保存

### 利用条件
- **認証不要**: API Keyの取得は不要
- **無料**: 誰でも自由に利用可能
- **用途**: 民間企業が自社サービスに補助金検索機能を実装することを想定

### データ保存について
調査した範囲では、**APIで取得したデータの保存や二次利用を明示的に禁止する記述は見当たりませんでした**。

むしろ、以下の点から**データ保存は許容されている**と考えられます:
- 民間IT企業が自社サービスに補助金検索・マッチング機能を実装することを推奨
- GAS（Google Apps Script）やPythonでのデータ取得・保存の実装例が公開されている
- データ分析による補助金設計の改善を目的としている

**ただし、念のため**:
- デジタル庁の公式利用規約ページ（https://www.jgrants-portal.go.jp/open-api）を確認することを推奨
- 商用利用の場合は事前確認が望ましい

---

## 4. 実装案の検討

### 案1: 全件データをローカルDBに保存（推奨）

**メリット**:
- レスポンスが高速
- APIレート制限の心配なし
- オフライン検索が可能
- Azure OpenAIとの連携が容易

**デメリット**:
- データの鮮度維持が必要（定期更新の仕組みが必要）
- ストレージコスト（ただし一覧データのみなら数百KB程度）

**実装イメージ**:
```python
# 1. 日次バッチで全件取得
import requests

def fetch_all_subsidies():
    # 一覧取得（募集中のみ）
    response = requests.get(
        "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies",
        params={
            "keyword": "補助金",  # 広めのキーワード
            "sort": "created_date",
            "order": "DESC",
            "acceptance": "1"  # 募集中のみ
        }
    )
    subsidies = response.json()["result"]
    
    # 詳細情報を取得（PDFは除外して軽量化）
    for subsidy in subsidies:
        detail = get_subsidy_detail(subsidy["id"])
        # Azure SQL Database or Cosmos DBに保存
        save_to_db(detail)

# 2. ユーザーの問い合わせに応じて検索
def search_subsidies(user_query):
    # Azure OpenAIでユーザークエリを解析
    search_params = analyze_query_with_aoai(user_query)
    
    # ローカルDBから検索
    results = search_from_db(search_params)
    return results
```

---

### 案2: リアルタイムAPI呼び出し

**メリット**:
- 常に最新データ
- ストレージコスト不要

**デメリット**:
- レスポンスがやや遅い
- APIレート制限の可能性
- ネットワーク障害のリスク

**実装イメージ**:
```python
def search_subsidies_realtime(user_query):
    # Azure OpenAIでユーザークエリを解析
    search_params = analyze_query_with_aoai(user_query)
    
    # JグランツAPIを呼び出し
    response = requests.get(
        "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies",
        params=search_params
    )
    return response.json()["result"]
```

---

### 案3: ハイブリッド方式（推奨度: 高）

**概要**:
- 一覧データ（軽量）はAzure Blob Storageに日次で保存
- PDFなどの重いファイルは必要時にAPIから取得
- 検索はAzure Cognitive Searchで実現

**メリット**:
- 高速検索とデータの鮮度を両立
- ストレージコストを抑制
- スケーラビリティが高い

**構成図**:
```
[日次バッチ]
  ↓
[JグランツAPI] → 一覧データ取得
  ↓
[Azure Blob Storage] ← データ保存（JSON形式）
  ↓
[Azure Cognitive Search] ← インデックス作成

[ユーザー問い合わせ]
  ↓
[Azure OpenAI] → クエリ解析・検索パラメータ生成
  ↓
[Azure Cognitive Search] → 補助金検索
  ↓
[必要に応じて] → JグランツAPI（詳細・PDF取得）
```

---

## 5. 検索機能の実装パターン

### パターンA: フリーワード検索
```python
# ユーザー入力: "中小企業のDX支援に使える補助金"
# ↓ Azure OpenAIで抽出
keywords = ["DX", "デジタル化", "IT導入"]
industry = "情報通信業"
target_employees = "50名以下"
```

### パターンB: カテゴリ絞り込み
```python
# ユーザー入力: "新規事業を始めたい、従業員20名の製造業です"
# ↓ Azure OpenAIで構造化
{
    "use_purpose": "新たな事業を行いたい",
    "industry": "製造業",
    "target_number_of_employees": "20名以下"
}
```

### パターンC: 会話型検索
```python
# 会話履歴を考慮した検索
user: "県内で使える補助金を教えて"
assistant: "どのような用途の補助金をお探しですか？"
user: "設備投資です"
# ↓ 履歴を踏まえた検索
{
    "keyword": "設備投資",
    "target_area_search": "富山県",  # ユーザーの所属から推定
    "acceptance": "1"
}
```

---

## 6. Azure OpenAI活用案

### 活用シーン1: クエリの構造化
```python
# プロンプト例
prompt = f"""
ユーザーの問い合わせ: {user_query}

以下のJSONフォーマットで検索パラメータを抽出してください:
{{
    "keyword": "...",
    "use_purpose": "...",
    "industry": "...",
    "target_area_search": "...",
    "target_number_of_employees": "..."
}}

利用可能な選択肢:
- use_purpose: 新たな事業を行いたい, 販路拡大・海外展開をしたい, ...
- industry: 製造業, 情報通信業, ...
- target_area_search: 富山県, 全国, ...
"""
```

### 活用シーン2: 検索結果の要約
```python
# 検索結果を分かりやすく要約
results = search_subsidies(params)
summary = aoai_summarize(results, user_query)

# 出力例
"""
ご質問の「DX推進のための補助金」について、以下3件が該当します:

1. IT導入補助金2024
   - 上限額: 450万円
   - 補助率: 1/2
   - 締切: 2024年12月末
   - 詳細: ITツール導入費用を補助

2. デジタル化応援隊事業
   - 上限額: 100万円
   - 補助率: 2/3
   - 締切: 随時募集
   ...
"""
```

### 活用シーン3: 要求内容との適合性判定
```python
# ユーザーの要求と補助金の適合度を判定
def check_compatibility(user_request, subsidy):
    prompt = f"""
    要求内容: {user_request}
    補助金: {subsidy["title"]}
    詳細: {subsidy["detail"]}
    
    この補助金がユーザーの要求に適合するか、適合度を0-100で評価してください。
    また、適合しない理由があれば指摘してください。
    """
    return aoai_evaluate(prompt)
```

---

## 7. 推奨実装ステップ

### Phase 1: PoC（1-2週間）
1. JグランツAPIの動作確認
2. シンプルなキーワード検索の実装
3. Azure OpenAIによるクエリ解析のテスト

### Phase 2: MVP（2-4週間）
1. Azure Blob Storageへのデータ保存
2. 日次更新バッチの実装
3. カテゴリ別絞り込み機能
4. 検索結果の要約表示

### Phase 3: 本番導入（4-8週間）
1. Azure Cognitive Searchの導入
2. 会話型検索の実装
3. 適合性スコアリング機能
4. PDFダウンロード機能
5. ユーザーフィードバック機能

---

## 8. コスト試算（月額）

### パターンA: 小規模（職員100名想定）
- Azure Blob Storage: ¥100未満（1GB程度）
- Azure OpenAI: ¥5,000-10,000（月1,000リクエスト）
- **合計**: ¥5,000-10,000/月

### パターンB: 中規模（職員500名想定）
- Azure Blob Storage: ¥100未満
- Azure Cognitive Search: ¥10,000-15,000（Basic tier）
- Azure OpenAI: ¥20,000-30,000（月5,000リクエスト）
- **合計**: ¥30,000-45,000/月

---

## 9. 注意点とリスク

### ⚠️ 確認が必要な項目
1. **利用規約の正式確認**
   - https://www.jgrants-portal.go.jp/open-api にアクセスできれば確認
   - 商用利用・データ保存の可否を明確化

2. **APIレート制限**
   - ドキュメントに明記なし
   - 実装時に確認が必要

3. **データの正確性**
   - APIデータと実際の募集状況に差異がある可能性
   - 最終確認はJグランツの公式サイトを案内

### ✅ リスク対策
- API障害時のフォールバック（キャッシュデータの利用）
- データ更新失敗時のアラート
- ユーザーへの免責事項の明示

---

## 10. まとめと推奨アプローチ

### 推奨実装方針: **ハイブリッド方式**

**理由**:
1. データ量は軽量（一覧のみなら数百KB）→ ストレージコスト低
2. 検索速度重視 → Azure Cognitive Search活用
3. データの鮮度は日次更新で十分
4. Azure OpenAIとの親和性が高い

**実装優先度**:
1. 🔴 高: 一覧データの定期取得・保存
2. 🔴 高: Azure OpenAIによるクエリ解析
3. 🟡 中: Azure Cognitive Searchでの全文検索
4. 🟡 中: 詳細情報・PDFのオンデマンド取得
5. 🟢 低: 会話型インターフェース（Phase 2以降）

**次のアクションアイテム**:
- [ ] デジタル庁へ利用規約の確認（必要に応じて）
- [ ] PoC環境でのAPI接続テスト
- [ ] Azure OpenAIプロンプトの設計
- [ ] データモデルの設計（DB/Blobスキーマ）

---

**作成日**: 2025年12月16日  
**作成者**: Claude (Anthropic)  
**参考URL**: https://developers.digital.go.jp/documents/jgrants/api/
