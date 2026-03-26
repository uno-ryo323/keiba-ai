import racedb
import pandas as pd

if __name__ == "__main__":
    race_id_list = pd.read_csv('C:\\keibaAI\\Data\\netKeiba\\common\\race_id_list_2010-2021.csv', sep=',', encoding='cp932',\
                               dtype={'year':int,'race_id':object})
    for year in range(2010,2010-1,-1):
        tmp_list = race_id_list[race_id_list['year'] == year]
        race_ids = tmp_list['race_id']
        rd = racedb.raceDB
        rd.get_race_result(race_ids)
            

