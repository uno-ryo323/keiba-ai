import time
import requests
from bs4 import BeautifulSoup
import re

from config import NETKEIBA_PASSWORD, NETKEIBA_USER, RACE_ALL_CSV, URL_DB, URL_LOGIN


class Scraping:

    def get_race_info(soup, race_id):
        key = [
            "year",
            "month",
            "day",
            "race_name",
            "place",
            "kai",
            "day2",
            "race_num",
            "class",
            "mare_only",
            "handiy",
            "course",
            "turn",
            "distance",
            "weather",
            "state",
        ]
        values = []

        # レース番号
        race_num = race_id[-2:]

        # レース名，年月日
        title = soup.find("title")
        title = str(title).replace("<title>", "")
        tmp = title.replace("｜2", ",2")
        tmp = tmp.split(",")

        race_name = tmp[0]
        date = re.findall(r"\d+", tmp[1])
        year = date[0]
        month = date[1]
        day = date[2]

        # コースタイプ，距離，天候，馬場
        race_info = soup.find("dl", class_="racedata fc")
        race_info = re.sub(r"\n", "", str(race_info))
        race_info = re.sub(r".*<span>", "", str(race_info))
        race_info = re.sub(r"</span>.*", "", str(race_info))
        race_info = str(race_info.replace("/", ","))
        race_info = str(race_info.replace(" 芝 :", ""))
        race_info = str(race_info.replace(" ダート :", ""))
        race_info = str(race_info.replace(" 障害 :", ""))
        race_info = str(race_info.replace(" 天候 :", ""))
        race_info = race_info.replace(" ", "")
        tmp = race_info.split(",")
        tmp2 = re.sub(r"[0-9]*m", "", tmp[0])
        course = tmp2[0]
        turn = tmp2[1:].replace("\xa0", "")
        distance = re.findall(r"\d+", tmp[0])
        weather = tmp[1].replace("\xa0", "")
        state = tmp[2].replace("\xa0", "")

        # 取得しないデータ
        place = race_id[4:6]
        if place.isdigit():
            place = 11
        else:
            place = 12
        kai = ""
        day2 = ""
        class_ = "None"
        mare_only = ""
        handiy = ""

        values.append(year)
        values.append(int(month))
        values.append(day)
        values.append(race_name)
        values.append(place)
        values.append(kai)
        values.append(day2)
        values.append(int(race_num))
        values.append(class_)
        values.append(mare_only)
        values.append(handiy)
        values.append(course)
        values.append(turn)
        values.append(distance[0])
        values.append(weather)
        values.append(state)
        dicts = dict(zip(key, values))
        return dicts

    """get_horse_info
    馬の情報を取得する
    ToDo：海外，地方，JRAごとに振る舞いを変える
    """

    def get_horse_info(horses):
        key = [
            "horse_id",
            "trainer",
            "banusi",
            "breeder",
            "father",
            "father_father",
            "father_mother",
            "mother",
            "mother_father",
            "mother_mother",
            "pre_race1",
            "pre_race2",
            "pre_race3",
            "pre_race4",
            "pre_race5",
        ]
        values = []
        lists = []
        for horse in horses:
            horse_number = horse.find("a")
            if horse_number is None:
                horse_number = ""
            else:
                horse_number = re.sub(r"<a href=", "", str(horse_number))
                horse_number = re.sub(r" id.*", "", horse_number)
                horse_number = horse_number.replace('"', "")
                horse_number = horse_number.replace("/", "")
                horse_number = horse_number.replace("horse", "")

            horse_id = horse_number
            trainer = ""
            banusi = ""
            breeder = ""
            father = ""
            father_father = ""
            father_mother = ""
            mother = ""
            mother_father = ""
            mother_mother = ""
            pre_race1 = "0"
            pre_race2 = "0"
            pre_race3 = "0"
            pre_race4 = "0"
            pre_race5 = "0"

            values.append(horse_id)
            values.append(trainer)
            values.append(banusi)
            values.append(breeder)
            values.append(father)
            values.append(father_father)
            values.append(father_mother)
            values.append(mother)
            values.append(mother_father)
            values.append(mother_mother)
            values.append(pre_race1)
            values.append(pre_race2)
            values.append(pre_race3)
            values.append(pre_race4)
            values.append(pre_race5)

            dicts = dict(zip(key, values))
            lists.append(dicts)
            values.clear()
        return lists

    def get_jockey_info(jockeys, session):
        jockey_info = []
        for jockey in jockeys:
            jockey_number = jockey.find("a")
            if jockey_number is None:
                jockey_info.append("")
            else:
                jockey_number = re.sub(r"<a href=", "", str(jockey_number))
                jockey_number = re.sub(r" id.*", "", jockey_number)
                jockey_number = jockey_number.replace('"', "")
                time.sleep(1)
                res = session.get(URL_DB + jockey_number)
                soup = BeautifulSoup(res.content, "lxml")
                title = soup.find("title")
                title = re.sub(r"騎手データ - netkeiba.com</title>", "", str(title))
                title = re.sub(r" | ", "", title)
                title = re.sub(r"<title>", "", str(title))
                title = title.replace("|", "")
                jockey_info.append(title)
        return jockey_info

    """trim_table
    htmlテーブルを成型するメソッド
    """

    def trim_table(table):
        table = re.sub(r"\n", "", str(table))
        table = re.sub(r" ", "", table)
        table = re.sub(r"</td>", "_", table)
        table = re.sub(r"<[^>]*?>", "", table)
        table = re.sub(r"\[", "", table)
        table = re.sub(r"\]", "", table)
        table = table.replace("\xa0", "")
        table = table.replace(
            "着順枠番馬番馬名性齢斤量騎手タイム着差ﾀｲﾑ指数通過上り単勝人気馬体重調教ﾀｲﾑ厩舎ｺﾒﾝﾄ備考調教師馬主賞金(万円)",
            "",
        )
        tmp = table.split("_")
        return tmp

    def get_leg_type(corner, length):
        tmp = corner.split("-")
        if tmp[0] == "":
            return 0
        tmp = [int(s) for s in tmp]
        horse_type = 0
        sasi = 2 * length / 3
        if 1 in tmp[0:-1]:
            horse_type = 1
        elif tmp[-1] <= 4:
            horse_type = 2
        elif tmp[-1] <= sasi or length <= 8:
            horse_type = 3
        else:
            horse_type = 4
        return horse_type

    def make_record(race_id, table_data, race_info, horse_info, jockey_info):
        records = []
        length = round(len(table_data) / 21)

        head_str = (
            str(race_id)
            + ","
            + str(race_info["year"])
            + ","
            + str(race_info["month"])
            + ","
            + str(race_info["day"])
            + ","
            + race_info["race_name"]
            + ","
            + str(race_info["place"])
            + ","
            + str(race_info["kai"])
            + ","
            + str(race_info["day2"])
            + ","
            + str(race_info["race_num"])
            + ","
            + str(race_info["class"])
            + ","
            + str(race_info["mare_only"])
            + ","
            + str(race_info["handiy"])
            + ","
            + str(race_info["course"])
            + ","
            + str(race_info["turn"])
            + ","
            + str(race_info["distance"])
            + ","
            + race_info["weather"]
            + ","
            + race_info["state"]
            + ","
            + str(length)
        )

        for i in range(0, length):
            rank = table_data[i * 21]
            waku = table_data[21 * i + 1]
            umaban = table_data[21 * i + 2]
            horse_name = table_data[21 * i + 3]
            sex = re.sub(r"\d+", "", table_data[21 * i + 4])
            old = table_data[21 * i + 4].replace(str(sex), "")
            handiycap = table_data[21 * i + 5]
            goal_time = table_data[21 * i + 7]
            tmp2 = str(goal_time).split(":")
            if len(tmp2) == 2:
                goal_time = float(tmp2[0]) * 60 + float(tmp2[1])
            time_index = table_data[21 * i + 9]
            corner = table_data[21 * i + 10]
            corner_position1 = 0
            corner_position2 = 0
            corner_position3 = 0
            corner_position4 = 0
            if len(corner.split("-")) == 4:
                corner_position1 = corner.split("-")[0]
                corner_position2 = corner.split("-")[1]
                corner_position3 = corner.split("-")[2]
                corner_position4 = corner.split("-")[3]
            elif len(corner.split("-")) == 3:
                corner_position2 = corner.split("-")[0]
                corner_position3 = corner.split("-")[1]
                corner_position4 = corner.split("-")[2]
            elif len(corner.split("-")) == 2:
                corner_position3 = corner.split("-")[0]
                corner_position4 = corner.split("-")[1]
            elif len(corner.split("-")) == 1:
                corner_position4 = corner.split("-")[0]
            if corner_position4 == "":
                corner_position4 = 0

            kaku4 = table_data[21 * i + 10].split("-")[-1]
            agari = table_data[21 * i + 11]
            odds = table_data[21 * i + 12]
            rank_popular = table_data[21 * i + 13]
            weight = table_data[21 * i + 14].split("(")[0]
            zougen = (
                table_data[21 * i + 14]
                .replace(str(weight), "")
                .replace("(", "")
                .replace(")", "")
            )
            remarks = table_data[21 * i + 17]
            kanri = ""
            if table_data[21 * i + 18] != "":
                kanri = table_data[21 * i + 18][0]
            leg_type = Scraping.get_leg_type(corner, length)

            record = head_str
            record = (
                record
                + ","
                + str(rank)
                + ","
                + str(waku)
                + ","
                + str(umaban)
                + ","
                + str(horse_name)
                + ","
                + str(sex)
                + ","
                + str(old)
                + ","
                + str(handiycap)
                + ","
                + str(weight)
                + ","
                + str(zougen)
                + ","
                + str(goal_time)
                + ","
                + str(rank_popular)
                + ","
                + str(odds)
                + ","
                + str(agari)
            )
            record = (
                record
                + ","
                + str(corner_position1)
                + ","
                + str(corner_position2)
                + ","
                + str(corner_position3)
                + ","
                + str(corner_position4)
            )
            record = (
                record
                + ","
                + str(time_index)
                + ","
                + str(kanri)
                + ","
                + str(remarks)
                + ","
                + str(leg_type)
                + ","
                + jockey_info[i]
            )
            record = (
                record
                + ","
                + horse_info[i]["trainer"]
                + ","
                + horse_info[i]["banusi"]
                + ","
                + horse_info[i]["breeder"]
                + ","
                + horse_info[i]["father"]
                + ","
                + horse_info[i]["father_father"]
                + ","
                + horse_info[i]["father_mother"]
                + ","
                + horse_info[i]["mother"]
                + ","
                + horse_info[i]["mother_father"]
                + ","
                + horse_info[i]["mother_mother"]
                + ","
                + horse_info[i]["horse_id"]
                + ","
                + horse_info[i]["pre_race1"]
                + ","
                + horse_info[i]["pre_race2"]
                + ","
                + horse_info[i]["pre_race3"]
                + ","
                + horse_info[i]["pre_race4"]
                + ","
                + horse_info[i]["pre_race5"]
            )
            records.append(record)

        return records

    def out_csv(path, records):
        file = open(path, "a")
        for i in range(0, len(records)):
            file.write(records[i] + "\n")

    """get_race_result
    与えられたレースIDの結果を取得してcsv出力するメソッド
    地方競馬と海外競馬の結果取得に利用する
    """

    def get_race_result(race_ids):
        USER = NETKEIBA_USER
        PASS = NETKEIBA_PASSWORD
        login_info = {
            "login_id": USER,
            "pswd": PASS,
        }
        session = requests.session()
        ses = session.post(URL_LOGIN, data=login_info)
        path = str(RACE_ALL_CSV)
        for i in range(0, len(race_ids)):
            race_id = str(race_ids[i])
            if race_id == "0":
                continue
            place = race_id[4:6]
            # print(place)
            if race_id.isdecimal() == True:
                if int(place) < 10:
                    continue

            url = f"{URL_DB}/race/{race_id}/"
            time.sleep(0.5)
            res = session.get(url)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.content, "lxml")
            race_info = Scraping.get_race_info(soup, race_id)
            table = soup.find("table", class_="race_table_01 nk_tb_common")
            td = table.find_all("td")
            horse = [td[i] for i in range(0, len(td)) if (i % 21) == 3]
            jockey = [td[i] for i in range(0, len(td)) if (i % 21) == 6]

            """
            link = table.find_all("a")
            horse_link = [link[i] for i in range(0,len(link)) if "umalink" in str(link[i])]
            jockey_link = [link[i] for i in range(0,len(link)) if "jockey" in str(link[i])]
            """
            horse_info = Scraping.get_horse_info(horse)
            jockey_info = Scraping.get_jockey_info(jockey, session)
            table_data = Scraping.trim_table(table)
            records = Scraping.make_record(
                race_id, table_data, race_info, horse_info, jockey_info
            )
            # print(records)
            Scraping.out_csv(path, records)
