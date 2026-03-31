"""
test_e2e.py — エンドツーエンドテスト

driver.py の forecast() 関数を通して全処理パイプラインを検証する。
Selenium が必要なステップ（レースカード取得・オッズ取得）は flag=0 でスキップ。

テスト内容:
  - [全レース] flag=0: encode_use_LabelEncoder → forecast_race（_c.csv から予測）
  - [1レース]  前処理込み: join_pre_race_result → encode → forecast → calcticket

実行方法:
    cd C:/KeibaAI/Source
    python test_e2e.py

テストデータ:
    date    = "20210105"
    race_id = "202106010101" 〜 "202107010112"（24レース）
"""

import sys
import traceback
import warnings

warnings.simplefilter("ignore")

import pandas as pd

import driver
import calcticket
import preprocess
from config import RACECARD_DIR

# ---------------------------------------------------------------------------
# テスト対象
# ---------------------------------------------------------------------------
DATE = "20210105"
RACE_IDS = [
    "202106010101",
    "202106010102",
    "202106010103",
    "202106010104",
    "202106010105",
    "202106010106",
    "202106010107",
    "202106010108",
    "202106010109",
    "202106010110",
    "202106010111",
    "202106010112",
    "202107010101",
    "202107010102",
    "202107010103",
    "202107010104",
    "202107010105",
    "202107010106",
    "202107010107",
    "202107010108",
    "202107010109",
    "202107010110",
    "202107010111",
    "202107010112",
]
# 前処理込みテストの対象（代表レース1件）
PREPROCESS_TARGET = "202106010101"

PASS = "PASS"
FAIL = "FAIL"


# ---------------------------------------------------------------------------
# テスト1: flag=0 で全24レースを通し実行（encode → forecast）
# ---------------------------------------------------------------------------
def test_predict_all_races():
    print("\n" + "=" * 70)
    print("テスト1: 全レース予測パイプライン（flag=0, encode → forecast）")
    print("=" * 70)

    results = []
    for race_id in RACE_IDS:
        try:
            # _forecast.csv を削除して新規生成を確認
            forecast_csv = RACECARD_DIR / DATE / race_id / f"{race_id}_forecast.csv"
            if forecast_csv.exists():
                forecast_csv.unlink()

            driver.forecast(DATE, race_id, 1, flag=0)

            # 出力ファイルの確認
            assert (
                forecast_csv.exists()
            ), f"_forecast.csv が生成されなかった: {forecast_csv}"

            # 中身の確認（16頭以下、Win/Quinella/Place 列あり）
            df = pd.read_csv(forecast_csv, encoding="cp932")
            assert len(df) > 0, "_forecast.csv が空"
            for col in ("Win", "Quinella", "Place"):
                assert col in df.columns, f"列 {col} が存在しない"
            assert df["Win"].between(0, 1).all(), "Win スコアが [0,1] 範囲外"

            results.append((race_id, PASS, len(df), None))
        except Exception as e:
            results.append((race_id, FAIL, None, str(e)))
            traceback.print_exc()

    # サマリ表示
    print(f"\n{'race_id':<16} {'状態':<6} {'頭数':>4}")
    print("-" * 30)
    for race_id, status, n_horses, err in results:
        icon = "[OK]" if status == PASS else "[NG]"
        heads = str(n_horses) if n_horses is not None else "-"
        msg = f"  ← {err}" if status == FAIL else ""
        print(f"{icon} {race_id}  {heads:>4}{msg}")

    pass_count = sum(1 for _, s, _, _ in results if s == PASS)
    fail_count = len(results) - pass_count
    print(f"\n結果: {pass_count}/{len(results)} PASS, {fail_count} FAIL")
    return fail_count == 0


# ---------------------------------------------------------------------------
# テスト2: 前処理込み E2E（join_pre_race_result → encode → forecast → calcticket）
# ---------------------------------------------------------------------------
def test_full_pipeline_one_race():
    print("\n" + "=" * 70)
    print(f"テスト2: 前処理込み E2E（race_id={PREPROCESS_TARGET}）")
    print("  join_pre_race_result → encode → forecast → calcticket")
    print("=" * 70)

    race_id = PREPROCESS_TARGET
    race_dir = RACECARD_DIR / DATE / race_id
    errors = []

    # 中間ファイルを削除して全ステップを再実行
    for suffix in ("_c.csv", "_c2.csv", "_forecast.csv", "ticket.csv"):
        target = (
            race_dir / f"{race_id}{suffix}"
            if suffix.endswith(".csv") and suffix.startswith("_")
            else race_dir / suffix
        )
        if target.exists():
            target.unlink()

    steps = [
        ("join_pre_race_result", _run_join_pre),
        ("encode_use_LabelEncoder", _run_encode),
        ("forecast_race", _run_forecast),
        ("calcticket.main", _run_calcticket),
    ]

    ok = True
    for label, func in steps:
        try:
            func(race_id)
            print(f"  [OK] {label}")
        except Exception as e:
            print(f"  [NG] {label}: {e}")
            traceback.print_exc()
            errors.append((label, str(e)))
            ok = False
            # 依存する後続ステップも実行不可のため中断
            break

    if ok:
        # 最終出力の内容確認
        _verify_outputs(race_id)

    print(f"\n結果: {'PASS' if ok else 'FAIL'}")
    return ok


def _run_join_pre(race_id):
    pp = preprocess.PreProcess(DATE, race_id)
    pp.join_pre_race_result()
    out = RACECARD_DIR / DATE / race_id / f"{race_id}_c.csv"
    assert out.exists(), f"_c.csv が生成されなかった: {out}"


def _run_encode(race_id):
    pp = preprocess.PreProcess(DATE, race_id)
    pp.encode_use_LabelEncoder()
    out = RACECARD_DIR / DATE / race_id / f"{race_id}_c2.csv"
    assert out.exists(), f"_c2.csv が生成されなかった: {out}"


def _run_forecast(race_id):
    import keibaai

    ai = keibaai.KeibaAI(DATE, race_id)
    ai.forecast_race(1)
    out = RACECARD_DIR / DATE / race_id / f"{race_id}_forecast.csv"
    assert out.exists(), f"_forecast.csv が生成されなかった: {out}"


def _run_calcticket(race_id):
    ct = calcticket.CalcTicket(DATE, race_id)
    ct.main()
    out = RACECARD_DIR / DATE / race_id / "ticket.csv"
    assert out.exists(), f"ticket.csv が生成されなかった: {out}"


def _verify_outputs(race_id):
    """出力ファイルの内容を簡易チェック"""
    race_dir = RACECARD_DIR / DATE / race_id

    forecast_csv = race_dir / f"{race_id}_forecast.csv"
    df = pd.read_csv(forecast_csv, encoding="cp932")
    print(f"\n  _forecast.csv: {len(df)} 頭")
    print(df[["horse_name", "Win", "Quinella", "Place"]].to_string(index=False))

    ticket_csv = race_dir / "ticket.csv"
    ticket = pd.read_csv(ticket_csv, encoding="cp932")
    print(f"\n  ticket.csv: {len(ticket)} 件の買い目")
    if len(ticket) > 0:
        print(ticket.head(5).to_string(index=False))


# ---------------------------------------------------------------------------
# メイン実行
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"E2E テスト開始: date={DATE}, 対象レース={len(RACE_IDS)}件")
    print("※ Selenium必須のステップ（レースカード取得・オッズ取得）はスキップ")

    t1_ok = test_predict_all_races()
    t2_ok = test_full_pipeline_one_race()

    print("\n" + "=" * 70)
    print("最終結果")
    print("=" * 70)
    print(f"  テスト1（全レース予測）: {'PASS' if t1_ok else 'FAIL'}")
    print(f"  テスト2（前処理込みE2E）: {'PASS' if t2_ok else 'FAIL'}")

    if t1_ok and t2_ok:
        print("\n全テスト PASS")
    else:
        print("\nFAIL あり。上記のスタックトレースを確認してください。")
        sys.exit(1)
