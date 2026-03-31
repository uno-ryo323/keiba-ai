import pickle
from sklearn import preprocessing
import pandas as pd

from ..config import ENCODE_DIR, RESULT_DIR, TARGET_DIR


class encode:
    def make_encode_pickle():
        keiba_data = pd.read_csv(
            RESULT_DIR / "race_jra2.1.csv", sep=",", encoding="cp932"
        )
        columns = [
            "class",
            "course",
            "turn",
            "weather",
            "state",
            "sex",
            "kanri",
            "jockey",
            "trainer",
            "banusi",
            "breeder",
            "father",
            "father_father",
            "father_mother",
            "mother",
            "mother_father",
            "mother_mother",
        ]

        for column in columns:
            le = preprocessing.LabelEncoder()
            keiba_data[column].fillna("NoneData", inplace=True)
            le.fit_transform(keiba_data[column])
            pickle.dump(le, open(ENCODE_DIR / "Ver1.1" / f"{column}.pickle", "wb"))

    def encode_use_LabelEncoder():
        keiba_data = pd.read_csv(
            RESULT_DIR / "race_jra2.1.csv", sep=",", encoding="cp932"
        )
        columns = [
            "class",
            "course",
            "turn",
            "weather",
            "state",
            "sex",
            "kanri",
            "jockey",
            "trainer",
            "banusi",
            "breeder",
            "father",
            "father_father",
            "father_mother",
            "mother",
            "mother_father",
            "mother_mother",
        ]

        for column in columns:
            print(column)
            le = pickle.load(open(ENCODE_DIR / "Ver1.1" / f"{column}.pickle", "rb"))
            keiba_data[column].fillna("NoneData", inplace=True)
            keiba_data[column] = keiba_data[column].astype(object)
            keiba_data[column] = le.transform(keiba_data[column])
        keiba_data.to_csv(RESULT_DIR / "race_jra2.2.csv", sep=",", encoding="cp932")

    # netkeibaとtargetのデータを結合する
    # <param>keiba_data：予測対象レースの前5走のデータ
    def join_netkeiba_target():
        print("targetのデータを結合します")
        netkeiba_data = pd.read_csv(
            RESULT_DIR / "race_jra2.4.csv",
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

        length = len(netkeiba_data)
        for i in range(0, length):
            print(i, length)
            if i <= 570000:
                continue
            year = netkeiba_data.loc[i, "year"]
            year = str(year)[2:4]
            month = netkeiba_data.loc[i, "month"]
            day = netkeiba_data.loc[i, "day"]
            horse_code = netkeiba_data.loc[i, "horse_id"]
            target_data["date"] = target_data["date"].astype(str)
            target_data["month"] = target_data["month"].astype(str)

            index = target_data.index[
                (target_data["year"] == year)
                & (target_data["month"] == month)
                & (target_data["date"] == day)
                & (target_data["horse_code"] == horse_code)
            ]
            index = index[0]

            netkeiba_data.loc[i, "class_code"] = target_data.loc[index, "class_code"]
            netkeiba_data.loc[i, "grade_code"] = target_data.loc[index, "grade_code"]
            netkeiba_data.loc[i, "track_code"] = target_data.loc[index, "track_code"]
            netkeiba_data.loc[i, "track_code2"] = target_data.loc[index, "track_code2"]
            netkeiba_data.loc[i, "corner_count"] = target_data.loc[
                index, "corner_count"
            ]
            netkeiba_data.loc[i, "course_class"] = target_data.loc[
                index, "course_class"
            ]
            netkeiba_data.loc[i, "race_prize"] = target_data.loc[index, "race_prize"]
            netkeiba_data.loc[i, "rpci"] = target_data.loc[index, "rpci"]
            netkeiba_data.loc[i, "pci3"] = target_data.loc[index, "pci3"]
            netkeiba_data.loc[i, "race_type_code"] = target_data.loc[
                index, "race_type_code"
            ]
            netkeiba_data.loc[i, "race_symbol_code"] = target_data.loc[
                index, "race_symbol_code"
            ]
            netkeiba_data.loc[i, "weight_type_code"] = target_data.loc[
                index, "weight_type_code"
            ]
            netkeiba_data.loc[i, "race_type_code"] = target_data.loc[
                index, "race_type_code"
            ]
            netkeiba_data.loc[i, "weight_type_code"] = target_data.loc[
                index, "weight_type_code"
            ]
            netkeiba_data.loc[i, "blinkers"] = target_data.loc[index, "blinkers"]
            netkeiba_data.loc[i, "rank_offical"] = target_data.loc[
                index, "rank_offical"
            ]
            netkeiba_data.loc[i, "rank_arrival"] = target_data.loc[
                index, "rank_arrival"
            ]
            netkeiba_data.loc[i, "abnormal_code"] = target_data.loc[
                index, "abnormal_code"
            ]
            netkeiba_data.loc[i, "time_diff"] = target_data.loc[index, "time_diff"]
            netkeiba_data.loc[i, "ave_3f"] = target_data.loc[index, "ave_3f"]
            netkeiba_data.loc[i, "pci"] = target_data.loc[index, "pci"]
            netkeiba_data.loc[i, "minus_3f"] = target_data.loc[index, "minus_3f"]
            netkeiba_data.loc[i, "father_type"] = target_data.loc[index, "father_type"]
            netkeiba_data.loc[i, "mother_father_type"] = target_data.loc[
                index, "mother_father_type"
            ]
            # if i % 10000 == 0:
            #   netkeiba_data.to_csv("C:\\keibaAI\\Data\\netKeiba\\result\\race_jra2.4.csv", index=False, sep=",", encoding="cp932")
        netkeiba_data.to_csv(
            RESULT_DIR / "race_jra2.4.csv", index=False, sep=",", encoding="cp932"
        )
        print("targetのデータの結合が完了しました")


if __name__ == "__main__":
    # encode.make_encode_pickle()
    # encode.encode_use_LabelEncoder()
    encode.join_netkeiba_target()
