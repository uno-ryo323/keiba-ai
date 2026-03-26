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
| Phase 2 | パス・設定のコンフィグ化 | 🔲 未着手 |
| Phase 3 | 認証情報の外部化（.env） | 🔲 未着手 |
| Phase 4 | Kelly基準バグ修正 | 🔲 未着手 |
| Phase 5 | 旧版/新版ファイルの整理・統合 | 🔲 未着手 |
| Phase 6 | purchaseticket.py の修正・完成 | 🔲 未着手 |
| Phase 7 | 動作確認・エンドツーエンドテスト | 🔲 未着手 |
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

<!-- 以降、作業のたびに追記 -->
