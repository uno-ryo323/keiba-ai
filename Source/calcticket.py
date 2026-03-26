import pandas as pd
import numpy as np

class CalcTicket():
    
    BANK = 50000
    #コンストラクタ
    def __init__(self, date, race_id):
        self.date = date
        self.race_id = race_id
        self.forecast_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + date + "\\" + race_id + "\\" + race_id + "_forecast.csv", sep=",", encoding="cp932")
        self.tiketFile = open("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + date + "\\" + race_id + "\\ticket.csv","w")
        pd.set_option('display.max_rows', 500)
        
    #単勝の購入
    def calc_Win(self):
        odds_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date + "\\" + self.race_id + "\\tanfuku.csv", sep=",", encoding="cp932")
        df_data = pd.merge(self.forecast_data, odds_data, on='horse_gate')
        df_data['EV'] = df_data['Win'] * df_data['odds_Win']
        length = len(df_data)
        #df_data = df_data[df_data['EV'] >= 1]
        #if length >= len(df_data) + 2:
         #   return
        df_data = df_data.sort_values('Win', ascending=False)
        df_data = df_data.reset_index(drop=True)
        sum_odds = 0
        #print(df_data)
        count = 0
        for i in range(0,len(df_data)):
            if count == 1:
                break
            count = count + 1
            sum_odds = sum_odds + (1/df_data.loc[i,'odds_Win'])
            if (1/sum_odds) >= 0:
                out_str = "Win," + str(df_data.loc[i,'horse_gate']) + ",,," + str(df_data.loc[i,"Win"]) + "," + str(df_data.loc[i,"odds_Win"])
                self.tiketFile.write(out_str  + "\n")
                #print(out_str)
        
    #複勝の購入
    def calc_Show(self):
        odds_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date + "\\" + self.race_id + "\\tanfuku.csv", sep=",", encoding="cp932")
        odds_data = odds_data.select_dtypes(include=np.number)
        
        df_data = pd.merge(self.forecast_data, odds_data, on='horse_gate')
        #print(df_data)
        df_data['EV1'] = df_data['Place'] * df_data['odds_Show_Min']
        df_data['EV2'] = df_data['Place'] * df_data['odds_Show_Max']
        length = len(df_data)
        #df_data = df_data[df_data['EV1'] >= 1]
        #if length >= len(df_data) + 3:
         #   return
        df_data = df_data.sort_values('Place', ascending=False)
        df_data = df_data.reset_index(drop=True)
        sum_odds = 0
        #print(df_data)
        count = 0
        for i in range(0,len(df_data)):
            if count == 1:
                break
            count = count + 1
            sum_odds = sum_odds + (1/df_data.loc[i,'odds_Show_Min'])
            if (1/sum_odds) >= 0:
                out_str = "Show," + str(df_data.loc[i,'horse_gate']) + ",,," + str(df_data.loc[i,"Place"]) + "," + str(df_data.loc[i,"odds_Show_Min"])
                self.tiketFile.write(out_str  + "\n")
                #print(out_str)
        
    #ワイドの購入
    def calc_QuinellaPlace(self):
        odds_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date + "\\" + self.race_id + "\\wide.csv", sep=",", encoding="cp932")
        odds_data = odds_data.select_dtypes(include=np.number)
        
        forecast_data = self.forecast_data[['horse_gate','Place']]
        df_data = pd.merge(odds_data, forecast_data, left_on='horse_gate1', right_on='horse_gate')
        df_data = pd.merge(df_data, forecast_data, left_on='horse_gate2', right_on='horse_gate')
        df_data['prob'] = df_data['Place_x'] * df_data['Place_y']
        df_data['EV'] = df_data['QuinellaPlace'] * df_data['prob']
        length = len(df_data)
        #df_data = df_data[df_data['EV'] >= 1]
        #if length >= len(df_data) + 3:
          #  return
        df_data = df_data.sort_values('prob', ascending=False)
        df_data = df_data.reset_index(drop=True)
        df_data = df_data[['horse_gate1','horse_gate2','QuinellaPlace','prob','EV']]
        sum_odds = 0
        #print(df_data)
        count = 0
        for i in range(0,len(df_data)):
            if count == 1:
                break
            count = count + 1
            sum_odds = sum_odds + (1/df_data.loc[i,'QuinellaPlace'])
            if (1/sum_odds) >= 0:
                out_str = "QuinellaPlace," + str(df_data.loc[i,'horse_gate1']) + "," + str(df_data.loc[i,'horse_gate2']) + ",," + str(df_data.loc[i,'prob']) + "," + str(df_data.loc[i,'QuinellaPlace'])        
                #print(out_str)
                self.tiketFile.write(out_str  + "\n")  
    
    #枠連の購入
    def calc_BracketPlace(self):
        odds_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date + "\\" + self.race_id + "\\wakuren.csv", sep=",", encoding="cp932")
        if len(odds_data) <= 1:
            return
        
        forecast_data = self.forecast_data[['lane_gate','Quinella']]
        lane_values = []
        prob_values = []
        for waku in range(1,9):
            waku_data = forecast_data[forecast_data['lane_gate'] == waku]
            waku_data = waku_data.reset_index(drop=True)
            prob = 1
            for i in range(0,len(waku_data)):
                prob = prob * (1- waku_data.loc[i,'Quinella'])
            prob = 1 - prob
            lane_values.append(waku)
            prob_values.append(prob)
        mydict1 = {'lane_gate': lane_values,'prob': prob_values}
        my_df1 = pd.DataFrame.from_dict(mydict1)
        df_data = pd.merge(odds_data, my_df1, left_on='lane_gate1', right_on='lane_gate')
        df_data = pd.merge(df_data, my_df1, left_on='lane_gate2', right_on='lane_gate')
        df_data['prob'] = df_data['prob_x'] * df_data['prob_y']
        for waku in range(1,9):
            waku_data = forecast_data[forecast_data['lane_gate'] == waku]
            waku_data = waku_data.reset_index(drop=True)
            prob = 1
            for i in range(0,len(waku_data)):
                prob = prob * waku_data.loc[i,'Quinella']
            index = df_data.index[(df_data['lane_gate1'] == waku) & (df_data['lane_gate2'] == waku)]
            df_data.loc[index,'prob'] = prob
        df_data['EV'] = df_data['BracketQuinella'] * df_data['prob']
        df_data = df_data.sort_values('prob', ascending=False)
        length = len(df_data)
        #df_data = df_data[df_data['EV'] >= 1]
        #if length >= len(df_data) + 3:
        #    return
        df_data = df_data.sort_values('prob', ascending=False)
        df_data = df_data.reset_index(drop=True)
        sum_odds = 0
        #print(df_data)
        count = 0
        for i in range(0,len(df_data)):
            if count == 1:
                break
            count = count + 1
            sum_odds = sum_odds + (1/df_data.loc[i,'BracketQuinella'])
            if (1/sum_odds) >= 0:
                out_str = "BracketQuinella," + str(df_data.loc[i,'lane_gate1']) + "," + str(df_data.loc[i,'lane_gate2']) + ",," + str(df_data.loc[i,'prob']) + "," + str(df_data.loc[i,'BracketQuinella'])        
                self.tiketFile.write(out_str  + "\n")
                #print(out_str)
    
    #馬連の購入
    def calc_Quinella(self):
        odds_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date + "\\" + self.race_id + "\\umaren.csv", sep=",", encoding="cp932")
        odds_data = odds_data.select_dtypes(include=np.number)
        
        forecast_data = self.forecast_data[['horse_gate','Quinella']]
        df_data = pd.merge(odds_data, forecast_data, left_on='horse_gate1', right_on='horse_gate')
        df_data = pd.merge(df_data, forecast_data, left_on='horse_gate2', right_on='horse_gate')
        df_data['prob'] = df_data['Quinella_x'] * df_data['Quinella_y']
        df_data['EV'] = df_data['Quinella_odds'] * df_data['prob']
        length = len(df_data)
        #df_data = df_data[df_data['EV'] >= 1]
        #if length >= len(df_data) + 3:
         #   return
        df_data = df_data.sort_values('prob', ascending=False)
        df_data = df_data.reset_index(drop=True)
        df_data = df_data[['horse_gate1','horse_gate2','Quinella_odds','prob','EV']]
        sum_odds = 0
        #print(df_data)
        count = 0
        for i in range(0,len(df_data)):
            if count == 1:
                break
            count = count + 1
            sum_odds = sum_odds + (1/df_data.loc[i,'Quinella_odds'])
            if (1/sum_odds) >= 0:
                out_str = "Quinella," + str(df_data.loc[i,'horse_gate1']) + "," + str(df_data.loc[i,'horse_gate2']) + ",," + str(df_data.loc[i,'prob']) + "," + str(df_data.loc[i,'Quinella_odds'])        
                #print(out_str)
                self.tiketFile.write(out_str  + "\n")
    
    #馬単の購入
    def calc_Exacta(self):
        odds_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date + "\\" + self.race_id + "\\umatan.csv", sep=",", encoding="cp932")
        odds_data = odds_data.select_dtypes(include=np.number)
        
        forecast_data = self.forecast_data[['horse_gate','Win','Quinella']]
        df_data = pd.merge(odds_data, forecast_data, left_on='horse_gate1', right_on='horse_gate')
        df_data = pd.merge(df_data, forecast_data, left_on='horse_gate2', right_on='horse_gate')
        df_data['prob'] = df_data['Win_x'] * df_data['Quinella_y'] * (1-df_data['Win_y'])
        df_data['EV'] = df_data['Exacta'] * df_data['prob']
        length = len(df_data)
        #df_data = df_data[df_data['EV'] >= 1]
        #if length >= len(df_data) + 3:
         #   return
        df_data = df_data[['horse_gate1','horse_gate2','Exacta','prob','EV']]
        df_data = df_data.sort_values('prob', ascending=False)
        df_data = df_data.reset_index(drop=True)
        sum_odds = 0
        #print(df_data)
        count = 0
        for i in range(0,len(df_data)):
            if count == 1:
                break
            count = count + 1
            sum_odds = sum_odds + (1/df_data.loc[i,'Exacta'])
            if (1/sum_odds) >= 0:
                out_str = "Exacta," + str(df_data.loc[i,'horse_gate1']) + "," + str(df_data.loc[i,'horse_gate2']) + ",," + str(df_data.loc[i,'prob']) + "," + str(df_data.loc[i,'Exacta'])        
                self.tiketFile.write(out_str  + "\n")
                #print(out_str)
    
    #3連複の購入
    def calc_Trio(self):
        odds_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date + "\\" + self.race_id + "\\fuku3.csv", sep=",", encoding="cp932",\
                                dtype={'horse_gate1':int,'horse_gate2':int,'horse_gate3':int,'Trio':object})
        odds_data['Trio'] = odds_data['Trio'].replace({'None':0})
        odds_data['Trio'] = odds_data['Trio'].astype(float)
        #print(odds_data.duplicated())
        odds_data = odds_data.reset_index(drop=True)
        odds_data = odds_data[odds_data.duplicated()]
        odds_data = odds_data.reset_index(drop=True)
        odds_data = odds_data[odds_data.duplicated()]
        odds_data = odds_data.reset_index(drop=True)
        forecast_data = self.forecast_data[['horse_gate','Place',]]
        df_data = pd.merge(odds_data, forecast_data, left_on='horse_gate1', right_on='horse_gate')
        df_data = pd.merge(df_data, forecast_data, left_on='horse_gate2', right_on='horse_gate')
        df_data = pd.merge(df_data, forecast_data, left_on='horse_gate3', right_on='horse_gate')
        df_data['prob'] = df_data['Place'] * df_data['Place_x'] * df_data['Place_y']
        df_data['EV'] = df_data['prob'] * df_data['Trio']
        length = len(df_data)
        #df_data = df_data[df_data['EV'] >= 1]
        #if length >= len(df_data) + 3:
         #   return
        df_data = df_data.sort_values('prob',ascending=False)
        df_data = df_data.reset_index(drop=True)
        #print(df_data)
        count = 0
        sum_odds = 0
        for i in range(0,len(df_data)):
            sum_odds = sum_odds + (1/df_data.loc[i,'Trio'])
            if (1/sum_odds) <= 3:
                break
            if count == 30:
                break
            count = count + 1
            out_str = "Trio," + str(df_data.loc[i,'horse_gate_x']) + "," + str(df_data.loc[i,'horse_gate_y']) + "," + str(df_data.loc[i,'horse_gate']) + "," + str(df_data.loc[i,'prob']) + "," + str(df_data.loc[i,'Trio'])        
            #print(out_str)
            self.tiketFile.write(out_str  + "\n")
    
    def calc_Trio2(self):
        forecast_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date + "\\" + self.race_id + "\\"+self.race_id+"_forecast.csv", sep=",", encoding="cp932")
        forecast_data = forecast_data.sort_values('Place',ascending=False)
        forecast_data = forecast_data.reset_index(drop=True)
        retu1 = []
        retu2 = []
        retu3 = []
        for i in range(0,len(forecast_data)):
            if i < 2:
                retu1.append(forecast_data.loc[i,'horse_gate'])
            if i < 4:
                retu2.append(forecast_data.loc[i,'horse_gate'])
            if i < 13:
                retu3.append(forecast_data.loc[i,'horse_gate'])
        lists = CalcTicket.calc_TrioCombi(retu1,retu2,retu3)
        for data in lists:
            out_str = "Trio," + str(data[0]) + "," + str(data[1]) + "," + str(data[2]) + ",,"       
            #print(out_str)
            self.tiketFile.write(out_str  + "\n")
    
    def calc_TrioCombi(retu1,retu2,retu3):
        lists_all = []
        for i in range(0,len(retu1)):
            for j in range(0,len(retu2)):
                for k in range(0,len(retu3)):
                    lists = []
                    if retu1[i] == retu2[j] or retu1[i] == retu3[k] or retu2[j] == retu3[k]:
                        continue
                    lists.append(retu1[i])
                    lists.append(retu2[j])
                    lists.append(retu3[k])
                    lists.sort()
                    lists_all.append(lists)
        return CalcTicket.get_unique_list(lists_all)
    
    def get_unique_list(seq):
        seen = []
        return [x for x in seq if x not in seen and not seen.append(x)]
        
    """ToDo
    #3連単の購入
    def calc_QuinellaPlace():
        #odds_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + date + "\\" + race_id + "\\wide.csv", sep=",", encoding="cp932")
    """
    
    def set_bettingmoney(self):
        ticket_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date  + "\\" + self.race_id + "\\ticket.csv", sep=',', encoding='cp932',
                                  names=[1,2,3,4,5,6,7,8,9])
        #ToDo
        
        ticket_types = ['Win','Show','BracketQuinella','Quinella','QuinellaPlace','Exacta','Trio','Trifecta']
        for ticket_type in ticket_types:
            index = ticket_data.index[ticket_data[1] == ticket_type]
            count = len(index)
            for i in index:
                    #ticket_data.loc[i,7] = round((float(count)*1.5/float(ticket_data.loc[i,6]))*100,-2)
                    ticket_data.loc[i,7] = 100
                    #if ticket_data.loc[i,7] == 0:
                     #   ticket_data.loc[i,7] = 100
        
        #ticket_data[7] = 100
        ticket_data = ticket_data.to_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date  + "\\" + self.race_id + "\\ticket.csv", sep=',', encoding='cp932')
        
    
    def main(self):
        #self.calc_Win()
        #self.calc_Show()
        #self.calc_QuinellaPlace()
        #self.calc_Quinella()
        #self.calc_BracketPlace()
        #self.calc_Exacta()
        self.calc_Trio()
        #self.calc_Trio2()
        self.tiketFile.close()
        self.set_bettingmoney()
    
    
def main():
    calcTicket = CalcTicket('sample' ,'202109050411')
    """
    calcTicket.calc_Win()
    calcTicket.calc_Show()
    calcTicket.calc_QuinellaPlace()
    calcTicket.calc_Quinella()
    calcTicket.calc_BracketPlace()
    calcTicket.calc_Exacta()
    calcTicket.calc_Trio()
    """
    calcTicket.calc_Trio2()
    calcTicket.tiketFile.close()
    calcTicket.set_bettingmoney()
    
    
if __name__ == "__main__":
    main()
        
    
    
    
    
    
    
    