# KeibaAI — スタート時点スナップショット

> このREADMEは整理作業開始時点（2026-03-26）のコードベース現状を記録したものです。
> 改善完了後の `README.md` と比較するために保存しています。

---

## 概要

netKeiba.com から競馬データをWebスクレイピングで取得し、過去の出走履歴をLightGBMで学習。
単勝・馬連・複勝の的中確率を予測し、期待値ベースで買い目を算出する競馬予想AIシステム。

---

## コードベース規模（スタート時点）

| 項目 | 数 |
|------|-----|
| Pythonファイル数 | 18本 |
| 総行数 | 4,843行 |
| 総関数・メソッド数 | 133個 |
| 処理ステップ数 | 6ステップ |
| 学習済みモデル（.sav） | 現用3本（Win/Quinella/Place v3）＋旧バージョン複数 |
| LabelEncoder（.pickle） | 約30種 |
| 既知の問題 | 6件 |
| 未完成ファイル | 1本（purchaseticket.py） |

### ファイル別行数

| ファイル | 行数 | 役割 |
|---------|------|------|
| preprocess.py | 880 | データ結合・前処理・エンコード |
| racedb_new.py | 687 | レース結果DB取得（新版） |
| getinfo.py | 638 | Seleniumでレースカード取得 |
| calcticket.py | 348 | 買い目計算 |
| scraping.py | 326 | HTML解析・レース情報抽出 |
| keibaai.py | 284 | LightGBMモデル学習・予測 |
| keibaai_new.py | 227 | 新版予測モデル |
| judgeticket.py | 184 | 的中判定 |
| racedb.py | 402 | レース結果DB取得（旧版） |
| driver.py | 151 | メイン処理フロー |
| mycalender.py | 163 | カレンダーUI |
| keibaAI_batch.py | 139 | バッチ処理・LINE通知 |
| keiba_ai_tool.py | 135 | GUIツール（Tkinter） |
| purchaseticket.py | 123 | 自動投票（未完成） |
| encode.py | 88 | LabelEncoding |
| delete.py | 31 | データ削除 |
| sample2.py | 24 | サンプル検証 |
| getresult.py | 13 | 結果取得 |

---

## ディレクトリ構成

```
KeibaAI/
├── CLAUDE.md                          # Claude Code 作業方針
├── Common/
│   └── chromedriver.exe               # Selenium用Chromeドライバ
├── Data/
│   └── netKeiba/
│       ├── common/                    # 共通データ
│       │   ├── column.csv             # カラム定義
│       │   ├── encode_list.csv        # エンコード対応表
│       │   ├── feature_importance.csv # 特徴量重要度
│       │   ├── race_id_list_2010-2021.csv
│       │   └── race_id_list_2021_2.csv
│       ├── result/                    # 累積レース結果（race_all.csv等）
│       ├── racelist/                  # レース一覧
│       └── racecard/                  # 日付/レースIDごとのCSV群
└── Source/
    ├── scraping.py                    # HTML解析・レース情報抽出
    ├── racedb.py                      # レース結果DB取得（旧版）
    ├── racedb_new.py                  # レース結果DB取得（新版）
    ├── getinfo.py                     # Selenium/BSでレースカード取得
    ├── getresult.py                   # 結果取得スクリプト
    ├── preprocess.py                  # データ結合・前処理・エンコード
    ├── encode.py                      # LabelEncoding
    ├── keibaai.py                     # LightGBMモデル学習・予測
    ├── keibaai_new.py                 # 新版予測モデル
    ├── calcticket.py                  # 買い目計算
    ├── judgeticket.py                 # 的中判定
    ├── purchaseticket.py              # 自動投票（未完成）
    ├── driver.py                      # メイン処理フロー
    ├── keibaAI_batch.py               # バッチ処理・LINE通知
    ├── keiba_ai_tool.py               # GUIツール（Tkinter）
    ├── mycalender.py                  # カレンダーUI
    ├── sample2.py                     # サンプル検証
    ├── delete.py                      # データ削除
    ├── model/                         # 学習済みLightGBMモデル（.sav）
    │   ├── Win_3.sav
    │   ├── Quinella_3.sav
    │   └── Place_3.sav（他複数バージョン）
    ├── encode/                        # LabelEncoderのpickleファイル（約30種）
    └── Batch/                         # バッチスクリプト
```

---

## 処理フロー

```
[1] レースカード取得
    getinfo.py + Selenium → {race_id}.csv

[2] 前5走データ補完
    racedb.py / scraping.py → race_all.csv に蓄積

[3] データ統合・前処理
    preprocess.py → {race_id}_c.csv

[4] エンコーディング
    preprocess.py / encode.py → {race_id}_c2.csv

[5] LightGBM 予測
    keibaai.py → {race_id}_forecast.csv
    （Win / 馬連 / 複勝 の確率）

[6] 買い目計算
    calcticket.py → ticket.csv
    （EV >= 1.0 の券種・金額）
```

---

## 使用ライブラリ

| ライブラリ | 用途 |
|----------|------|
| pandas | データフレーム操作 |
| numpy | 数値計算 |
| scikit-learn | LabelEncoder |
| lightgbm | 予測モデル |
| selenium | ブラウザ自動操作 |
| beautifulsoup4 | HTML解析 |
| requests | HTTP通信 |
| matplotlib | 特徴量重要度グラフ |
| tkinter | GUI（Python標準） |

---

## 実行方法（現状）

### GUI起動
```bash
cd Source
python keiba_ai_tool.py
```

### バッチ実行
```bash
cd Source
python keibaAI_batch.py
```

### 個別予測（driver.py）
```python
from driver import forecast
forecast(date="20261201", race_id="2026120101010101", type_ai=1, flag=True)
```

---

## 既知の問題（スタート時点）

以下はすべて未修正の状態。改善後の `README.md` と比較すること。

### 1. Selenium API が旧式（動作不可）
`find_element_by_name()` など廃止済みAPIを全ファイルで使用。
`find_element(By.NAME, ...)` 形式への更新が必要。

**影響ファイル：** `getinfo.py`, `judgeticket.py`, `purchaseticket.py`

### 2. 認証情報のハードコード
netKeibaのログインID・パスワードがソースコードに直書きされている。

**影響ファイル：** `getinfo.py`, `keibaAI_batch.py`

### 3. Kelly基準のバグ
```python
# 現状（常にTrueで意味なし）
if (1/sum_odds) >= 0:
```
本来は期待値 >= 1.0 の判定であるべき。

**影響ファイル：** `calcticket.py`

### 4. Windowsパスのハードコード
```python
base_path = "C:\\keibaAI\\Data\\"
```
環境依存で移植性がない。

**影響ファイル：** 複数ファイル

### 5. `purchaseticket.py` が未完成
syntax error を含む未実装状態。

### 6. 旧版・新版ファイルが混在
`racedb.py` と `racedb_new.py`、`keibaai.py` と `keibaai_new.py` など、
どちらを使うべきか不明瞭。

---

## データについて

- `race_all.csv`：過去レースの累積結果（主要訓練データ）
- `race_id_list_2010-2021.csv`：2010〜2021年の全レースID
- `feature_importance.csv`：学習済みモデルの特徴量重要度
- モデルはv1〜v3まで複数バージョンが混在、現用はv3（`*_3.sav`）

---

*このファイルはスタート時点の記録として変更しないこと*
