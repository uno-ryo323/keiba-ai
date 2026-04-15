# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 19:11:49 2021

@author: RYO
"""

import requests
import codecs
import time
from bs4 import BeautifulSoup
import re

from ..config import NETKEIBA_PASSWORD, NETKEIBA_USER, RACE_ALL_CSV, URL_DB, URL_LOGIN

"""
レース結果を管理するクラス
次の機能を実装する．
１．レース結果を取得してｃｓｖに出力する
"""


class raceDB:

    USER = NETKEIBA_USER
    PASS = NETKEIBA_PASSWORD

    login_info = {
        "login_id": USER,
        "pswd": PASS,
    }

    url_login = URL_LOGIN

    session = requests.session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
    )
    ses = session.post(url_login, data=login_info)

    PATH = str(RACE_ALL_CSV)

    @staticmethod
    def my_index(list, x, default=-1):
        if x in list:
            return list.index(x)
        else:
            return default

    def get_horse_info(horse_link, race_id, driver):
        bloods = []
        horse_info = []
        return_list = []
        horse_ids = []
        pre_race_lists = []
        # print("------------horse-----------")
        for horse_number in horse_link:
            horse_number = re.sub(r"<a href=", "", str(horse_number))
            horse_number = re.sub(r" id.*", "", horse_number)
            horse_number = horse_number.replace('"', "")
            time.sleep(1.5)
            driver.get(URL_DB + horse_number)

            horse_number = horse_number.replace("/", "")
            horse_number = horse_number.replace("horse", "")
            # print(horse_number)
            horse_ids.append(horse_number)
            soup = BeautifulSoup(driver.page_source, "lxml")

            horse_blood = soup.find("table", {"class": "blood_table"})
            horse_blood = horse_blood.find_all("a")
            horse_prof = soup.find("table", {"class": "db_prof_table no_OwnerUnit"})

            if horse_prof is None:
                horse_prof = soup.find("table", {"class": "db_prof_table"})
            horse_prof = horse_prof.find_all("tr")

            for i in range(1, 5):
                if (
                    "調教師" in str(horse_prof[i])
                    or "馬主" in str(horse_prof[i])
                    or "生産者" in str(horse_prof[i])
                ):
                    horse_prof[i] = str(horse_prof[i]).replace("\n", "")
                    horse_prof[i] = str(horse_prof[i]).replace("<tr>", "")
                    horse_prof[i] = str(horse_prof[i]).replace("</tr>", "")
                    # print(horse_prof[i])
                    horse_prof[i] = re.sub(r"<th>.*</th>", "", str(horse_prof[i]))
                    horse_prof[i] = re.sub(r".*\">", "", str(horse_prof[i]))
                    horse_prof[i] = re.sub(r"</a>", "", str(horse_prof[i]))
                    horse_prof[i] = re.sub(r"</td>", "", str(horse_prof[i]))
                    horse_prof[i] = re.sub(r"<td>", "", str(horse_prof[i]))
                    horse_prof[i] = re.sub(r"\(.*", "", str(horse_prof[i]))
                    #  print(horse_prof[i])
                    horse_info.append(horse_prof[i])
            for blood in horse_blood:
                # <a> タグと <span> タグ（2024年頃追加）を除去して血統名のみ抽出
                blood = blood.get_text(strip=True)
                bloods.append(blood)

            # 前5走の取得

            pre_race_results = soup.find(
                "table", {"class": "db_h_race_results nk_tb_common"}
            )
            pre_race1 = 0
            pre_race2 = 0
            pre_race3 = 0
            pre_race4 = 0
            pre_race5 = 0
            if pre_race_results is not None:
                pre_race_results = pre_race_results.find_all("td")
                pre_race_tags = [
                    str(x) for x in pre_race_results if "/race/20" in str(x)
                ]
                pre_race_tags = [re.sub(r".*/race/", "", x) for x in pre_race_tags]
                pre_race_tags = [re.sub(r"/\".*", "", x) for x in pre_race_tags]

                count = 0
                start = raceDB().my_index(pre_race_tags, race_id) + 1
                careear = len(pre_race_tags) - start
                for j in range(start, len(pre_race_tags)):
                    if count == 0:
                        pre_race1 = pre_race_tags[j]
                    elif count == 1:
                        pre_race2 = pre_race_tags[j]
                    elif count == 2:
                        pre_race3 = pre_race_tags[j]
                    elif count == 3:
                        pre_race4 = pre_race_tags[j]
                    elif count == 4:
                        pre_race5 = pre_race_tags[j]
                        break
                    count = count + 1

            pre_race_lists.append(pre_race1)
            pre_race_lists.append(pre_race2)
            pre_race_lists.append(pre_race3)
            pre_race_lists.append(pre_race4)
            pre_race_lists.append(pre_race5)
            pre_race_lists.append(careear)

        return_list.append(horse_info)
        return_list.append(bloods)
        return_list.append(horse_ids)
        return_list.append(pre_race_lists)

        # print(return_list)
        return return_list

    def get_jockey_info(jockey_link):
        jockeys = []
        # print("------------jockey-----------")
        for jockey_tag in jockey_link:
            # 騎手名はレース結果テーブルの <a> タグテキストに直接含まれる。
            # 旧実装は別ページを HTTP 取得してタイトルから抽出していたが、
            # netKeiba の HTML 変更（title 属性追加・ページタイトル形式変更）で
            # URL 構築と文字列処理が壊れるため、タグテキストを直接取得する方式に変更。
            name = jockey_tag.get_text(strip=True)
            jockeys.append(name)
        return jockeys

    def horse_list_split(HorseList):
        # ヘッダ行（<th> のみ）を除外し、データ行（<td> を含む行）だけを結合して処理する。
        # <th> は </td> 変換されないため、そのままテキスト処理すると
        # ヘッダ文字列と1着馬の rank が結合されてインデックスがずれる不具合を防ぐ。
        data_rows = [row for row in HorseList.find_all("tr") if row.find("td")]
        HorseList = "".join(str(row) for row in data_rows)
        HorseList = re.sub(r"\n", "", str(HorseList))
        HorseList = re.sub(r" ", "", str(HorseList))
        HorseList = re.sub(r"</td>", "_", str(HorseList))
        HorseList = re.sub(r"<[^>]*?>", "", str(HorseList))
        HorseList = re.sub(r"\[", "", str(HorseList))
        HorseList = re.sub(r"\]", "", str(HorseList))
        HorseList = str(HorseList).replace("\xa0", "")
        tmp = str(HorseList).split("_")
        # print(tmp)
        i = 0
        count = 0
        Race_lists = []
        while i + 3 < len(tmp):
            # 数値でない rank（除外・中止馬など）はスキップ
            if not str(tmp[i]).strip().isdigit():
                i += 1
                continue
            rank_race = tmp[i]
            number_frame = tmp[i + 1]
            number_horse = tmp[i + 2]
            horse_name = tmp[i + 3]
            horse_sex = re.sub(r"\d+", "", tmp[i + 4])
            horse_old = tmp[i + 4].replace(str(horse_sex), "")
            handiycap = tmp[i + 5]
            _jockey = tmp[i + 6]
            goal_time = tmp[i + 7]
            tmp2 = str(goal_time).split(":")
            if len(tmp2) == 2:
                goal_time = float(tmp2[0]) * 60 + float(tmp2[1])
            _difference = tmp[i + 8]
            time_index = tmp[i + 9]
            # i+10〜i+13 は新規追加列（後半指数M・通過指数・追切指数・オッズ指数）のためスキップ
            corner = tmp[i + 14]
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

            _kaku4 = tmp[i + 14].split("-")[-1]
            agari = tmp[i + 15]
            odds = tmp[i + 16]
            rank_popular = tmp[i + 17]
            weight = tmp[i + 18].split("(")[0]
            zougen = (
                tmp[i + 18].replace(str(weight), "").replace("(", "").replace(")", "")
            )
            remarks = tmp[i + 21]
            kanri = ""
            if tmp[i + 22] != "":
                kanri = tmp[i + 22][0]
            _trainer = tmp[i + 22][1:]
            _banusi = tmp[i + 23]

            Race_lists.append(
                str(rank_race)
                + ","
                + str(number_frame)
                + ","
                + str(number_horse)
                + ","
                + horse_name
                + ","
                + horse_sex
                + ","
                + str(horse_old)
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
                + ","
                + str(corner_position1)
                + ","
                + str(corner_position2)
                + ","
                + str(corner_position3)
                + ","
                + str(corner_position4)
                + ","
                + str(time_index)
                + ","
                + kanri
                + ","
                + remarks
            )
            i = i + 25
            count = count + 1
        return Race_lists

    def get_horse_type(position, head_num):

        if position[3] == "":
            return 0
        position = [int(s) for s in position]
        horse_type = 0
        sasi = 2 * head_num / 3
        if 1 in position[0:-1]:
            horse_type = 1
        elif position[-1] <= 4:
            horse_type = 2
        elif position[-1] <= sasi or head_num <= 8:
            horse_type = 3
        else:
            horse_type = 4
        return horse_type

    def get_race_info1(title):
        race_info = []
        title = str(title).replace('<p class="smalltxt">', "")
        title = title.replace("</p>", "")
        num = re.findall(r"\d+", title)
        # year month day
        date = num[0:3]
        race_info.append(date)
        # 開催情報
        event_info = num[3:5]
        race_info.append(event_info)
        # クラス，条件
        tmp = title.split("目 ")
        tmp2 = tmp[1].split("\xa0")
        class1 = tmp2[0]
        race_info.append([class1])
        condition = raceDB.get_race_condition(tmp2[2])
        race_info.append(condition)
        # print(race_info)
        return race_info

    def get_race_condition(tmp):
        tmplist = []
        woman = 0
        handiy = 0
        if "牝" in tmp:
            woman = 1
        if "馬齢" in tmp:
            handiy = 1
        elif "定量" in tmp:
            handiy = 2
        elif "ハンデ" in tmp:
            handiy = 3
        elif "別定" in tmp:
            handiy = 4
        tmplist.append(woman)
        tmplist.append(handiy)
        return tmplist

    def get_race_info2(condition):
        race_info = []
        condition = re.sub(r"\n", "", str(condition))
        condition = re.sub(r".*<span>", "", str(condition))
        condition = re.sub(r"</span>.*", "", str(condition))
        condition = str(condition.replace("/", ","))
        condition = str(condition.replace(" 芝 :", ""))
        condition = str(condition.replace(" ダート :", ""))
        condition = str(condition.replace(" 障害 :", ""))
        condition = str(condition.replace(" 天候 :", ""))
        condition = condition.replace(" ", "")
        tmp = condition.split(",")
        tmp2 = re.sub(r"[0-9]*m", "", tmp[0])
        course_type = tmp2[0]
        turn = tmp2[1:].replace("\xa0", "")
        distance = re.findall(r"\d+", tmp[0])
        weather = tmp[1].replace("\xa0", "")
        state = tmp[2].replace("\xa0", "")
        race_info.append(course_type)
        race_info.append(turn)
        race_info.append(distance[0])
        race_info.append(weather)
        race_info.append(state)
        # print(race_info)
        return race_info

    # JRAのレース結果をnetkeibaから取得する
    # race_ids:取得するレース一覧
    def get_race_result(race_ids):
        # 取得済み race_id をセットとして読み込み（重複スキップ用）
        existing_ids = set()
        try:
            import pandas as pd

            existing_ids = set(
                pd.read_csv(
                    raceDB.PATH,
                    encoding="cp932",
                    usecols=["race_id"],
                    dtype={"race_id": str},
                    low_memory=False,
                )["race_id"].dropna()
            )
            print(f"取得済み race_id: {len(existing_ids)} 件")
        except Exception:
            pass  # ファイルが存在しない・ヘッダなし等は無視

        # 馬ページ取得用 Selenium ドライバー（JS レンダリングが必要なため）
        from .getinfo import GetInfo

        driver = GetInfo._create_driver()
        GetInfo.login_process(driver)

        loop_count = 0
        try:
            for race_id in race_ids:
                loop_count = loop_count + 1
                race_id = str(race_id)
                if race_id == "0":
                    continue
                race_num = race_id[-2:]
                place = race_id[4:6]
                if not place.isdigit():
                    continue
                if int(place) > 10:
                    continue
                # 既に取得済みの race_id はスキップ
                if race_id in existing_ids:
                    print(
                        f"{loop_count}/{len(race_ids)} {race_id} - スキップ（取得済み）"
                    )
                    continue
                print(loop_count, len(race_ids), race_id)

                url = f"{URL_DB}/race/{race_id}/"

                time.sleep(1)
                res = raceDB.session.get(url)
                res.encoding = res.apparent_encoding

                soup = BeautifulSoup(res.content, "lxml")
                title = soup.find("p", class_="smalltxt")

                race_name = soup.find_all("h1")
                if len(race_name) < 2:
                    continue
                race_name = str(race_name[1]).replace("<h1>", "")
                race_name = re.sub(r"<!.*", "", race_name)
                race_info1 = raceDB.get_race_info1(title)

                condition = soup.find("dl", class_="racedata fc")
                race_info2 = raceDB.get_race_info2(condition)
                table = soup.find("table", class_="race_table_01 nk_tb_common")
                link = table.find_all("a")
                horse_link = [
                    link[i] for i in range(0, len(link)) if "umalink" in str(link[i])
                ]
                jockey_link = [
                    link[i] for i in range(0, len(link)) if "jockey" in str(link[i])
                ]
                horse_info = raceDB.get_horse_info(horse_link, race_id, driver)
                jockey_info = raceDB.get_jockey_info(jockey_link)

                # ,変換
                # raceDB.comvert_comma(race_info1,race_info2,horse_info,jockey_info)
                # print(race_info1,race_info2,horse_info,jockey_info)
                race_info1 = [
                    [str(s).replace("amp;", "") for s in text] for text in race_info1
                ]
                race_info2 = [str(s).replace("amp;", "") for s in race_info2]
                horse_info = [
                    [str(s).replace("amp;", "") for s in text] for text in horse_info
                ]
                jockey_info = [str(s).replace("amp;", "") for s in jockey_info]
                # print(race_info1,race_info2,horse_info,jockey_info)

                result_table = raceDB.horse_list_split(table)
                # print(result_table)
                horse_len = len(result_table)
                types = []
                # 脚質の取得
                for n in range(0, horse_len):
                    tmp = result_table[n].split(",")
                    corner_position_list = [tmp[13], tmp[14], tmp[15], tmp[16]]
                    types.append(raceDB.get_horse_type(corner_position_list, horse_len))

                # csvに書き込み
                out = codecs.open(raceDB.PATH, "a", encoding="shift_jis")
                count1 = 0
                count2 = 0
                count3 = 0
                for o in range(0, horse_len):
                    result_str = (
                        race_id
                        + ","
                        + str(race_info1[0][0])
                        + ","
                        + str(race_info1[0][1])
                        + ","
                        + str(race_info1[0][2])
                    )
                    result_str = result_str + "," + race_name + "," + place
                    result_str = (
                        result_str
                        + ","
                        + str(race_info1[1][0])
                        + ","
                        + str(race_info1[1][1])
                        + ","
                        + race_num
                    )
                    result_str = (
                        result_str
                        + ","
                        + str(race_info1[2][0])
                        + ","
                        + str(race_info1[3][0])
                        + ","
                        + str(race_info1[3][1])
                    )
                    result_str = (
                        result_str
                        + ","
                        + str(race_info2[0])
                        + ","
                        + str(race_info2[1])
                        + ","
                        + str(race_info2[2])
                        + ","
                        + str(race_info2[3])
                        + ","
                        + str(race_info2[4])
                    )
                    result_str = (
                        result_str
                        + ","
                        + str(horse_len)
                        + ","
                        + result_table[o]
                        + ","
                        + str(types[o])
                    )
                    result_str = (
                        result_str
                        + ","
                        + jockey_info[o]
                        + ","
                        + horse_info[0][count1]
                        + ","
                        + horse_info[0][count1 + 1]
                        + ","
                        + horse_info[0][count1 + 2]
                    )
                    result_str = (
                        result_str
                        + ","
                        + horse_info[1][count2]
                        + ","
                        + horse_info[1][count2 + 1]
                        + ","
                        + horse_info[1][count2 + 2]
                        + ","
                        + horse_info[1][count2 + 3]
                        + ","
                        + horse_info[1][count2 + 4]
                        + ","
                        + horse_info[1][count2 + 5]
                    )
                    result_str = result_str + "," + horse_info[2][o]
                    result_str = (
                        result_str
                        + ","
                        + str(horse_info[3][count3])
                        + ","
                        + str(horse_info[3][count3 + 1])
                        + ","
                        + str(horse_info[3][count3 + 2])
                        + ","
                        + str(horse_info[3][count3 + 3])
                        + ","
                        + str(horse_info[3][count3 + 4])
                        + ","
                        + str(horse_info[3][count3 + 5])
                    )
                    # print(result_str)
                    count1 = count1 + 3
                    count2 = count2 + 6
                    count3 = count3 + 6
                    result_str = result_str.replace("", "")
                    out.write(result_str + "\n")
                out.close()
        finally:
            driver.quit()
