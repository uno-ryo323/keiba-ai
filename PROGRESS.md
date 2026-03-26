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

| フェーズ | 内容 | ステータス |
|---------|------|-----------|
| Phase 0 | 現状把握・ドキュメント整備 | ✅ 完了 |
| Phase 1 | Selenium API 更新（旧式→新式） | 🔲 未着手 |
| Phase 2 | パス・設定のコンフィグ化 | 🔲 未着手 |
| Phase 3 | 認証情報の外部化（.env等） | 🔲 未着手 |
| Phase 4 | Kelly基準バグ修正 | 🔲 未着手 |
| Phase 5 | 旧版/新版ファイルの整理・統合 | 🔲 未着手 |
| Phase 6 | purchaseticket.py の修正・完成 | 🔲 未着手 |
| Phase 7 | 動作確認・エンドツーエンドテスト | 🔲 未着手 |
| Phase 8 | README.md 最終版作成 | 🔲 未着手 |

---

## 詳細ログ

---

### Phase 0 — 現状把握・ドキュメント整備

**日付：** 2026-03-26
**対応内容：**
- リポジトリ全体の構造・処理フローを解析
- Pythonファイル15本、モデル(.sav)・エンコーダ(.pickle)・データ(CSV)の全体像を把握
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

**把握した問題点（5つ）：**
1. Selenium API が旧式（`find_element_by_name` 等）→ 動作不可
2. 認証情報（netKeiba ID/PW）がソースにハードコード
3. Kelly基準の実装バグ（`if (1/sum_odds) >= 0` → 常にTrue）
4. Windowsパスのハードコード（移植性ゼロ）
5. `purchaseticket.py` が未完成（syntax error あり）

**所感：**
コード自体のロジックは整っており、スクレイピング→予測→買い目の流れは明確。
最大の問題はSeleniumの旧式API。ここを直せばまず動かせる状態になるはず。

---

<!-- 以降、作業のたびに追記 -->
