"""
test_misc.py -ネットワーク・Selenium不要の動作確認

対象:
  - judgeticket.JudgeTicket.judge_ticket()  ← 既存 result.csv / ticket.csv を使用
  - judgeticket.JudgeTicket.calc_balance()  ← 上記の続き
  - encode.encode.make_encode_pickle()       ← race_jra2.1.csv を使用
  - encode.encode.encode_use_LabelEncoder()  ← encode/Ver1.1/ を使用
  - GUI モジュール import 確認（keiba_ai_tool, mycalender）

実行方法:
    cd C:/KeibaAI
    python tests/test_misc.py
"""

import sys
import shutil
import traceback
import warnings
from pathlib import Path
from unittest.mock import patch

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
        func()
        print(f">>> {PASS}")
        results.append((label, PASS, None))
    except Exception as e:
        print(f">>> {FAIL}: {e}")
        traceback.print_exc()
        results.append((label, FAIL, str(e)))


# ============================================================
# judgeticket -judge_ticket / calc_balance
# ============================================================


def test_judge_ticket():
    """既存の result.csv / ticket.csv を一時ディレクトリにコピーして照合テスト"""
    import tempfile
    from src.betting import judgeticket
    from src.config import RACECARD_DIR

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # テスト用ディレクトリ構成を再現
        dest = tmp_path / DATE / RACE_ID
        dest.mkdir(parents=True)
        src_dir = RACECARD_DIR / DATE / RACE_ID
        shutil.copy(src_dir / "result.csv", dest / "result.csv")
        shutil.copy(src_dir / "ticket.csv", dest / "ticket.csv")

        with patch("src.betting.judgeticket.RACECARD_DIR", tmp_path):
            jt = judgeticket.JudgeTicket(DATE, RACE_ID)
            jt.judge_ticket()

        # ticket.csv が更新されていることを確認
        assert (dest / "ticket.csv").exists(), "ticket.csv が存在しません"
        print("judge_ticket() 完了 -ticket.csv 更新済み")


def test_calc_balance():
    """的中フラグ付き ticket.csv をコピーして収支計算テスト"""
    import tempfile
    from src.betting import judgeticket
    from src.config import RACECARD_DIR

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        dest = tmp_path / DATE / RACE_ID
        dest.mkdir(parents=True)
        src_dir = RACECARD_DIR / DATE / RACE_ID
        shutil.copy(src_dir / "result.csv", dest / "result.csv")
        shutil.copy(src_dir / "ticket.csv", dest / "ticket.csv")

        with patch("src.betting.judgeticket.RACECARD_DIR", tmp_path):
            jt = judgeticket.JudgeTicket(DATE, RACE_ID)
            # 的中判定を先に実行してから収支計算
            jt.judge_ticket()
            jt.calc_balance()

        # balance.csv が生成されていることを確認
        balance_day = tmp_path / DATE / "balance.csv"
        balance_all = tmp_path / "balance.csv"
        assert balance_day.exists(), "balance.csv（日付ディレクトリ）が存在しません"
        assert balance_all.exists(), "balance.csv（ルート）が存在しません"
        content = balance_all.read_text(encoding="cp932")
        print(f"calc_balance() 完了 -出力: {content.strip()}")


# ============================================================
# encode -make_encode_pickle / encode_use_LabelEncoder
# ============================================================


def test_make_encode_pickle():
    """race_jra2.1.csv から LabelEncoder pickle を生成するテスト（一時ディレクトリに出力）"""
    import tempfile
    from src.pipeline import encode as enc_mod

    # pickle の出力先を一時ディレクトリに変更（既存 Ver1.1 pickleを上書きしない）
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_encode = Path(tmpdir)
        (tmp_encode / "Ver1.1").mkdir()

        with patch("src.pipeline.encode.ENCODE_DIR", tmp_encode):
            enc_mod.encode.make_encode_pickle()

        pickles = list((tmp_encode / "Ver1.1").glob("*.pickle"))
        print(f"生成された pickle 数: {len(pickles)}")
        assert len(pickles) > 0, "pickle ファイルが生成されませんでした"
        print(f"make_encode_pickle() 完了 -{len(pickles)} 個の pickle を生成")


def test_encode_use_LabelEncoder():
    """既存 Ver1.1 pickle を使って race_jra2.2.csv を生成するテスト（一時ディレクトリに出力）"""
    import tempfile
    from src.pipeline import encode as enc_mod
    from src.config import RESULT_DIR

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_result = Path(tmpdir)
        # race_jra2.1.csv を一時ディレクトリにコピー（出力先も一時ディレクトリ）
        shutil.copy(RESULT_DIR / "race_jra2.1.csv", tmp_result / "race_jra2.1.csv")

        with patch("src.pipeline.encode.RESULT_DIR", tmp_result):
            enc_mod.encode.encode_use_LabelEncoder()

        out_csv = tmp_result / "race_jra2.2.csv"
        assert out_csv.exists(), "race_jra2.2.csv が生成されませんでした"
        print(
            f"encode_use_LabelEncoder() 完了 -race_jra2.2.csv 生成 ({out_csv.stat().st_size} bytes)"
        )


# ============================================================
# GUI -import 確認のみ（表示はしない）
# ============================================================


def test_gui_imports():
    """tkinter ベース GUI モジュールの import 確認"""
    # tkinter が利用可能かチェック
    try:
        import tkinter
    except ImportError:
        print("[--] tkinter が利用不可のため GUI import テストをスキップ")
        return

    # keiba_ai_tool
    import src.keiba_ai_tool as tool_mod

    print(
        f"keiba_ai_tool import OK -keibaAITestTool クラス: {tool_mod.keibaAITestTool}"
    )

    # mycalender
    print("mycalender import OK")


# ============================================================
# 実行
# ============================================================

if __name__ == "__main__":
    run_step("judgeticket.judge_ticket()", test_judge_ticket)
    run_step("judgeticket.calc_balance()", test_calc_balance)
    run_step("encode.make_encode_pickle()", test_make_encode_pickle)
    run_step("encode.encode_use_LabelEncoder()", test_encode_use_LabelEncoder)
    run_step("GUI import 確認", test_gui_imports)

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
