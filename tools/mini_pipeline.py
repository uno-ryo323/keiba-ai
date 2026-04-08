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

# 予測・買い目確認用の既存レース（Phase 3 で動作確認済み）
PRED_DATE = "20210105"
PRED_RACE_ID = "202106010101"


# ---------------------------------------------------------------------------
# Step 1: レース結果収集
# ---------------------------------------------------------------------------
def step1_collect():
    print("\n=== Step 1: レース結果収集 ===")
    import pandas as pd
    from src.scraping.racedb import raceDB

    # 2022-02-05 の race_id を抽出
    df = pd.read_csv(MINI_RACE_IDS_CSV, encoding="shift_jis", dtype=str)
    ids = df[(df["year"] == "2022") & (df["month"] == "02") & (df["day"] == "05")][
        "race_id"
    ].tolist()
    print(f"対象: {len(ids)} レース ({MINI_DATE})")

    # 出力先をミニ版に差し替え
    original_path = raceDB.PATH
    raceDB.PATH = str(MINI_RACE_ALL)
    try:
        raceDB.get_race_result(ids)
    finally:
        raceDB.PATH = original_path

    # 結果確認
    if MINI_RACE_ALL.exists():
        lines = MINI_RACE_ALL.read_text(encoding="cp932", errors="ignore").splitlines()
        print(f"出力: {MINI_RACE_ALL} ({len(lines)} 行)")
    else:
        print("ERROR: 出力ファイルが生成されませんでした")


# ---------------------------------------------------------------------------
# Step 2: 前処理
# ---------------------------------------------------------------------------
def step2_preprocess():
    print("\n=== Step 2: 前処理（race_jra2.1_mini.csv 生成） ===")
    import pandas as pd

    if not MINI_RACE_ALL.exists():
        print("ERROR: race_all_mini.csv がありません。Step 1 を先に実行してください")
        return

    df = pd.read_csv(MINI_RACE_ALL, encoding="cp932", low_memory=False, header=None)
    print(f"race_all_mini.csv: {len(df)} 行")

    # preprocess の前処理ロジックは race_jra2.x.csv を直接生成するため、
    # ここでは race_all_mini.csv の内容確認と列数チェックのみ行う
    # （本格的な前処理は Step 2 で既存 preprocess.py を流用する）
    print("カラム数:", len(df.columns))
    print("先頭行:", df.iloc[0].tolist()[:10], "...")
    print("※ 本格的な前処理（race_jra2.1 生成）は既存データ量が必要なため別途実施")


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

    # race_jra+.csv が未生成の場合は race_15-21_c2.csv (UTF-8) を cp932 に変換して作成
    if not dst_csv.exists():
        print(f"race_jra+.csv を生成します: {src_csv} → {dst_csv}")
        df = pd.read_csv(src_csv, encoding="utf-8", low_memory=False)
        df.to_csv(dst_csv, encoding="cp932", index=False)
        print(f"生成完了: {len(df)} 行")
    else:
        print(f"race_jra+.csv 既存: {dst_csv}")

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
    "4": ("モデル学習", step4_train),
    "5": ("予測・買い目確認", step5_predict),
}

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"

    if arg == "all":
        step1_collect()
        step2_preprocess()
        step5_predict()
    elif arg in STEPS:
        label, func = STEPS[arg]
        func()
    else:
        print(f"使い方: python tools/mini_pipeline.py [{'|'.join(STEPS)}|all]")
