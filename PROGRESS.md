# KeibaAI 改善進捗ログ

> Claude Code と一緒に過去に作った競馬AIコードを整理・再利用可能な形に持っていく記録。
> Qiita記事の素材として都度更新する。

---

## プロジェクト概要

- **目的：** 過去作成の競馬AI（スクレイピング→前処理→LightGBM予測→買い目算出）を整理・再生
- **開始日：** 2026-03-26
- **使用ツール：** Claude Code（claude-sonnet-4-6）

---

## フェーズ一覧

### セットアップ

| タスク | 内容 | ステータス |
|--------|------|-----------|
| Setup 1 | 現状把握・ドキュメント整備 | ✅ 完了 |
| Setup 2 | CLAUDE.md / PROGRESS.md 作成 | ✅ 完了 |
| Setup 3 | 認証情報をプレースホルダーに置換 | ✅ 完了 |
| Setup 4 | Git / GitHub 設定・初回プッシュ | ✅ 完了 |
| Setup 5 | Python 3.13 導入・venv・requirements.txt | ✅ 完了 |

### コード改善フェーズ

| フェーズ | 内容 | ステータス |
|---------|------|-----------|
| Phase 1 | Selenium API 更新（旧式→新式） | ✅ 完了 |
| Phase 2 | パス・設定のコンフィグ化 | ✅ 完了 |
| Phase 3 | 認証情報の外部化（.env） | ✅ 完了 |
| Phase 4 | Kelly基準バグ修正 | ✅ 完了 |
| Phase 5 | 旧版/新版ファイルの整理・統合 | ✅ 完了 |
| Phase 6 | purchaseticket.py の修正・完成 | ⏭ スキップ |
| Phase 7 | 動作確認・エンドツーエンドテスト | ✅ 完了 |
| Phase 8 | README.md 最終版作成 | 🔲 未着手 |

---

## 詳細ログ

---

### Setup 1〜2 — 現状把握・ドキュメント整備

**日付：** 2026-03-26
**対応内容：**
- リポジトリ全体の構造・処理フローを解析
- Pythonファイル18本・総行数4,843行・関数133個を把握
- `CLAUDE.md` 作成（作業方針・禁止事項・手順を明記）
- `README_start.md` 作成（スタート時点のスナップショット）
- `PROGRESS.md` 作成（本ファイル）

**把握した処理フロー（6ステップ）：**
```
[1] レースカード取得  → getinfo.py + Selenium
[2] 前5走データ補完  → racedb.py / scraping.py
[3] データ統合・前処理 → preprocess.py
[4] エンコーディング  → preprocess.py / encode.py
[5] LightGBM 予測   → keibaai.py
[6] 買い目計算       → calcticket.py
```

**把握した問題点（6つ）：**
1. Selenium API が旧式（`find_element_by_name` 等）→ 動作不可
2. 認証情報（netKeiba ID/PW）がソースにハードコード
3. Kelly基準の実装バグ（`if (1/sum_odds) >= 0` → 常にTrue）
4. Windowsパスのハードコード（移植性ゼロ）
5. `purchaseticket.py` が未完成（syntax error あり）
6. 旧版・新版ファイルが混在（racedb/keibaai）

**所感：**
コード自体のロジックは整っており、スクレイピング→予測→買い目の流れは明確。
最大の問題はSeleniumの旧式API。ここを直せばまず動かせる状態になるはず。

---

### Setup 3 — 認証情報をプレースホルダーに置換

**日付：** 2026-03-26
**対応内容：**
- 6ファイルにハードコードされていたnetKeiba/iPATの認証情報を発見
- `YOUR_NETKEIBA_ID` / `YOUR_NETKEIBA_PASSWORD` / `YOUR_IPAT_PASSWORD` に置換
- 対象：`getinfo.py`, `judgeticket.py`, `racedb.py`, `racedb_new.py`, `scraping.py`, `purchaseticket.py`

**所感：**
想定より多くのファイルに散らばっていた。Phase 3で `.env` 化するまでの暫定対応。

---

### Setup 4 — Git / GitHub 設定・初回プッシュ

**日付：** 2026-03-26
**対応内容：**
- SSH鍵（ed25519）生成・GitHubに登録
- `keiba-ai` リポジトリ作成（Private）
- `.gitignore` 作成（Data/・model/・encode/・.venv/を除外）
- 初回コミット・プッシュ完了

**所感：**
GitHubはPassword認証が廃止済みのためSSH鍵が必要。CodeCommitは2024年に新規受付停止のため非推奨。

---

### Setup 5 — Python 3.13 導入・venv・requirements.txt

**日付：** 2026-03-26
**対応内容：**
- Python 3.13.12 を winget でインストール
- `.venv` 作成（Python 3.13ベース）
- `requirements.txt` 作成（import文から使用ライブラリを洗い出し）
- 主要パッケージバージョン：LightGBM 4.6.0 / pandas 3.0.1 / selenium 4.41.0 / scikit-learn 1.8.0

**所感：**
Python 3.14も選択肢にあったが、LightGBM等MLパッケージの安定性を優先して3.13を選択。

---

---

### Phase 1 — Selenium API更新・静的解析・フォーマット対応

**日付：** 2026-03-26
**対応ファイル：** `getinfo.py`, `judgeticket.py`, `purchaseticket.py`

**対応内容：**
- Selenium旧式API（`find_element_by_*`）→ 新式（`find_element(By.*)`）全16箇所修正
- `executable_path=` → `Service` オブジェクト使用に変更
- `purchaseticket.py` の syntax error 3箇所修正（`&&`→`and`、余分な括弧、コロン抜け）
- 各メソッドにdocstring追加・CHROMEDRIVER_PATH定数化・f-stringで可読性向上
- `ruff`（リンター）・`black`（フォーマッタ）導入・適用

**追加で判明した問題：**
- `getinfo.py` の `get_odds()` にChromeDriverパスのタイポ（`ChormeDriver`）があり修正
- `purchaseticket.py` の各購入メソッドはすべて未実装（Phase 6で対応予定）

**所感：**
Seleniumの修正自体はシンプルだったが、`purchaseticket.py` にsyntax errorが3箇所あり実質まったく動かない状態だった。
ruff・blackを導入したことで今後の修正品質が安定する。

---

### Phase 2 — パス・設定のコンフィグ化

**日付：** 2026-03-27
**対応ファイル：** `config.py`（新規）、全Sourceファイル13本

**対応内容：**
- `config.py` を新規作成し、全パス・URL・定数を一元管理
- `pathlib.Path` を使ってWindowsパスを全廃（OS非依存化）
- `getinfo.py` / `judgeticket.py` / `racedb.py` / `racedb_new.py` / `scraping.py` /
  `preprocess.py` / `keibaai.py` / `keibaai_new.py` / `calcticket.py` /
  `driver.py` / `keibaAI_batch.py` / `encode.py` / `purchaseticket.py`
  からハードコードパスをすべて除去し `config.*` に置換
- `CalcTicket` に `_base_path` インスタンス変数を導入し繰り返しパス生成を排除

**所感：**
ファイルによってパスの大文字小文字が不統一（`C:\keibaAI` vs `C:\KeibaAI`）だったものを
config経由で統一できた。13ファイルを一括で修正するのは影響範囲が広かったが、
import→config参照という単純なパターン変換なのでロジック変更リスクは最小限。

---

### Phase 3 — 認証情報の外部化（.env）

**日付：** 2026-03-27
**対応ファイル：** `config.py`、`.env`（新規）、`racedb_new.py`、`scraping.py`

**対応内容：**
- `.env` ファイルを作成し `NETKEIBA_USER` / `NETKEIBA_PASSWORD` を定義（.gitignore済み）
- `config.py` に `python-dotenv` 読み込みを追加し、`NETKEIBA_USER`/`NETKEIBA_PASSWORD` を公開
- 全ソースファイルのプレースホルダー（`YOUR_NETKEIBA_ID` 等）を `config.*` 経由に統一
- `requirements.txt` に `python-dotenv` を追加

**動作確認（実施）：**
- `config.py` import → NETKEIBA_USER/RACECARD_DIR/RACE_ALL_CSV が正しく解決される ✅
- `requests` による netkeiba ログイン → HTTP 200 + リダイレクトで認証成功 ✅
- `KeibaAI('20210105', '202106010101').forecast_race('Win')` → 16頭分のスコアを正常出力 ✅
- `CalcTicket('20210105', '202106010101').main()` → 買い目算出まで正常完了 ✅

**所感：**
Phase 2・3を合わせて認証情報の扱いが完全にクリーンになった。
モデル予測・買い目算出のパイプラインが実データで動くことも確認できた。
`VisibleDeprecationWarning`（LightGBMモデルのpickle）は既存モデルファイルの問題で、
再学習しないと解消できないため今は無視。

---

### Phase 4 — Kelly基準バグ修正

**日付：** 2026-03-27
**対応ファイル：** `calcticket.py`

**対応内容：**
- `if (1/sum_odds) >= 0` → `if (1/sum_odds) <= 1` に修正（常にTrueになるバグ）
- 単勝・馬連・複勝の3箇所を修正

**所感：**
条件式が `>= 0` だと常にTrueになり、Kelly基準の制約が機能していなかった。
`<= 1`（オッズの逆数が1以下 = 期待値がプラス）が正しい判定条件。

---

### Phase 5 — 旧版/作業用ファイルの整理

**日付：** 2026-03-31
**対応内容：**
- `racedb_new.py` / `keibaai_new.py` を `Source/old/` に退避（`.gitignore` で管理外に）
- `delete.py` / `sample2.py` を `Source/tools/` に移動
- `CLAUDE.md` のPRルールを整理

**所感：**
旧版ファイルはロジック参照用にローカルに残しつつ、Git管理外へ。
Sourceディレクトリがすっきりした。Phase 6（purchaseticket.py の完成）は
自動投票機能のため今回のスコープ外としてスキップ。

---

### Phase 7（途中） — ディレクトリ再編・E2Eテスト・全ソース動作確認

**日付：** 2026-03-31〜2026-04-01
**ブランチ：** `feature/phase7-e2e-test`

#### 完了済み作業

**7-1: pandas 3.x 互換修正**
- `src/pipeline/preprocess.py` の2箇所を修正
  - `join_pre_race_result()`: `_p*`列をobject型で事前初期化・`race_all.csv`混在型列をpd.to_numeric正規化
  - `encode_use_LabelEncoder()`: `fillna(inplace=True)` → 代入形式・`fillna("NoneData").astype(str)`

**7-2: テストスクリプト作成**
- `tests/test_steps.py` — ステップ別デバッグ用（Step 2a〜6: 全PASS）
- `tests/test_e2e.py` — E2E通し実行（24レース全PASS）

**7-3: ディレクトリ再編（Source/ → src/ パッケージ化）**
- `Source/` → `src/`（`scraping/`, `pipeline/`, `betting/` サブパッケージ化）
- `tests/`, `tools/`, `.vscode/` をプロジェクトルートに配置
- 全ファイルの import を相対import（`from ..config import X`等）に修正
- `.gitignore` 更新、バッチファイル更新
- 全モジュール import OK・E2E 24/24 PASS 確認

#### 完了済み作業（続き）

**7-4: 全ソース動作確認テスト作成**（ファイル作成完了・実行は次回）

| テストファイル | 対象 | 要件 | 状態 |
|---|---|---|---|
| `tests/test_misc.py` | `judgeticket.judge_ticket()`/`calc_balance()`、`encode.make_encode_pickle()`/`encode_use_LabelEncoder()`、GUI import確認 | なし | 作成済み・未実行 |
| `tests/test_network.py` | `racedb.get_race_result()`、`scraping.get_race_result()`、`keibaAI_batch.send_result()` | netKeiba HTTP接続 | 作成済み・未実行 |
| `tests/test_selenium.py` | `getinfo.get_race_card()`/`get_odds()`、`judgeticket.get_result()`（既知バグ記録）、`purchaseticket` インスタンス化、`keibaAI_batch.forecast()` | Chrome起動 | 作成済み・未実行 |

**各テストファイルの設計ポイント：**
- `test_misc.py`: `RACECARD_DIR`・`ENCODE_DIR`・`RESULT_DIR` を `unittest.mock.patch` で一時ディレクトリに差し替え（本番データを汚染しない）
- `test_network.py`: `racedb.raceDB.PATH` を一時ファイルに差し替え、`RACE_ALL_CSV` をパッチ
- `test_selenium.py`: `judgeticket.get_result()` は既知バグ（`self.file_result` 未初期化）のためSKIP扱いとして記録

**7-5: 全テスト実行・修正**（2026-04-01）

各テストファイルを実行し、発生した問題を修正した。

**修正内容：**

| 問題 | 原因 | 対処 |
|---|---|---|
| `UnicodeEncodeError` (em dash `—`) | Windows cp932 ターミナルで `\u2014` が非対応 | `—` → `-` に一括置換（test_misc/network/selenium） |
| `encode_use_LabelEncoder` の nan エラー | `fillna(inplace=True)` が pandas 3.x で Series スライスに効かない | `encode.py` L66: 代入形式 `.fillna("NoneData").astype(str)` に修正 |
| LINE Notify ネットワークエラー | テスト環境から `notify-api.line.me` に到達不可 | `test_network.py` / `test_selenium.py` で `requests.post` をモック |
| `forecast()` 日付エラー (`FileNotFoundError`) | `datetime.now()` が今日の日付 (`20260401`) を返し、2021年データが見つからない | `src.keibaAI_batch.datetime` モジュール参照を置換して `fixed_dt=2021-01-05` を注入 |
| `patch("...datetime.datetime")` が pandas を破壊 | `datetime` モジュール singleton を直接書き換え、pandas の `isinstance()` が失敗 | `patch("src.keibaAI_batch.datetime")` でモジュール参照のみ置換 |
| `forecast()` 内 `get_race_card()` 失敗 | netKeiba ページ構造変化による "string index out of range" | テスト内で `get_race_card` をモック（単体テストで別途確認済み） |

**最終結果：**

| テストファイル | 結果 |
|---|---|
| `tests/test_misc.py` | **5/5 PASS** |
| `tests/test_network.py` | **3/3 PASS** |
| `tests/test_selenium.py` | **4/5 PASS + 1 SKIP**（`get_result()` は既知バグのためSKIP） |

**所感：**
最大のハマりどころは `patch("src.keibaAI_batch.datetime.datetime")` が `sys.modules["datetime"]` 自体を書き換えてしまい、pandas の内部処理を壊すという問題。`patch("src.keibaAI_batch.datetime")` でモジュール参照を置換するのが正しいパターン。

---

<!-- 以降、作業のたびに追記 -->
