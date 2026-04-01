# KeibaAI

netKeiba.com からデータをスクレイピングし、LightGBM で単勝・馬連・複勝を予測、Kelly 基準で買い目を算出する競馬予想 AI。

過去に作ったコードを整理・再利用可能な形に持っていくリポジトリ。

---

## 処理フロー

```
[1] レースカード取得    getinfo.py + Selenium  → {race_id}.csv
[2] 前5走データ補完    racedb.py / scraping.py → race_all.csv
[3] データ統合・前処理  preprocess.py          → {race_id}_c.csv
[4] エンコーディング    preprocess.py          → {race_id}_c2.csv
[5] LightGBM 予測     keibaai.py             → {race_id}_forecast.csv
[6] 買い目計算         calcticket.py          → ticket.csv
```

---

## ディレクトリ構成

```
KeibaAI/
├── src/
│   ├── config.py          # パス・URL・定数の一元管理
│   ├── driver.py          # メイン処理フロー
│   ├── keibaAI_batch.py   # バッチ処理・LINE 通知
│   ├── keiba_ai_tool.py   # GUI ツール（Tkinter）
│   ├── scraping/
│   │   ├── getinfo.py     # Selenium でレースカード・オッズ取得
│   │   ├── racedb.py      # netKeiba からレース結果 DB 取得
│   │   └── scraping.py    # HTML 解析でレース情報抽出
│   ├── pipeline/
│   │   ├── preprocess.py  # データ結合・前処理・エンコード
│   │   ├── encode.py      # LabelEncoder pickle 生成・適用
│   │   └── keibaai.py     # LightGBM 学習・予測
│   ├── betting/
│   │   ├── calcticket.py  # EV 計算・買い目算出（Kelly 基準）
│   │   ├── judgeticket.py # 的中判定・収支計算
│   │   └── purchaseticket.py  # 自動投票（iPAT 連携・未完成）
│   ├── model/             # 学習済みモデル（.gitignore）
│   ├── encode/            # LabelEncoder pickle（.gitignore）
│   └── batch/             # バッチ実行スクリプト（.bat）
├── data/                  # データ一式（.gitignore）
│   ├── netkeiba/
│   │   ├── assets/        # column.csv・encode_list.csv 等
│   │   ├── racecard/      # 日付/レース ID ごとの出馬表・オッズ
│   │   ├── racelist/      # 開催日ごとのレース一覧
│   │   └── result/        # 累積レース結果（race_all.csv 等）
│   └── target/            # 目的変数データ
├── tests/
│   ├── test_e2e.py        # E2E 通し実行（全ステップ）
│   ├── test_steps.py      # ステップ別デバッグ実行
│   ├── test_misc.py       # ネットワーク・Selenium 不要の単体確認
│   ├── test_network.py    # HTTP 接続が必要な確認
│   └── test_selenium.py   # Chrome が必要な確認
├── tools/                 # 作業用スクリプト
├── .env                   # 認証情報（.gitignore）
├── requirements.txt
└── PROGRESS.md            # 作業ログ
```

---

## セットアップ

### 前提条件

- Python 3.13+
- Google Chrome（Selenium 用。ChromeDriver は webdriver-manager が自動管理）

### インストール

```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 認証情報の設定

`.env` をプロジェクトルートに作成する（`.gitignore` 済み）。

```
NETKEIBA_USER=your_netkeiba_id
NETKEIBA_PASSWORD=your_netkeiba_password
```

---

## 使い方

### E2E 実行（ステップ 2〜6）

```bash
python tests/test_e2e.py
```

ステップ 1（レースカード取得）は Selenium が必要なため、既存の CSV がある場合はスキップして 2 以降から動かせる。

### ステップ別実行

```python
from src.scraping import racedb, scraping
from src.pipeline import preprocess, keibaai
from src.betting import calcticket

DATE = "20210105"
RACE_ID = "202106010101"

# Step 2: 前5走データ補完
racedb.raceDB.get_race_result([...])
scraping.Scraping.get_race_result([...])

# Step 3-4: 前処理・エンコード
pp = preprocess.PreProcess(DATE, RACE_ID)
pp.join_pre_race_result()
pp.encode_use_LabelEncoder()

# Step 5: 予測
ai = keibaai.KeibaAI(DATE, RACE_ID)
ai.forecast_race("Win")

# Step 6: 買い目算出
calcticket.CalcTicket(DATE, RACE_ID).main()
```

### Step 1 込みのフル実行（Selenium 必要）

```python
from src.keibaAI_batch import keibaAIBatch
keibaAIBatch.forecast("202106010101")
```

---

## テスト

```bash
python tests/test_misc.py      # ネットワーク不要 5/5
python tests/test_network.py   # HTTP 接続必要 3/3
python tests/test_selenium.py  # Chrome 必要  4/5 + 1 SKIP
python tests/test_e2e.py       # E2E 24/24
```

---

## 設定変更

パス・URL・モデルバージョン等はすべて `src/config.py` で管理している。
ディレクトリを移動する場合は `BASE_DIR` だけ変更すればよい。

```python
# src/config.py
BASE_DIR = Path("C:/KeibaAI")   # ← ここだけ変える
```

---

## 注意事項

- `purchaseticket.py` の自動投票機能は未完成。実行しても購入は行われない。
- `judgeticket.py` の `get_result()` は既知バグあり（`self.file_result` 未初期化）。
- 学習済みモデルは scikit-learn 0.23.1 形式のため、現行バージョンで読み込むと `InconsistentVersionWarning` が出る。再学習するまでは無視してよい。
- netKeiba のページ構造変更により `get_race_card()` が失敗することがある（過去レース ID でのテスト時に確認済み）。
