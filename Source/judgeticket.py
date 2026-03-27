import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

from config import NETKEIBA_PASSWORD, NETKEIBA_USER, RACECARD_DIR, URL_LOGIN


class JudgeTicket:
    """レース結果の取得・的中判定・収支計算を行うクラス"""

    USER = NETKEIBA_USER
    PASS = NETKEIBA_PASSWORD
    login_info = {
        "login_id": USER,
        "pswd": PASS,
    }
    url_login = URL_LOGIN
    options = Options()

    def __init__(self, date, race_id):
        self.date = date
        self.race_id = race_id

    def login_process(driver):
        """netKeibaにログインする"""
        driver.get(URL_LOGIN)
        driver.find_element(By.NAME, "login_id").send_keys(JudgeTicket.USER)
        driver.find_element(By.NAME, "pswd").send_keys(JudgeTicket.PASS)
        driver.find_element(By.XPATH, '//input[@alt="ログイン"]').click()

    def get_result(self):
        """netKeibaからレース結果（払戻情報）を取得してCSVに保存する"""
        url = "https://race.netkeiba.com/race/result.html?race_id=" + self.race_id
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=JudgeTicket.options)
        JudgeTicket.login_process(driver)
        driver.get(url)
        time.sleep(2.0)
        html = driver.page_source
        driver.close()

        soup = BeautifulSoup(html, "lxml")
        table = soup.find_all("table", class_="Payout_Detail_Table")

        # ブロック1: 単勝・複勝・枠連・馬連
        block1 = ["Tansho", "Fukusho", "Wakuren", "Umaren"]
        # ブロック2: ワイド・馬単・3連複・3連単
        block2 = ["Wide", "Umatan", "Fuku3", "Tan3"]

        for ticket in block1:
            data = table[0].find("tr", class_=ticket)
            if data is None:
                continue
            result = re.findall(r"\d+", str(data.find("td", class_="Result")))
            payout = data.find("td", class_="Payout")
            payout = re.sub(r".*<span>", "", str(payout))
            payout = re.sub(r"</span>.*", "", payout)
            payout = (
                payout.replace(",", "")
                .replace("<br/>", ",")
                .replace("円", "")
                .split(",")
            )

            if ticket in ("Tansho", "Fukusho"):
                ticket_name = "Win" if ticket == "Tansho" else "Show"
                for i in range(len(result)):
                    out_str = f"{ticket_name},{result[i]},{float(payout[i])/100}"
                    self.file_result.write(out_str + "\n")

            elif ticket in ("Wakuren", "Umaren"):
                ticket_name = "BracketQuinella" if ticket == "Wakuren" else "Quinella"
                for i, loop_count in zip(range(0, len(result), 2), range(len(payout))):
                    out_str = f"{ticket_name},{result[i]},{result[i+1]},{float(payout[loop_count])/100}"
                    self.file_result.write(out_str + "\n")

        for ticket in block2:
            data = table[1].find("tr", class_=ticket)
            result = re.findall(r"\d+", str(data.find("td", class_="Result")))
            payout = data.find("td", class_="Payout")
            payout = re.sub(r".*<span>", "", str(payout))
            payout = re.sub(r"</span>.*", "", payout)
            payout = (
                payout.replace(",", "")
                .replace("<br/>", ",")
                .replace("円", "")
                .split(",")
            )

            if ticket in ("Wide", "Umatan"):
                ticket_name = "QuinellaPlace" if ticket == "Wide" else "Exacta"
                for i, loop_count in zip(range(0, len(result), 2), range(len(payout))):
                    out_str = f"{ticket_name},{result[i]},{result[i+1]},{float(payout[loop_count])/100}"
                    self.file_result.write(out_str + "\n")

            elif ticket in ("Fuku3", "Tan3"):
                ticket_name = "Trio" if ticket == "Fuku3" else "Trifecta"
                for i, loop_count in zip(range(0, len(result), 3), range(len(payout))):
                    out_str = f"{ticket_name},{result[i]},{result[i+1]},{result[i+2]},{float(payout[loop_count])/100}"
                    self.file_result.write(out_str + "\n")

    def judge_ticket(self):
        """購入チケットと結果を照合して的中フラグを付与する"""
        base_path = RACECARD_DIR / self.date / self.race_id
        ticket_data = pd.read_csv(base_path / "ticket.csv", sep=",", encoding="cp932")
        result_data = pd.read_csv(
            base_path / "result.csv", sep=",", encoding="cp932", names=[1, 2, 3, 4, 5]
        )

        for i in range(len(result_data)):
            ticket_type = result_data.loc[i, 1]

            if ticket_type in ("Win", "Show"):
                # 単勝・複勝: 馬番で照合
                index = ticket_data.index[
                    (ticket_data["1"] == ticket_type)
                    & (ticket_data["2"] == result_data.loc[i, 2])
                ]
            elif ticket_type in (
                "BracketQuinella",
                "Quinella",
                "QuinellaPlace",
                "Exacta",
            ):
                # 枠連・馬連・ワイド・馬単: 2頭で照合
                index = ticket_data.index[
                    (ticket_data["1"] == ticket_type)
                    & (ticket_data["2"] == result_data.loc[i, 2])
                    & (ticket_data["3"] == result_data.loc[i, 3])
                ]
            elif ticket_type in ("Trio", "Trifecta"):
                # 3連複・3連単: 3頭で照合
                index = ticket_data.index[
                    (ticket_data["1"] == ticket_type)
                    & (ticket_data["2"] == result_data.loc[i, 2])
                    & (ticket_data["3"] == result_data.loc[i, 3])
                    & (ticket_data["4"] == result_data.loc[i, 4])
                ]
            else:
                continue

            if len(index) > 0:
                payout_col = (
                    3
                    if ticket_type in ("Win", "Show")
                    else (
                        4
                        if ticket_type
                        in ("BracketQuinella", "Quinella", "QuinellaPlace", "Exacta")
                        else 5
                    )
                )
                ticket_data.loc[index[0], "8"] = result_data.loc[i, payout_col]
                ticket_data.loc[index[0], "9"] = "的中"

        ticket_data.to_csv(base_path / "ticket.csv", sep=",", encoding="cp932")

    def calc_balance(self):
        """レースの収支（投資額・払戻額・損益）を計算してCSVに保存する"""
        base_path = RACECARD_DIR / self.date / self.race_id
        ticket_data = pd.read_csv(base_path / "ticket.csv", sep=",", encoding="cp932")

        total_bet = ticket_data["7"].sum()
        ticket_data["payout"] = ticket_data["7"] * ticket_data["8"]
        hit_index = ticket_data.index[ticket_data["9"] == "的中"]
        payout = ticket_data.loc[hit_index, "payout"].sum()
        balance = -total_bet + payout

        out_str = f"{self.race_id},{total_bet},{int(payout)},{int(balance)}"

        bet_types = [
            "Win",
            "Show",
            "BracketQuinella",
            "Quinella",
            "QuinellaPlace",
            "Exacta",
            "Trio",
            "Trifecta",
        ]
        for bet_type in bet_types:
            bet = ticket_data.loc[ticket_data["1"] == bet_type, "7"].sum()
            hit_payout = ticket_data.loc[
                (ticket_data["1"] == bet_type) & (ticket_data["9"] == "的中"), "payout"
            ].sum()
            out_str += f",{bet},{hit_payout}"

        print(out_str)
        open(RACECARD_DIR / self.date / "balance.csv", "a").write(out_str + "\n")
        open(RACECARD_DIR / "balance.csv", "a").write(out_str + "\n")

    def main(self):
        self.judge_ticket()
        self.calc_balance()


if __name__ == "__main__":
    jt = JudgeTicket("20211114", "202105050406")
    jt.get_result()
    jt.judge_ticket()
    jt.calc_balance()
