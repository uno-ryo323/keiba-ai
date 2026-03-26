import pandas as pd
import time
from selenium import webdriver
import datetime
import locale


class PurchaseTicket:
    
    userid = '63484396'
    password = 'YOUR_IPAT_PASSWORD'
    pars = 'YOUR_IPAT_PARS'
    
    def __init__(self, race_id, date):
        self.race_id = race_id
        self.place = PurchaseTicket.change_place(race_id[4:6])
        self.race_num = race_id[-2]
        self.date = date
        self.money_total = 0
        self.driver = webdriver.Chrome(executable_path="C:\\ChormeDriver\\chromedriver.exe")
    
    def change_place(place_code):
        place = place_code.replace('01','札幌').replace('02','函館').replace('03','福島').replace('04','新潟').replace('05','東京').replace('06','中山').replace('07','中京').replace('08','京都').replace('09','阪神').replace('10','小倉')
        return place
        
    
    def auto_purchase(self):
        ticket_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date + "\\" + self.race_id + "\\ticket.csv", sep=",", encoding="cp932")
        for i in range(0,len(ticket_data)):
            ticket_type = ticket_data.loc[i,'1']
            money = ticket_data.loc[i,'6']
            self.money_total = self.money_total + money
            horse_number1 = ticket_data.loc[i,'2']
            horse_number2 = ticket_data.loc[i,'3']
            if ticket_type == 'Win':
                purchase_win(horse_number1, money)
            elif ticket_type == 'Show':
                purchase_show(horse_number1, money)
            elif ticket_type == 'QuinellaPlace':
                purchase_quinellaplace(horse_number1, horse_number2, money)
            elif ticket_type == 'Quiella':
                purchase_quinella(horse_number1, horse_number2, money)
            elif ticket_type == 'BracketQuiella':
                purchase_bracketquinella(horse_number1, horse_number2, money)
            elif ticket_type == 'Exacta':
                purchase_exacta(horse_number1, horse_number2, money)
            elif ticket_type == 'Trio':
                purchase_trio(horse_number1, horse_number2, horse_number3, money)

    def purchase_trio(horse_number1, horse_number2, horse_number3, money)        
    

            
    """
    def purchase_win(horse_number, money):
        
    def purchase_show(horse_number, money):

    def purchase_quinellaplace(horse_number1, horse_number2, money):
    
    def purchase_quinella(horse_number1, horse_number2, money):

    def purchase_bracketquinella(horse_number1, horse_number2, money):        

    def purchase_exacta(horse_number1, horse_number2, money):        
    """

    def common_process(self):
                #ドライバーの読み込み
        #driver = webdriver.Chrome(executable_path="C:\\ChormeDriver\\chromedriver.exe")
        
        #---------ipatにログイン------------
        self.driver.get('https://www.ipat.jra.go.jp/sp/')
        self.driver.find_element_by_id('userid').send_keys(PurchaseTicket.userid)
        self.driver.find_element_by_id('password').send_keys(PurchaseTicket.password)
        self.driver.find_element_by_id('pars').send_keys(PurchaseTicket.pars)
        self.driver.execute_script('JavaScript:ToSPMenu();return false;')
        time.sleep(5)
        
        #---------投票ボタンの選択------------        
        link = self.driver.find_element_by_xpath('//*[text()=\'通常投票\']')
        link.click()
        time.sleep(5)
        
        #---------競馬場の選択------------
        place_list = self.driver.find_elements_by_xpath('/html/body/div/div/ul')
        place_list = place_list[0].text.split('\n')
        place_links = self.driver.find_elements_by_xpath('/html/body/div/div/ul/li/a')
        year = self.date[0:4]
        month = self.date[4:6]
        day = self.date[6:8]
        locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
        dt = datetime.datetime(int(year),int(month),int(day))
        dw = dt.strftime('%a'))
        target_link = None
        for i in range(0,len(place_list)):
            if self.place in place_list[i] && dw in place_list[i]:     
                target_link = place_links[i]
                break
        target_link.click()   
        time.sleep(2)
        
        #---------レース番号の選択------------
        race_num_list = self.driver.find_element_by_xpath('/html/body/div/div/ul')
        print(race_num_list.text)
        race_num_list = race_num_list.text.split('\n')
        race_num_link = self.driver.find_element_by_xpath('/html/body/div/div/ul/li/a') 
        target_link = None
        for i in range(0,len(race_num_list)):
            if self.race_num in race_num_list[i]:     
                target_link = race_num_link[i]
                break
        target_link.click()
        time.sleep(2)
        
        self.driver.close()
        
if __name__ == "__main__":
    pt = PurchaseTicket('202105050812','20211127')
    pt.common_process(1,2,3)
    
        
        
        