"""
config.py — KeibaAI 全体設定・パス定義

すべてのファイルパス・URL・定数をここで一元管理する。
パスの変更が必要な場合はこのファイルのみを編集すること。
認証情報は .env ファイルで管理する（リポジトリには含めない）。
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# プロジェクトルートの .env を読み込む
load_dotenv(Path(__file__).parent.parent / ".env")

# ---------------------------------------------------------------------------
# ベースディレクトリ
# ---------------------------------------------------------------------------
BASE_DIR = Path("C:/KeibaAI")
DATA_DIR = BASE_DIR / "data" / "netkeiba"
SOURCE_DIR = BASE_DIR / "src"

# ---------------------------------------------------------------------------
# データパス
# ---------------------------------------------------------------------------
RACECARD_DIR = DATA_DIR / "racecard"
RACELIST_DIR = DATA_DIR / "racelist"
RESULT_DIR = DATA_DIR / "result"
TARGET_DIR = BASE_DIR / "data" / "target"

# result サブディレクトリ
RESULT_PROCESS_DIR = RESULT_DIR / "process"

# 固定CSVファイル
RACE_ALL_CSV = RESULT_DIR / "race_all.csv"
ENCODE_LIST_CSV = DATA_DIR / "assets" / "encode_list.csv"
ASSETS_DIR = DATA_DIR / "assets"

# ---------------------------------------------------------------------------
# モデル・エンコーダ・バッチパス
# ---------------------------------------------------------------------------
MODEL_DIR = SOURCE_DIR / "model"
ENCODE_DIR = SOURCE_DIR / "encode"
BATCH_DIR = SOURCE_DIR / "batch"

# ---------------------------------------------------------------------------
# 認証情報（.env から読み込み）
# ---------------------------------------------------------------------------
NETKEIBA_USER = os.getenv("NETKEIBA_USER", "")
NETKEIBA_PASSWORD = os.getenv("NETKEIBA_PASSWORD", "")

# ---------------------------------------------------------------------------
# モデルバージョン（学習済みモデルのサフィックス）
# ---------------------------------------------------------------------------
MODEL_VERSION = "v3"

# ---------------------------------------------------------------------------
# URL
# ---------------------------------------------------------------------------
URL_LOGIN = "https://regist.netkeiba.com/account/?pid=login&action=auth"
URL_CALENDAR = "https://race.netkeiba.com/top/calendar.html"
URL_RACELIST_PAGE = "https://race.netkeiba.com/top/race_list.html"
URL_SHUTUBA = "https://race.netkeiba.com/race/shutuba.html"
URL_ODDS = "https://race.netkeiba.com/odds/index.html"
URL_DB = "https://db.netkeiba.com"
URL_IPAT = "https://www.ipat.jra.go.jp/sp/"

# ---------------------------------------------------------------------------
# オッズCSVファイル名（getinfo.py / calcticket.py 共通）
# ---------------------------------------------------------------------------
ODDS_FILES = {
    "tanfuku": "tanfuku.csv",
    "wakuren": "wakuren.csv",
    "umaren": "umaren.csv",
    "wide": "wide.csv",
    "umatan": "umatan.csv",
    "fuku3": "fuku3.csv",
}
