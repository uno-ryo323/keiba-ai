# モデル学習仕様

## 概要

netKeibaから収集したレース結果データを使い、LightGBMで単勝・馬連・複勝の勝率を予測する。

---

## 学習データ

### ファイル

| ファイル | 場所 | 説明 |
|--------|------|------|
| `race_jra+.csv` | `data/netkeiba/result/process/` | 学習に使う最終データ |

### 生成の流れ

```
race_all.csv（スクレイピング結果の生データ）
  ↓ preprocess.join_pre_race_result()
race_jra2.1.csv（基本列 153 列 + 前走 5 走データ結合済み）
  ↓ encode.make_encode_pickle()
  ↓ encode.encode_use_LabelEncoder()
race_jra2.2.csv（LabelEncoder でカテゴリ列をエンコード済み）
  ↓ preprocess.make_new_column()
race_jra+.csv（325 列・特徴量追加済み）
```

### データ量（2015〜2021年データで学習した場合の参考値）

| 項目 | 値 |
|------|------|
| 総行数（フィルタ前） | 約 32.5 万行 |
| フィルタ後 | 約 32.5 万行（大部分が残る） |
| 学習/テスト分割 | 80% / 20%（`random_state=0`） |

### フィルタリング条件

```python
course < 2   # 芝（0）・ダート（1）のみ。障害コース除外
rank >= 1    # 除外・取消馬を除く（rank が NaN になるケースを除去）
```

---

## 特徴量（使用する列）

学習に使う特徴量は **273 列**。`remove_data(data, ai_type=1)` で不要列を除去した後の残り。

### 現レース情報（レースカード段階で判明している値）

| カテゴリ | 列名 |
|--------|------|
| 日程 | `month`, `place`, `kai`, `day2`, `race_num` |
| レース条件 | `class`, `mare_only`, `hande`, `course`, `turn`, `distance`, `weather`, `state`, `headcount` |
| 出走馬情報 | `lane_gate`, `horse_gate`, `sex`, `old`, `handiy`, `weight`, `zougen`, `kanri` |
| 関係者 | `jockey`, `trainer`, `banusi`, `breeder` |
| 血統 | `father`, `father_father`, `father_mother`, `mother`, `mother_father`, `mother_mother` |

### 前走データ（`_p1`〜`_p5` サフィックス）

1 走前〜5 走前について、以下の列が各 5 本存在する（計 22 種 × 5 = 110 列）。

| 列名（ベース） | 説明 |
|------------|------|
| `rank` | 着順 |
| `odds` | 単勝オッズ |
| `popular_rank` | 人気順位 |
| `class` | クラス |
| `distance` | 距離 |
| `place` | 開催場 |
| `headcount` | 出走頭数 |
| `jockey` | 騎手 |
| `handiy` | ハンデ重量 |
| `weight` | 馬体重 |
| `zougen` | 馬体重増減 |
| `agari` | 上がり 3F タイム |
| `horse_gate` | 馬番 |
| `lane_gate` | 枠番 |
| `month` | 開催月 |
| `day` | 開催日 |
| `turn` | 回り |
| `weather` | 天気 |
| `state` | 馬場状態 |
| `time_index` | タイム指数 |
| `course` | コース種別 |
| `race_name` | レース名 |

---

## 除外列と理由

### 1. 識別子・文字列（予測に使えない）

| 除外列 | 理由 |
|--------|------|
| `race_id`, `horse_id` | ID 列、過学習の原因になる |
| `horse_name` | 文字列、モデルが扱えない |
| `race_name`, `race_name_p1-5` | 文字列 |
| `pre_race1`〜`pre_race5` | 前走 race_id（文字列） |
| `year`, `day` | 時系列情報（過学習リスク） |
| `odds`, `popular_rank` | レース直前の情報（本番予測時には使えない可能性）|

### 2. 現レース結果列（データリーク防止）

予測時点では確定していない値。これらをモデルに含めると**データリーク**になる。

| 除外列 | 説明 |
|--------|------|
| `rank` | 着順（ターゲット変数の源泉） |
| `time` | 走破タイム |
| `time_index` | タイム指数 |
| `agari` | 上がり 3F |
| `agari_rank` | 上がり 3F 順位 |
| `corner_position1-4` | コーナー通過順位 |
| `remarks` | 備考（失格・降着等） |
| `time_diff` | タイム差 |
| `horse_type` | 馬区分（去勢等、レース後確定） |

### 3. 前走結果由来の指数（データリーク防止）

`_p1`〜`_p5` サフィックス付きで 5 本ずつ存在。これらも結果が確定した後に算出される値のため除外。

| 除外列（ベース） | 説明 |
|------------|------|
| `rank_offical` | 公式着順（降着等込み） |
| `rank_arrival` | 到達着順 |
| `abnormal_code` | 異常区分コード |
| `rpci` | RPCI 指数 |
| `pci`, `pci3` | PCI 指数 |
| `minus_3f` | マイナス 3F |
| `ave_3f` | 平均 3F |
| `agari_rank` | 上がり 3F 順位 |

> **背景:** 当初これらを除外せずに学習したところ `rank` の重要度が 100%、`rank_offical` が 61% になりデータリークが判明。除外後は `odds_p1`（前走オッズ）が最重要特徴量になった。

### 4. 文字列型列（LightGBM が扱えない）

pandas で `object` 型になる列は学習前に自動除外される。

| 除外列 | 説明 |
|--------|------|
| `grade_code` | グレードコード |
| `course_class` | コースクラス |
| `race_symbol_code` | レース記号コード |
| `blinkers` | ブリンカー有無 |
| `father_type`, `mother_father_type` | 血統タイプ |

### 5. ターゲット変数の競合

学習時、各モデルの**ターゲット以外**のターゲット列は除外する。

| モデル | ターゲット（Y） | 除外するターゲット |
|--------|--------------|----------------|
| Win | `rank_Win` | `rank_Quinella`, `rank_Place` |
| Quinella | `rank_Quinella` | `rank_Win` は X から drop、`rank_Place` は除外 |
| Place | `rank_Place` | `rank_Win` は X から drop、`rank_Quinella` は除外 |

---

## ターゲット変数の定義

| 変数 | 意味 | 値 |
|------|------|------|
| `rank_Win` | 単勝対象か | 1 位 → 1, それ以外 → 0 |
| `rank_Quinella` | 馬連対象か | 1〜2 位 → 1, それ以外 → 0 |
| `rank_Place` | 複勝対象か | 1〜3 位 → 1, それ以外 → 0（頭数によって変動）|

---

## アルゴリズム

### LightGBM（Gradient Boosted Decision Trees）

- 決定木を弱学習器として勾配ブースティングで反復学習する
- 大規模データ・カテゴリ変数に強い
- `objective: binary` で二値分類（勝つ / 勝たない）として解く

### ハイパーパラメータ

```python
{
    "objective": "binary",
    "metric": "binary_logloss",
    "boosting_type": "gbdt",
    "num_iterations": 100000,
    "early_stopping_round": 100,
}
```

- `num_iterations: 100000` だが `early_stopping_round: 100` で検証スコアが 100 ラウンド改善しなければ自動停止
- 分割は `train_test_split(test_size=0.2, shuffle=True, random_state=0)`

---

## 生成モデル

| ファイル名 | 予測対象 | 保存先 | 備考 |
|----------|--------|--------|------|
| `Win_new.sav` | 単勝（1 位確率） | `src/model/` | make_model() で生成 |
| `Quinella_new.sav` | 馬連（1〜2 位確率） | `src/model/` | make_model() で生成 |
| `Place_new.sav` | 複勝（1〜3 位確率） | `src/model/` | make_model() で生成 |
| `Win_3.sav` | 単勝（旧） | `src/model/` | 旧パイプラインで学習 |
| `Quinella_3.sav` | 馬連（旧） | `src/model/` | 旧パイプラインで学習 |
| `Place_3.sav` | 複勝（旧） | `src/model/` | 旧パイプラインで学習 |

`forecast_race(ai_type)` の `ai_type` でロードするモデルを切り替える：
- `ai_type=2` → `_new.sav`（新モデル）
- `ai_type=1`（または文字列）→ `_3.sav`（旧モデル）
- `ai_type=0` → `_model2.sav`（最旧モデル）

---

## 学習結果（参考値）

2015〜2021 年データ（`race_15-21_c2.csv` → `race_jra+.csv`）で学習した場合。

| モデル | 停止イテレーション | Train loss | Test loss |
|--------|--------------|-----------|-----------|
| Win | 237 | 0.1849 | 0.2197 |
| Quinella | 388 | 0.2921 | 0.3421 |
| Place | 389 | 0.3826 | 0.4285 |

### 特徴量重要度トップ 5（Win モデル）

| 順位 | 特徴量 | 重要度 |
|------|--------|--------|
| 1 | `odds_p1`（前走オッズ） | 22.0% |
| 2 | `rank_p1`（前走着順） | 5.0% |
| 3 | `rank_arrival_p1`（前走到達着順） | 3.5% |
| 4 | `jockey`（騎手） | 2.8% |
| 5 | `odds_p2`（2 走前オッズ） | 2.4% |

---

## 既知の課題

1. **レースカードデータとの列ズレ**
   学習データ（`race_jra+.csv`）には `class_code`, `track_code`, `track_code2`, `corner_count`, `race_prize`, `race_type_code`, `weight_type_code` の 7 列が存在するが、予測用レースカード（`_c2.csv`）には含まれていない。
   現状は `forecast_race()` 内でこれらをゼロ埋めして対応している。将来的にはレースカード生成パイプラインに追加が望ましい。

2. **race_jra2.1.csv の更新手順が未整備**
   新データ（2022 年以降）を学習に組み込む手順が未確立。`preprocess.join_pre_race_result()` を使って `race_all.csv` から `race_jra2.1.csv` を生成する方法が必要。
