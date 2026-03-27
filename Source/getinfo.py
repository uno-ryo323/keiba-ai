import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import re
import pandas as pd
import codecs
import datetime

from config import (
    BATCH_DIR,
    NETKEIBA_PASSWORD,
    NETKEIBA_USER,
    ODDS_FILES,
    RACECARD_DIR,
    RACELIST_DIR,
    URL_CALENDAR,
    URL_LOGIN,
    URL_ODDS,
    URL_RACELIST_PAGE,
    URL_SHUTUBA,
)


class GetInfo:
    """netKeibaからレース情報・出馬表・オッズを取得するクラス"""

    USER = NETKEIBA_USER
    PASS = NETKEIBA_PASSWORD
    login_info = {
        "login_id": USER,
        "pswd": PASS,
    }
    url_login = URL_LOGIN
    options = Options()
    # options.add_argument('--headless')  # ヘッドレスモードを使う場合はコメントアウトを外す

    def __init__(self, date, race_id):
        self.path = str(RACECARD_DIR / date / race_id) + "/"
        self.race_id = race_id
        self.date = date

    def _create_driver():
        """ChromeDriverを生成して返す（webdriver-managerで自動バージョン管理）"""
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=GetInfo.options)

    def get_race_day(year, month):
        """指定年月の開催日一覧を取得してCSVに保存する"""
        driver = GetInfo._create_driver()
        driver.get(f"{URL_CALENDAR}?year={year}&month={month}")
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        RaceCellBox = soup.find_all("td", class_="RaceCellBox")

        filePath = (
            BATCH_DIR
            / f"schedule_{datetime.date(int(year), int(month), 1).strftime('%Y%m')}.csv"
        )
        out = codecs.open(str(filePath), "w", encoding="shift_jis")
        out.write("kaisai_date,get_list_date,get_result_date,get_predata_date\n")

        for i in range(0, len(RaceCellBox)):
            place = RaceCellBox[i].find_all("span", class_="JyoName")
            if len(place) > 0:
                day = RaceCellBox[i].find("span", class_="Day").contents[0]
                kaisai_date = datetime.date(int(year), int(month), int(day)).strftime(
                    "%Y%m%d"
                )
                get_list_date = datetime.date(
                    int(year), int(month), int(day) - 1
                ).strftime("%Y%m%d")
                get_result_date = kaisai_date
                get_predata_date = datetime.date(
                    int(year), int(month), int(day) - 1
                ).strftime("%Y%m%d")
                result_str = (
                    kaisai_date
                    + ","
                    + get_list_date
                    + ","
                    + get_result_date
                    + ","
                    + get_predata_date
                )
                out.write(result_str + "\n")

        out.close()
        driver.close()

    def get_race_time(self, kaisai_date):
        """指定開催日のレース一覧（レースID・発走時刻等）を取得する"""
        print("レース一覧を取得します")
        key = [
            "place",
            "race_num",
            "race_name",
            "race_id",
            "startTime",
            "course",
            "headcount",
        ]
        lists = []

        driver = GetInfo._create_driver()
        driver.get(f"{URL_RACELIST_PAGE}?kaisai_date={kaisai_date}")
        GetInfo.login_process(driver)
        time.sleep(2)

        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        datalist = soup.find_all("dd", class_="RaceList_Data")
        placelist = soup.find_all("p", class_="RaceList_DataTitle")

        # 競馬場名を抽出（2文字の漢字）
        match_pattern = r"[札幌函館新潟阪神京都小倉中山中京福島東京]{2}"
        placelist = [
            re.search(match_pattern, str(place)).group() for place in placelist
        ]

        count = -1
        for data in datalist:
            li_list = data.find_all("li")
            count += 1
            for li in li_list:
                race_list = []

                race_num = li.find("div", class_="Race_Num")
                if race_num is None:
                    race_num = li.li.find("div", class_="Race_Num Race_Fixed")
                race_num = re.sub(r"\D", "", str(race_num))

                race_name = li.find("span", class_="ItemTitle")
                race_name = re.sub(r'.*">', "", str(race_name))
                race_name = re.sub(r"</span>", "", str(race_name))

                race_id = re.sub(r"\n", "", str(li))
                race_id = re.sub(r".*race_id=", "", str(race_id))
                race_id = re.sub(r"&amp;rf.*", "", str(race_id))

                race_data = li.find("div", class_="RaceData")
                span = race_data.find_all("span")
                span = [
                    re.sub(r'.*">', "", str(data).replace("</span>", ""))
                    for data in span
                ]

                startTime = span[0].replace(" ", "")
                course = span[1]
                headcount = span[2]

                # 発走時刻が先頭にない場合のフォールバック
                if ":" not in startTime:
                    startTime = span[1].replace(" ", "")
                    course = span[2]
                    headcount = span[3]

                race_list = [
                    placelist[count],
                    race_num,
                    race_name,
                    race_id,
                    startTime,
                    course,
                    headcount,
                ]
                lists.append(dict(zip(key, race_list)))

        if len(lists) == 0:
            print("レース一覧の取得に失敗しました")
        else:
            print("レース一覧の取得に成功しました")
            df = pd.DataFrame(lists)
            df.to_csv(
                str(RACELIST_DIR / f"{kaisai_date}.csv"),
                index=False,
                sep=",",
                encoding="Shift-jis",
            )

        return lists

    def get_race_card(self):
        """出馬表を取得してCSVに保存する"""
        try:
            driver = GetInfo._create_driver()
            print("レース表を取得します")
            GetInfo.login_process(driver)
            time.sleep(1)

            url = f"{URL_SHUTUBA}?race_id={self.race_id}&rf=race_list"
            driver.get(url)
            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")
            table = soup.find(
                "table",
                class_="Shutuba_Table RaceTable01 ShutubaTable tablesorter tablesorter-default",
            )

            if table is None:
                print("レース表の取得に失敗しました")
                return

            link = table.find_all("a")
            horse_link = [link[i] for i in range(len(link)) if "horse/" in str(link[i])]
            jockey_link = [
                link[i] for i in range(len(link)) if "jockey/" in str(link[i])
            ]

            table = GetInfo.trim_table(table)
            table_data = table.split("_")
            race_info = GetInfo.get_race_info(soup, self.race_id)
            horse_info = GetInfo.get_horse_info(horse_link, driver, self.race_id)
            jockey_info = GetInfo.get_jockey_info(jockey_link, driver)
            records = GetInfo.make_record(
                table_data, race_info, horse_info, jockey_info, self.race_id
            )
            GetInfo.out_csv(records, self.path, self.race_id)
            print("レース表の取得に成功しました")

        except Exception as e:
            print("レース表の取得に失敗しました")
            print(e)
        finally:
            if driver is not None:
                driver.close()

    def login_process(driver):
        """netKeibaにログインする"""
        driver.get(URL_LOGIN)
        driver.find_element(By.NAME, "login_id").send_keys(GetInfo.USER)
        driver.find_element(By.NAME, "pswd").send_keys(GetInfo.PASS)
        driver.find_element(By.XPATH, '//input[@alt="ログイン"]').click()

    def trim_table(table):
        """出馬表HTMLを整形してパースしやすい文字列に変換する"""
        table = re.sub(r"\n", "", str(table))
        table = re.sub(r" ", "", table)
        table = re.sub(r"</td>", "_", table)
        table = re.sub(r"<[^>]*?>", "", table)
        table = re.sub(r"\[", "", table)
        table = re.sub(r"\]", "", table)
        table = table.replace("\xa0", "")
        table = table.replace(
            "枠馬番印馬名性齢斤量騎手厩舎馬体重(増減)オッズ更新人気お気に入り馬登録メモ",
            "",
        )
        # 印・記号を除去
        for symbol in ["-", "◎", "◯", "▲", "△", "☆", "✓", "消", "&amp;#10003"]:
            table = table.replace(symbol, "")
        return table

    def get_race_info(soup, race_id):
        """レース情報（年月日・コース・クラス等）を辞書で返す"""
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

        # race_idから開催情報を取得
        place = race_id[4:6]
        kai = race_id[6:8]
        day2 = race_id[8:10]
        race_num = race_id[10:12]

        # レース名・年月日
        title = soup.find("title")
        race_name = re.sub(r" 出馬表.*", "", str(title))
        race_name = re.sub(r"<title>", "", race_name)
        tmp = str(title).split("|")
        date = re.findall(r"\d+", tmp[1])
        year, month, day = date[0], date[1], date[2]

        # コース・距離・天候・馬場状態
        race_data1 = soup.find("div", class_="RaceData01")
        race_data1 = str(race_data1).replace("\n", "")
        course = re.sub(r".*--><span> ", "", re.sub(r"</span>.*", "", race_data1))
        course_type = course[0]
        distance = re.findall(r"\d+", course)
        turn = re.sub(r"\).*", "", race_data1)
        turn = re.sub(r".*\(", "", turn)
        weather = re.sub(r".*天候:*", "", race_data1)
        weather = re.sub(r"<span.*", "", weather)
        state = re.sub(r".*馬場:", "", race_data1)
        state = re.sub(r"</span.*", "", state)

        # クラス・牝馬限定・ハンデ種別
        race_data2 = soup.find("div", class_="RaceData02")
        race_data2 = race_data2.find_all("span")
        class_ = str(race_data2[3]) + str(race_data2[4])
        class_ = (
            class_.replace("<span>", "").replace("</span>", "").replace("サラ系", "")
        )
        mare_only = 1 if "牝" in str(race_data2[5]) else 0

        # ハンデ種別: 1=馬齢, 2=定量, 3=ハンデ, 4=別定
        handiy_map = {"馬齢": 1, "定量": 2, "ハンデ": 3, "別定": 4}
        handiy = next((v for k, v in handiy_map.items() if k in str(race_data2[6])), 0)

        values = [
            year,
            month,
            day,
            race_name,
            place,
            kai,
            day2,
            race_num,
            class_,
            str(mare_only),
            str(handiy),
            course_type,
            turn,
            str(distance[0]),
            weather,
            state,
        ]
        return dict(zip(key, values))

    def get_jockey_info(jockey_link, driver):
        """騎手リンクから騎手名一覧を取得する"""
        jockeys = []
        for link in jockey_link:
            time.sleep(1)
            link = re.sub(r"\" target.*", "", str(link))
            link = re.sub(r"<a href=\"", "", link)
            driver.get(link)
            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")
            title = soup.find("title")
            jockey_name = (
                str(title)
                .replace("<title>", "")
                .replace("</title>", "")
                .replace(" | 騎手データ - netkeiba.com", "")
            )
            jockeys.append(jockey_name)
        return jockeys

    @staticmethod
    def my_index(lists, x, default=-1):
        """リスト内のインデックスを返す。見つからない場合はdefaultを返す"""
        return lists.index(x) if x in lists else default

    @staticmethod
    def get_horse_info(horse_link, driver, race_id):
        """馬リンクから馬情報（血統・前5走・調教師等）を取得する"""
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
        lists = []

        for horse_number in horse_link:
            value = []
            horse_number = re.sub(r"<a href=\"", "", str(horse_number))
            horse_number = re.sub(r" target.*", "", horse_number).replace('"', "")
            time.sleep(1)
            driver.get(horse_number)
            html = driver.page_source
            horse_number = re.sub(r".*/", "", horse_number)
            soup = BeautifulSoup(html, "lxml")

            # プロフィール（調教師・馬主・生産者）の取得
            horse_prof = soup.find("table", {"class": "db_prof_table no_OwnerUnit"})
            if horse_prof is None:
                horse_prof = soup.find("table", {"class": "db_prof_table"})
            horse_prof = horse_prof.find_all("tr")

            trainer = banusi = breeder = ""
            for prof in horse_prof:
                prof_str = re.sub(r"\n", "", str(prof))
                prof_str = re.sub(r".*\">", "", prof_str)
                prof_str = re.sub(r".*\">", "", prof_str)
                prof_str = re.sub(r"</a>.*", "", prof_str)
                if "調教師" in str(prof):
                    trainer = prof_str
                elif "馬主" in str(prof):
                    banusi = prof_str
                elif "生産者" in str(prof):
                    breeder = prof_str

            # 血統の取得
            blood_table = soup.find("table", class_="blood_table")
            blood_data = blood_table.find_all("td")
            blood_names = []
            for bd in blood_data[:6]:
                blood = re.sub(r"\n", "", str(bd))
                blood = re.sub(r".*\">", "", blood)
                blood = re.sub(r"</a>.*", "", blood)
                blood_names.append(blood)
            (
                father,
                father_father,
                father_mother,
                mother,
                mother_father,
                mother_mother,
            ) = blood_names

            # 前5走のレースIDを取得
            pre_race_results = soup.find(
                "table", {"class": "db_h_race_results nk_tb_common"}
            )
            pre_races = [0, 0, 0, 0, 0]
            if pre_race_results is not None:
                pre_race_results = pre_race_results.find_all("td")
                pre_race_tags = [
                    str(x) for x in pre_race_results if "/race/20" in str(x)
                ]
                pre_race_tags = [re.sub(r".*/race/", "", x) for x in pre_race_tags]
                pre_race_tags = [re.sub(r"/\".*", "", x) for x in pre_race_tags]

                start = GetInfo.my_index(pre_race_tags, race_id) + 1
                for count, j in enumerate(range(start, len(pre_race_tags))):
                    if count >= 5:
                        break
                    pre_races[count] = pre_race_tags[j]

            value = [
                horse_number,
                trainer,
                banusi,
                breeder,
                father,
                father_father,
                father_mother,
                mother,
                mother_father,
                mother_mother,
            ] + pre_races
            lists.append(dict(zip(key, value)))

        return lists

    def make_record(table_data, race_info, horse_info, jockey_info, race_id):
        """出馬表データ・レース情報・馬情報を結合してレコードリストを作る"""
        # 取消・除外馬を除去
        for removal in ["取", "除外"]:
            while removal in table_data:
                index = table_data.index(removal)
                del table_data[index - 2 : index + 12]

        length = round(len(table_data) / 13)
        head_str = ",".join(
            [
                race_id,
                race_info["year"],
                race_info["month"],
                race_info["day"],
                race_info["race_name"],
                race_info["place"],
                race_info["kai"],
                race_info["day2"],
                race_info["race_num"],
                race_info["class"],
                race_info["mare_only"],
                race_info["handiy"],
                race_info["course"],
                race_info["turn"],
                race_info["distance"],
                race_info["weather"],
                race_info["state"],
                str(length),
            ]
        )

        records = []
        for i in range(length):
            waku = table_data[i * 13]
            umaban = table_data[i * 13 + 1]
            horse_name = table_data[i * 13 + 3]
            sex = table_data[i * 13 + 4][0]
            old = table_data[i * 13 + 4][1]
            handicap = table_data[i * 13 + 5]

            # 管理区分（東/西/地/外）
            stable = table_data[i * 13 + 7]
            if "美浦" in stable:
                kanri = "東"
            elif "栗東" in stable:
                kanri = "西"
            elif "地方" in stable:
                kanri = "地"
            elif "海外" in stable:
                kanri = "外"
            else:
                kanri = ""

            weight = table_data[i * 13 + 8].split("(")[0]
            zougen = (
                table_data[i * 13 + 8]
                .replace(str(weight), "")
                .replace("(", "")
                .replace(")", "")
            )
            odds = table_data[i * 13 + 9]
            popular_rank = table_data[i * 13 + 10]

            hi = horse_info[i]
            record = ",".join(
                [
                    head_str,
                    waku,
                    umaban,
                    horse_name,
                    sex,
                    old,
                    handicap,
                    weight,
                    zougen,
                    odds,
                    popular_rank,
                    kanri,
                    jockey_info[i],
                    str(hi["horse_id"]),
                    hi["trainer"],
                    hi["banusi"],
                    hi["breeder"],
                    hi["father"],
                    hi["father_father"],
                    hi["father_mother"],
                    hi["mother"],
                    hi["mother_father"],
                    hi["mother_mother"],
                    str(hi["pre_race1"]),
                    str(hi["pre_race2"]),
                    str(hi["pre_race3"]),
                    str(hi["pre_race4"]),
                    str(hi["pre_race5"]),
                ]
            )
            records.append(record)

        return records

    def out_csv(records, path, race_id):
        """レコードリストをCSVファイルに出力する"""
        file = open(path + race_id + ".csv", "a")
        header = "race_id,year,month,day,race_name,place,kai,day2,race_num,class,mare_only,hande,course,turn,distance,weather,state,headcount,"
        header += "lane_gate,horse_gate,horse_name,sex,old,handiy,weight,zougen,odds,popular_rank,kanri,jockey,"
        header += "horse_id,trainer,banusi,breeder,father,father_father,father_mother,"
        header += "mother,mother_father,mother_mother,pre_race1,pre_race2,pre_race3,pre_race4,pre_race5"
        file.write(header + "\n")
        for record in records:
            file.write(record + "\n")

    def get_odds(self):
        """各券種のオッズを取得してCSVに保存する"""
        try:
            print("オッズを取得します")
            driver = GetInfo._create_driver()
            race_id = str(self.race_id)
            base_path = RACECARD_DIR / self.date / race_id

            file_tanfuku = open(base_path / ODDS_FILES["tanfuku"], "w")
            file_wakuren = open(base_path / ODDS_FILES["wakuren"], "w")
            file_umaren = open(base_path / ODDS_FILES["umaren"], "w")
            file_wide = open(base_path / ODDS_FILES["wide"], "w")
            file_umatan = open(base_path / ODDS_FILES["umatan"], "w")
            file_trio = open(base_path / ODDS_FILES["fuku3"], "w")

            # 単複オッズ
            print("単複オッズの取得")
            driver.get(f"{URL_ODDS}?type=b1&race_id={race_id}")
            time.sleep(2.0)
            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")
            odds_tan = [
                re.sub(r'.*">', "", str(o)).replace("</span></td>", "")
                for o in soup.select("#odds_tan_block")[0].find_all("td", class_="Odds")
            ]
            odds_fuku = [
                re.sub(r'.*">', "", str(o)).replace("</span></td>", "")
                for o in soup.select("#odds_fuku_block")[0].find_all(
                    "td", class_="Odds"
                )
            ]
            odds_fuku_min = [o.split("-")[0][0:-1] for o in odds_fuku]
            odds_fuku_max = [o.split("-")[1][1:] for o in odds_fuku]

            file_tanfuku.write("horse_gate,odds_Win,odds_Show_Min,odds_Show_Max\n")
            for i in range(len(odds_tan)):
                if ("-" in odds_tan[i]) or ("<" in odds_tan[i]):
                    continue
                file_tanfuku.write(
                    f"{i+1},{odds_tan[i]},{odds_fuku_min[i]},{odds_fuku_max[i]}\n"
                )

            # 枠連オッズ
            print("枠連オッズの取得")
            driver.get(f"{URL_ODDS}?type=b3&race_id={race_id}")
            time.sleep(1.0)
            soup = BeautifulSoup(driver.page_source, "lxml")
            file_wakuren.write("lane_gate1,lane_gate2,BracketQuinella\n")
            for waku, table in enumerate(
                soup.find_all("table", class_="Odds_Table"), start=1
            ):
                waku2 = [
                    re.sub(
                        r'.*">', "", re.sub(r"</td>.*", "", str(w).replace("\n", ""))
                    )
                    for w in table.find_all("td", class_="Waku_Normal")
                ]
                odds = [
                    re.sub(
                        r'.*">', "", re.sub(r"</span>.*", "", str(o).replace("\n", ""))
                    )
                    for o in table.find_all("td", class_="Odds")
                ]
                for i in range(len(waku2)):
                    if ("<" in odds[i]) or ("-" in odds[i]):
                        continue
                    file_wakuren.write(f"{waku},{waku2[i]},{odds[i]}\n")

            # 馬連オッズ
            print("馬連オッズの取得")
            driver.get(f"{URL_ODDS}?type=b4&race_id={race_id}")
            time.sleep(1.0)
            soup = BeautifulSoup(driver.page_source, "lxml")
            file_umaren.write("horse_gate1,horse_gate2,Quinella_odds\n")
            for umaban, table in enumerate(
                soup.find_all("table", class_="Odds_Table"), start=1
            ):
                umaban2 = [
                    re.sub(
                        r'.*">', "", re.sub(r"</td>.*", "", str(t).replace("\n", ""))
                    )
                    for t in table.find_all("td", class_="Waku_Normal")
                ]
                odds = [
                    re.sub(
                        r'.*">', "", re.sub(r"</span>.*", "", str(o).replace("\n", ""))
                    )
                    for o in table.find_all("td", class_="Odds")
                ]
                for i in range(len(umaban2)):
                    if ("<" in odds[i]) or ("-" in odds[i]):
                        continue
                    file_umaren.write(f"{umaban},{umaban2[i]},{odds[i]}\n")

            # ワイドオッズ
            print("ワイドオッズの取得")
            driver.get(f"{URL_ODDS}?type=b5&race_id={race_id}")
            time.sleep(1.0)
            soup = BeautifulSoup(driver.page_source, "lxml")
            file_wide.write("horse_gate1,horse_gate2,QuinellaPlace\n")
            for umaban, table in enumerate(
                soup.find_all("table", class_="Odds_Table"), start=1
            ):
                umaban2 = [
                    re.sub(
                        r'.*">', "", re.sub(r"</td>.*", "", str(t).replace("\n", ""))
                    )
                    for t in table.find_all("td", class_="Waku_Normal")
                ]
                odds = [
                    re.sub(
                        r'.*">', "", re.sub(r"</span>.*", "", str(o).replace("\n", ""))
                    )
                    for o in table.find_all("td", class_="Odds")
                ]
                for i in range(len(umaban2)):
                    if ("<" in odds[i]) or ("-" in odds[i]):
                        continue
                    file_wide.write(f"{umaban},{umaban2[i]},{odds[i]}\n")

            # 馬単オッズ
            print("馬単オッズの取得")
            driver.get(f"{URL_ODDS}?type=b6&race_id={race_id}")
            time.sleep(1.0)
            soup = BeautifulSoup(driver.page_source, "lxml")
            file_umatan.write("horse_gate1,horse_gate2,Exacta\n")
            for umaban, table in enumerate(
                soup.find_all("table", class_="Odds_Table"), start=1
            ):
                umaban2 = [
                    re.sub(
                        r'.*">', "", re.sub(r"</td>.*", "", str(t).replace("\n", ""))
                    )
                    for t in table.find_all("td", class_="Waku_Normal")
                ]
                odds = [
                    re.sub(
                        r'.*">', "", re.sub(r"</span>.*", "", str(o).replace("\n", ""))
                    )
                    for o in table.find_all("td", class_="Odds")
                ]
                for i in range(len(umaban2)):
                    if ("<" in odds[i]) or ("-" in odds[i]):
                        continue
                    file_umatan.write(f"{umaban},{umaban2[i]},{odds[i]}\n")

            # 3連複オッズ（馬番選択で組み合わせを取得）
            print("3連複オッズの取得")
            driver.get(f"{URL_ODDS}?type=b7&race_id={race_id}")
            time.sleep(1.0)
            soup = BeautifulSoup(driver.page_source, "lxml")
            odds_table = soup.find_all("table", class_="Odds_Table")
            headcount = len(odds_table) + 2
            file_trio.write("horse_gate1,horse_gate2,horse_gate3,Trio\n")

            horse_select = driver.find_element(By.ID, "list_select_horse")
            select = Select(horse_select)

            for i in range(headcount):
                horse_gate1 = i + 1
                select.select_by_value(str(horse_gate1))
                time.sleep(0.5)
                soup = BeautifulSoup(driver.page_source, "lxml")
                odds_table = soup.find_all("table", class_="Odds_Table")

                for j in range(len(odds_table)):
                    horse_gate2 = odds_table[j].find("tr", class_="col_label")
                    horse_gate2 = re.sub(
                        r'.*">',
                        "",
                        re.sub(
                            r"</tr>",
                            "",
                            re.sub(r"</th>", "", str(horse_gate2).replace("\n", "")),
                        ),
                    )
                    horse_gate_rows = odds_table[j].find_all("tr")

                    for k in range(1, len(horse_gate_rows)):
                        odds = horse_gate_rows[k].find("td", class_="Odds Popular")
                        odds = re.sub(
                            r'.*-......">',
                            "",
                            re.sub(r"</span>.*", "", str(odds).replace("\n", "")),
                        )
                        horse_gate3 = horse_gate_rows[k].find(
                            "td", class_="Waku_Normal"
                        )
                        horse_gate3 = re.sub(
                            r"</td>", "", re.sub(r'.*">', "", str(horse_gate3))
                        )
                        combo = sorted(
                            [int(horse_gate1), int(horse_gate2), int(horse_gate3)]
                        )
                        file_trio.write(f"{combo[0]},{combo[1]},{combo[2]},{odds}\n")

                # 次の馬番選択のためにselectを再取得
                horse_select = driver.find_element(By.ID, "list_select_horse")
                select = Select(horse_select)

            print("オッズの取得が完了しました")

        except Exception:
            print("オッズの取得に失敗しました")
            import traceback

            traceback.print_exc()
        finally:
            driver.close()


if __name__ == "__main__":
    # GetInfo("20210130", "202107010909").get_odds()
    GetInfo.get_race_day("2022", "3")
