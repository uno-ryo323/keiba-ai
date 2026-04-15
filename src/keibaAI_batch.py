import sys
import datetime
import pandas as pd
from .scraping import getinfo
from .scraping import racedb
import os
from .scraping import scraping
from .pipeline import preprocess
from .pipeline import keibaai

from .config import BATCH_DIR, RACELIST_DIR


class keibaAIBatch:
    # LINE Notify はサービス終了（2025-03-31）のため通知機能は無効化
    _LINE_NOTIFY_DISABLED = True

    # Batch起動スケジュール決定
    def get_race_day(year, month):
        getinfo.GetInfo.get_race_day(year, month)
        data = pd.read_csv(
            BATCH_DIR
            / f"schedule_{datetime.date(int(year), int(month), 1).strftime('%Y%m')}.csv",
            sep=",",
            encoding="cp932",
        )
        batchPath = str(BATCH_DIR / "getRacelist.bat")
        for i in range(0, len(data)):
            print(data.loc[i])
            taskName = "getRaceList" + "_" + str(data.loc[i, "kaisai_date"])
            date = str(data.loc[i, "get_list_date"])
            command = (
                "schtasks /Create /SC ONCE /TN "
                + taskName
                + ' /TR "'
                + batchPath
                + ' 1 "'
                + str(data.loc[i, "kaisai_date"])
                + " /ST 18:00 /SD "
                + str(
                    datetime.date(
                        int(date[0:4]), int(date[4:6]), int(date[6:])
                    ).strftime("%Y/%m/%d")
                )
            )
            # print(command)
            os.system(command)
        # print(data)

    # レース一覧取得
    def get_race_list(date):
        getInfo = getinfo.GetInfo("", "")
        getInfo.get_race_time(date)
        data = pd.read_csv(RACELIST_DIR / f"{date}.csv", sep=",", encoding="cp932")
        batchPath1 = str(BATCH_DIR / "forecast.bat")
        batchPath2 = str(BATCH_DIR / "getRaceResult.bat")
        # 事前データ取得
        for i in range(0, len(data)):
            # レース予想
            taskName = "forecast" + "_" + str(data.loc[i, "race_id"])
            time = str(data.loc[i, "startTime"]).split(":")
            dt_start = datetime.datetime(
                int(date[0:4]),
                int(date[4:6]),
                int(date[6:]),
                int(time[0]),
                int(time[1]),
            )
            dt_diff = datetime.timedelta(minutes=20)
            exeDate = dt_start - dt_diff
            command = (
                "schtasks /Create /SC ONCE /TN "
                + taskName
                + ' /TR "'
                + batchPath1
                + " 4 "
                + str(data.loc[i, "race_id"])
                + '" /ST '
                + str(exeDate.strftime("%H:%M"))
                + " /SD "
                + str(
                    datetime.date(
                        int(date[0:4]), int(date[4:6]), int(date[6:])
                    ).strftime("%Y/%m/%d")
                )
            )
            # print(command)
            os.system(command)
            # 結果確認
            taskName = "getRaceResult" + "_" + str(data.loc[i, "race_id"])
            exeDate = dt_start + dt_diff
            command = (
                "schtasks /Create /SC ONCE /TN "
                + taskName
                + ' /TR "'
                + batchPath2
                + " 2 "
                + str(data.loc[i, "race_id"])
                + '" /ST '
                + str(exeDate.strftime("%H:%M"))
                + " /SD "
                + str(
                    datetime.date(
                        int(date[0:4]), int(date[4:6]), int(date[6:])
                    ).strftime("%Y/%m/%d")
                )
            )
            # print(command)
            os.system(command)

    # レース結果取得
    def get_race_result():
        dt_now = datetime.datetime.now()
        kaisai_date = dt_now.strftime("%Y%m%d")
        kaisai_date = "20220105"
        race_list = pd.read_csv(
            RACELIST_DIR / f"{kaisai_date}.csv",
            sep=",",
            encoding="cp932",
            dtype={"race_id": str},
        )
        rd = racedb.raceDB
        rd.get_race_result(race_list["race_id"])

    # レース事前データ取得
    def get_predata(race_id):
        pass

    # レース予想
    @classmethod
    def forecast(cls, race_id):
        # LINE Notify サービス終了のため通知はスキップ
        dt_now = datetime.datetime.now()
        date = dt_now.strftime("%Y%m%d")

        getInfo = getinfo.GetInfo(date, race_id)
        pp = preprocess.PreProcess(date, race_id)

        # レー表の取得
        getInfo.get_race_card()

        # 前処理
        diff = pp.get_diff_race()
        if not (len(diff) == 0):
            if not ((len(diff) == 1) and ((diff[0] == "0") or (diff[0] == 0))):
                rd = racedb.raceDB
                rd.get_race_result(diff)
                sc = scraping.Scraping
                sc.get_race_result(diff)
                pp.join_netkeiba_target(diff)
                pp.calc_agari_rank(diff)

        pp.join_pre_race_result()
        pp.encode_use_LabelEncoder()

        # 予想の実行
        ai = keibaai.KeibaAI(date, race_id)
        ai.forecast_race(1)

    # 馬券購入
    @classmethod
    def purchase(cls):
        # LINE Notify サービス終了のため通知はスキップ
        pass

    # 結果送信
    @classmethod
    def send_result(cls):
        # LINE Notify サービス終了のため通知はスキップ
        pass


if __name__ == "__main__":
    type = int(sys.argv[1])
    # 引数により処理を分岐
    if type == 1:
        date = sys.argv[2]
        keibaAIBatch.get_race_list(date)
    elif type == 2:
        keibaAIBatch.get_race_result()
    elif type == 3:
        keibaAIBatch.get_race_day("2022", "3")
    elif type == 4:
        race_id = sys.argv[2]
        keibaAIBatch.forecast()
    elif type == 6:
        keibaAIBatch.send_result()
