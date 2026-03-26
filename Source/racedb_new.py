import requests
import codecs
from bs4 import BeautifulSoup
import re
import datetime
import pandas as pd

"""
レース結果を管理するクラス
次の機能を実装する．
１．レース結果を取得してｃｓｖに出力する
"""
class raceDB():    

    USER = "YOUR_NETKEIBA_ID"
    PASS = "YOUR_NETKEIBA_PASSWORD"

    login_info = {
        "login_id":USER,
        "pswd":PASS,
        }

    url_login ="https://regist.netkeiba.com/account/?pid=login&action=auth"

    session = requests.session()
    ses = session.post(url_login, data=login_info)

    PATH = "C:\\keibaAI\\Data\\netKeiba\\result\\race_jra(HorseInfo).csv"

    def calc_step(table, race_date):
        DEF_REST_INTERVAL = 70
        dt2 = datetime.datetime(race_date[0],race_date[1],race_date[2])
        count = 0
        for row in table:
            count = count + 1
            tmp = row['date'].split('/')
            dt1 = datetime.datetime(int(tmp[0]),int(tmp[1]),int(tmp[2]))
            diff = dt2 - dt1
            if diff.days > DEF_REST_INTERVAL:
                break
            dt2 = dt1
        #print(count)
        return str(count)

    def gate_performance(table):
        gate_in = [1,2,3]
        gate_middle = [4,5,6]
        gate_out = [7,8]
        gate_in_list = [0,0,0,0,0]
        gate_midlle_list = [0,0,0,0,0]
        gate_out_list = [0,0,0,0,0]
        
        for row in table:
            if row['gate'].isdigit():
                row['gate'] = int(row['gate'])
            else:
                continue
            if str(row['rank']).isdigit():
                row['rank'] = int(row['rank'])
            else:
                continue
            rank_index = row['rank']
            if row['rank'] >= 4:
                rank_index = 4
            if row['gate'] in gate_in:
                gate_in_list[rank_index-1] = gate_in_list[rank_index-1] + 1 
                gate_in_list[4] = gate_in_list[4] + 1 
            elif row['gate'] in gate_middle:
                gate_midlle_list[rank_index-1] = gate_midlle_list[rank_index-1] + 1 
                gate_midlle_list[4] = gate_midlle_list[4] + 1 
            elif row['gate'] in gate_out:
                gate_out_list[rank_index-1] = gate_out_list[rank_index-1] + 1 
                gate_out_list[4] = gate_out_list[4] + 1 
        #print(gate_in_list,gate_midlle_list,gate_out_list)
        gate_in_list = [str(num) for num in gate_in_list]
        gate_midlle_list = [str(num) for num in gate_midlle_list]
        gate_out_list = [str(num) for num in gate_out_list]
        return gate_in_list,gate_midlle_list,gate_out_list

    def place_performance(table,place):
        place_count = [0,0,0,0,0]
        for row in table:
            if str(row['rank']).isdigit():
                row['rank'] = int(row['rank'])
            else:
                continue
            if place in row['place']:
                rank_index = row['rank']
                if row['rank'] >= 4:
                    rank_index = 4
                place_count[rank_index-1] = place_count[rank_index-1] + 1 
                place_count[4] = place_count[4] + 1 
        #print(place_count)
        place_count = [str(num) for num in place_count]
        return place_count
    
    def jockey_performance(table,jockey):
        jockey_count = [0,0,0,0,0]
        for row in table:
            if str(row['rank']).isdigit():
                row['rank'] = int(row['rank'])
            else:
                continue
            if jockey in row['jockey']:
                rank_index = row['rank']
                if row['rank'] >= 4:
                    rank_index = 4
                jockey_count[rank_index-1] = jockey_count[rank_index-1] + 1 
                jockey_count[4] = jockey_count[4] + 1 
        #print(jockey_count)
        jockey_count = [str(num) for num in jockey_count]
        return jockey_count
    
    def calc_odds_popular(table):
        odds_count = 0
        popular_count = 0
        rank_count = 0
        odds = 0
        popular = 0
        rank = 0
        odds_ave = "NoneData"
        popular_ave = "NoneData"
        rank_ave = "NoneData"
        for row in table:
            if raceDB.is_float(row['odds']):
                odds = odds + float(row['odds'])
                odds_count = odds_count + 1
            if str(row['popular']).isdigit():    
                popular = popular + int(row['popular'])
                popular_count = popular_count + 1
            if str(row['rank']).isdigit():    
                rank = rank + int(row['rank'])
                rank_count = rank_count + 1
        if odds_count != 0:
            odds_ave = round(odds/odds_count,1)
        if popular_count != 0:
            popular_ave = round(popular/popular_count,1)
        if rank_count != 0:
            rank_ave = round(rank/rank_count,1)
        #print(odds_ave,popular_ave,rank_ave)
        return str(odds_ave),str(popular_ave),str(rank_ave)
        
    def is_float(num):
        try:
            float(num)
            return True
        except:
            return False
            

    def my_index(list, x, default=-1):
        if x in list:
            return list.index(x)
        else:
            return default
    
    def distance_performance(table,distance,course):
        
        distance_list_turf = [1000,1200,1400,1500,1600,1700,1800,2000,\
                              2200,2300,2400,2500,2600,3000,3200,3400,3600]
        distance_list_dart = [1000,1150,1200,1300,1400,1600,1700,1800,\
                              1900,2000,2100,2400,2500]

        distance_m_count = [0,0,0,0,0]
        distance_p_count = [0,0,0,0,0]
        distance_count = [0,0,0,0,0]
        
        if course == '芝':
            index = distance_list_turf.index(distance)
            if index == 0:
                distance_m = 0
                distance_p = distance_list_turf[index+1]
            elif index == len(distance_list_turf)-1:
                distance_m = distance_list_turf[index-1]
                distance_p = 0
            else:
                distance_m = distance_list_turf[index-1]
                distance_p = distance_list_turf[index+1]
            if distance_m % 200 != 0:
                distance_m = distance_list_turf[index-2]
            if distance_p % 200 != 0:
                distance_p = distance_list_turf[index+2]
        elif course == 'ダ':
            if distance == 2300:
                distance_m = 2100
                distance_p = 2400
            else:
                index = distance_list_dart.index(distance)
                if index == 0:
                    distance_m = 0
                    distance_p = distance_list_dart[index+1]
                elif index == len(distance_list_dart)-1:
                    distance_m = distance_list_dart[index-1]
                    distance_p = 0
                else:
                    distance_m = distance_list_dart[index-1]
                    distance_p = distance_list_dart[index+1]
                if distance_m % 200 != 0:
                    distance_m = distance_list_dart[index-2]
                if distance_p % 200 != 0 and distance_p != 2500:
                    distance_p = distance_list_dart[index+2]
        else:
            distance_count = [str(num) for num in distance_count]
            distance_m_count = [str(num) for num in distance_m_count]
            distance_p_count = [str(num) for num in distance_p_count]
            return distance_count,distance_m_count,distance_p_count
        
        for row in table:
            if str(row['distance']).isdigit():
                row['distance'] = int(row['distance'])
            else:
                continue
            if str(row['rank']).isdigit():
                row['rank'] = int(row['rank'])
            else:
                continue
            if distance_m == row['distance']:
                rank_index = row['rank']
                if row['rank'] >= 4:
                    rank_index = 4
                distance_m_count[rank_index-1] = distance_m_count[rank_index-1] + 1 
                distance_m_count[4] = distance_m_count[4] + 1 
            elif distance_p == row['distance']:
                rank_index = row['rank']
                if row['rank'] >= 4:
                    rank_index = 4
                distance_p_count[rank_index-1] = distance_p_count[rank_index-1] + 1 
                distance_p_count[4] = distance_p_count[4] + 1 
            elif distance == row['distance']:
                rank_index = row['rank']
                if row['rank'] >= 4:
                    rank_index = 4
                distance_count[rank_index-1] = distance_count[rank_index-1] + 1      
                distance_count[4] = distance_count[4] + 1      
        
        #print(distance_count,distance_m_count,distance_p_count)
        distance_count = [str(num) for num in distance_count]
        distance_m_count = [str(num) for num in distance_m_count]
        distance_p_count = [str(num) for num in distance_p_count]
        return distance_count,distance_m_count,distance_p_count
        
    def hande_performance(table,hande):
        hande_count = [0,0,0,0,0,0]
        if len(table) > 0:
            if raceDB.is_float(table[0]['hande']):
                hande_count[5] = hande - float(table[0]['hande']) 
        for row in table:
            if str(row['rank']).isdigit():
                row['rank'] = int(row['rank'])
            else:
                continue
            if raceDB.is_float(row['hande']):
                row['hande'] = float(row['hande'])
            if hande == row['hande']:
                rank_index = row['rank']
                if row['rank'] >= 4:
                    rank_index = 4
                hande_count[rank_index-1] = hande_count[rank_index-1] + 1 
                hande_count[4] = hande_count[4] + 1 
        #print(hande_count)
        hande_count = [str(num) for num in hande_count]
        return hande_count
    
    def weather_performance(table,weather):
        weather_count = [0,0,0,0,0]
        for row in table:
            if str(row['rank']).isdigit():
                row['rank'] = int(row['rank'])
            else:
                continue
            if weather == row['weather']:
                rank_index = row['rank']
                if row['rank'] >= 4:
                    rank_index = 4
                weather_count[rank_index-1] = weather_count[rank_index-1] + 1 
                weather_count[4] = weather_count[4] + 1 
        #print(weather_count)
        weather_count = [str(num) for num in weather_count]
        return weather_count
    
    def race_performance(table,race):
        race_count = [0,0,0,0,0]
        for row in table:
            if str(row['rank']).isdigit():
                row['rank'] = int(row['rank'])
            else:
                continue
            if race in row['race_name']:
                rank_index = row['rank']
                if row['rank'] >= 4:
                    rank_index = 4
                race_count[rank_index-1] = race_count[rank_index-1] + 1 
                race_count[4] = race_count[4] + 1 
        #print(race_count)
        race_count = [str(num) for num in race_count]
        return race_count

    def state_performance(table,state):
        state_count = [0,0,0,0,0]
        for row in table:
            if str(row['rank']).isdigit():
                row['rank'] = int(row['rank'])
            else:
                continue
            if state == row['state']:
                rank_index = row['rank']
                if row['rank'] >= 4:
                    rank_index = 4
                state_count[rank_index-1] = state_count[rank_index-1] + 1 
                state_count[4] = state_count[4] + 1 
        #print(state_count)
        state_count = [str(num) for num in state_count]
        return state_count

    def calc_time_diff(table):
        diff = 0
        diff_count = 0
        diff_ave = "NoneData"
        for row in table:
            if raceDB.is_float(row['time_diff']):
                diff = diff + float(row['time_diff'])
                diff_count = diff_count + 1
        
        if diff_count != 0:
            diff_ave = round(diff/diff_count,1)
        #print(diff_ave)
        return str(diff_ave)

    def calc_time_index(table,course,distance,place):
        #全て
        time_index = 0
        #同距離
        time_index_d = 0
        #同コース(芝，ダ)
        time_index_c = 0
        #同場所
        time_index_p = 0
        #同距離，コース（芝，ダ）
        time_index_dc = 0
        #同コース
        time_index_dcp = 0

        #カウント変数
        time_index_count = 0
        time_index_d_count = 0
        time_index_c_count= 0
        time_index_p_count= 0
        time_index_dc_count = 0
        time_index_dcp_count = 0

        #結果格納変数
        time_index_ave = "NoneData"
        time_index_ave3 = "NoneData"
        time_index_ave5 = "NoneData"
        time_index_d_ave = "NoneData"
        time_index_c_ave = "NoneData"
        time_index_p_ave = "NoneData"
        time_index_dc_ave = "NoneData"
        time_index_dcp_ave = "NoneData"

        
        time_index_max = 0
        time_index_min = 999
        time_index_d_max = 0
        time_index_c_max= 0
        time_index_p_max= 0
        time_index_dc_max= 0
        time_index_dcp_max= 0

        for row in table:
            if raceDB.is_float(row['time_index']):
                row['distance'] = int(row['distance'])
                time_index = time_index + float(row['time_index'])
                time_index_count = time_index_count + 1
                if time_index_count == 3:
                    time_index_ave3 = round(time_index/3,1)
                if time_index_count == 5:
                    time_index_ave5 = round(time_index/5,1)
                if float(row['time_index']) > time_index_max:
                    time_index_max = float(row['time_index'])
                if float(row['time_index']) < time_index_min:
                    time_index_min = float(row['time_index'])
                if distance == row['distance']:
                    time_index_d = time_index_d + float(row['time_index'])
                    time_index_d_count = time_index_d_count + 1
                    if float(row['time_index']) > time_index_d_max:
                        time_index_d_max = float(row['time_index'])
                if course == row['course']:
                    time_index_c = time_index_c + float(row['time_index'])
                    time_index_c_count = time_index_c_count + 1
                    if float(row['time_index']) > time_index_c_max:
                        time_index_c_max = float(row['time_index'])
                if place in row['place']:
                    time_index_p = time_index_p + float(row['time_index'])
                    time_index_p_count = time_index_p_count + 1            
                    if float(row['time_index']) > time_index_p_max:
                        time_index_p_max = float(row['time_index'])
                if (distance == row['distance']) and (course == row['course']):
                    time_index_dc = time_index_dc + float(row['time_index'])
                    time_index_dc_count = time_index_dc_count + 1
                    if float(row['time_index']) > time_index_dc_max:
                        time_index_dc_max = float(row['time_index'])
                if (distance == row['distance']) and (course == row['course']) and (place in row['place']):
                    time_index_dcp = time_index_dcp + float(row['time_index'])
                    time_index_dcp_count = time_index_dcp_count + 1
                    if float(row['time_index']) > time_index_dcp_max:
                        time_index_dcp_max = float(row['time_index'])
        
        if time_index_count != 0:
            time_index_ave = round(time_index/time_index_count,1)
        if time_index_d_count != 0:
            time_index_d_ave = round(time_index_d/time_index_d_count,1)
        if time_index_c_count != 0:
            time_index_c_ave = round(time_index_c/time_index_c_count,1)
        if time_index_p_count != 0:
            time_index_p_ave = round(time_index_p/time_index_p_count,1)
        if time_index_dc_count != 0:
            time_index_dc_ave = round(time_index_dc/time_index_dc_count,1)
        if time_index_dcp_count != 0:
            time_index_dcp_ave = round(time_index_dcp/time_index_dcp_count,1)
        
        if  time_index_max == 0:
            time_index_max = "NoneData"
        if  time_index_min == 999:
            time_index_min = "NoneData"
        if  time_index_d_max == 0:
            time_index_d_max = "NoneData"
        if  time_index_c_max == 0:
            time_index_c_max= "NoneData"
        if  time_index_p_max == 0:
            time_index_p_max= "NoneData"
        if  time_index_dc_max == 0:
            time_index_dc_max= "NoneData"
        if  time_index_dcp_max == 0:
            time_index_dcp_max= "NoneData"
        """
        print(time_index_ave,
        time_index_ave3,
        time_index_ave5,
        time_index_d_ave,
        time_index_c_ave,
        time_index_p_ave,
        time_index_dc_ave,
        time_index_dcp_ave,
        time_index_max,
        time_index_min,
        time_index_d_max,
        time_index_c_max,
        time_index_p_max,
        time_index_dc_max,
        time_index_dcp_max)
        """
        return [str(time_index_ave),str(time_index_ave3),str(time_index_ave5),str(time_index_d_ave),str(time_index_c_ave),str(time_index_p_ave),str(time_index_dc_ave),str(time_index_dcp_ave),str(time_index_max),str(time_index_min),str(time_index_d_max),str(time_index_c_max),str(time_index_p_max),str(time_index_dc_max),str(time_index_dcp_max)]

    def calc_horsetype(table):
        horse_type = [0,0,0,0,0,0]
        for row in table:
            if not str(row['headcount']).isdigit():
                continue
            head_count = int(row['headcount'])
            sasi = 2*head_count/3
            position = row['corner'].split('-')
            if len(position) == 1:
                continue
            position = [int(s) for s in position]

            if 1 in position[0:]:
                horse_type[0] = horse_type[0] + 1
            elif position[-1] <= 4:
                horse_type[1] = horse_type[1] + 1
            elif position[-1] <= sasi or head_count <= 8:
                horse_type[2] = horse_type[2] + 1
            else:
                horse_type[3] = horse_type[3] + 1
            horse_type[4] = horse_type[4] + 1
        #print(horse_type[0:-2])
        max_count = max(horse_type[0:-2])
        index = horse_type.index(max_count)
        horse_type[5] = index
        #print(horse_type)
        horse_type = [str(num) for num in horse_type]
        return horse_type

    def weight_performance(table,weight_current):
        #print(weight_current)
        weight_count = [0,0,0,0,0]
        if weight_current == '計不':
            weight_count = [str(num) for num in weight_count]
            return weight_count
        weight_up = int(weight_current) + 4
        weight_minus = int(weight_current) - 4
        
        for row in table:
            if str(row['rank']).isdigit():
                row['rank'] = int(row['rank'])
            else:
                continue
            if row['weight'] == '計不':
                continue
            weight = int(row['weight'].split("(")[0])
            if (weight_minus <=  weight) and(weight <=  weight_up):
                rank_index = row['rank']
                if row['rank'] >= 4:
                    rank_index = 4
                weight_count[rank_index-1] = weight_count[rank_index-1] + 1 
                weight_count[4] = weight_count[4] + 1 
        #print(weight_count)
        weight_count = [str(num) for num in weight_count]
        return weight_count
    
    def calc_start_performance(table):
        count = 0
        for row in table:
            if str(row['rank']).isdigit():
                row['rank'] = int(row['rank'])
            else:
                continue
            if '出遅れ' in row['remarks']:
                count = count + 1
        #print(count)
        return str(count)

    def get_prize(table):
        prize_total = 0
        for row in table:
            prize = row['prize'].replace(',','')
            if raceDB.is_float(prize):
                prize_total = prize_total + float(row['prize'].replace(',',''))
        prize_total = round(prize_total,1)
        #print(prize_total)
        return str(prize_total)

    def all_performance(table):
        rank_count = [0,0,0,0]
        for row in table:
            if str(row['rank']).isdigit():
                row['rank'] = int(row['rank'])
            else:
                continue
            rank_index = row['rank']
            if row['rank'] >= 4:
                rank_index = 4
            rank_count[rank_index-1] = rank_count[rank_index-1] + 1 
        #print(rank_count)
        rank_count = [str(num) for num in rank_count]
        return rank_count

    def get_horse_info(keiba_data):
        keys = ['date','place','weather','R','race_name','headcount','gate','horse_number'\
                ,'odds','popular','rank','jockey','hande','course','distance','state','state_index'\
                    ,'time','time_diff','time_index','corner','pace','agari','weight','remarks','prize']
        table = []
        res = raceDB.session.get("https://db.netkeiba.com/horse/"+str(keiba_data['horse_id']))
        soup = BeautifulSoup(res.content, 'lxml')
        pre_race_results = soup.find('table',{'class':'db_h_race_results nk_tb_common'})
        pre_race_results = pre_race_results.find_all('td')
        pre_race_tags = [str(x) for x in pre_race_results if '/race/20' in str(x)]
        pre_race_tags = [re.sub(r".*/race/","",x) for x in pre_race_tags]
        pre_race_tags = [re.sub(r"/\".*","",x) for x in pre_race_tags]
        start = raceDB.my_index(pre_race_tags,str(keiba_data['race_id'])) + 1
        if pre_race_results is not None:
            row = int(len(pre_race_results)/28)
            for i in range(start,row):
                date = pre_race_results[i*28].contents[0].contents[0].replace("\xa0","")
                if len(pre_race_results[i*28+1].contents[0].contents) != 0:
                    place = pre_race_results[i*28+1].contents[0].contents[0].replace("\xa0","")
                else:
                    place = ""
                weather = pre_race_results[i*28+2].contents[0].replace("\xa0","")
                R = pre_race_results[i*28+3].contents[0].replace("\xa0","")
                race_name = pre_race_results[i*28+4].contents[0].contents[0]
                headcount = pre_race_results[i*28+6].contents[0].replace("\xa0","")
                gate_number = pre_race_results[i*28+7].contents[0].replace("\xa0","")
                horse_number = pre_race_results[i*28+8].contents[0].replace("\xa0","")
                odds = pre_race_results[i*28+9].contents[0].replace("\xa0","")
                popular = pre_race_results[i*28+10].contents[0].replace("\xa0","")
                if len(pre_race_results[i*28+11].contents) != 0:
                    rank = pre_race_results[i*28+11].contents[0].replace("\xa0","")
                else:
                    rank = ""
                if len(pre_race_results[i*28+12].contents) > 2:
                    if len(pre_race_results[i*28+12].contents[1].contents) > 1:
                        jockey = pre_race_results[i*28+12].contents[1].contents[0].replace("\xa0","")
                    else:
                        jockey = ""
                else:
                    jockey = ""
                if len(pre_race_results[i*28+13].contents) != 0:
                    hande = pre_race_results[i*28+13].contents[0].replace("\xa0","")
                else:
                    hande = ""
                course = pre_race_results[i*28+14].contents[0][0].replace("\xa0","")
                distance = pre_race_results[i*28+14].contents[0][1:].replace("\xa0","")
                if len(pre_race_results[i*28+15].contents) != 0:
                    state = pre_race_results[i*28+15].contents[0].replace("\xa0","")
                else:
                    state = ""
                state_index = pre_race_results[i*28+16].contents[0].replace("\n","").replace("\xa0","")
                time = pre_race_results[i*28+17].contents[0].replace("\xa0","")
                diff = pre_race_results[i*28+18].contents[0].replace("\xa0","")
                time_index = pre_race_results[i*28+19].contents[0].replace("\n","").replace("\xa0","")
                corner = pre_race_results[i*28+20].contents[0].replace("\xa0","")
                pace = pre_race_results[i*28+21].contents[0].replace("\xa0","")
                agari = pre_race_results[i*28+22].contents[0].replace("\xa0","")
                weight = pre_race_results[i*28+23].contents[0].replace("\xa0","")
                remarks = pre_race_results[i*28+25].contents[0].replace("\xa0","")
                prize = pre_race_results[i*28+27].contents[0].replace("\xa0","")
                lists = [date,place,weather,R,race_name,headcount,gate_number,horse_number,odds,popular,rank,jockey,hande,\
                         course,distance,state,state_index,time,diff,time_index,corner,pace,agari,weight,remarks,prize]
                table.append(dict(zip(keys,lists)))
            #print(table)
            if len(table) == 0:
                horse_info_str = str(keiba_data['race_id']) + "," + str(keiba_data['horse_id'])
            else:
                all_performance = raceDB.all_performance(table)
                race_data = [keiba_data['year'],keiba_data['month'],keiba_data['day']]
                calc_step = raceDB.calc_step(table,race_data)
                place_performance = raceDB.place_performance(table, keiba_data['place2'])
                weather_performance = raceDB.weather_performance(table,keiba_data['weather'])
                race_performance = raceDB.race_performance(table,keiba_data['race_name'])
                gate_performance = raceDB.gate_performance(table)
                calc_odds_popular = raceDB.calc_odds_popular(table)
                jockey_performance = raceDB.jockey_performance(table,keiba_data['jockey'])
                hande_performance = raceDB.hande_performance(table,keiba_data['handiy'])
                distance_performance = raceDB.distance_performance(table,keiba_data['distance'],keiba_data['course'])
                state_performance = raceDB.state_performance(table,keiba_data['state'])
                calc_time_diff = raceDB.calc_time_diff(table)
                calc_time_index = raceDB.calc_time_index(table,keiba_data['course'],keiba_data['distance'],keiba_data['place2'])
                calc_horsetype = raceDB.calc_horsetype(table)
                weight_performance = raceDB.weight_performance(table,keiba_data['weight'])
                calc_start_performance = raceDB.calc_start_performance(table)
                get_prize = raceDB.get_prize(table)
                
                horse_info_str = str(keiba_data['race_id']) + "," + str(keiba_data['horse_id'])
                horse_info_str = horse_info_str + "," + all_performance[0] + "," + all_performance[1] + "," + all_performance[2] + "," + all_performance[3]
                horse_info_str = horse_info_str + "," + calc_step
                horse_info_str = horse_info_str + "," + place_performance[0] + "," + place_performance[1] + "," + place_performance[2] + "," + place_performance[3] + "," + place_performance[4]
                horse_info_str = horse_info_str + "," + weather_performance[0] + "," + weather_performance[1] + "," + weather_performance[2] + "," + weather_performance[3] + "," + weather_performance[4]
                horse_info_str = horse_info_str + "," + race_performance[0] + "," + race_performance[1] + "," + race_performance[2] + "," + race_performance[3] + "," + race_performance[4]
                horse_info_str = horse_info_str + "," + gate_performance[0][0] + "," + gate_performance[0][1] + "," + gate_performance[0][2] + "," + gate_performance[0][3] + "," + gate_performance[0][4]
                horse_info_str = horse_info_str + "," + gate_performance[1][0] + "," + gate_performance[1][1] + "," + gate_performance[1][2] + "," + gate_performance[1][3] + "," + gate_performance[1][4]
                horse_info_str = horse_info_str + "," + gate_performance[2][0] + "," + gate_performance[2][1] + "," + gate_performance[2][2] + "," + gate_performance[2][3] + "," + gate_performance[2][4]
                horse_info_str = horse_info_str + "," + calc_odds_popular[0] + "," + calc_odds_popular[1] + "," + calc_odds_popular[2]
                horse_info_str = horse_info_str + "," + jockey_performance[0] + "," + jockey_performance[1] + "," + jockey_performance[2] + "," + jockey_performance[3] + "," + jockey_performance[4]
                horse_info_str = horse_info_str + "," + hande_performance[0] + "," + hande_performance[1] + "," + hande_performance[2] + "," + hande_performance[3] + "," + hande_performance[4] + "," + hande_performance[5]
                horse_info_str = horse_info_str + "," + distance_performance[0][0] + "," + distance_performance[0][1] + "," + distance_performance[0][2] + "," + distance_performance[0][3] + "," + distance_performance[0][4]
                horse_info_str = horse_info_str + "," + distance_performance[1][0] + "," + distance_performance[1][1] + "," + distance_performance[1][2] + "," + distance_performance[1][3] + "," + distance_performance[1][4]
                horse_info_str = horse_info_str + "," + distance_performance[2][0] + "," + distance_performance[2][1] + "," + distance_performance[2][2] + "," + distance_performance[2][3] + "," + distance_performance[2][4]
                horse_info_str = horse_info_str + "," + state_performance[0] + "," + state_performance[1] + "," + state_performance[2] + "," + state_performance[3] + "," + state_performance[4]
                horse_info_str = horse_info_str + "," + calc_time_diff
                horse_info_str = horse_info_str + "," + calc_time_index[0] + "," + calc_time_index[1] + "," + calc_time_index[2] + "," + calc_time_index[3] + "," + calc_time_index[4] + "," + calc_time_index[5] + "," + calc_time_index[6] + "," + calc_time_index[7] + "," + calc_time_index[8] 
                horse_info_str = horse_info_str + "," + calc_time_index[9] + "," + calc_time_index[10] + "," + calc_time_index[11] + "," + calc_time_index[12] + "," + calc_time_index[13] + "," + calc_time_index[14]
                horse_info_str = horse_info_str + "," + calc_horsetype[0] + "," + calc_horsetype[1] + "," + calc_horsetype[2] + "," + calc_horsetype[3] + "," + calc_horsetype[4]
                horse_info_str = horse_info_str + "," + weight_performance[0] + "," + weight_performance[1] + "," + weight_performance[2] + "," + weight_performance[3] + "," + weight_performance[4]
                horse_info_str = horse_info_str + "," + calc_start_performance
                horse_info_str = horse_info_str + "," + get_prize
            
            #print(horse_info_str)
            out=codecs.open(raceDB.PATH,"a",encoding="shift_jis")
            out.write(horse_info_str+"\n")
            out.close()
        
    def main():
        keiba_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\result\\race_jra.csv",  sep=",", encoding="cp932")
        length = len(keiba_data)
        for i in range(0,length):
            
            if i < 570401:
                continue
            
            print(keiba_data.loc[i,'race_id'],keiba_data.loc[i,'horse_id'],i,length)
            raceDB.get_horse_info(keiba_data.loc[i])



if __name__ == "__main__":
    raceDB.main()
    
    
    
    
    
    
    
    
    

    