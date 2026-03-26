import time
from selenium import webdriver
from bs4 import BeautifulSoup
import re
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
import pandas as pd
import codecs
import datetime

class GetInfo():
    
    USER = "darjiling0917@docomo.ne.jp"
    PASS = "fjrkk117349"
    login_info = {
        "login_id":USER,
        "pswd":PASS,
        }
    url_login ="https://regist.netkeiba.com/account/?pid=login&action=auth"
    options = Options()
    #options.add_argument('--headless')

    def __init__(self, date, race_id):
        self.path = "C:\\keibaAI\\Data\\netKeiba\\racecard\\" + date + "\\" + race_id + "\\"
        self.race_id = race_id 
        self.date = date

    def get_race_day(year, month):
        driver = webdriver.Chrome(executable_path="C:\\KeibaAI\\Common\\chromedriver.exe",options=GetInfo.options)
        driver.get('https://race.netkeiba.com/top/calendar.html?year=' + year + '&month=' + month)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        RaceCellBox = soup.find_all('td',class_='RaceCellBox')
        days = []
        filePath = "C:\\KeibaAI\\Source\\Batch\\schedule_" + str(datetime.date(int(year),int(month),1).strftime('%Y%m')) + ".csv"
        out=codecs.open(filePath,"w",encoding="shift_jis")
        out.write("kaisai_date,get_list_date,get_result_date,get_predata_date"+"\n")
        for i in range(0,len(RaceCellBox)):
            place = RaceCellBox[i].find_all('span', class_='JyoName')
            if len(place) > 0: 
                day = RaceCellBox[i].find('span', class_='Day').contents[0]
                kaisai_date = datetime.date(int(year),int(month),int(day)).strftime('%Y%m%d')
                get_list_date = datetime.date(int(year),int(month),int(day) - 1).strftime('%Y%m%d')
                get_result_date = kaisai_date
                get_predata_date = datetime.date(int(year),int(month),int(day) - 1).strftime('%Y%m%d')
                result_str = str(kaisai_date) + "," + str(get_list_date) + "," + str(get_result_date) + "," + str(get_predata_date)
                out.write(result_str+"\n")
        out.close()
        driver.close()

    def get_race_time(self,kaisai_date):
        print("レース一覧を取得します")
        key = ['place','race_num','race_name','race_id','startTime','course','headcount']
        lists = []
        
        driver = webdriver.Chrome(executable_path="C:\\KeibaAI\\Common\\chromedriver.exe",options=GetInfo.options)
        driver.get('https://race.netkeiba.com/top/race_list.html?kaisai_date=' + kaisai_date)
        GetInfo.login_process(driver)
        time.sleep(0.5)
        time.sleep(2)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        datalist = soup.find_all('dd',class_='RaceList_Data')
        placelist = soup.find_all('p', class_='RaceList_DataTitle')
        match_pattern = r'[札幌函館新潟阪神京都小倉中山中京福島東京]{2}'
        placelist = [re.search(match_pattern,str(place)).group() for place in placelist]
        count = -1
        for data in datalist:
            li_list = data.find_all('li')
            count = count + 1
            for li in li_list:
                race_list = []
                race_num = li.find('div',class_='Race_Num')
                if race_num == None:
                    race_num = li.li.find('div',class_='Race_Num Race_Fixed')
                race_num = re.sub(r'\D','',str(race_num))
                
                race_name = li.find('span',class_='ItemTitle')
                race_name = re.sub(r'.*">','',str(race_name))
                race_name = re.sub(r'</span>','',str(race_name))                
                                   
                race_id = re.sub(r"\n", "", str(li))                    
                race_id = re.sub(r".*race_id=", "", str(race_id))
                race_id = re.sub(r"&amp;rf.*", "", str(race_id))
                
                #print(race_id)
                race_data = li.find('div',class_='RaceData')
                span = race_data.find_all('span')
                span = [re.sub(r'.*">','',str(data).replace('</span>','')) for data in span]
                
                startTime = span[0].replace(" ","")
                course = span[1]
                headcount = span[2]
                
                if ':' not in startTime:
                    startTime = span[1].replace(" ","")
                    course = span[2]
                    headcount = span[3]
                
                race_list.append(placelist[count])
                race_list.append(race_num)
                race_list.append(race_name)
                race_list.append(race_id)
                race_list.append(startTime)
                race_list.append(course)
                race_list.append(headcount)
                
                dicts = dict(zip(key,race_list))
                lists.append(dicts)
                
        #print(lists)
        #cls.driver.close()
        if len(lists) == 0:
            print("レース一覧の取得に失敗しました")
        else:
            print("レース一覧の取得に成功しました")
            df = pd.DataFrame(lists)
            df.to_csv("C:\\keibaAI\\Data\\netKeiba\\racelist\\" + kaisai_date + ".csv", index=False,sep=",",encoding="Shift-jis")

        return lists

    def get_race_card(self):
        try:
            
            driver = webdriver.Chrome(executable_path="C:\\KeibaAI\\Common\\chromedriver.exe",options=GetInfo.options)
            print("レース表を取得します")
            GetInfo.login_process(driver)
            time.sleep(1)
            url = "https://race.netkeiba.com/race/shutuba.html?race_id=" + str(self.race_id) + "&rf=race_list"
            driver.get(url)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            table = soup.find('table',class_='Shutuba_Table RaceTable01 ShutubaTable tablesorter tablesorter-default')
            if table == None:
                print("レース表の取得に失敗しました")
                return
            link = table.find_all("a")
            horse_link = [link[i] for i in range(0,len(link)) if "horse/" in str(link[i])]
            jockey_link = [link[i] for i in range(0,len(link)) if "jockey/" in str(link[i])]
            
            table = GetInfo.trim_table(table)
            table_data = table.split("_")
            race_info = GetInfo.get_race_info(soup, self.race_id)
            horse_info = GetInfo.get_horse_info(horse_link, driver, self.race_id)   
            jockey_info = GetInfo.get_jockey_info(jockey_link, driver)
            records = GetInfo.make_record(table_data, race_info, horse_info, jockey_info, self.race_id)
            GetInfo.out_csv(records, self.path, self.race_id)
            print("レース表の取得に成功しました")
        except Exception as e:            
            print("レース表の取得に失敗しました")
            print(e)
        finally:
            if driver is None:
                driver.close()
    
    def login_process(driver):
        driver.get('https://regist.netkeiba.com/account/?pid=login')
        driver.find_element_by_name('login_id').send_keys(GetInfo.USER)
        driver.find_element_by_name('pswd').send_keys(GetInfo.PASS)
        driver.find_element_by_xpath('//input[@alt=\"ログイン\"]').click()
    
    #出馬表の整形
    def trim_table(table):
        table = re.sub(r"\n","",str(table))
        table = re.sub(r" ","",table)
        table = re.sub(r"</td>","_",table)
        table = re.sub(r"<[^>]*?>","",table)
        table = re.sub(r"\[","",table)
        table = re.sub(r"\]","",table)
        table = table.replace("\xa0","")
        table = table.replace("枠馬番印馬名性齢斤量騎手厩舎馬体重(増減)オッズ更新人気お気に入り馬登録メモ","")
        table = table.replace("-","")
        table = table.replace("◎","")
        table = table.replace("◯","")
        table = table.replace("▲","")
        table = table.replace("△","")
        table = table.replace("☆","")
        table = table.replace("✓","")
        table = table.replace("消","")
        table = table.replace("&amp;#10003","")
                
        return table

    #レース情報の取得
    def get_race_info(soup,race_id):
        key = ['year','month','day','race_name','place','kai','day2','race_num','class','mare_only','handiy','course','turn','distance','weather','state']
        values = []
        
        place = race_id[4:6]
        kai = race_id[6:8]
        day2 = race_id[8:10]
        race_num = race_id[10:12]
        
        #レース名，クラス，年月日
        title = soup.find('title')
        race_name = re.sub(r' 出馬表.*','',str(title))
        race_name = re.sub(r'<title>','',race_name)
        tmp = str(title).split('|')
        date = re.findall(r"\d+", tmp[1])
        year = date[0]
        month = date[1]
        day = date[2]
        
        #コースタイプ，距離，天候，馬場
        race_data1 = soup.find('div',class_='RaceData01')
        race_data1 = str(race_data1).replace('\n','')
        course = re.sub(r'.*--><span> ','',re.sub(r'</span>.*','',race_data1))
        course_type = course[0]
        distance = re.findall(r"\d+", course)
        turn = re.sub(r'\).*','',race_data1)
        turn = re.sub(r'.*\(','',turn)
        weather = re.sub(r'.*天候:*','',race_data1)
        weather = re.sub(r'<span.*','',weather)
        state = re.sub(r'.*馬場:','',race_data1)
        state = re.sub(r'</span.*','',state)
        
        race_data2 = soup.find('div',class_='RaceData02')
        race_data2 = race_data2.find_all('span')
        class_ = str(race_data2[3]) + str(race_data2[4])
        class_ = class_.replace('<span>','').replace('</span>','').replace('サラ系','')
        mare_only = 0
        if '牝' in str(race_data2[5]): 
            mare_only = 1
        handiy = 0
        if "馬齢" in str(race_data2[6]):
            handiy = 1
        elif "定量" in str(race_data2[6]):
            handiy = 2
        elif "ハンデ" in str(race_data2[6]):
            handiy = 3
        elif "別定" in str(race_data2[6]):
            handiy = 4
        
        values.append(str(year))
        values.append(str(month))
        values.append(str(day))
        values.append(race_name)
        values.append(place)
        values.append(kai)
        values.append(day2)
        values.append(race_num)
        values.append(class_)
        values.append(str(mare_only))
        values.append(str(handiy))        
        values.append(course_type)
        values.append(turn)
        values.append(str(distance[0]))
        values.append(weather)
        values.append(state)
        dicts = dict(zip(key,values))
        
        return dicts
    
    #騎手情報の取得
    def get_jockey_info(jockey_link,driver):
        jockeys = []
        for i in range(0,len(jockey_link)):
            time.sleep(1)
            link = re.sub(r"\" target.*","",str(jockey_link[i]))
            link = re.sub(r"<a href=\"","",link)
            driver.get(link)
            html = driver.page_source
            soup = BeautifulSoup(html,'lxml')
            title = soup.find('title')
            jockey_name = str(title).replace('<title>','')
            jockey_name = jockey_name.replace('</title>','')
            jockey_name = jockey_name.replace(' | 騎手データ - netkeiba.com','')
            jockeys.append(jockey_name)
        return jockeys
    
    
    def my_index(lists, x, default=-1):
        if x in lists:
            return lists.index(x)
        else:
            return default
    
    @staticmethod
    def get_horse_info(horse_link, driver, race_id):
        key=['horse_id','trainer','banusi','breeder','father','father_father','father_mother','mother','mother_father','mother_mother', \
             'pre_race1','pre_race2','pre_race3','pre_race4','pre_race5']
        value = []
        lists = []
        
        for horse_number in horse_link:
            
            horse_number = re.sub(r"<a href=\"","",str(horse_number))
            horse_number = re.sub(r" target.*","",horse_number)
            horse_number = horse_number.replace("\"","")
            time.sleep(1)
            driver.get(horse_number)
            html = driver.page_source
            horse_number = re.sub(r".*/","",horse_number)
            soup = BeautifulSoup(html, 'lxml')
            
            #プロフィールの取得    
            horse_prof = soup.find('table',{'class':'db_prof_table no_OwnerUnit'})        
            if horse_prof is None:
                horse_prof = soup.find('table',{'class':'db_prof_table'})    
            horse_prof = horse_prof.find_all('tr')
            for prof in horse_prof:
                if "調教師" in str(prof):
                    prof = re.sub(r'\n','',str(prof))
                    prof = re.sub(r'.*\">','',str(prof))
                    prof = re.sub(r'.*\">','',str(prof))
                    prof = re.sub(r'</a>.*','',str(prof))
                    trainer = prof
                if "馬主" in str(prof):
                    prof = re.sub(r'\n','',str(prof))
                    prof = re.sub(r'.*\">','',str(prof))
                    prof = re.sub(r'.*\">','',str(prof))
                    prof = re.sub(r'</a>.*','',str(prof))
                    banusi = prof
                if "生産者" in str(prof):
                    prof = re.sub(r'\n','',str(prof))
                    prof = re.sub(r'.*\">','',str(prof))
                    prof = re.sub(r'.*\">','',str(prof))
                    prof = re.sub(r'</a>.*','',str(prof))
                    breeder = prof
                
            #血統の取得
            blood_table = soup.find('table',class_='blood_table')
            blood_data = blood_table.find_all('td')
            for i in range(0,len(blood_data)):
                blood = re.sub(r"\n","",str(blood_data[i]))
                blood = re.sub(r".*\">","",blood)
                blood = re.sub(r"</a>.*","",blood)
                if i == 0:
                    father = blood
                elif i ==  1:
                    father_father = blood
                elif i == 2:
                    father_mother = blood
                elif i == 3:
                    mother = blood
                elif i == 4:
                    mother_father = blood
                elif i == 5:
                    mother_mother = blood
            
            #前5走の取得
            pre_race_results = soup.find('table',{'class':'db_h_race_results nk_tb_common'})
            pre_race1 = 0
            pre_race2 = 0
            pre_race3 = 0
            pre_race4 = 0
            pre_race5 = 0
            if pre_race_results is not None:
                pre_race_results = pre_race_results.find_all('td')
                pre_race_tags = [str(x) for x in pre_race_results if '/race/20' in str(x)]
                pre_race_tags = [re.sub(r".*/race/","",x) for x in pre_race_tags]
                pre_race_tags = [re.sub(r"/\".*","",x) for x in pre_race_tags]
                
                count = 0
                start = GetInfo.my_index(pre_race_tags,race_id) + 1
                for j in range(start,len(pre_race_tags)):                        
                    if count == 0:
                        pre_race1 = pre_race_tags[j]
                    elif count ==  1:
                        pre_race2 = pre_race_tags[j]
                    elif count == 2:
                        pre_race3 = pre_race_tags[j]
                    elif count == 3:
                        pre_race4 = pre_race_tags[j]
                    elif count == 4:
                        pre_race5 = pre_race_tags[j]
                        break
                    count = count + 1
                    
            value.append(horse_number)
            value.append(trainer)
            value.append(banusi)
            value.append(breeder)
            value.append(father)
            value.append(father_father)
            value.append(father_mother)
            value.append(mother)            
            value.append(mother_father)            
            value.append(mother_mother)            
            value.append(pre_race1)
            value.append(pre_race2)
            value.append(pre_race3)            
            value.append(pre_race4)            
            value.append(pre_race5) 
            
            dicts = dict(zip(key,value))
            lists.append(dicts)
            value.clear()
            
        return lists

    def make_record(table_data, race_info, horse_info, jockey_info, race_id):
        records = []
        
        i = 0
        while '取' in table_data:
            index = table_data.index('取')
            del table_data[index-2:index+12]
        while '除外' in table_data:
            index = table_data.index('除外')
            del table_data[index-2:index+12]
        length = round(len(table_data)/13)
        head_str = race_id + "," + race_info['year'] + "," + race_info['month'] + "," + race_info['day'] + "," + race_info['race_name'] + "," + race_info['place'] \
                    + "," + race_info['kai'] + "," + race_info['day2'] + "," + race_info['race_num'] +"," + race_info['class'] + "," + race_info['mare_only'] + "," + race_info['handiy'] \
                    + "," + race_info['course'] + "," + race_info['turn'] + "," + race_info['distance'] + "," + race_info['weather'] + "," + race_info['state'] +"," + str(length)

        for i in range(0,length):    
            waku = table_data[i*13]
            umaban = table_data[i*13+1]
            horse_name = table_data[i*13+3]
            sex = table_data[i*13+4][0]
            old = table_data[i*13+4][1]
            handicap = table_data[i*13+5]
            if '美浦' in table_data[i*13+7]:
                kanri = '東'
            elif '栗東' in table_data[i*13+7]:
                kanri = '西'
            elif '地方' in table_data[i*13+7]:
                kanri = '地'
            elif '海外' in table_data[i*13+7]:
                kanri = '外'
            
            weight = table_data[i*13+8].split("(")[0]
            zougen = table_data[i*13+8].replace(str(weight), "").replace("(", "").replace(")","")
            odds = table_data[i*13+9]
            popular_rank = table_data[i*13+10]
            
            record = head_str
            record = record + "," + waku + "," + umaban + "," + horse_name + "," + sex + "," + old + "," + handicap + "," + weight + "," + zougen \
                    + "," + odds + "," + popular_rank + "," +  kanri
            record = record + "," + jockey_info[i]
            record = record + "," + str(horse_info[i]['horse_id']) + ","  + horse_info[i]['trainer'] + ","  + horse_info[i]['banusi'] + "," + horse_info[i]['breeder'] \
                    + "," + horse_info[i]['father'] + "," + horse_info[i]['father_father'] + "," + horse_info[i]['father_mother'] + "," + horse_info[i]['mother'] \
                    + "," + horse_info[i]['mother_father'] +  "," + horse_info[i]['mother_mother'] + "," + str(horse_info[i]['pre_race1']) \
                    + "," + str(horse_info[i]['pre_race2']) + "," + str(horse_info[i]['pre_race3']) + "," + str(horse_info[i]['pre_race4']) + "," + str(horse_info[i]['pre_race5']) 
            records.append(record)
        
        return records

    def out_csv(records, path, race_id):
        file = open(path + race_id + ".csv","a")
        header = 'race_id,year,month,day,race_name,place,kai,day2,race_num,class,mare_only,hande,course,turn,distance,weather,state,headcount,lane_gate,horse_gate,'
        header = header + 'horse_name,sex,old,handiy,weight,zougen,odds,popular_rank,kanri,jockey,horse_id,trainer,banusi,breeder,father,father_father,father_mother,'
        header = header + 'mother,mother_father,mother_mother,pre_race1,pre_race2,pre_race3,pre_race4,pre_race5'
        file.write(header + "\n")
        for i in range(0,len(records)):
            file.write(records[i] + "\n")
                       
    def get_odds(self):
        try:
            print("オッズを取得します")
            driver = webdriver.Chrome(executable_path="C:\\ChormeDriver\\chromedriver.exe",options=GetInfo.options)
            race_id = str(self.race_id)
            file_tanfuku = open("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date  + "\\" + race_id + "\\tanfuku.csv","w")
            file_wakuren = open("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date  + "\\" + race_id + "\\wakuren.csv","w")
            file_umaren = open("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date  + "\\" + race_id + "\\umaren.csv","w")
            file_wide = open("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date  + "\\" + race_id + "\\wide.csv","w")
            file_umatan = open("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date  + "\\" + race_id + "\\umatan.csv","w")
            file_trio = open("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date  + "\\" + race_id + "\\fuku3.csv","w")
            
            
            #単複オッズの取得
            print("単複オッズの取得")
            url = "https://race.netkeiba.com/odds/index.html?type=b1&race_id=" + race_id
            driver.get(url)
            time.sleep(2.0)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            tan = soup.select('#odds_tan_block')
            odds_tan = tan[0].find_all('td',class_='Odds')
            odds_tan = [re.sub(r".*\">","",str(odds)).replace("</span></td>","") for odds in odds_tan]
            fuku = soup.select('#odds_fuku_block')
            odds_fuku = fuku[0].find_all('td',class_='Odds')
            odds_fuku = [re.sub(r".*\">","",str(odds)).replace("</span></td>","") for odds in odds_fuku]
            odds_fuku_min = [odds.split('-')[0][0:-1] for odds in odds_fuku]
            odds_fuku_max = [odds.split('-')[1][1:] for odds in odds_fuku]
            file_tanfuku.write("horse_gate,odds_Win,odds_Show_Min,odds_Show_Max" + "\n")
            for i in range(0,len(odds_tan)):
                if ('-' in odds_tan[i]) or ('<' in odds_tan[i]):
                    continue
                out_str = str(i+1) + "," + odds_tan[i] + "," + odds_fuku_min[i] + "," + odds_fuku_max[i]
                #print(out_str)
                file_tanfuku.write(out_str + "\n")
            #枠連オッズの取得
            print("枠連オッズの取得")
            url = "https://race.netkeiba.com/odds/index.html?type=b3&race_id=" + race_id
            driver.get(url)
            time.sleep(1.0)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            odds_table = soup.find_all('table',class_="Odds_Table")
            waku = 0
            file_wakuren.write("lane_gate1,lane_gate2,BracketQuinella" + "\n")
            for table in odds_table:
                waku = waku + 1
                odds = table.find_all('td',class_='Odds')
                waku2 = table.find_all('td',class_='Waku_Normal')
                waku2 = [re.sub(r".*\">","",re.sub(r"</td>.*","",str(wakuban).replace("\n",""))) for wakuban in waku2]
                odds = [re.sub(r".*\">","",re.sub(r"</span>.*","",str(odd).replace("\n",""))) for odd in odds]
                for i in range(0,len(waku2)):
                    if ('<' in odds[i]) or ('-' in odds[i]):
                        continue
                    out_str = str(waku) + "," + waku2[i] + "," + odds[i]
                    #print(out_str)
                    file_wakuren.write(out_str + "\n")
                
            #馬連オッズの取得
            print("馬連オッズの取得")
            url = "https://race.netkeiba.com/odds/index.html?type=b4&race_id=" + race_id
            driver.get(url)
            time.sleep(1.0)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            odds_table = soup.find_all('table',class_="Odds_Table")
            umaban = 0
            file_umaren.write("horse_gate1,horse_gate2,Quinella_odds" + "\n")  
            for table in odds_table:
                umaban = umaban + 1
                umaban2 = table.find_all('td',class_='Waku_Normal')
                umaban2 = [re.sub(r".*\">","",re.sub(r"</td>.*","",str(tmp).replace("\n",""))) for tmp in umaban2]
                odds = table.find_all('td',class_='Odds')
                odds = [re.sub(r".*\">","",re.sub(r"</span>.*","",str(odd).replace("\n",""))) for odd in odds]
                for i in range(0,len(umaban2)):
                    if ('<' in odds[i]) or ('-' in odds[i]):
                        continue
                    out_str = str(umaban) + "," + umaban2[i] + "," + odds[i]
                    #print(out_str)
                    file_umaren.write(out_str + "\n")  
            
            #ワイドオッズの取得
            print("ワイドオッズの取得")
            url = "https://race.netkeiba.com/odds/index.html?type=b5&race_id=" + race_id
            driver.get(url)
            time.sleep(1.0)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            odds_table = soup.find_all('table',class_="Odds_Table")
            umaban = 0
            file_wide.write("horse_gate1,horse_gate2,QuinellaPlace" + "\n")
            for table in odds_table:
                umaban = umaban + 1
                umaban2 = table.find_all('td',class_='Waku_Normal')
                umaban2 = [re.sub(r".*\">","",re.sub(r"</td>.*","",str(tmp).replace("\n",""))) for tmp in umaban2]
                odds = table.find_all('td',class_='Odds')
                odds = [re.sub(r".*\">","",re.sub(r"</span>.*","",str(odd).replace("\n",""))) for odd in odds]
                for i in range(0,len(umaban2)):
                    if ('<' in odds[i]) or ('-' in odds[i]):
                        continue
                    out_str = str(umaban) + "," + umaban2[i] + "," + odds[i]
                    #print(out_str)
                    file_wide.write(out_str + "\n")
                    
            #馬単オッズの取得
            print("馬単オッズの取得")
            url = "https://race.netkeiba.com/odds/index.html?type=b6&race_id=" + race_id
            driver.get(url)
            time.sleep(1.0)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            odds_table = soup.find_all('table',class_="Odds_Table")
            umaban = 0
            file_umatan.write("horse_gate1,horse_gate2,Exacta" + "\n")    
            for table in odds_table:
                umaban = umaban + 1
                umaban2 = table.find_all('td',class_='Waku_Normal')
                umaban2 = [re.sub(r".*\">","",re.sub(r"</td>.*","",str(tmp).replace("\n",""))) for tmp in umaban2]
                odds = table.find_all('td',class_='Odds')
                odds = [re.sub(r".*\">","",re.sub(r"</span>.*","",str(odd).replace("\n",""))) for odd in odds]
                for i in range(0,len(umaban2)):
                    if ('<' in odds[i]) or ('-' in odds[i]):
                        continue
                    out_str = str(umaban) + "," + umaban2[i] + "," + odds[i]
                    #print(out_str)
                    file_umatan.write(out_str + "\n")
        
            #3連複オッズの取得
            print("3連複オッズの取得")
            url = "https://race.netkeiba.com/odds/index.html?type=b7&race_id=" + race_id
            driver.get(url)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            odds_table = soup.find_all('table',class_="Odds_Table")
            time.sleep(1.0)
            horse_list = driver.find_element_by_id('list_select_horse')
            select = Select(horse_list)
            headcount = len(odds_table)+2
            file_trio.write("horse_gate1,horse_gate2,horse_gate3,Trio" + "\n")
            horse_list = []
            for i in range(0,headcount):
                horse_gate1 = i+1
                select.select_by_value(str(horse_gate1))
                time.sleep(0.5)
                html = driver.page_source
                soup = BeautifulSoup(html, 'lxml')
                odds_table = soup.find_all('table',class_="Odds_Table")
                for j in range(0,len(odds_table)):
                    horse_gate2 = odds_table[j].find('tr',class_='col_label')
                    horse_gate2 = str(horse_gate2).replace('\n','')
                    horse_gate2 = re.sub(r'.*">','',horse_gate2)
                    horse_gate2 = re.sub(r'</tr>','',horse_gate2)
                    horse_gate2 = re.sub(r'</th>','',horse_gate2)    
                    horse_gate = odds_table[j].find_all('tr')
                    for k in range(1,len(horse_gate)):
                        odds = horse_gate[k].find('td',class_='Odds Popular')
                        odds = str(odds).replace('\n','')
                        odds = re.sub(r'.*-......">','',odds)
                        odds = re.sub(r'</span>.*','',odds)
                        horse_gate3 = horse_gate[k].find('td',class_='Waku_Normal')
                        horse_gate3 = re.sub(r'.*">','',str(horse_gate3))
                        horse_gate3 = re.sub(r'</td>','',str(horse_gate3))
                        horse_list = [int(horse_gate1),int(horse_gate2),int(horse_gate3)]
                        horse_list.sort()
                        #print(horse_list)
                        out_str = str(horse_list[0]) + "," + str(horse_list[1]) + "," + str(horse_list[2]) + "," + str(odds)
                        horse_list = []
                        #print(out_str)
                        file_trio.write(out_str + "\n")

                horse_list = driver.find_element_by_id('list_select_horse')
                select = Select(horse_list)
                
            print("オッズの取得が完了しました")
        except:
            print("オッズの取得に失敗しました")
            import traceback
            traceback.print_exc()
        finally:
            #driver.quit() 
            driver.close()
            
        
if __name__ == "__main__":
    #getInfo = GetInfo("20210130", "202107010909")
    #getInfo.get_odds()
    GetInfo.get_race_day("2022","3")
    
    
    