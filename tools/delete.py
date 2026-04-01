import pandas as pd
import racedb

data = pd.read_csv(
    "C:\\KeibaAI\\Data\\netKeiba\\result\\race_jra.csv", sep=",", encoding="cp932"
)
data2 = pd.read_csv(
    "C:\\KeibaAI\\Data\\netKeiba\\result\\race_jra2.csv", sep=",", encoding="cp932"
)

race_id_list1 = data["race_id"].unique()
race_id_list2 = data2["race_id"].unique()
pre_race_sum = set(race_id_list1) - set(race_id_list2)

print(len(race_id_list1))
print(len(race_id_list2))
print(len(pre_race_sum))
# print(pre_race_sum)

"""print(len(data['race_id'].unique()))
index = data.index[(data['delete1'] != "Not Delete")]
race_list = data.loc[index,'race_id'].unique()
print(len(race_list))"""
"""for race_id in race_list:
    print(race_id)
    index = data.index[(data['race_id'] == race_id)]
    data = data.drop(index)""
data.to_csv("C:\\KeibaAI\\Data\\netKeiba\\result\\race_jra2.csv", sep=",", encoding="cp932")

print(len(data['race_id'].unique()))
"""
rd = racedb.raceDB
rd.get_race_result(pre_race_sum)
# 201105050810
