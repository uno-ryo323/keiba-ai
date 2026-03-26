import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
import pickle

class KeibaAI():
        
    def __init__(self, date, race_id):
        self.date = date
        self.race_id = race_id
    
    def plot_feature_importance(df): 
        n_features = len(df)
        df_plot = df.sort_values("importance")            # df_importanceをプロット用に特徴量重要度を昇順ソート 
        f_importance_plot = df_plot['importance'].values  # 特徴量重要度の取得 
        plt.barh(range(n_features), f_importance_plot, align='center') 
        cols_plot = df_plot['feature'].values             # 特徴量の取得 
        plt.yticks(np.arange(n_features), cols_plot)      # x軸,y軸の値の設定
        plt.xlabel('Feature importance')                  # x軸のタイトル
        plt.ylabel('Feature')                             # y軸のタイトル
    
    @staticmethod
    def remove_data(data):
        data = data.drop("race_id",axis=1)        
        #data = data.drop("year",axis=1)
        data = data.drop("day",axis=1)
        data = data.drop("race_name",axis=1)       
        data = data.drop("rank",axis=1)       
        data = data.drop("horse_name",axis=1)
        data = data.drop("time",axis=1)
        data = data.drop("agari",axis=1)
        data = data.drop("corner_position1",axis=1)
        data = data.drop("corner_position2",axis=1)
        data = data.drop("corner_position3",axis=1)
        data = data.drop("corner_position4",axis=1)
        data = data.drop("time_index",axis=1)
        data = data.drop("remarks",axis=1)
        data = data.drop("horse_type",axis=1)
        data = data.drop("horse_id",axis=1)
        data = data.drop("pre_race1",axis=1)        
        data = data.drop("pre_race2",axis=1)        
        data = data.drop("pre_race3",axis=1)        
        data = data.drop("pre_race4",axis=1)        
        data = data.drop("pre_race5",axis=1)        
 
        data = data.drop("rank_Win", axis=1)
        data = data.drop("rank_Quinella", axis=1)
        data = data.drop("rank_Place", axis=1)
        
        return data
    
    @staticmethod
    def trim_data(data):
        race_id = data['race_id']
        rank = data['rank']
        year = data['year']
        month = data['month']
        day = data['day']
        place = data['place']
        race_name = data['race_name']
        class_ = data['class']
        course = data['course']
        distance = data['distance']
        race_num = data['race_num']
        gate_lane = data['lane_gate']
        horse_lane = data['horse_gate']
        horse_name = data['horse_name']
        jockey = data['jockey']
        popular_rank = data['popular_rank']
        odds = data['odds']
        
        data = pd.concat([
                          race_id,
                          rank,
                          year,
                          month,
                          day,
                          place,
                          race_name,
                          class_,
                          course,
                          distance,
                          race_num,
                          gate_lane, 
                          horse_lane, 
                          horse_name, 
                          jockey,
                          popular_rank, 
                          odds], axis=1) 
        
        return data
    
    def make_model():        
        #レース結果を読み込み
        print("csvファイルを読み込みます")
        keiba_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\result\\race_jra2.3.csv", sep=",", encoding="cp932")
        keiba_data = keiba_data[keiba_data['course'] < 2]
        keiba_data = keiba_data[keiba_data['rank'] >= 1]
        keiba_data = keiba_data[keiba_data['year'] <= 2020]
        keiba_data = KeibaAI.remove_data(keiba_data)

        """train_X = keiba_data[keiba_data['year'] <= 2019].drop("year", axis=1).drop("rank_Win", axis=1)       
        test_X = keiba_data[keiba_data['year'] == 2020].drop("year", axis=1).drop("rank_Win", axis=1)      
        train_Y = keiba_data.loc[keiba_data['year'] <= 2019,'rank_Win']
        test_Y = keiba_data.loc[keiba_data['year'] == 2020,'rank_Win']"""


        #説明変数（馬場や騎手など）
        X = keiba_data.drop("rank_Place", axis=1)       
        train_X = X[X['year'] <= 2019].drop("year", axis=1)
        test_X = X[X['year'] == 2020].drop("year", axis=1)
        #目的変数（順位）
        train_Y = keiba_data.loc[keiba_data['year'] <= 2019,"rank_Place"]
        test_Y = keiba_data.loc[keiba_data['year'] == 2020,"rank_Place"]
        #データの準備
        #train_X, test_X, train_Y, test_Y = train_test_split(X, Y, test_size=0.2, shuffle=True,random_state=0)


        lgb_train = lgb.Dataset(train_X, train_Y)
        lgb_test = lgb.Dataset(test_X, test_Y, reference=lgb_train)

        # LightGBMのハイパーパラメータを設定
        
        params = {'objective': 'binary', 
                  'metric': 'binary_logloss', 
                  'boosting_type': 'gbdt', 
                  'num_iterations': 100000, 
                  'early_stopping_round': 100}
    
        lgb_results = {}                                    # 学習の履歴を入れる入物
        model = lgb.train(params=params,                    # ハイパーパラメータをセット
                          train_set=lgb_train,              # 訓練データを訓練用にセット
                          valid_sets=[lgb_train, lgb_test], # 訓練データとテストデータをセット
                          valid_names=['Train', 'Test'],    # データセットの名前をそれぞれ設定
                          evals_result=lgb_results)       # 履歴を保存する
        
        print(model.params)
        print(model.best_iteration)
        print(model.best_score)
        filename = 'C:\\keibaAI\\Source\\model\\Ver1.1\\Place.sav'
        pickle.dump(model, open(filename, 'wb'))
        KeibaAI.show_feature_value(X.drop('year', axis=1).columns, model)
        
        
    def forecast_race():
        #modelのインポート(ToDo)
        path = "C:\\keibaAI\\Source\\model\\Ver1.1\\"

        model_filename = 'Win' + '.sav'
        model1 = pickle.load(open(path + model_filename, 'rb'))
        model_filename = 'Quinella' + '.sav'
        model2 = pickle.load(open(path + model_filename, 'rb'))
        model_filename = 'Place' + '.sav'
        model3 = pickle.load(open(path + model_filename, 'rb'))

        #予測データの読み込み      
        test_data = pd.read_csv("C:\\KeibaAI\\Data\\netKeiba\\result\\race_jra2.3.csv", sep=",", encoding="cp932")
        #test_data = pd.read_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date +  "\\" + self.race_id + "\\" + self.race_id + "_c2.csv", sep=",", encoding="cp932")
        #test_data = test_data.drop(columns=test_data.columns[[0]])
        
        temp_data = test_data 
        test_data = KeibaAI.remove_data(test_data)
        test_data = test_data[test_data['year'] == 2021]
        test_data = test_data.drop('year', axis=1)
        #予測の実行
        y_pred_prob1 = model1.predict(test_data)
        y_pred_prob2 = model2.predict(test_data)
        y_pred_prob3 = model3.predict(test_data)
       
        #予測結果の出力
        result_data1 = pd.DataFrame(y_pred_prob1).set_axis(['Win'], axis=1)
        result_data2 = pd.DataFrame(y_pred_prob2).set_axis(['Quinella'], axis=1)
        result_data3 = pd.DataFrame(y_pred_prob3).set_axis(['Place'], axis=1)
        #result_data3 = pd.DataFrame(y_pred_prob3).set_axis(['Place','1','2'], axis=1)
    
        result_data1 = result_data1.reset_index(drop=True)
        result_data2 = result_data2.reset_index(drop=True)
        result_data3 = result_data3.reset_index(drop=True)

        temp_data = KeibaAI.remove_data2(temp_data[temp_data['year'] == 2021])
        temp_data = temp_data.reset_index(drop=True)
        #予測結果とレース表をマージして出力
        result_data = pd.concat([result_data1, result_data2, result_data3['Place'], temp_data], axis=1)
        #result_data.to_csv("C:\\keibaAI\\Data\\netKeiba\\racecard\\" + self.date +  "\\" + self.race_id + "\\" + self.race_id + "_forecast.csv", sep=",", encoding="shift_jis")
        result_data.to_csv("C:\\KeibaAI\\Data\\netKeiba\\result\\2021_forecast.csv", sep=",", encoding="cp932")

        #result_data = result_data.sort_values('Place', ascending=False)
        #print(result_data)
        
        return result_data
        
    def remove_data2(data):
       return data[['race_id','year','month','day','place','race_num','race_name','rank','lane_gate','horse_gate','horse_name','popular_rank','odds']]
        #return data[['lane_gate','horse_gate','horse_name','popular_rank']]
        

    @staticmethod
    def show_feature_value(columns, model):
        pd.set_option("display.max_rows",200)
        cols = columns
        f_importance = np.array(model.feature_importance(importance_type="gain"))
        f_importance = f_importance/np.sum(f_importance)
        df_importance = pd.DataFrame({"feature":cols, "importance": f_importance})
        df_importance = df_importance.sort_values("importance", ascending=False)
        print(df_importance)
        #df_importance.to_csv(r"C:\keibaAI\Data\netKeiba\common\feature_importance.csv", sep=",", encoding="shift_jis")
        
        
if __name__ == "__main__":
    #KeibaAI.make_model()
    #keibaAi = KeibaAI('20211106','202103020101')
    KeibaAI.forecast_race()
    
    
    
    
    
    
    
    
    
    
    
    
    
