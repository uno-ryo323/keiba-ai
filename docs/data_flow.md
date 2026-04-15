# データフロー仕様

netKeibaスクレイピング → 前処理 → モデル学習 → 予測・買い目算出 の全体フロー。

---

## 1. 学習データ収集・前処理フロー

新しいレース結果を集めてモデルを学習するまでの手順。

```
[1] race_id 収集
      racelist.py
        ↓ race_id_list_*.csv
[2] レース結果スクレイピング
      racedb.py
        ↓ race_all.csv（追記）
[3] コード情報付与
      preprocess.py: join_netkeiba_target()
        ↓ race_all.csv（更新）
[4] 上がり順位算出
      preprocess.py: calc_agari_rank()
        ↓ race_all.csv（更新）
[5] LabelEncoder 生成
      preprocess.py: make_encode_pickle()
        ↓ src/encode/*.pickle
[6] 前5走データ結合
      preprocess.py: join_pre_race_result()
        ↓ race_jra2.1.csv
[7] エンコード
      preprocess.py: encode_use_LabelEncoder()  ※学習データ用
        ↓ race_jra2.2.csv
[8] 集計列追加
      preprocess.py: make_new_column()
        ↓ race_jra+.csv（最終学習データ）
[9] モデル学習
      keibaai.py: KeibaAI.make_model()
        ↓ Win_new.sav / Quinella_new.sav / Place_new.sav
```

### 各ステップの詳細

| ステップ | スクリプト | クラス/メソッド | 入力 | 出力 | 補足 |
|--------|-----------|--------------|------|------|------|
| 1 | `racelist.py` | `RaceList.fetch()` | netKeibaカレンダーページ | `race_id_list_*.csv` | 年月単位で race_id を一括取得 |
| 2 | `racedb.py` | `raceDB.get_race_result()` | netKeiba レース結果ページ | `race_all.csv`（追記） | JRA レース。Selenium使用（JS描画対応）。取得済み race_id はスキップ |
| 3 | `preprocess.py` | `PreProcess.join_netkeiba_target()` | `race_all.csv` + `race_2010-2021_target.csv` | `race_all.csv`（更新） | class_code, track_code等のJRAコードを付与。2022年以降は対象外（target.csv が 2021年まで） |
| 4 | `preprocess.py` | `PreProcess.calc_agari_rank()` | `race_all.csv` | `race_all.csv`（更新） | 同一レース内で `agari`（上がり3Fタイム）を昇順ランク付けして `agari_rank` 列を生成 |
| 5 | `preprocess.py` | `PreProcess.make_encode_pickle()` | `race_all.csv` | `src/encode/*.pickle` | class, course, jockey 等カテゴリ列の LabelEncoder を生成・保存 |
| 6 | `preprocess.py` | `PreProcess.join_pre_race_result()` | `race_all.csv` | `race_jra2.1.csv` | 各馬の前5走データ（約50列 × 5走）を横結合。153列→325列相当に拡張 |
| 7 | `preprocess.py` | `PreProcess.encode_use_LabelEncoder()` | `race_jra2.1.csv` | `race_jra2.2.csv` | pickle を使ってカテゴリ列を数値に変換 |
| 8 | `preprocess.py` | `PreProcess.make_new_column()` | `race_jra2.2.csv`（※現状は `race_15-21_c2.csv` を参照） | `race_jra+.csv` | `time_index_ave`（タイム指数平均）等の集計列を追加。325列 |
| 9 | `keibaai.py` | `KeibaAI.make_model()` | `race_jra+.csv` | `Win_new.sav` 等 | LightGBM で Win/Quinella/Place の3モデルを学習 |

---

## 2. 予測フロー（レース当日）

対象レースの出馬表を取得して予測・買い目を出力するまでの手順。
`keibaAI_batch.py: keibaAIBatch.forecast()` がオーケストレーションしている。

```
[1] 出馬表取得
      getinfo.py: GetInfo.get_race_card()
        ↓ {race_id}.csv
[2] 前5走の不足レース特定
      preprocess.py: PreProcess.get_diff_race()
        ↓ 不足 race_id リスト
[3] 不足前走データ取得
      racedb.py: raceDB.get_race_result()   ← JRA
      scraping.py: Scraping.get_race_result() ← 地方・海外
        ↓ race_all.csv（追記）
[4] コード情報付与
      preprocess.py: join_netkeiba_target()
        ↓ race_all.csv（更新）
[5] 上がり順位算出
      preprocess.py: calc_agari_rank()
        ↓ race_all.csv（更新）
[6] 前5走データ結合
      preprocess.py: join_pre_race_result()
        ↓ {race_id}_c.csv
[7] エンコード
      preprocess.py: encode_use_LabelEncoder()  ※予測データ用
        ↓ {race_id}_c2.csv
[8] 予測
      keibaai.py: KeibaAI.forecast_race()
        ↓ {race_id}_forecast.csv
[9] 買い目算出
      calcticket.py: CalcTicket.main()
        ↓ ticket.csv
```

### 各ステップの詳細

| ステップ | スクリプト | クラス/メソッド | 入力 | 出力 | 補足 |
|--------|-----------|--------------|------|------|------|
| 1 | `getinfo.py` | `GetInfo.get_race_card()` | netKeiba 出馬表ページ | `{race_id}.csv` | Selenium使用。馬ページも巡回して血統・調教師・馬主・前走 race_id を取得 |
| 2 | `preprocess.py` | `PreProcess.get_diff_race()` | `{race_id}.csv` + `race_all.csv` | 不足 race_id リスト | 前5走のうち `race_all.csv` に未収録の race_id を特定 |
| 3 | `racedb.py` / `scraping.py` | `get_race_result()` | netKeibaレース結果ページ | `race_all.csv`（追記） | JRA は `racedb.py`、地方・海外は `scraping.py` を使い分け |
| 4 | `preprocess.py` | `join_netkeiba_target()` | `race_all.csv` + `target.csv` | `race_all.csv`（更新） | ステップ3で追加した前走データにコード情報を付与 |
| 5 | `preprocess.py` | `calc_agari_rank()` | `race_all.csv` | `race_all.csv`（更新） | ステップ3で追加した前走データの `agari_rank` を算出 |
| 6 | `preprocess.py` | `join_pre_race_result()` | `{race_id}.csv` + `race_all.csv` | `{race_id}_c.csv` | 学習フローの [6] と同じロジック。入力が出馬表である点のみ異なる |
| 7 | `preprocess.py` | `encode_use_LabelEncoder()` | `{race_id}_c.csv` + `src/encode/*.pickle` | `{race_id}_c2.csv` | 学習時と同じ LabelEncoder を使って変換（値の一貫性を保つ） |
| 8 | `keibaai.py` | `KeibaAI.forecast_race(ai_type=2)` | `{race_id}_c2.csv` + `*_new.sav` | `{race_id}_forecast.csv` | Win/Quinella/Place の確率を出力 |
| 9 | `calcticket.py` | `CalcTicket.main()` | `{race_id}_forecast.csv` + オッズCSV各種 | `ticket.csv` | Kelly基準で買い目・購入金額を算出 |

---

## 3. データファイル一覧

| ファイル | 場所 | 生成元 | 内容 |
|--------|------|--------|------|
| `race_id_list_*.csv` | `data/netkeiba/assets/` | `racelist.py` | 年月別 race_id 一覧 |
| `race_all.csv` | `data/netkeiba/result/` | `racedb.py` + `preprocess.py` | 全レース結果の生データ（約80列） |
| `race_2010-2021_target.csv` | `data/target/` | 別途収集済み | JRAコード情報マスター（2021年まで） |
| `*.pickle` | `src/encode/` | `preprocess.make_encode_pickle()` | カテゴリ列の LabelEncoder |
| `race_jra2.1.csv` | `data/netkeiba/result/process/` | `preprocess.join_pre_race_result()` | 前5走結合済み（約325列） |
| `race_jra2.2.csv` | `data/netkeiba/result/process/` | `preprocess.encode_use_LabelEncoder()` | エンコード済み |
| `race_jra+.csv` | `data/netkeiba/result/process/` | `preprocess.make_new_column()` | 集計列追加済み・最終学習データ |
| `Win_new.sav` 等 | `src/model/` | `keibaai.make_model()` | 学習済みモデル |
| `{race_id}.csv` | `data/netkeiba/racecard/{date}/{race_id}/` | `getinfo.get_race_card()` | 出馬表生データ |
| `{race_id}_c.csv` | 同上 | `preprocess.join_pre_race_result()` | 前5走結合済み出馬表 |
| `{race_id}_c2.csv` | 同上 | `preprocess.encode_use_LabelEncoder()` | エンコード済み出馬表（モデル入力） |
| `{race_id}_forecast.csv` | 同上 | `keibaai.forecast_race()` | 予測結果（Win/Quinella/Place 確率） |
| `ticket.csv` | 同上 | `calcticket.main()` | 買い目・購入金額 |

---

## 4. スクリプト別役割早見表

| スクリプト | クラス | 役割 | ネットワーク | 備考 |
|----------|--------|------|------------|------|
| `racelist.py` | `RaceList` | race_id 収集 | requests | カレンダーページをスクレイピング |
| `racedb.py` | `raceDB` | JRAレース結果収集 | Selenium | 馬ページ巡回あり（重い） |
| `scraping.py` | `Scraping` | 地方・海外レース結果収集 | requests | JRAより軽量 |
| `getinfo.py` | `GetInfo` | 出馬表・オッズ収集 | Selenium | レース当日に実行 |
| `preprocess.py` | `PreProcess` | データ前処理全般 | なし | 学習・予測の両方で使用 |
| `encode.py` | `encode` | LabelEncoder 生成・適用 | なし | `preprocess.py` と一部重複 |
| `keibaai.py` | `KeibaAI` | モデル学習・予測 | なし | LightGBM |
| `calcticket.py` | `CalcTicket` | 買い目算出 | なし | Kelly基準 |
| `keibaAI_batch.py` | `keibaAIBatch` | 予測フロー統括 | LINE Notify | forecast() が予測フロー全体を実行 |

---

## 5. 既知の課題・制約

| 課題 | 詳細 |
|------|------|
| `race_2010-2021_target.csv` が 2021 年まで | 2022年以降のレースは `join_netkeiba_target()` でコードを付与できない。7列（class_code, track_code等）が NaN になる |
| `agari_rank_p1~p5` が既存学習データで NaN | 旧 `race_jra+.csv` 生成時に `calc_agari_rank()` が未実行だったため。再収集・再前処理で解消する |
| `make_new_column()` が `race_15-21_c2.csv` を直参照 | ステップ8が特定ファイル名にハードコード依存。汎用化が必要 |
| 学習データと予測データの特徴量ズレ（7列） | 上記コード列が予測時の `_c2.csv` に存在しない。現状は `forecast_race()` 内でゼロ埋め補完 |
