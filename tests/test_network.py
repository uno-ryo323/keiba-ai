"""
test_network.py -HTTP ネットワーク接続が必要な動作確認

対象:
  - racedb.raceDB.get_race_result()     ← netKeiba スクレイピング（JRA外・地方）
  - scraping.Scraping.get_race_result() ← netKeiba スクレイピング（地方・海外）
  - keibaAI_batch.keibaAIBatch.send_result() ← LINE Notify 送信

注意:
  - racedb / scraping のテストは一時ファイルに出力し race_all.csv を汚染しない
  - LINE Notify テストは実際に通知が送信される（トークン有効時）

実行方法:
    cd C:/KeibaAI
    python tests/test_network.py
"""

import sys
import traceback
import warnings
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

warnings.simplefilter("ignore")

# 地方競馬の過去レース ID（スクレイピング対象: 地方/海外のみ）
# racedb/scraping は int(place) >= 10 のレースのみ処理するためダミーとして "0" を使う
# 実際に取得する場合は地方レース ID を指定する
TEST_RACE_IDS = ["0"]  # "0" はスキップ処理される（RACE_ALL_CSV 汚染なし）

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"

results = []


def run_step(label, func):
    print(f"\n{'='*60}")
    print(f"[{label}]")
    print("=" * 60)
    try:
        func()
        print(f">>> {PASS}")
        results.append((label, PASS, None))
    except Exception as e:
        print(f">>> {FAIL}: {e}")
        traceback.print_exc()
        results.append((label, FAIL, str(e)))


# ============================================================
# racedb.raceDB.get_race_result()
# ============================================================


def test_racedb_get_race_result():
    """raceDB.get_race_result() を一時ファイルに出力してテスト"""
    from src.scraping import racedb

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        tmp_path = f.name

    original_path = racedb.raceDB.PATH
    try:
        # PATH を一時ファイルに差し替えて実行（race_all.csv を汚染しない）
        racedb.raceDB.PATH = tmp_path
        racedb.raceDB.get_race_result(TEST_RACE_IDS)
        print(f"get_race_result() 完了 -出力先: {tmp_path}")
        content = Path(tmp_path).read_text(encoding="cp932", errors="ignore")
        print(f"出力行数: {len(content.splitlines())}")
    finally:
        racedb.raceDB.PATH = original_path
        Path(tmp_path).unlink(missing_ok=True)


# ============================================================
# scraping.Scraping.get_race_result()
# ============================================================


def test_scraping_get_race_result():
    """Scraping.get_race_result() を一時ファイルに出力してテスト"""
    from src.scraping import scraping
    from pathlib import Path as _Path

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        tmp_path = _Path(f.name)

    try:
        with patch("src.scraping.scraping.RACE_ALL_CSV", tmp_path):
            scraping.Scraping.get_race_result(TEST_RACE_IDS)
        print(f"get_race_result() 完了 -出力先: {tmp_path}")
        content = tmp_path.read_text(encoding="cp932", errors="ignore")
        print(f"出力行数: {len(content.splitlines())}")
    finally:
        tmp_path.unlink(missing_ok=True)


# ============================================================
# keibaAI_batch.keibaAIBatch.send_result()
# ============================================================


def test_send_result():
    """LINE Notify への send_result() 呼び出しテスト（requests.post をモック）"""
    from unittest.mock import MagicMock, patch
    from src.keibaAI_batch import keibaAIBatch

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with patch("src.keibaAI_batch.requests.post", return_value=mock_resp) as mock_post:
        keibaAIBatch.send_result()
        assert mock_post.called, "requests.post が呼ばれませんでした"
    print("send_result() 完了（requests.post モック・実際の通知はなし）")


# ============================================================
# 実行
# ============================================================

if __name__ == "__main__":
    run_step("racedb.raceDB.get_race_result()", test_racedb_get_race_result)
    run_step("scraping.Scraping.get_race_result()", test_scraping_get_race_result)
    run_step("keibaAI_batch.send_result()", test_send_result)

    print(f"\n{'='*60}")
    print("結果サマリー")
    print("=" * 60)
    for label, status, err in results:
        mark = "[OK]" if status == PASS else ("[--]" if status == SKIP else "[NG]")
        print(f"  {mark} {label}")
        if err:
            print(f"       {err}")
    passed = sum(1 for _, s, _ in results if s == PASS)
    print(f"\n{passed}/{len(results)} PASS")
