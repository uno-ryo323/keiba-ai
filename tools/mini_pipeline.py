"""
mini_pipeline.py — パイプライン疎通確認用ミニマム実行スクリプト

1日分（2022-02-05, 36レース）のデータで以下を通しで確認する:
  Step 1: レース結果収集  → data/netkeiba/result/race_all_mini.csv
  Step 2: 前処理          → data/netkeiba/result/race_jra2.1_mini.csv
  Step 3: エンコード      → data/netkeiba/result/race_jra2.2_mini.csv
  Step 4: モデル学習      → src/model/mini/
  Step 5: 予測・買い目    → data/netkeiba/racecard/ 以下の既存データを使用

実行:
    cd C:/KeibaAI
    .venv/Scripts/python tools/mini_pipeline.py [step]
    例: .venv/Scripts/python tools/mini_pipeline.py 1
        step 省略時は全ステップ実行
"""

import sys
from pathlib import Path

# プロジェクトルートを sys.path に追加
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ミニマム版の設定
MINI_DATE = "20220205"
MINI_RACE_IDS_CSV = ROOT / "data/netkeiba/assets/race_id_list_202202_202604.csv"
MINI_RACE_ALL = ROOT / "data/netkeiba/result/race_all_mini.csv"
MINI_JRA21 = ROOT / "data/netkeiba/result/race_jra2.1_mini.csv"
MINI_JRA22 = ROOT / "data/netkeiba/result/race_jra2.2_mini.csv"
MINI_MODEL_DIR = ROOT / "src/model/mini"

# 本番データ収集用の設定（2023-2025）
FULL_RACE_IDS_CSV = ROOT / "data/netkeiba/assets/race_id_list_202301_202512.csv"

# 予測・買い目確認用の既存レース（Phase 3 で動作確認済み）
PRED_DATE = "20210105"
PRED_RACE_ID = "202106010101"


# ---------------------------------------------------------------------------
# Step 1: レース結果収集
# ---------------------------------------------------------------------------
def step1_collect(year_from=None, month_from=None, year_to=None, month_to=None):
    """
    race_id_list_202301_202512.csv から指定年月範囲のレース結果を収集する。

    引数省略時は CSV 全件を対象とする。
    半年ごとのバッチ実行例:
        python tools/mini_pipeline.py 1 2023 1 2023 6
        python tools/mini_pipeline.py 1 2023 7 2023 12
    取得済み race_id は raceDB.get_race_result() 内でスキップされる。
    出力先: data/netkeiba/result/race_all.csv（BackUp版と同ディレクトリ外）
    """
    print("\n=== Step 1: レース結果収集 ===")
    import pandas as pd
    from src.scraping.racedb import raceDB
    from src.config import RACE_ALL_CSV

    df = pd.read_csv(FULL_RACE_IDS_CSV, encoding="shift_jis", dtype=str)

    # 年月範囲フィルタ
    if year_from and month_from and year_to and month_to:
        yf, mf = str(year_from), str(month_from).zfill(2)
        yt, mt = str(year_to), str(month_to).zfill(2)
        mask = (df["year"] + df["month"].str.zfill(2) >= yf + mf) & (
            df["year"] + df["month"].str.zfill(2) <= yt + mt
        )
        df = df[mask]
        print(f"対象期間: {yf}-{mf} 〜 {yt}-{mt}")
    else:
        print("対象期間: 全件（2023-01〜2025-12）")

    ids = df["race_id"].tolist()
    print(f"対象: {len(ids)} レース")
    print(f"出力先: {RACE_ALL_CSV}")

    raceDB.get_race_result(ids)

    if RACE_ALL_CSV.exists():
        lines = RACE_ALL_CSV.read_text(encoding="cp932", errors="ignore").splitlines()
        print(f"出力行数（累計）: {len(lines)} 行")
    else:
        print("ERROR: 出力ファイルが生成されませんでした")


# ---------------------------------------------------------------------------
# Step 2: agari_rank_p1~p5 パッチ
# ---------------------------------------------------------------------------
def step2_patch_agari_rank():
    """
    race_15-21_c2.csv の agari_rank_p1~p5 を race_all.csv から補完する。

    race_15-21_c2.csv 生成時に calc_agari_rank() が未実行だったため、
    agari_rank_p1~p5 が全NaNになっている問題を修正する。
    """
    print("\n=== Step 2: agari_rank_p1~p5 パッチ ===")
    import pandas as pd

    src_csv = ROOT / "data/netkeiba/result/process/race_15-21_c2.csv"
    race_all_csv = ROOT / "data/netkeiba/result/BackUp/race_all.csv"

    if not src_csv.exists():
        print(f"ERROR: {src_csv} が見つかりません")
        return
    if not race_all_csv.exists():
        print(f"ERROR: {race_all_csv} が見つかりません")
        return

    print("race_all.csv を読み込み中...")
    race_all = pd.read_csv(
        race_all_csv,
        encoding="cp932",
        dtype={"race_id": str, "horse_id": str},
        usecols=["race_id", "horse_id", "agari_rank"],
        low_memory=False,
    )
    # (race_id, horse_id) 重複がある場合は最初の行を採用
    race_all = race_all.drop_duplicates(subset=["race_id", "horse_id"])
    print(f"  {len(race_all)} 行（重複除去後）")

    print("race_15-21_c2.csv を読み込み中（時間がかかります）...")
    dtype_map = {
        "horse_id": str,
        "race_id": str,
        "pre_race1": str,
        "pre_race2": str,
        "pre_race3": str,
        "pre_race4": str,
        "pre_race5": str,
    }
    df = pd.read_csv(src_csv, encoding="utf-8", dtype=dtype_map, low_memory=False)
    print(f"  {len(df)} 行")

    # pre_race{n} + horse_id で race_all.csv の agari_rank を逆引きして埋める
    for n in range(1, 6):
        col_pre = f"pre_race{n}"
        col_rank = f"agari_rank_p{n}"
        temp = df[[col_pre, "horse_id"]].rename(columns={col_pre: "race_id"})
        merged = temp.merge(race_all, on=["race_id", "horse_id"], how="left")
        df[col_rank] = merged["agari_rank"].values
        filled = df[col_rank].notna().sum()
        print(f"  {col_rank}: {filled} 件補完")

    print("保存中...")
    df.to_csv(src_csv, encoding="utf-8", index=False)
    print(f"完了: {src_csv}")


# ---------------------------------------------------------------------------
# Step 4: モデル学習
# ---------------------------------------------------------------------------
def step4_train():
    print("\n=== Step 4: モデル学習 ===")
    import warnings
    import pandas as pd

    warnings.filterwarnings("ignore")

    from src.config import RESULT_PROCESS_DIR
    from src.pipeline.keibaai import KeibaAI

    src_csv = RESULT_PROCESS_DIR / "race_15-21_c2.csv"
    dst_csv = RESULT_PROCESS_DIR / "race_jra+.csv"

    # race_15-21_c2.csv (UTF-8) を cp932 に変換して race_jra+.csv を生成
    # ※ Step 2 でパッチした内容を反映するため、毎回再生成する
    print(f"race_jra+.csv を生成します: {src_csv} → {dst_csv}")
    df = pd.read_csv(src_csv, encoding="utf-8", low_memory=False)
    df.to_csv(dst_csv, encoding="cp932", index=False)
    print(f"生成完了: {len(df)} 行")

    print("モデル学習を開始します（Win / Quinella / Place の順、時間がかかります）...")
    KeibaAI.make_model()
    print("モデル学習完了（Win_new.sav / Quinella_new.sav / Place_new.sav）")


# ---------------------------------------------------------------------------
# Step 5: 予測・買い目（既存データで確認）
# ---------------------------------------------------------------------------
def step5_predict():
    print("\n=== Step 5: 予測・買い目確認（既存レースデータ使用） ===")
    import warnings

    warnings.filterwarnings("ignore")

    from src.pipeline.keibaai import KeibaAI
    from src.betting.calcticket import CalcTicket

    print(f"対象: {PRED_DATE} / {PRED_RACE_ID}")

    ai = KeibaAI(PRED_DATE, PRED_RACE_ID)
    result = ai.forecast_race(
        2
    )  # ai_type=2 → Win_new.sav / Quinella_new.sav / Place_new.sav
    print("予測完了")
    print(result[["horse_name", "Win", "horse_gate", "popular_rank"]].head())

    print("\n--- 買い目算出 ---")
    ct = CalcTicket(PRED_DATE, PRED_RACE_ID)
    ct.main()
    print("買い目算出完了")


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------
STEPS = {
    "1": ("レース結果収集", step1_collect),
    "2": ("agari_rank パッチ", step2_patch_agari_rank),
    "4": ("モデル学習", step4_train),
    "5": ("予測・買い目確認", step5_predict),
}

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"

    if arg == "all":
        step1_collect()
        step2_patch_agari_rank()
        step4_train()
        step5_predict()
    elif arg == "1":
        # step1 のみ: 引数で年月範囲を指定可能
        # 例: python tools/mini_pipeline.py 1 2023 1 2023 6
        if len(sys.argv) == 6:
            _, _, yf, mf, yt, mt = sys.argv
            step1_collect(yf, mf, yt, mt)
        else:
            step1_collect()
    elif arg in STEPS:
        label, func = STEPS[arg]
        func()
    else:
        print(f"使い方: python tools/mini_pipeline.py [{'|'.join(STEPS)}|all]")
        print("  step1 の半年バッチ例:")
        print("    python tools/mini_pipeline.py 1 2023 1 2023 6")
        print("    python tools/mini_pipeline.py 1 2023 7 2023 12")
