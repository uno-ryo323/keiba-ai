from selenium import webdriver
from bs4 import BeautifulSoup
import re
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

class JudgeTicket():
    
    USER = "YOUR_NETKEIBA_ID"
    PASS = "YOUR_NETKEIBA_PASSWORD"
    login_info = {
        "login_id":USER,
        "pswd":PASS,
        }
    url_login ="https://regist.netkeiba.com/account/?pid=login&action=auth"
    options = Options()
    
    def __init__(self, date, race_id):
        self.date = date
        self.race_id = race_id
        #self.file_result = open("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date  + "\\" + self.race_id + "\\result.csv","w")
        
        

    def login_process(driver):
        driver.get('https://regist.netkeiba.com/account/?pid=login')
        driver.find_element_by_name('login_id').send_keys(JudgeTicket.USER)
        driver.find_element_by_name('pswd').send_keys(JudgeTicket.PASS)
        driver.find_element_by_xpath('//input[@alt=\"ログイン\"]').click()
    
    #レース結果の取得
    def get_result(self):
        url = "https://race.netkeiba.com/race/result.html?race_id=" + self.race_id
        driver = webdriver.Chrome(executable_path="C:\\ChormeDriver\\chromedriver.exe",options=JudgeTicket.options)
        JudgeTicket.login_process(driver)
        driver.get(url)
        time.sleep(2.0)
        html = driver.page_source
        driver.close()
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find_all("table",class_="Payout_Detail_Table")
        #print(table)
        block1 = ['Tansho','Fukusho','Wakuren','Umaren']
        block2 = ['Wide','Umatan','Fuku3','Tan3']
        for ticket in block1:
            data = table[0].find('tr',class_=ticket)
            if data == None:
                continue
            result = data.find('td',class_='Result')
            result = re.findall(r"\d+", str(result))
            payout = data.find('td',class_='Payout')
            payout = re.sub(r'.*<span>', '', str(payout))
            payout = re.sub(r'</span>.*', '', payout)
            payout = payout.replace(',','').replace('<br/>',',').replace('円','')
            payout = payout.split(',')
            
            if (ticket == 'Tansho') or (ticket == 'Fukusho'):
                for i in range(0,len(result)):
                    if ticket == 'Tansho':
                        out_str = 'Win'
                    else:
                        out_str = 'Show'
                    out_str = out_str + "," + result[i] + "," + str(float(payout[i])/100)
                    self.file_result.write(out_str + "\n")
                    #print(out_str)
                    out_str = ""
            elif (ticket == 'Wakuren') or (ticket == 'Umaren'):
                loop_count = 0
                for i in range(0,len(result),2):
                    if ticket == 'Wakuren':
                        out_str = 'BracketQuinella'
                    else:
                        out_str = 'Quinella'
                    out_str = out_str + "," + result[i] + "," + result[i+1] + "," +  str(float(payout[loop_count])/100)
                    loop_count = loop_count + 1
                    self.file_result.write(out_str + "\n")
                    #print(out_str)
                    out_str = ""
                    
        for ticket in block2:
            data = table[1].find('tr',class_=ticket)
            result = data.find('td',class_='Result')
            result = re.findall(r"\d+", str(result))
            payout = data.find('td',class_='Payout')
            payout = re.sub(r'.*<span>', '', str(payout))
            payout = re.sub(r'</span>.*', '', payout)
            payout = payout.replace(',','').replace('<br/>',',').replace('円','')
            payout = payout.split(',')
            
            if (ticket == 'Wide') or (ticket == 'Umatan'):
                loop_count = 0
                for i in range(0,len(result),2):
                    if ticket == 'Wide':
                        out_str = 'QuinellaPlace'
                    else:
                        out_str = 'Exacta'
                    out_str = out_str + "," + result[i] + "," + result[i+1] + "," + str(float(payout[loop_count])/100)
                    loop_count = loop_count + 1
                    self.file_result.write(out_str + "\n")
                    #print(out_str)
                    out_str = ""
            elif (ticket == 'Fuku3') or (ticket == 'Tan3'):
                loop_count = 0
                for i in range(0,len(result),3):
                    if ticket == 'Fuku3':
                        out_str = 'Trio'
                    else:
                        out_str = 'Trifecta'
                    out_str = out_str + "," + result[i] + "," + result[i+1] + "," + result[i+2] + "," + str(float(payout[loop_count])/100)
                    loop_count = loop_count + 1
                    self.file_result.write(out_str + "\n")
                    #print(out_str)
                    out_str = ""

            
    #投票内容の的中判定
    def judge_ticket(self):
        ticket_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date  + "\\" + self.race_id + "\\ticket.csv", sep=',', encoding='cp932')
        result_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date  + "\\" + self.race_id + "\\result.csv", sep=',', encoding='cp932',\
                                  names=[1,2,3,4,5])
        for i in range(0,len(result_data)):
            if (result_data.loc[i,1] == 'Win') or (result_data.loc[i,1] == 'Show'):
                index = ticket_data.index[(ticket_data['1'] == result_data.loc[i,1]) & (ticket_data['2'] == result_data.loc[i,2])]
                if not len(index) == 0:
                    ticket_data.loc[index[0],'8'] = result_data.loc[i,3]
                    ticket_data.loc[index[0],'9'] = '的中'
                    #print(ticket_data.loc[index])
            elif (result_data.loc[i,1] == 'BracketQuinella') or (result_data.loc[i,1] == 'Quinella') or (result_data.loc[i,1] == 'QuinellaPlace') or (result_data.loc[i,1] == 'Exacta'):
                index = ticket_data.index[(ticket_data['1'] == result_data.loc[i,1]) & (ticket_data['2'] == result_data.loc[i,2]) & (ticket_data['3'] == result_data.loc[i,3])]
                if not len(index) == 0:
                    ticket_data.loc[index[0],'8'] = result_data.loc[i,4]
                    ticket_data.loc[index[0],'9'] = '的中'
                    #print(ticket_data.loc[index])
            elif (result_data.loc[i,1] == 'Trio') or (result_data.loc[i,1] == 'Trifecta'):
                index = ticket_data.index[(ticket_data['1'] == result_data.loc[i,1]) & (ticket_data['2'] == result_data.loc[i,2]) & (ticket_data['3'] == result_data.loc[i,3])  & (ticket_data['4'] == result_data.loc[i,4])]
                if not len(index) == 0:
                    ticket_data.loc[index[0],'8'] = result_data.loc[i,5]
                    ticket_data.loc[index[0],'9'] = '的中'
                    #print(ticket_data.loc[index])        
        ticket_data.to_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date  + "\\" + self.race_id + "\\ticket.csv", sep=',', encoding='cp932')
    
    #収支計算
    def calc_balance(self):
        ticket_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date  + "\\" + self.race_id + "\\ticket.csv", sep=',', encoding='cp932')
        total_bet = ticket_data['7'].sum()
        hit_index = ticket_data.index[ticket_data['9'] == '的中']
        payout = 0
        ticket_data['payout'] = ticket_data['7'] * ticket_data['8']
        for i in range(0,len(hit_index)):
            payout = payout + ticket_data.loc[hit_index[i],'7'] * ticket_data.loc[hit_index[i],'8']
        balance = - total_bet + payout
        out_str = self.race_id + "," + str(total_bet) + "," + str(int(payout)) + "," + str(int(balance))
        
        bet_types = ['Win','Show','BracketQuinella','Quinella', 'QuinellaPlace', 'Exacta', 'Trio', 'Trifecta']
        for bet_type in bet_types: 
            index = ticket_data.index[ticket_data['1'] == bet_type]
            bet = ticket_data.loc[index,'7'].sum()
            index = ticket_data.index[(ticket_data['1'] == bet_type) & (ticket_data['9'] == '的中')]
            payout = ticket_data.loc[index,'payout'].sum()
            out_str = out_str + "," + str(bet) + "," + str(payout)

        
        #print(total_bet, int(payout), int(balance))
        file_balance = open("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date  + "\\balance.csv","a")
        file_balance2 = open("C:\\keibaAI\\Data\\netKeiba\\racecard\\balance.csv","a")
        #file_balance.write("race_id,total_bet,total_payout,total_balance,win_bet,win_payout,show_bet,show_payout,bracketquinella_bet,"\
         #                  +"bracketquinella_payout,quinella_bet,quinella_payout,quinellaplace_bet,quinellaplace_payout,exacta_bet,exacta_payout,trio_bet,trio_payout,trifecta_bet,trifecta_payout" + "\n")
        print(out_str)
        file_balance.write(out_str + "\n")
        file_balance2.write(out_str + "\n")
        
    def main(self):
        #self.get_result()
        #self.file_result.close()
        self.judge_ticket()   
        self.calc_balance()
        
        
if __name__ == "__main__":
    jt = JudgeTicket('20211114','202105050406')
    jt.get_result()
    jt.judge_ticket()   
    jt.calc_balance()
        