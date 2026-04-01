"""
test_steps.py — ステップ別動作確認スクリプト

各処理ステップを個別に実行してエラーを切り分ける。
Selenium が必要なステップ（レースカード取得・オッズ取得）はスキップ。

実行方法:
    cd C:/KeibaAI
    python tests/test_steps.py

テストデータ:
    date    = "20210105"
    race_id = "202106010101"
"""

import sys
import traceback
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

warnings.simplefilter("ignore")

# テスト対象のレース
DATE = "20210105"
RACE_ID = "202106010101"

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"

results = []


def run_step(label, func):
    """ステップを実行してPASS/FAILを記録する"""
    print(f"\n{'='*60}")
    print(f"[{label}]")
    print("=" * 60)
    try:
        func()
        print(f">> {PASS}")
        results.append((label, PASS, None))
    except Exception as e:
        print(f">> {FAIL}: {e}")
        traceback.print_exc()
        results.append((label, FAIL, str(e)))


# ---------------------------------------------------------------------------
# Step 2a: preprocess — get_diff_race（前5走の不足レース算出）
# ---------------------------------------------------------------------------
def step_2a_get_diff_race():
    from src.pipeline import preprocess

    pp = preprocess.PreProcess(DATE, RACE_ID)
    diff = pp.get_diff_race()
    print(f"不足レース数: {len(diff)}")


# ---------------------------------------------------------------------------
# Step 2b: racedb — get_race_result（不足レース結果をDBから取得）
# ※ネットワーク通信あり。不足レースがある場合のみ実行。
# ---------------------------------------------------------------------------
def step_2b_racedb_get_race_result():
    from src.pipeline import preprocess
    from src.scraping import racedb

    pp = preprocess.PreProcess(DATE, RACE_ID)
    diff = pp.get_diff_race()
    if not diff or (len(diff) == 1 and str(diff[0]) in ("0", 0)):
        print("不足レースなし → スキップ")
        results[-1] = (results[-1][0], SKIP, "不足レースなし")
        return
    print(f"不足レース: {diff[:3]}...（{len(diff)}件）")
    racedb.raceDB.get_race_result(diff)


# ---------------------------------------------------------------------------
# Step 2c: scraping — get_race_result（スクレイピングで馬情報補完）
# ※ネットワーク通信あり。不足レースがある場合のみ実行。
# ---------------------------------------------------------------------------
def step_2c_scraping_get_race_result():
    from src.pipeline import preprocess
    from src.scraping import scraping

    pp = preprocess.PreProcess(DATE, RACE_ID)
    diff = pp.get_diff_race()
    if not diff or (len(diff) == 1 and str(diff[0]) in ("0", 0)):
        print("不足レースなし → スキップ")
        results[-1] = (results[-1][0], SKIP, "不足レースなし")
        return
    scraping.Scraping.get_race_result(diff)


# ---------------------------------------------------------------------------
# Step 2d: preprocess — join_netkeiba_target（前5走データをrace_all.csvに結合）
# ---------------------------------------------------------------------------
def step_2d_join_netkeiba_target():
    from src.pipeline import preprocess

    pp = preprocess.PreProcess(DATE, RACE_ID)
    diff = pp.get_diff_race()
    if not diff or (len(diff) == 1 and str(diff[0]) in ("0", 0)):
        print("不足レースなし → スキップ")
        results[-1] = (results[-1][0], SKIP, "不足レースなし")
        return
    pp.join_netkeiba_target(diff)


# ---------------------------------------------------------------------------
# Step 2e: preprocess — calc_agari_rank（上がりタイム順位の計算）
# ---------------------------------------------------------------------------
def step_2e_calc_agari_rank():
    from src.pipeline import preprocess

    pp = preprocess.PreProcess(DATE, RACE_ID)
    diff = pp.get_diff_race()
    if not diff or (len(diff) == 1 and str(diff[0]) in ("0", 0)):
        print("不足レースなし → スキップ")
        results[-1] = (results[-1][0], SKIP, "不足レースなし")
        return
    pp.calc_agari_rank(diff)


# ---------------------------------------------------------------------------
# Step 3: preprocess — join_pre_race_result（_c.csv 生成）
# ---------------------------------------------------------------------------
def step_3_join_pre_race_result():
    from src.pipeline import preprocess
    from src.config import RACECARD_DIR

    pp = preprocess.PreProcess(DATE, RACE_ID)
    pp.join_pre_race_result()
    out = RACECARD_DIR / DATE / RACE_ID / f"{RACE_ID}_c.csv"
    assert out.exists(), f"出力ファイルが存在しない: {out}"
    print(f"出力確認: {out}")


# ---------------------------------------------------------------------------
# Step 4: preprocess — encode_use_LabelEncoder（_c2.csv 生成）
# ---------------------------------------------------------------------------
def step_4_encode_use_LabelEncoder():
    from src.pipeline import preprocess
    from src.config import RACECARD_DIR

    pp = preprocess.PreProcess(DATE, RACE_ID)
    pp.encode_use_LabelEncoder()
    out = RACECARD_DIR / DATE / RACE_ID / f"{RACE_ID}_c2.csv"
    assert out.exists(), f"出力ファイルが存在しない: {out}"
    print(f"出力確認: {out}")


# ---------------------------------------------------------------------------
# Step 5: keibaai — forecast_race（予測スコア算出・_forecast.csv 生成）
# ---------------------------------------------------------------------------
def step_5_forecast_race():
    from src.pipeline import keibaai
    from src.config import RACECARD_DIR

    ai = keibaai.KeibaAI(DATE, RACE_ID)
    ai.forecast_race(1)  # type_ai=1（LabelEncoder版）
    out = RACECARD_DIR / DATE / RACE_ID / f"{RACE_ID}_forecast.csv"
    assert out.exists(), f"出力ファイルが存在しない: {out}"
    print(f"出力確認: {out}")


# ---------------------------------------------------------------------------
# Step 6: calcticket — main（買い目算出・ticket.csv 生成）
# ---------------------------------------------------------------------------
def step_6_calcticket_main():
    from src.betting import calcticket
    from src.config import RACECARD_DIR

    ct = calcticket.CalcTicket(DATE, RACE_ID)
    ct.main()
    out = RACECARD_DIR / DATE / RACE_ID / "ticket.csv"
    assert out.exists(), f"出力ファイルが存在しない: {out}"
    print(f"出力確認: {out}")


# ---------------------------------------------------------------------------
# メイン実行
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"テスト対象: date={DATE}, race_id={RACE_ID}")
    print("※ Step 1（レースカード取得）・オッズ取得は Selenium 必須のためスキップ")

    run_step("Step 2a: get_diff_race", step_2a_get_diff_race)
    run_step("Step 2b: racedb.get_race_result", step_2b_racedb_get_race_result)
    run_step("Step 2c: scraping.get_race_result", step_2c_scraping_get_race_result)
    run_step("Step 2d: join_netkeiba_target", step_2d_join_netkeiba_target)
    run_step("Step 2e: calc_agari_rank", step_2e_calc_agari_rank)
    run_step("Step 3: join_pre_race_result", step_3_join_pre_race_result)
    run_step("Step 4: encode_use_LabelEncoder", step_4_encode_use_LabelEncoder)
    run_step("Step 5: forecast_race", step_5_forecast_race)
    run_step("Step 6: calcticket.main", step_6_calcticket_main)

    # ---------------------------------------------------------------------------
    # 結果サマリ
    # ---------------------------------------------------------------------------
    print(f"\n{'='*60}")
    print("結果サマリ")
    print("=" * 60)
    all_ok = True
    for label, status, err in results:
        icon = {"PASS": "[OK]", "FAIL": "[NG]", "SKIP": "[--]"}.get(status, "[?]")
        msg = f"  {err}" if err and status == FAIL else ""
        print(f"{icon} {label}{msg}")
        if status == FAIL:
            all_ok = False

    print()
    if all_ok:
        print("全ステップ PASS（または SKIP）")
    else:
        fail_count = sum(1 for _, s, _ in results if s == FAIL)
        print(
            f"{fail_count} ステップで FAIL が発生しました。上記のスタックトレースを確認してください。"
        )
        sys.exit(1)
