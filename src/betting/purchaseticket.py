import time
import datetime
import locale
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from ..config import RACECARD_DIR, URL_IPAT

# 場コード→競馬場名のマッピング
PLACE_MAP = {
    "01": "札幌",
    "02": "函館",
    "03": "福島",
    "04": "新潟",
    "05": "東京",
    "06": "中山",
    "07": "中京",
    "08": "京都",
    "09": "阪神",
    "10": "小倉",
}


class PurchaseTicket:
    """iPATへの自動投票を行うクラス（未完成）"""

    userid = "63484396"
    password = "YOUR_IPAT_PASSWORD"
    pars = "YOUR_IPAT_PARS"

    def __init__(self, race_id, date):
        self.race_id = race_id
        self.place = PLACE_MAP.get(race_id[4:6], "")
        self.race_num = race_id[-2]
        self.date = date
        self.money_total = 0
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

    def auto_purchase(self):
        """ticket.csvを読み込んで券種ごとに投票関数を呼び出す（未完成）"""
        base_path = RACECARD_DIR / self.date / self.race_id
        ticket_data = pd.read_csv(base_path / "ticket.csv", sep=",", encoding="cp932")

        for i in range(len(ticket_data)):
            ticket_type = ticket_data.loc[i, "1"]
            money = ticket_data.loc[i, "6"]
            self.money_total += money
            horse_number1 = ticket_data.loc[i, "2"]
            horse_number2 = ticket_data.loc[i, "3"]

            # NOTE: 各purchase_*メソッドは未実装
            if ticket_type == "Win":
                self.purchase_win(horse_number1, money)
            elif ticket_type == "Show":
                self.purchase_show(horse_number1, money)
            elif ticket_type == "QuinellaPlace":
                self.purchase_quinellaplace(horse_number1, horse_number2, money)
            elif ticket_type == "Quinella":
                self.purchase_quinella(horse_number1, horse_number2, money)
            elif ticket_type == "BracketQuinella":
                self.purchase_bracketquinella(horse_number1, horse_number2, money)
            elif ticket_type == "Exacta":
                self.purchase_exacta(horse_number1, horse_number2, money)
            elif ticket_type == "Trio":
                horse_number3 = ticket_data.loc[i, "4"]
                self.purchase_trio(horse_number1, horse_number2, horse_number3, money)

    def purchase_trio(self, horse_number1, horse_number2, horse_number3, money):
        """3連複を投票する（未実装）"""
        pass

    # --- 以下、各券種の投票メソッド（未実装） ---

    def purchase_win(self, horse_number, money):
        """単勝を投票する（未実装）"""
        pass

    def purchase_show(self, horse_number, money):
        """複勝を投票する（未実装）"""
        pass

    def purchase_quinellaplace(self, horse_number1, horse_number2, money):
        """ワイドを投票する（未実装）"""
        pass

    def purchase_quinella(self, horse_number1, horse_number2, money):
        """馬連を投票する（未実装）"""
        pass

    def purchase_bracketquinella(self, horse_number1, horse_number2, money):
        """枠連を投票する（未実装）"""
        pass

    def purchase_exacta(self, horse_number1, horse_number2, money):
        """馬単を投票する（未実装）"""
        pass

    def common_process(self):
        """iPATにログインして競馬場・レース番号を選択する共通処理"""
        # iPATにログイン
        self.driver.get(URL_IPAT)
        self.driver.find_element(By.ID, "userid").send_keys(PurchaseTicket.userid)
        self.driver.find_element(By.ID, "password").send_keys(PurchaseTicket.password)
        self.driver.find_element(By.ID, "pars").send_keys(PurchaseTicket.pars)
        self.driver.execute_script("JavaScript:ToSPMenu();return false;")
        time.sleep(5)

        # 通常投票ボタンを選択
        link = self.driver.find_element(By.XPATH, "//*[text()='通常投票']")
        link.click()
        time.sleep(5)

        # 競馬場を選択（開催日と場名で一致するリンクをクリック）
        place_list = self.driver.find_elements(By.XPATH, "/html/body/div/div/ul")
        place_list = place_list[0].text.split("\n")
        place_links = self.driver.find_elements(By.XPATH, "/html/body/div/div/ul/li/a")

        year, month, day = self.date[0:4], self.date[4:6], self.date[6:8]
        locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")
        dt = datetime.datetime(int(year), int(month), int(day))
        dw = dt.strftime("%a")

        target_link = None
        for i in range(len(place_list)):
            if self.place in place_list[i] and dw in place_list[i]:
                target_link = place_links[i]
                break
        target_link.click()
        time.sleep(2)

        # レース番号を選択
        race_num_list = self.driver.find_element(By.XPATH, "/html/body/div/div/ul")
        race_num_list = race_num_list.text.split("\n")
        race_num_links = self.driver.find_elements(
            By.XPATH, "/html/body/div/div/ul/li/a"
        )

        target_link = None
        for i in range(len(race_num_list)):
            if self.race_num in race_num_list[i]:
                target_link = race_num_links[i]
                break
        target_link.click()
        time.sleep(2)

        self.driver.close()


if __name__ == "__main__":
    pt = PurchaseTicket("202105050812", "20211127")
    pt.common_process()
