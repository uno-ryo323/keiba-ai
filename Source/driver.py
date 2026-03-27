import getinfo
import preprocess
import racedb
import scraping
import keibaai
import pandas as pd
import os
import warnings

from config import RACECARD_DIR, RACELIST_DIR

section = 0


def forecast(date, race_id, type_ai, flag):

    getInfo = getinfo.GetInfo(date, race_id)
    pp = preprocess.PreProcess(date, race_id)

    # レー表の取得
    if flag == 1:
        getInfo.get_race_card()
        section = 1

        # 前処理

        diff = pp.get_diff_race()
        if not (len(diff) == 0):
            if not ((len(diff) == 1) and ((diff[0] == "0") or (diff[0] == 0))):
                rd = racedb.raceDB
                rd.get_race_result(diff)
                sc = scraping.Scraping
                sc.get_race_result(diff)
                pp.join_netkeiba_target(diff)
                pp.calc_agari_rank(diff)
                pp.join_pre_race_result()

    if type_ai == 1:
        pp.encode_use_LabelEncoder()
    else:
        pp.convert_data_old()

    # 予想の実行
    ai = keibaai.KeibaAI(date, race_id)
    ai.forecast_race(type_ai)

    section = 3
    """
    #オッズ取得から買い目決定
    getInfo.get_odds()
    
    section = 4
    
    calcTicket = calcticket.CalcTicket(date, race_id)
    calcTicket.main()
    """
    section = 5

    """
    #的中判定
    judgeTicket = judgeticket.JudgeTicket(date, race_id)
    judgeTicket.main()
    """


if __name__ == "__main__":
    mode = 1
    ai_type = 1
    start = 830
    flag = 0
    MAX_RETRY = 3
    warnings.simplefilter("ignore")
    if mode == 1:
        date = "20220320"
        race_id = "202209011211"
        if flag == 1:
            os.makedirs(RACECARD_DIR / date / race_id)
        forecast(date, race_id, ai_type, flag)
    elif mode == 2:
        date = "20211226"
        race_list = pd.read_csv(
            RACELIST_DIR / f"{date}.csv",
            sep=",",
            encoding="cp932",
            dtype={"race_id": str},
        )
        for i in range(0, len(race_list)):
            if i < 1:
                continue
            section = 0
            race_id = race_list.loc[i, "race_id"]
            course = race_list.loc[i, "course"]
            if "障" in course:
                continue
            os.makedirs(RACECARD_DIR / date / race_id)
            # print(race_id)
            forecast(date, race_id, ai_type)

    """
    for retry in range(MAX_RETRY + 1):
        try:
            if mode == 0:
                dates = ['20211106','20211107','20211113','20211114']
                #dates = ['20211107','20211113','20211114']
                for date in dates:
                    race_list = pd.read_csv(RACELIST_DIR / f"{date}.csv", sep="," , encoding="cp932",
                                            dtype={'race_id':str})
                    for i in range(0,len(race_list)):
                        section = 0
                        race_id = race_list.loc[i,'race_id']
                        course = race_list.loc[i,'course']
                        #if '障' in course:
                         #   continue
                        os.makedirs(RACECARD_DIR / date / race_id)
                        print(race_id)
                        forecast(date, race_id,ai_type)
            elif mode == 1:
                section = 0
                date = "20211205"
                race_id = "202107060212"
                
                if retry == 0:
                    os.makedirs(RACECARD_DIR / date / race_id)
                else:
                    shutil.rmtree(RACECARD_DIR / date / race_id)
                    os.makedirs(RACECARD_DIR / date / race_id)
                
                forecast(date, race_id, ai_type)
            else:
                race_list = pd.read_csv(DATA_DIR / "common" / "race_id_list_2021_2.csv", sep="," , encoding="cp932",
                                        dtype={'race_id':str,'date':str})
                for i in range(start,len(race_list)):
                     race_id = race_list.loc[i,'race_id']
                     date = race_list.loc[i,'date']
                     print(i,race_id)
                     if retry == 0:
                         os.makedirs(RACECARD_DIR / date / race_id)
                     else:
                         shutil.rmtree(RACECARD_DIR / date / race_id)
                         os.makedirs(RACECARD_DIR / date / race_id)
                     forecast(date, race_id,ai_type)
        except:
            print('Failed!. section={}'.format(section))
            time.sleep(5)
        else:
            break
    """
