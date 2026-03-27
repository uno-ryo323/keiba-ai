import pandas as pd
import datetime
import numpy as np
import pickle
from sklearn import preprocessing

from config import (
    ENCODE_DIR,
    ENCODE_LIST_CSV,
    RACE_ALL_CSV,
    RACECARD_DIR,
    RESULT_DIR,
    RESULT_PROCESS_DIR,
    TARGET_DIR,
)


class PreProcess:

    def __init__(self, date, race_id):
        self.date = date
        self.race_id = race_id

    # 前5走の不足レース算出
    # <param> keiba_data: 予測対象レースの出馬表
    # <return> race_ids_diff：　取得できていないレースIDのリスト
    def get_diff_race(self):
        print("前5走の不足レースを取得します")
        keiba_data = pd.read_csv(
            RACECARD_DIR / self.date / self.race_id / f"{self.race_id}.csv",
            sep=",",
            encoding="cp932",
            dtype={
                "race_id": object,
                "pre_race1": object,
                "pre_race2": object,
                "pre_race3": object,
                "pre_race4": object,
                "pre_race5": object,
            },
        )
        all_data = pd.read_csv(
            RACE_ALL_CSV,
            sep=",",
            encoding="cp932",
            dtype={
                "race_id": object,
                "pre_race1": object,
                "pre_race2": object,
                "pre_race3": object,
                "pre_race4": object,
                "pre_race5": object,
            },
        )
        race_id = all_data["race_id"]
        pre_race1 = keiba_data["pre_race1"]
        pre_race2 = keiba_data["pre_race2"]
        pre_race3 = keiba_data["pre_race3"]
        pre_race4 = keiba_data["pre_race4"]
        pre_race5 = keiba_data["pre_race5"]

        pre_race_sum = (
            set(pre_race1)
            | set(pre_race2)
            | set(pre_race3)
            | set(pre_race4)
            | set(pre_race5)
        )
        race_ids_diff = set(pre_race_sum) - set(race_id)
        race_ids_diff = list(race_ids_diff)
        print("前5走の不足レースの取得が完了しました")
        print("不足しているレース数は" + str(len(race_ids_diff)) + "です")
        return race_ids_diff

    # netkeibaとtargetのデータを結合する
    # <param>keiba_data：予測対象レースの前5走のデータ
    def join_netkeiba_target(self, race_ids):
        print("targetのデータを結合します")
        netkeiba_data = pd.read_csv(
            RACE_ALL_CSV,
            sep=",",
            encoding="cp932",
            dtype={
                "race_id": object,
                "horse_id": object,
                "year": object,
                "month": object,
                "day": object,
            },
        )
        target_data = pd.read_csv(
            TARGET_DIR / "race_2010-2021_target.csv",
            sep=",",
            encoding="cp932",
            dtype={"horse_code": object, "year": object, "month": int, "date": int},
        )

        length = len(race_ids)
        for i in range(0, length):
            print(race_ids[i])
            place = race_ids[i][4:6]
            if not place.isdigit():
                continue
            if int(place) > 10:
                continue
            data_index_list = netkeiba_data.index[
                netkeiba_data["race_id"] == race_ids[i]
            ]
            for data_index in data_index_list:
                year = netkeiba_data.loc[data_index, "year"]
                year = str(year)[2:4]
                month = netkeiba_data.loc[data_index, "month"]
                day = netkeiba_data.loc[data_index, "day"]
                horse_code = netkeiba_data.loc[data_index, "horse_id"]
                target_data["date"] = target_data["date"].astype(str)
                target_data["month"] = target_data["month"].astype(str)
                target_data["year"] = target_data["year"].astype(str)

                index = target_data.index[
                    (target_data["year"] == year)
                    & (target_data["month"] == month)
                    & (target_data["date"] == day)
                    & (target_data["horse_code"] == horse_code)
                ]
                index = index[0]

                netkeiba_data.loc[data_index, "class_code"] = target_data.loc[
                    index, "class_code"
                ]
                netkeiba_data.loc[data_index, "grade_code"] = target_data.loc[
                    index, "grade_code"
                ]
                netkeiba_data.loc[data_index, "track_code"] = target_data.loc[
                    index, "track_code"
                ]
                netkeiba_data.loc[data_index, "track_code2"] = target_data.loc[
                    index, "track_code2"
                ]
                netkeiba_data.loc[data_index, "corner_count"] = target_data.loc[
                    index, "corner_count"
                ]
                netkeiba_data.loc[data_index, "course_class"] = target_data.loc[
                    index, "course_class"
                ]
                netkeiba_data.loc[data_index, "race_prize"] = target_data.loc[
                    index, "race_prize"
                ]
                netkeiba_data.loc[data_index, "rpci"] = target_data.loc[index, "rpci"]
                netkeiba_data.loc[data_index, "pci3"] = target_data.loc[index, "pci3"]
                netkeiba_data.loc[data_index, "race_type_code"] = target_data.loc[
                    index, "race_type_code"
                ]
                netkeiba_data.loc[data_index, "race_symbol_code"] = target_data.loc[
                    index, "race_symbol_code"
                ]
                netkeiba_data.loc[data_index, "weight_type_code"] = target_data.loc[
                    index, "weight_type_code"
                ]
                netkeiba_data.loc[data_index, "race_type_code"] = target_data.loc[
                    index, "race_type_code"
                ]
                netkeiba_data.loc[data_index, "weight_type_code"] = target_data.loc[
                    index, "weight_type_code"
                ]
                netkeiba_data.loc[data_index, "blinkers"] = target_data.loc[
                    index, "blinkers"
                ]
                netkeiba_data.loc[data_index, "rank_offical"] = target_data.loc[
                    index, "rank_offical"
                ]
                netkeiba_data.loc[data_index, "rank_arrival"] = target_data.loc[
                    index, "rank_arrival"
                ]
                netkeiba_data.loc[data_index, "abnormal_code"] = target_data.loc[
                    index, "abnormal_code"
                ]
                netkeiba_data.loc[data_index, "time_diff"] = target_data.loc[
                    index, "time_diff"
                ]
                netkeiba_data.loc[data_index, "ave_3f"] = target_data.loc[
                    index, "ave_3f"
                ]
                netkeiba_data.loc[data_index, "pci"] = target_data.loc[index, "pci"]
                netkeiba_data.loc[data_index, "minus_3f"] = target_data.loc[
                    index, "minus_3f"
                ]
                netkeiba_data.loc[data_index, "father_type"] = target_data.loc[
                    index, "father_type"
                ]
                netkeiba_data.loc[data_index, "mother_father_type"] = target_data.loc[
                    index, "mother_father_type"
                ]

        netkeiba_data.to_csv(RACE_ALL_CSV, index=False, sep=",", encoding="cp932")
        print("targetのデータの結合が完了しました")

    # 前5走のレース結果を返却
    # <param>race_ids:
    def get_pre_race_data(cls, race_ids):
        all_data = pd.read_csv(
            RACE_ALL_CSV,
            sep=",",
            encoding="cp932",
            dtype={
                "race_id": object,
                "pre_race1": object,
                "pre_race2": object,
                "pre_race3": object,
                "pre_race4": object,
                "pre_race5": object,
            },
        )
        return all_data[all_data["race_id"].isin(race_ids)]

    # 上がり順位を算出
    # <param>keiba_data：予測対象レースの前5走のデータ
    def calc_agari_rank(self, race_ids):
        all_data = pd.read_csv(
            RACE_ALL_CSV,
            sep=",",
            encoding="cp932",
            dtype={
                "race_id": object,
                "pre_race1": object,
                "pre_race2": object,
                "pre_race3": object,
                "pre_race4": object,
                "pre_race5": object,
            },
        )
        length = len(race_ids)
        for i in range(0, length):
            race_index = all_data.index[all_data["race_id"] == race_ids[i]]
            all_data.loc[race_index, "agari_rank"] = all_data.loc[
                race_index, "agari"
            ].rank(method="min")
        all_data.to_csv(RACE_ALL_CSV, sep=",", encoding="cp932", index=False)

    # 前5走成績を1レコードに結合
    # <param>keiba_data：予測対象レース
    def join_pre_race_result(self):
        all_data = pd.read_csv(
            RACE_ALL_CSV,
            sep=",",
            encoding="cp932",
            dtype={
                "horse_id": object,
                "place": object,
                "race_id": str,
                "pre_race1": str,
                "pre_race2": str,
                "pre_race3": str,
                "pre_race4": str,
                "pre_race5": str,
            },
        )
        keiba_data = pd.read_csv(
            RACECARD_DIR / self.date / self.race_id / f"{self.race_id}.csv",
            sep=",",
            encoding="cp932",
            dtype={
                "horse_id": object,
                "race_id": str,
                "pre_race1": str,
                "pre_race2": str,
                "pre_race3": str,
                "pre_race4": str,
                "pre_race5": str,
            },
        )

        length = len(keiba_data)
        for i in range(0, length):
            pre_race1 = keiba_data.loc[i, "pre_race1"]

            pre_race1_index = all_data.index[
                (all_data["race_id"] == pre_race1)
                & (all_data["horse_id"] == keiba_data.loc[i, "horse_id"])
            ]

            pre_race2 = keiba_data.loc[i, "pre_race2"]
            pre_race3 = keiba_data.loc[i, "pre_race3"]
            pre_race4 = keiba_data.loc[i, "pre_race4"]
            pre_race5 = keiba_data.loc[i, "pre_race5"]

            pre_race_list = [pre_race1, pre_race2, pre_race3, pre_race4, pre_race5]
            print(keiba_data.loc[i, "horse_gate"], keiba_data.loc[i, "horse_name"])
            print(pre_race_list)
            # 乗り替わり，ダ芝変わり，距離変更（短縮，なし，延長），間隔
            course_change_flag = 0
            distance_change_flag = 0
            jockey_change_flag = 0
            step = 0

            if pre_race_list[0] != "0":
                # 出走間隔の取得
                year = keiba_data.loc[i, "year"]
                month = keiba_data.loc[i, "month"]
                day = keiba_data.loc[i, "day"]
                current_race_day = datetime.date(year, month, day)

                year_p1 = all_data.loc[pre_race1_index[0], "year"]
                month_p1 = all_data.loc[pre_race1_index[0], "month"]
                day_p1 = all_data.loc[pre_race1_index[0], "day"]
                print(year_p1, month_p1, day_p1)
                pre_race_day = datetime.date(int(year_p1), int(month_p1), int(day_p1))
                step = (current_race_day - pre_race_day).days

                # ダ芝変わり，距離変わり，乗り替わり
                current_course = keiba_data.loc[i, "course"]
                p1_course = all_data.loc[pre_race1_index[0], "course"]
                current_distance = int(keiba_data.loc[i, "distance"])
                p1_distance = int(all_data.loc[pre_race1_index[0], "distance"])
                print(current_distance, p1_distance)
                current_jockey = keiba_data.loc[i, "jockey"]
                p1_jockey = all_data.loc[pre_race1_index[0], "jockey"]
                if current_course != p1_course:
                    if current_course == "ダ":
                        course_change_flag = 1
                    if current_course == "芝":
                        course_change_flag = 2
                if current_distance > p1_distance:
                    distance_change_flag = 1
                if current_distance < p1_distance:
                    distance_change_flag = 2
                if current_jockey == p1_jockey:
                    jockey_change_flag = 1

            keiba_data.loc[i, "step"] = step
            keiba_data.loc[i, "course_change_flag"] = course_change_flag
            keiba_data.loc[i, "distance_change_flag"] = distance_change_flag
            keiba_data.loc[i, "jockey_change_flag"] = jockey_change_flag

            for j in range(0, len(pre_race_list)):
                index = all_data.index[
                    (all_data["race_id"] == pre_race_list[j])
                    & (all_data["horse_id"] == keiba_data.loc[i, "horse_id"])
                ]
                columns_str = "_p" + str(j + 1)
                if len(index) == 0:
                    keiba_data.loc[i, "place" + columns_str] = np.nan
                    keiba_data.loc[i, "year" + columns_str] = np.nan
                    keiba_data.loc[i, "month" + columns_str] = np.nan
                    keiba_data.loc[i, "day" + columns_str] = np.nan
                    keiba_data.loc[i, "race_name" + columns_str] = np.nan
                    keiba_data.loc[i, "class" + columns_str] = np.nan
                    keiba_data.loc[i, "course" + columns_str] = np.nan
                    keiba_data.loc[i, "turn" + columns_str] = np.nan
                    keiba_data.loc[i, "distance" + columns_str] = np.nan
                    keiba_data.loc[i, "weather" + columns_str] = np.nan
                    keiba_data.loc[i, "state" + columns_str] = np.nan
                    keiba_data.loc[i, "headcount" + columns_str] = np.nan
                    keiba_data.loc[i, "rank" + columns_str] = np.nan
                    keiba_data.loc[i, "lane_gate" + columns_str] = np.nan
                    keiba_data.loc[i, "horse_gate" + columns_str] = np.nan
                    keiba_data.loc[i, "handiy" + columns_str] = np.nan
                    keiba_data.loc[i, "popular_rank" + columns_str] = np.nan
                    keiba_data.loc[i, "odds" + columns_str] = np.nan
                    keiba_data.loc[i, "agari" + columns_str] = np.nan
                    keiba_data.loc[i, "agari_rank" + columns_str] = np.nan
                    keiba_data.loc[i, "time_index" + columns_str] = np.nan
                    keiba_data.loc[i, "jockey" + columns_str] = np.nan
                    keiba_data.loc[i, "horse_type" + columns_str] = np.nan
                    keiba_data.loc[i, "corner_position1" + columns_str] = np.nan
                    keiba_data.loc[i, "corner_position2" + columns_str] = np.nan
                    keiba_data.loc[i, "corner_position3" + columns_str] = np.nan
                    keiba_data.loc[i, "corner_position4" + columns_str] = np.nan

                    keiba_data.loc[i, "class_code" + columns_str] = np.nan
                    keiba_data.loc[i, "grade_code" + columns_str] = np.nan
                    keiba_data.loc[i, "track_code" + columns_str] = np.nan
                    keiba_data.loc[i, "track_code2" + columns_str] = np.nan
                    keiba_data.loc[i, "corner_count" + columns_str] = np.nan
                    keiba_data.loc[i, "course_class" + columns_str] = np.nan
                    keiba_data.loc[i, "race_prize" + columns_str] = np.nan
                    keiba_data.loc[i, "rpci" + columns_str] = np.nan
                    keiba_data.loc[i, "pci3" + columns_str] = np.nan
                    keiba_data.loc[i, "race_type_code" + columns_str] = np.nan
                    keiba_data.loc[i, "race_symbol_code" + columns_str] = np.nan
                    keiba_data.loc[i, "weight_type_code" + columns_str] = np.nan
                    keiba_data.loc[i, "race_type_code" + columns_str] = np.nan
                    keiba_data.loc[i, "weight_type_code" + columns_str] = np.nan
                    keiba_data.loc[i, "blinkers" + columns_str] = np.nan
                    keiba_data.loc[i, "rank_offical" + columns_str] = np.nan
                    keiba_data.loc[i, "rank_arrival" + columns_str] = np.nan
                    keiba_data.loc[i, "abnormal_code" + columns_str] = np.nan

                    keiba_data.loc[i, "time_diff" + columns_str] = np.nan

                    keiba_data.loc[i, "ave_3f" + columns_str] = np.nan
                    keiba_data.loc[i, "pci" + columns_str] = np.nan
                    keiba_data.loc[i, "minus_3f" + columns_str] = np.nan

                else:
                    index = index[0]
                    keiba_data.loc[i, "place" + columns_str] = all_data.loc[
                        index, "place"
                    ]
                    keiba_data.loc[i, "year" + columns_str] = all_data.loc[
                        index, "year"
                    ]
                    keiba_data.loc[i, "month" + columns_str] = all_data.loc[
                        index, "month"
                    ]
                    keiba_data.loc[i, "day" + columns_str] = all_data.loc[index, "day"]
                    keiba_data.loc[i, "race_name" + columns_str] = all_data.loc[
                        index, "race_name"
                    ]
                    keiba_data.loc[i, "class" + columns_str] = all_data.loc[
                        index, "class"
                    ]
                    keiba_data.loc[i, "course" + columns_str] = all_data.loc[
                        index, "course"
                    ]
                    keiba_data.loc[i, "turn" + columns_str] = all_data.loc[
                        index, "turn"
                    ]
                    keiba_data.loc[i, "distance" + columns_str] = all_data.loc[
                        index, "distance"
                    ]
                    keiba_data.loc[i, "weather" + columns_str] = all_data.loc[
                        index, "weather"
                    ]
                    keiba_data.loc[i, "state" + columns_str] = all_data.loc[
                        index, "state"
                    ]
                    keiba_data.loc[i, "headcount" + columns_str] = all_data.loc[
                        index, "headcount"
                    ]
                    keiba_data.loc[i, "rank" + columns_str] = all_data.loc[
                        index, "rank"
                    ]
                    keiba_data.loc[i, "lane_gate" + columns_str] = all_data.loc[
                        index, "lane_gate"
                    ]
                    keiba_data.loc[i, "horse_gate" + columns_str] = all_data.loc[
                        index, "horse_gate"
                    ]
                    keiba_data.loc[i, "handiy" + columns_str] = all_data.loc[
                        index, "handiy"
                    ]
                    keiba_data.loc[i, "popular_rank" + columns_str] = all_data.loc[
                        index, "popular_rank"
                    ]
                    keiba_data.loc[i, "odds" + columns_str] = all_data.loc[
                        index, "odds"
                    ]
                    keiba_data.loc[i, "agari" + columns_str] = all_data.loc[
                        index, "agari"
                    ]
                    keiba_data.loc[i, "agari_rank" + columns_str] = all_data.loc[
                        index, "agari_rank"
                    ]
                    keiba_data.loc[i, "time_index" + columns_str] = all_data.loc[
                        index, "time_index"
                    ]
                    keiba_data.loc[i, "jockey" + columns_str] = all_data.loc[
                        index, "jockey"
                    ]
                    keiba_data.loc[i, "horse_type" + columns_str] = all_data.loc[
                        index, "horse_type"
                    ]
                    keiba_data.loc[i, "corner_position1" + columns_str] = all_data.loc[
                        index, "corner_position1"
                    ]
                    keiba_data.loc[i, "corner_position2" + columns_str] = all_data.loc[
                        index, "corner_position2"
                    ]
                    keiba_data.loc[i, "corner_position3" + columns_str] = all_data.loc[
                        index, "corner_position3"
                    ]
                    keiba_data.loc[i, "corner_position4" + columns_str] = all_data.loc[
                        index, "corner_position4"
                    ]

                    keiba_data.loc[i, "class_code" + columns_str] = all_data.loc[
                        index, "class_code"
                    ]
                    keiba_data.loc[i, "grade_code" + columns_str] = all_data.loc[
                        index, "grade_code"
                    ]
                    keiba_data.loc[i, "track_code" + columns_str] = all_data.loc[
                        index, "track_code"
                    ]
                    keiba_data.loc[i, "track_code2" + columns_str] = all_data.loc[
                        index, "track_code2"
                    ]
                    keiba_data.loc[i, "corner_count" + columns_str] = all_data.loc[
                        index, "corner_count"
                    ]
                    keiba_data.loc[i, "course_class" + columns_str] = all_data.loc[
                        index, "course_class"
                    ]
                    keiba_data.loc[i, "race_prize" + columns_str] = all_data.loc[
                        index, "race_prize"
                    ]
                    keiba_data.loc[i, "rpci" + columns_str] = all_data.loc[
                        index, "rpci"
                    ]
                    keiba_data.loc[i, "pci3" + columns_str] = all_data.loc[
                        index, "pci3"
                    ]
                    keiba_data.loc[i, "race_type_code" + columns_str] = all_data.loc[
                        index, "race_type_code"
                    ]
                    keiba_data.loc[i, "race_symbol_code" + columns_str] = all_data.loc[
                        index, "race_symbol_code"
                    ]
                    keiba_data.loc[i, "weight_type_code" + columns_str] = all_data.loc[
                        index, "weight_type_code"
                    ]
                    keiba_data.loc[i, "race_type_code" + columns_str] = all_data.loc[
                        index, "race_type_code"
                    ]
                    keiba_data.loc[i, "weight_type_code" + columns_str] = all_data.loc[
                        index, "weight_type_code"
                    ]
                    keiba_data.loc[i, "blinkers" + columns_str] = all_data.loc[
                        index, "blinkers"
                    ]
                    keiba_data.loc[i, "rank_offical" + columns_str] = all_data.loc[
                        index, "rank_offical"
                    ]
                    keiba_data.loc[i, "rank_arrival" + columns_str] = all_data.loc[
                        index, "rank_arrival"
                    ]
                    keiba_data.loc[i, "abnormal_code" + columns_str] = all_data.loc[
                        index, "abnormal_code"
                    ]

                    keiba_data.loc[i, "time_diff" + columns_str] = all_data.loc[
                        index, "time_diff"
                    ]

                    keiba_data.loc[i, "ave_3f" + columns_str] = all_data.loc[
                        index, "ave_3f"
                    ]
                    keiba_data.loc[i, "pci" + columns_str] = all_data.loc[index, "pci"]
                    keiba_data.loc[i, "minus_3f" + columns_str] = all_data.loc[
                        index, "minus_3f"
                    ]

        agari_data = keiba_data[
            [
                "agari_rank_p1",
                "agari_rank_p2",
                "agari_rank_p3",
                "agari_rank_p4",
                "agari_rank_p5",
            ]
        ]
        agari_data["agari_rank_ave"] = agari_data.mean(axis="columns")

        time_index_data = keiba_data[
            [
                "time_index_p1",
                "time_index_p2",
                "time_index_p3",
                "time_index_p4",
                "time_index_p5",
            ]
        ]
        time_index_data["time_index_ave"] = time_index_data[time_index_data != 0].mean(
            axis="columns"
        )
        time_index_data["time_index_max"] = time_index_data.max(axis="columns")
        time_index_data["time_index_min"] = time_index_data.min(axis="columns")

        horse_type_data = keiba_data[
            [
                "horse_type_p1",
                "horse_type_p2",
                "horse_type_p3",
                "horse_type_p4",
                "horse_type_p5",
            ]
        ]
        horse_type_data["ave_horse_type"] = horse_type_data.mean(axis="columns")
        horse_type_data_bool = horse_type_data == 1
        horse_type_data["count_nige"] = horse_type_data_bool.sum(axis="columns") / 5

        keiba_data["agari_rank_ave"] = agari_data["agari_rank_ave"]
        keiba_data["time_index_ave"] = time_index_data["time_index_ave"]
        keiba_data["time_index_max"] = time_index_data["time_index_max"]
        keiba_data["time_index_min"] = time_index_data["time_index_min"]
        keiba_data["count_nige"] = horse_type_data["count_nige"]
        keiba_data["ave_horse_type"] = horse_type_data["ave_horse_type"]

        keiba_data = keiba_data.reset_index(drop=True)
        keiba_data.to_csv(
            RACECARD_DIR / self.date / self.race_id / f"{self.race_id}_c.csv",
            index=False,
            sep=",",
            encoding="cp932",
        )

    def make_encode_pickle():
        keiba_data = pd.read_csv(
            RACE_ALL_CSV,
            sep=",",
            encoding="cp932",
            dtype={
                "class_code": object,
                "track_code": object,
                "track_code2": object,
                "race_type_code": object,
                "weight_type_code": object,
                "abnormal_code": object,
            },
        )

        keiba_data = keiba_data.replace({"None": "NoneData"})
        le = preprocessing.LabelEncoder()
        keiba_data["class"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["class"])
        pickle.dump(le, open(ENCODE_DIR / "class.pickle", "wb"))
        keiba_data["course"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["course"])
        pickle.dump(le, open(ENCODE_DIR / "course.pickle", "wb"))
        keiba_data["turn"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["turn"])
        pickle.dump(le, open(ENCODE_DIR / "turn.pickle", "wb"))
        keiba_data["weather"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["weather"])
        pickle.dump(le, open(ENCODE_DIR / "weather.pickle", "wb"))
        keiba_data["state"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["state"])
        pickle.dump(le, open(ENCODE_DIR / "state.pickle", "wb"))
        keiba_data["sex"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["sex"])
        pickle.dump(le, open(ENCODE_DIR / "sex.pickle", "wb"))
        keiba_data["kanri"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["kanri"])
        pickle.dump(le, open(ENCODE_DIR / "kanri.pickle", "wb"))
        keiba_data["jockey"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["jockey"])
        pickle.dump(le, open(ENCODE_DIR / "jockey.pickle", "wb"))
        keiba_data["trainer"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["trainer"])
        pickle.dump(le, open(ENCODE_DIR / "trainer.pickle", "wb"))
        keiba_data["banusi"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["banusi"])
        pickle.dump(le, open(ENCODE_DIR / "banusi.pickle", "wb"))
        keiba_data["breeder"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["breeder"])
        pickle.dump(le, open(ENCODE_DIR / "breeder.pickle", "wb"))
        keiba_data["father"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["father"])
        pickle.dump(le, open(ENCODE_DIR / "father.pickle", "wb"))
        keiba_data["father_father"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["father_father"])
        pickle.dump(le, open(ENCODE_DIR / "father_father.pickle", "wb"))
        keiba_data["father_mother"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["father_mother"])
        pickle.dump(le, open(ENCODE_DIR / "father_mother.pickle", "wb"))
        keiba_data["mother"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["mother"])
        pickle.dump(le, open(ENCODE_DIR / "mother.pickle", "wb"))
        keiba_data["mother_father"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["mother_father"])
        pickle.dump(le, open(ENCODE_DIR / "mother_father.pickle", "wb"))
        keiba_data["mother_mother"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["mother_mother"])
        pickle.dump(le, open(ENCODE_DIR / "mother_mother.pickle", "wb"))
        keiba_data["class_code"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["class_code"])
        pickle.dump(le, open(ENCODE_DIR / "class_code.pickle", "wb"))
        keiba_data["grade_code"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["grade_code"])
        pickle.dump(le, open(ENCODE_DIR / "grade_code.pickle", "wb"))
        keiba_data["track_code"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["track_code"])
        pickle.dump(le, open(ENCODE_DIR / "track_code.pickle", "wb"))
        keiba_data["track_code2"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["track_code2"])
        pickle.dump(le, open(ENCODE_DIR / "track_code2.pickle", "wb"))
        keiba_data["course_class"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["course_class"])
        pickle.dump(le, open(ENCODE_DIR / "course_class.pickle", "wb"))
        keiba_data["race_type_code"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["race_type_code"])
        pickle.dump(le, open(ENCODE_DIR / "race_type_code.pickle", "wb"))
        keiba_data["race_symbol_code"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["race_symbol_code"])
        pickle.dump(le, open(ENCODE_DIR / "race_symbol_code.pickle", "wb"))
        keiba_data["weight_type_code"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["weight_type_code"])
        pickle.dump(le, open(ENCODE_DIR / "weight_type_code.pickle", "wb"))
        keiba_data["blinkers"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["blinkers"])
        pickle.dump(le, open(ENCODE_DIR / "blinkers.pickle", "wb"))
        keiba_data["abnormal_code"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["abnormal_code"])
        pickle.dump(le, open(ENCODE_DIR / "abnormal_code.pickle", "wb"))
        keiba_data["father_type"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["father_type"])
        pickle.dump(le, open(ENCODE_DIR / "father_type.pickle", "wb"))
        keiba_data["mother_father_type"].fillna("NoneData", inplace=True)
        le.fit_transform(keiba_data["mother_father_type"])
        pickle.dump(le, open(ENCODE_DIR / "mother_father_type.pickle", "wb"))

    def make_new_column():
        keiba_data = pd.read_csv(
            RESULT_PROCESS_DIR / "race_15-21_c2.csv",
            sep=",",
            encoding="cp932",
            dtype={
                "horse_id": object,
                "race_id": object,
                "pre_race1": object,
                "pre_race2": object,
                "pre_race3": object,
                "pre_race4": object,
                "pre_race5": object,
                "class_code": object,
                "track_code": object,
                "track_code2": object,
                "race_type_code": object,
                "weight_type_code": object,
                "abnormal_code": object,
            },
        )

        # agari_data = keiba_data.loc[:,['agari_rank_p1','agari_rank_p2','agari_rank_p3','agari_rank_p4','agari_rank_p5']]
        # agari_data['agari_rank_ave'] = agari_data.mean(axis='columns')

        time_index_data = keiba_data.loc[
            :,
            [
                "time_index_p1",
                "time_index_p2",
                "time_index_p3",
                "time_index_p4",
                "time_index_p5",
            ],
        ]
        time_index_data["time_index_ave"] = time_index_data[time_index_data != 0].mean(
            axis="columns"
        )
        time_index_data["time_index_max"] = time_index_data.max(axis="columns")
        time_index_data["time_index_min"] = time_index_data.min(axis="columns")

        horse_type_data = keiba_data.loc[
            :,
            [
                "horse_type_p1",
                "horse_type_p2",
                "horse_type_p3",
                "horse_type_p4",
                "horse_type_p5",
            ],
        ]
        horse_type_data["ave_horse_type"] = horse_type_data.mean(axis="columns")
        horse_type_data_bool = horse_type_data == 1
        horse_type_data["count_nige"] = horse_type_data_bool.sum(axis="columns") / 5

        rank_data = keiba_data["rank"]
        rank_data_win = rank_data == "1"
        rank_data_win = rank_data_win.replace({False: 0, True: 1})
        rank_data_quinella = (rank_data == "1") | (rank_data == "2")
        rank_data_quinella = rank_data_quinella.replace({False: 0, True: 1})
        rank_data_place = (rank_data == "1") | (rank_data == "2") | (rank_data == "3")
        rank_data_place = rank_data_place.replace({False: 0, True: 1})

        keiba_data["rank_Win"] = rank_data_win
        keiba_data["rank_Quinella"] = rank_data_quinella
        keiba_data["rank_Place"] = rank_data_place

        # keiba_data['agari_rank_ave'] = agari_data['agari_rank_ave']
        keiba_data["time_index_ave"] = time_index_data["time_index_ave"]
        keiba_data["time_index_max"] = time_index_data["time_index_max"]
        keiba_data["time_index_min"] = time_index_data["time_index_min"]
        keiba_data["count_nige"] = horse_type_data["count_nige"]
        keiba_data["ave_horse_type"] = horse_type_data["ave_horse_type"]

        keiba_data.to_csv(
            RESULT_PROCESS_DIR / "race_15-21_c2.csv", sep=",", encoding="cp932"
        )

    def encode_use_LabelEncoder(self):
        # print("データを変換します")

        keiba_data = pd.read_csv(
            RACECARD_DIR / self.date / self.race_id / f"{self.race_id}_c.csv",
            sep=",",
            encoding="cp932",
            dtype={
                "race_symbol_code_p1": object,
                "race_symbol_code_p2": object,
                "race_symbol_code_p3": object,
                "race_symbol_code_p4": str,
                "race_symbol_code_p5": str,
                "horse_id": object,
                "race_id": object,
                "pre_race1": object,
                "pre_race2": object,
                "pre_race3": object,
                "pre_race4": object,
                "pre_race5": object,
            },
        )

        # keiba_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\result\\process\\race_15-21_c.csv", sep=",", encoding="cp932",\
        #                      dtype={'course':str,'horse_id':object,'race_id':object,'pre_race1':object,'pre_race2':object,'pre_race3':object,'pre_race4':object,'pre_race5':object,\
        #                            'class_code':object,'track_code':object,'track_code2':object,'race_type_code':object,'weight_type_code':object,'abnormal_code':object})

        columns = [
            "course",
            "class",
            "turn",
            "weather",
            "state",
            "jockey",
            "class_code",
            "grade_code",
            "track_code",
            "track_code2",
            "course_class",
            "race_type_code",
            "race_symbol_code",
            "weight_type_code",
            "blinkers",
            "abnormal_code",
        ]
        columns = [
            "course",
            "class",
            "turn",
            "weather",
            "state",
            "jockey",
            "grade_code",
            "course_class",
            "race_symbol_code",
            "blinkers",
        ]
        # columns = ['course','class','turn','weather','state','jockey','grade_code','blinkers','course_class','race_symbol_code']
        columns_ex = ["course", "class", "turn", "weather", "state", "jockey"]

        le = pickle.load(open(ENCODE_DIR / "class.pickle", "rb"))

        keiba_data["class"] = keiba_data["class"].replace(
            {"２": "2", "３": "3", "４": "4", "１": "1", "５": "5", "６": "6"},
            regex=True,
        )
        if type(keiba_data["class_p1"][0]) != np.float64:
            keiba_data["class_p1"] = keiba_data["class_p1"].replace(
                {"２": "2", "３": "3", "４": "4", "１": "1", "５": "5", "６": "6"},
                regex=True,
            )
        if type(keiba_data["class_p2"][0]) != np.float64:
            keiba_data["class_p2"] = keiba_data["class_p2"].replace(
                {"２": "2", "３": "3", "４": "4", "１": "1", "５": "5", "６": "6"},
                regex=True,
            )
        if type(keiba_data["class_p3"][0]) != np.float64:
            keiba_data["class_p3"] = keiba_data["class_p3"].replace(
                {"２": "2", "３": "3", "４": "4", "１": "1", "５": "5", "６": "6"},
                regex=True,
            )
        if type(keiba_data["class_p4"][0]) != np.float64:
            keiba_data["class_p4"] = keiba_data["class_p4"].replace(
                {"２": "2", "３": "3", "４": "4", "１": "1", "５": "5", "６": "6"},
                regex=True,
            )
        if type(keiba_data["class_p5"][0]) != np.float64:
            keiba_data["class_p5"] = keiba_data["class_p5"].replace(
                {"２": "2", "３": "3", "４": "4", "１": "1", "５": "5", "６": "6"},
                regex=True,
            )

        keiba_data["state"] = keiba_data["state"].replace({"稍": "稍重"})
        if type(keiba_data["state_p1"][0]) != np.float64:
            keiba_data["state_p1"] = keiba_data["state_p1"].replace({"稍": "稍重"})
        if type(keiba_data["state_p2"][0]) != np.float64:
            keiba_data["state_p2"] = keiba_data["state_p2"].replace({"稍": "稍重"})
        if type(keiba_data["state_p3"][0]) != np.float64:
            keiba_data["state_p3"] = keiba_data["state_p3"].replace({"稍": "稍重"})
        if type(keiba_data["state_p4"][0]) != np.float64:
            keiba_data["state_p4"] = keiba_data["state_p4"].replace({"稍": "稍重"})
        if type(keiba_data["state_p5"][0]) != np.float64:
            keiba_data["state_p5"] = keiba_data["state_p5"].replace({"稍": "稍重"})

        keiba_data["turn"] = keiba_data["turn"].replace({"右 外": "右外"}, regex=True)

        for column in columns:
            print(column)
            le = pickle.load(open(ENCODE_DIR / f"{column}.pickle", "rb"))
            if column in columns_ex:
                keiba_data[column] = keiba_data[column].astype(str)
                keiba_data[column].fillna("NoneData", inplace=True)
                keiba_data[column] = le.transform(keiba_data[column])

            keiba_data[column + "_p1"] = keiba_data[column + "_p1"].astype(str)
            keiba_data[column + "_p2"] = keiba_data[column + "_p2"].astype(str)
            keiba_data[column + "_p3"] = keiba_data[column + "_p3"].astype(str)
            keiba_data[column + "_p4"] = keiba_data[column + "_p4"].astype(str)
            keiba_data[column + "_p5"] = keiba_data[column + "_p5"].astype(str)

            keiba_data[column + "_p1"] = keiba_data[column + "_p1"].replace(
                {"nan": "NoneData"}
            )
            keiba_data[column + "_p2"] = keiba_data[column + "_p2"].replace(
                {"nan": "NoneData"}
            )
            keiba_data[column + "_p3"] = keiba_data[column + "_p3"].replace(
                {"nan": "NoneData"}
            )
            keiba_data[column + "_p4"] = keiba_data[column + "_p4"].replace(
                {"nan": "NoneData"}
            )
            keiba_data[column + "_p5"] = keiba_data[column + "_p5"].replace(
                {"nan": "NoneData"}
            )
            keiba_data[column + "_p1"] = keiba_data[column + "_p1"].replace(
                {"None": "NoneData"}
            )
            keiba_data[column + "_p2"] = keiba_data[column + "_p2"].replace(
                {"None": "NoneData"}
            )
            keiba_data[column + "_p3"] = keiba_data[column + "_p3"].replace(
                {"None": "NoneData"}
            )
            keiba_data[column + "_p4"] = keiba_data[column + "_p4"].replace(
                {"None": "NoneData"}
            )
            keiba_data[column + "_p5"] = keiba_data[column + "_p5"].replace(
                {"None": "NoneData"}
            )

            if column == "race_symbol_code":
                keiba_data[column + "_p1"] = keiba_data[column + "_p1"].replace(
                    {"000": "0"}
                )
                keiba_data[column + "_p2"] = keiba_data[column + "_p2"].replace(
                    {"000": "0"}
                )
                keiba_data[column + "_p3"] = keiba_data[column + "_p3"].replace(
                    {"000": "0"}
                )
                keiba_data[column + "_p4"] = keiba_data[column + "_p4"].replace(
                    {"000": "0"}
                )
                keiba_data[column + "_p5"] = keiba_data[column + "_p5"].replace(
                    {"000": "0"}
                )
                keiba_data[column + "_p1"] = keiba_data[column + "_p1"].replace(
                    {"020": "20"}
                )
                keiba_data[column + "_p2"] = keiba_data[column + "_p2"].replace(
                    {"020": "20"}
                )
                keiba_data[column + "_p3"] = keiba_data[column + "_p3"].replace(
                    {"020": "20"}
                )
                keiba_data[column + "_p4"] = keiba_data[column + "_p4"].replace(
                    {"020": "20"}
                )
                keiba_data[column + "_p5"] = keiba_data[column + "_p5"].replace(
                    {"020": "20"}
                )
                keiba_data[column + "_p1"] = keiba_data[column + "_p1"].replace(
                    {"002": "2"}
                )
                keiba_data[column + "_p2"] = keiba_data[column + "_p2"].replace(
                    {"002": "2"}
                )
                keiba_data[column + "_p3"] = keiba_data[column + "_p3"].replace(
                    {"002": "2"}
                )
                keiba_data[column + "_p4"] = keiba_data[column + "_p4"].replace(
                    {"002": "2"}
                )
                keiba_data[column + "_p5"] = keiba_data[column + "_p5"].replace(
                    {"002": "20"}
                )

            keiba_data[column + "_p1"] = le.transform(keiba_data[column + "_p1"])
            keiba_data[column + "_p2"] = le.transform(keiba_data[column + "_p2"])
            keiba_data[column + "_p3"] = le.transform(keiba_data[column + "_p3"])
            keiba_data[column + "_p4"] = le.transform(keiba_data[column + "_p4"])
            keiba_data[column + "_p5"] = le.transform(keiba_data[column + "_p5"])

        # print('rank')
        # keiba_data["rank"] = keiba_data["rank"].astype(str)
        # keiba_data['rank'] = keiba_data['rank'].replace({'中':-1,'取':-2,'除':-3,'失':-4})
        keiba_data["rank_p1"] = keiba_data["rank_p1"].astype(str)
        keiba_data["rank_p1"] = keiba_data["rank_p1"].replace(
            {"中": -1, "取": -2, "除": -3, "失": -4}
        )
        keiba_data["rank_p1"] = keiba_data["rank_p1"].str.strip("(降)")
        keiba_data["rank_p2"] = keiba_data["rank_p2"].astype(str)
        keiba_data["rank_p2"] = keiba_data["rank_p2"].replace(
            {"中": -1, "取": -2, "除": -3, "失": -4}
        )
        keiba_data["rank_p2"] = keiba_data["rank_p2"].str.strip("(降)")
        keiba_data["rank_p3"] = keiba_data["rank_p3"].astype(str)
        keiba_data["rank_p3"] = keiba_data["rank_p3"].replace(
            {"中": -1, "取": -2, "除": -3, "失": -4}
        )
        keiba_data["rank_p3"] = keiba_data["rank_p3"].str.strip("(降)")
        keiba_data["rank_p4"] = keiba_data["rank_p4"].astype(str)
        keiba_data["rank_p4"] = keiba_data["rank_p4"].replace(
            {"中": -1, "取": -2, "除": -3, "失": -4}
        )
        keiba_data["rank_p4"] = keiba_data["rank_p4"].str.strip("(降)")
        keiba_data["rank_p5"] = keiba_data["rank_p5"].astype(str)
        keiba_data["rank_p5"] = keiba_data["rank_p5"].replace(
            {"中": -1, "取": -2, "除": -3, "失": -4}
        )
        keiba_data["rank_p5"] = keiba_data["rank_p5"].str.strip("(降)")

        # print('odds')
        keiba_data["odds"] = keiba_data["odds"].astype(str)
        keiba_data["odds_p1"] = keiba_data["odds_p1"].astype(str)
        keiba_data["odds_p2"] = keiba_data["odds_p2"].astype(str)
        keiba_data["odds_p3"] = keiba_data["odds_p3"].astype(str)
        keiba_data["odds_p4"] = keiba_data["odds_p4"].astype(str)
        keiba_data["odds_p5"] = keiba_data["odds_p5"].astype(str)

        keiba_data["odds"] = keiba_data["odds"].replace({"---": ""})
        keiba_data["odds_p1"] = keiba_data["odds_p1"].replace({"---": ""})
        keiba_data["odds_p2"] = keiba_data["odds_p2"].replace({"---": ""})
        keiba_data["odds_p3"] = keiba_data["odds_p3"].replace({"---": ""})
        keiba_data["odds_p4"] = keiba_data["odds_p4"].replace({"---": ""})
        keiba_data["odds_p5"] = keiba_data["odds_p5"].replace({"---": ""})

        keiba_data["place"] = keiba_data["place"].replace(
            (r"[a-zA-Z]."), "12", regex=True
        )
        keiba_data["place_p1"] = keiba_data["place_p1"].replace(
            (r"[a-zA-Z]."), "12", regex=True
        )
        keiba_data["place_p2"] = keiba_data["place_p2"].replace(
            (r"[a-zA-Z]."), "12", regex=True
        )
        keiba_data["place_p3"] = keiba_data["place_p3"].replace(
            (r"[a-zA-Z]."), "12", regex=True
        )
        keiba_data["place_p4"] = keiba_data["place_p4"].replace(
            (r"[a-zA-Z]."), "12", regex=True
        )
        keiba_data["place_p5"] = keiba_data["place_p5"].replace(
            (r"[a-zA-Z]."), "12", regex=True
        )

        # print('time_diff')
        keiba_data["time_diff_p1"] = keiba_data["time_diff_p1"].astype(str)
        keiba_data["time_diff_p2"] = keiba_data["time_diff_p2"].astype(str)
        keiba_data["time_diff_p3"] = keiba_data["time_diff_p3"].astype(str)
        keiba_data["time_diff_p4"] = keiba_data["time_diff_p4"].astype(str)
        keiba_data["time_diff_p5"] = keiba_data["time_diff_p5"].astype(str)

        keiba_data["time_diff_p1"] = keiba_data["time_diff_p1"].replace({"----": ""})
        keiba_data["time_diff_p2"] = keiba_data["time_diff_p2"].replace({"----": ""})
        keiba_data["time_diff_p3"] = keiba_data["time_diff_p3"].replace({"----": ""})
        keiba_data["time_diff_p4"] = keiba_data["time_diff_p4"].replace({"----": ""})
        keiba_data["time_diff_p5"] = keiba_data["time_diff_p5"].replace({"----": ""})

        # print('weight')
        keiba_data["weight"] = keiba_data["weight"].astype(object)
        keiba_data["weight"] = keiba_data["weight"].replace({"計不": ""})

        keiba_data["zougen"] = keiba_data["zougen"].astype(object)
        keiba_data["zougen"] = keiba_data["zougen"].replace({"前計不": ""})

        # print('sex')
        le = pickle.load(open(ENCODE_DIR / "sex.pickle", "rb"))
        keiba_data["sex"] = keiba_data["sex"].astype(object)
        keiba_data["sex"] = le.transform(keiba_data["sex"])

        # print('kanri')
        le = pickle.load(open(ENCODE_DIR / "kanri.pickle", "rb"))
        keiba_data["kanri"] = le.transform(keiba_data["kanri"])

        # print('trainer')
        keiba_data["trainer"].fillna("NoneData", inplace=True)
        le = pickle.load(open(ENCODE_DIR / "trainer.pickle", "rb"))
        keiba_data["trainer"] = le.transform(keiba_data["trainer"])

        # print('banusi')
        keiba_data["banusi"].fillna("NoneData", inplace=True)
        le = pickle.load(open(ENCODE_DIR / "banusi.pickle", "rb"))
        keiba_data["banusi"] = le.transform(keiba_data["banusi"])

        # print('breeder')
        keiba_data["breeder"].fillna("NoneData", inplace=True)
        le = pickle.load(open(ENCODE_DIR / "breeder.pickle", "rb"))
        keiba_data["breeder"] = le.transform(keiba_data["breeder"])

        # print('father')
        keiba_data["father"].fillna("NoneData", inplace=True)
        le = pickle.load(open(ENCODE_DIR / "father.pickle", "rb"))
        keiba_data["father"] = le.transform(keiba_data["father"])

        # print('father_father')
        keiba_data["father_father"].fillna("NoneData", inplace=True)
        le = pickle.load(open(ENCODE_DIR / "father_father.pickle", "rb"))
        keiba_data["father_father"] = le.transform(keiba_data["father_father"])

        # print('father_mother')
        keiba_data["father_mother"].fillna("NoneData", inplace=True)
        le = pickle.load(open(ENCODE_DIR / "father_mother.pickle", "rb"))
        keiba_data["father_mother"] = le.transform(keiba_data["father_mother"])

        # print('mother')
        keiba_data["mother"].fillna("NoneData", inplace=True)
        le = pickle.load(open(ENCODE_DIR / "mother.pickle", "rb"))
        keiba_data["mother"] = le.transform(keiba_data["mother"])

        # print('mother_father')
        keiba_data["mother_father"].fillna("NoneData", inplace=True)
        le = pickle.load(open(ENCODE_DIR / "mother_father.pickle", "rb"))
        keiba_data["mother_father"] = le.transform(keiba_data["mother_father"])

        # print('mother_mother')
        keiba_data["mother_mother"].fillna("NoneData", inplace=True)
        le = pickle.load(open(ENCODE_DIR / "mother_mother.pickle", "rb"))
        keiba_data["mother_mother"] = le.transform(keiba_data["mother_mother"])

        keiba_data = keiba_data.reset_index(drop=True)
        keiba_data.to_csv(
            RACECARD_DIR / self.date / self.race_id / f"{self.race_id}_c2.csv",
            sep=",",
            encoding="cp932",
        )
        # print("データの変換が完了しました")

    def convert_data_old(self):
        keiba_data = pd.read_csv(
            RACECARD_DIR / self.date / self.race_id / f"{self.race_id}_c.csv",
            sep=",",
            encoding="cp932",
            dtype={
                "horse_id": object,
                "race_id": object,
                "pre_race1": object,
                "pre_race2": object,
                "pre_race3": object,
                "pre_race4": object,
                "pre_race5": object,
            },
        )
        convert_table = pd.read_csv(ENCODE_LIST_CSV, sep=",", encoding="Shift_jis")

        for i in range(0, 6):
            pre_str = ""
            if i > 0:
                pre_str = "_p" + str(i)
            if (
                keiba_data["class" + pre_str].dtype == np.int64
                or keiba_data["class" + pre_str].dtype == np.float64
            ):
                continue
            keiba_data = keiba_data.replace(
                {
                    "class"
                    + pre_str: {
                        "None": "",
                        "2歳新馬": 0,
                        "2歳未勝利": 1,
                        "2歳500万下": 2,
                        "2歳1勝クラス": 2,
                        "2歳オープン": 3,
                        "3歳新馬": 4,
                        "3歳未勝利": 5,
                        "3歳500万下": 6,
                        "3歳1勝クラス": 6,
                        "3歳オープン": 7,
                        "3歳以上500万下": 8,
                        "3歳以上1勝クラス": 8,
                        "3歳以上1000万下": 9,
                        "3歳以上2勝クラス": 9,
                        "3歳以上1600万下": 10,
                        "3歳以上3勝クラス": 10,
                        "3歳以上オープン": 11,
                        "4歳以上500万下": 12,
                        "4歳以上1勝クラス": 12,
                        "4歳以上1000万下": 13,
                        "4歳以上2勝クラス": 13,
                        "4歳以上1600万下": 14,
                        "4歳以上3勝クラス": 14,
                        "4歳以上オープン": 15,
                        "障害3歳以上未勝利": 16,
                        "障害3歳以上オープン": 17,
                        "障害4歳以上未勝利": 18,
                        "障害4歳以上オープン": 19,
                    }
                }
            )
            if (
                keiba_data["class" + pre_str].dtype == np.int64
                or keiba_data["class" + pre_str].dtype == np.float64
            ):
                continue
            keiba_data = keiba_data.replace(
                {
                    "class"
                    + pre_str: {
                        "None": "",
                        "２歳新馬": 0,
                        "２歳未勝利": 1,
                        "２歳５００万下": 2,
                        "２歳１勝クラス": 2,
                        "２歳オープン": 3,
                        "３歳新馬": 4,
                        "３歳未勝利": 5,
                        "3歳500万下": 6,
                        "３歳１勝クラス": 6,
                        "３歳オープン": 7,
                        "３歳以上５００万下": 8,
                        "３歳以上１勝クラス": 8,
                        "３歳以上１０００万下": 9,
                        "３歳以上２勝クラス": 9,
                        "３歳以上１６００万下": 10,
                        "３歳以上３勝クラス": 10,
                        "３歳以上オープン": 11,
                        "４歳以上５００万下": 12,
                        "４歳以上１勝クラス": 12,
                        "４歳以上１０００万下": 13,
                        "４歳以上２勝クラス": 13,
                        "４歳以上１６００万下": 14,
                        "４歳以上３勝クラス": 14,
                        "４歳以上オープン": 15,
                        "障害３歳以上未勝利": 16,
                        "障害３歳以上オープン": 17,
                        "障害４歳以上未勝利": 18,
                        "障害４歳以上オープン": 19,
                    }
                }
            )
        if keiba_data["class"].dtype != np.int64:
            keiba_data = keiba_data.replace({"class": {"None": np.nan}})

        for i in range(0, len(convert_table["trainer"])):
            if keiba_data["trainer"].dtype == np.int64:
                break
            if convert_table.loc[i, "trainer"] == "0":
                break
            keiba_data = keiba_data.replace(
                {"trainer": {convert_table.loc[i, "trainer"]: i}}
            )
        keiba_data["trainer"] = pd.to_numeric(keiba_data["trainer"], errors="coerce")

        columns = ["turn", "weather", "course", "state", "jockey"]
        for column in columns:
            pre_str = ""
            for j in range(0, 6):
                if j > 0:
                    pre_str = "_p" + str(j)
                for i in range(0, len(convert_table[column])):
                    if (
                        keiba_data[column + pre_str].dtype == np.int64
                        or keiba_data[column + pre_str].dtype == np.float64
                    ):
                        break
                    if convert_table.loc[i, column] == "0":
                        break
                    keiba_data = keiba_data.replace(
                        {column + pre_str: {convert_table.loc[i, column]: i}}
                    )
                keiba_data[column + pre_str] = pd.to_numeric(
                    keiba_data[column + pre_str], errors="coerce"
                )

        for i in range(0, len(convert_table["sex"])):
            if keiba_data["sex"].dtype == np.int64:
                break
            if convert_table.loc[i, "sex"] == "0":
                break
            keiba_data = keiba_data.replace({"sex": {convert_table.loc[i, "sex"]: i}})

        for i in range(0, len(convert_table["kanri"])):
            if keiba_data["kanri"].dtype == np.int64:
                break
            if convert_table.loc[i, "kanri"] == "0":
                break
            keiba_data = keiba_data.replace(
                {"kanri": {convert_table.loc[i, "kanri"]: i}}
            )

        for i in range(0, len(convert_table["jockey"])):
            if keiba_data["jockey"].dtype == np.int64 or (
                keiba_data["jockey"].dtype == np.float64
            ):
                break
            if convert_table.loc[i, "jockey"] == "0":
                break
            keiba_data = keiba_data.replace(
                {"jockey": {convert_table.loc[i, "jockey"]: i}}
            )
        keiba_data["jockey"] = pd.to_numeric(keiba_data["jockey"], errors="coerce")

        for i in range(0, len(convert_table["banusi"])):
            if keiba_data["banusi"].dtype == np.int64 or (
                keiba_data["banusi"].dtype == np.float64
            ):
                break
            if convert_table.loc[i, "banusi"] == "0":
                break
            keiba_data = keiba_data.replace(
                {"banusi": {convert_table.loc[i, "banusi"]: i}}
            )
        keiba_data["banusi"] = pd.to_numeric(keiba_data["banusi"], errors="coerce")

        for i in range(0, len(convert_table["breeder"])):
            if keiba_data["breeder"].dtype == np.int64 or (
                keiba_data["breeder"].dtype == np.float64
            ):
                break
            if convert_table.loc[i, "breeder"] == "0":
                break
            keiba_data = keiba_data.replace(
                {"breeder": {convert_table.loc[i, "breeder"]: i}}
            )
        keiba_data["breeder"] = pd.to_numeric(keiba_data["breeder"], errors="coerce")

        for i in range(0, len(convert_table["father"])):
            if (keiba_data["father"].dtype == np.int64) or (
                keiba_data["father"].dtype == np.float64
            ):
                break
            if convert_table.loc[i, "father"] == "0":
                break
            keiba_data = keiba_data.replace(
                {"father": {convert_table.loc[i, "father"]: i}}
            )
        keiba_data["father"] = pd.to_numeric(keiba_data["father"], errors="coerce")

        for i in range(0, len(convert_table["father_father"])):
            if keiba_data["father_father"].dtype == np.int64 or (
                keiba_data["father_father"].dtype == np.float64
            ):
                break
            if convert_table.loc[i, "father_father"] == "0":
                break
            keiba_data = keiba_data.replace(
                {"father_father": {convert_table.loc[i, "father_father"]: i}}
            )
        keiba_data["father_father"] = pd.to_numeric(
            keiba_data["father_father"], errors="coerce"
        )

        for i in range(0, len(convert_table["father_mother"])):
            if keiba_data["father_mother"].dtype == np.int64 or (
                keiba_data["father_mother"].dtype == np.float64
            ):
                break
            if convert_table.loc[i, "father_mother"] == "0":
                break
            keiba_data = keiba_data.replace(
                {"father_mother": {convert_table.loc[i, "father_mother"]: i}}
            )
        keiba_data["father_mother"] = pd.to_numeric(
            keiba_data["father_mother"], errors="coerce"
        )

        for i in range(0, len(convert_table["mother"])):
            if keiba_data["mother"].dtype == np.int64 or (
                keiba_data["mother"].dtype == np.float64
            ):
                break
            if convert_table.loc[i, "mother"] == "0":
                break
            keiba_data = keiba_data.replace(
                {"mother": {convert_table.loc[i, "mother"]: i}}
            )
        keiba_data["mother"] = pd.to_numeric(keiba_data["mother"], errors="coerce")

        for i in range(0, len(convert_table["mother_father"])):
            if keiba_data["mother_father"].dtype == np.int64 or (
                keiba_data["mother_father"].dtype == np.float64
            ):
                break
            if convert_table.loc[i, "mother_father"] == "0":
                break
            keiba_data = keiba_data.replace(
                {"mother_father": {convert_table.loc[i, "mother_father"]: i}}
            )
        keiba_data["mother_father"] = pd.to_numeric(
            keiba_data["mother_father"], errors="coerce"
        )

        for i in range(0, len(convert_table["mother_mother"])):
            if keiba_data["mother_mother"].dtype == np.int64 or (
                keiba_data["mother_mother"].dtype == np.float64
            ):
                break
            if convert_table.loc[i, "mother_mother"] == "0":
                break
            keiba_data = keiba_data.replace(
                {"mother_mother": {convert_table.loc[i, "mother_mother"]: i}}
            )
        keiba_data["mother_mother"] = pd.to_numeric(
            keiba_data["mother_mother"], errors="coerce"
        )

        keiba_data["odds"] = pd.to_numeric(keiba_data["odds"], errors="coerce")
        for j in range(1, 6):
            pre_str = "_p" + str(j)
            if not (
                keiba_data["rank" + pre_str].dtype == np.int64
                or (keiba_data["rank" + pre_str].dtype == np.float64)
            ):
                keiba_data["rank" + pre_str] = keiba_data["rank" + pre_str].replace(
                    {"中": -1, "取": -2, "除": -3, "失": -4}
                )
            if not (
                keiba_data["odds" + pre_str].dtype == np.int64
                or (keiba_data["odds" + pre_str].dtype == np.float64)
            ):
                keiba_data["odds" + pre_str] = pd.to_numeric(
                    keiba_data["odds" + pre_str], errors="coerce"
                )

        keiba_data.to_csv(
            RACECARD_DIR / self.date / self.race_id / f"{self.race_id}_c2.csv",
            sep=",",
            encoding="cp932",
        )

    # データの重複を削除する
    def remove_race():
        keiba_data = pd.read_csv(
            RESULT_PROCESS_DIR / "race_2015-2021.csv",
            sep=",",
            encoding="cp932",
            dtype={
                "horse_id": object,
                "race_id": object,
                "pre_race1": object,
                "pre_race2": object,
                "pre_race3": object,
                "pre_race4": object,
                "pre_race5": object,
                "class_code": object,
                "track_code": object,
                "track_code2": object,
                "race_type_code": object,
                "weight_type_code": object,
                "abnormal_code": object,
            },
        )
        remove_data = pd.read_csv(
            RESULT_DIR / "remove_race.csv",
            sep=",",
            encoding="cp932",
            dtype={"race_id": object},
        )

        race_ids = remove_data["race_id"]
        length = len(race_ids)
        for i in range(0, length):
            print(i)
            remove_index = keiba_data.index[keiba_data["race_id"] == race_ids[i]]
            pre_index = remove_index[0]
            remove_lists = []
            for index in remove_index:
                if pre_index + 1 >= index:
                    pre_index = index
                    remove_lists.append(index)
            keiba_data = keiba_data.drop(remove_lists)
            # remove_index = keiba_data.index[keiba_data['race_id'] == race_ids[i]]

        keiba_data.to_csv(
            RESULT_PROCESS_DIR / "race_15-21_c.csv", sep=",", encoding="cp932"
        )


if __name__ == "__main__":
    # PreProcess.make_encode_pickle()
    # PreProcess.encode_use_LabelEncoder("race_15-21")
    # PreProcess.make_new_column()
    # PreProcess.remove_race()
    # pp = PreProcess('20211212','202106050403')
    # pp.encode_use_LabelEncoder()

    race_ids = [
        "202103020102",
        "202145121511",
        "202210020409",
        "202105050111",
        "202205010110",
        "202105050309",
        "202210010309",
        "202105050506",
        "202109050503",
        "202109060709",
        "202207010406",
        "202105050808",
        "202135092009",
        "202130071306",
        "202135110204",
        "202107060510",
        "202135100304",
        "202135081510",
        "202210010205",
        "202105040602",
        "202109040603",
        "202207010510",
        "202106050707",
        "202109050206",
    ]
    pp = PreProcess("", "")
    pp.join_netkeiba_target(race_ids)
