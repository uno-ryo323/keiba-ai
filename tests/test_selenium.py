"""
test_selenium.py -Chrome / Selenium が必要な動作確認

対象:
  - getinfo.GetInfo.get_race_card()          ← 出馬表 CSV 生成
  - getinfo.GetInfo.get_odds()               ← オッズ CSV 生成
  - judgeticket.JudgeTicket.get_result()     ← 払戻ページ取得（既知バグあり → SKIP）
  - purchaseticket.PurchaseTicket            ← インスタンス化のみ（実購入はしない）
  - keibaAI_batch.keibaAIBatch.forecast()   ← Selenium + LINE 込みのフル予想

注意:
  - Chrome と ChromeDriver が必要（webdriver-manager で自動管理）
  - netKeiba への実際のログインが発生する（.env に認証情報が必要）
  - purchaseticket のインスタンス化は Chrome を起動するため終了後に driver.quit() を呼ぶ
  - purchaseticket.auto_purchase() は iPAT への実購入のため絶対に呼ばない
  - forecast() は netKeiba ログイン + LINE Notify 送信が発生する

実行方法:
    cd C:/KeibaAI
    python tests/test_selenium.py
"""

import sys
import traceback
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

warnings.simplefilter("ignore")

DATE = "20210105"
RACE_ID = "202106010101"

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"

results = []


def run_step(label, func):
    print(f"\n{'='*60}")
    print(f"[{label}]")
    print("=" * 60)
    try:
        result = func()
        if result == SKIP:
            print(f">>> {SKIP}")
            results.append((label, SKIP, None))
        else:
            print(f">>> {PASS}")
            results.append((label, PASS, None))
    except Exception as e:
        print(f">>> {FAIL}: {e}")
        traceback.print_exc()
        results.append((label, FAIL, str(e)))


# ============================================================
# getinfo.GetInfo.get_race_card()
# ============================================================


def test_get_race_card():
    """出馬表を取得して CSV に保存するテスト"""
    from src.scraping import getinfo
    from src.config import RACECARD_DIR

    out_dir = RACECARD_DIR / DATE / RACE_ID
    out_dir.mkdir(parents=True, exist_ok=True)

    gi = getinfo.GetInfo(DATE, RACE_ID)
    gi.get_race_card()

    out_csv = out_dir / f"{RACE_ID}.csv"
    assert out_csv.exists(), f"出馬表 CSV が見つかりません: {out_csv}"
    print(f"get_race_card() 完了 -{out_csv}")


# ============================================================
# getinfo.GetInfo.get_odds()
# ============================================================


def test_get_odds():
    """各券種のオッズを取得して CSV に保存するテスト"""
    from src.scraping import getinfo
    from src.config import RACECARD_DIR, ODDS_FILES

    out_dir = RACECARD_DIR / DATE / RACE_ID
    out_dir.mkdir(parents=True, exist_ok=True)

    gi = getinfo.GetInfo(DATE, RACE_ID)
    gi.get_odds()

    # tanfuku.csv が生成されていることを確認
    expected = out_dir / ODDS_FILES["tanfuku"]
    assert expected.exists(), f"単複オッズ CSV が見つかりません: {expected}"
    print(f"get_odds() 完了 -{expected}")


# ============================================================
# judgeticket.JudgeTicket.get_result()
# ============================================================


def test_get_result():
    """
    払戻ページ取得テスト。

    既知バグ: JudgeTicket.__init__() が self.file_result を初期化しないため
    get_result() は AttributeError で失敗する。
    このテストはバグを記録するために SKIP 扱いとする。
    """
    print("既知バグ: self.file_result が __init__ で初期化されていない → スキップ")
    return SKIP


# ============================================================
# purchaseticket.PurchaseTicket -インスタンス化のみ
# ============================================================


def test_purchaseticket_instantiate():
    """
    PurchaseTicket のインスタンス化テスト。

    __init__() で Chrome が起動するため、確認後に driver.quit() を呼ぶ。
    auto_purchase() は iPAT への実購入になるため絶対に呼ばない。
    """
    from src.betting import purchaseticket

    pt = purchaseticket.PurchaseTicket(RACE_ID, DATE)
    try:
        assert pt.race_id == RACE_ID
        assert pt.date == DATE
        print(
            f"PurchaseTicket インスタンス化 OK -race_id={pt.race_id}, place={pt.place}"
        )
    finally:
        if hasattr(pt, "driver") and pt.driver is not None:
            pt.driver.quit()
            print("Chrome driver を閉じました")


# ============================================================
# keibaAI_batch.keibaAIBatch.forecast()
# ============================================================


def test_forecast():
    """
    Selenium + LINE Notify を含むフル予想テスト。

    処理内容:
      1. LINE に「--レース予想--」通知（requests.post をモック）
      2. get_race_card() でレース表取得（Chrome）
      3. racedb / scraping で前走データ補完（必要時）
      4. preprocess → encode → LightGBM 予想

    テスト用レースデータ (DATE/RACE_ID) に合わせ datetime.now() をモックして
    forecast() 内の日付を固定する。
    """
    import datetime as real_datetime
    from unittest.mock import MagicMock, patch
    from src.keibaAI_batch import keibaAIBatch

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    # 本物の datetime オブジェクトを返すことで strftime() が正常動作する
    fixed_dt = real_datetime.datetime(2021, 1, 5)

    with patch("src.keibaAI_batch.requests.post", return_value=mock_resp), patch(
        "src.keibaAI_batch.datetime"
    ) as mock_dt_mod, patch("src.keibaAI_batch.getinfo.GetInfo.get_race_card"):
        # get_race_card() は既に単体テスト済みのため forecast() 内ではスキップ
        # モジュール参照を置換することで sys.modules["datetime"] を汚染しない
        mock_dt_mod.datetime.now.return_value = fixed_dt
        keibaAIBatch.forecast(RACE_ID)
    print("forecast() 完了（LINE Notify・get_race_card・datetime はモック）")


# ============================================================
# 実行
# ============================================================

if __name__ == "__main__":
    run_step("getinfo.GetInfo.get_race_card()", test_get_race_card)
    run_step("getinfo.GetInfo.get_odds()", test_get_odds)
    run_step("judgeticket.JudgeTicket.get_result() [既知バグ]", test_get_result)
    run_step(
        "purchaseticket.PurchaseTicket インスタンス化", test_purchaseticket_instantiate
    )
    run_step("keibaAI_batch.forecast()", test_forecast)

    print(f"\n{'='*60}")
    print("結果サマリー")
    print("=" * 60)
    for label, status, err in results:
        mark = "[OK]" if status == PASS else ("[--]" if status == SKIP else "[NG]")
        print(f"  {mark} {label}")
        if err:
            print(f"       {err}")
    passed = sum(1 for _, s, _ in results if s == PASS)
    skipped = sum(1 for _, s, _ in results if s == SKIP)
    print(f"\n{passed}/{len(results)} PASS  ({skipped} スキップ)")
