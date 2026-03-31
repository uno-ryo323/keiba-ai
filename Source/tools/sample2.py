import pandas as pd

forecast_data = pd.read_csv("C:\\KeibaAI\\Data\\netKeiba\\result\\2021_forecast.csv", sep=",", encoding="cp932")

race_ids = forecast_data['race_id'].unique()

odds_sum = 0
count = 0
byCount = 0

for race_id in race_ids:
    data = forecast_data[forecast_data['race_id'] == race_id]
    data = data.sort_values('Win', ascending=False)
    data = data.reset_index(drop=True)
    data['EV'] = data['Win'] * data['odds']
    if data.loc[0,'EV'] >= 1:
        byCount = byCount + 1
        if data.loc[0,'rank'] == 1:
            odds_sum = odds_sum + data.loc[0,'odds']
            count = count + 1

print(odds_sum)
print(count)
print(byCount)
print(odds_sum/byCount,count/byCount)