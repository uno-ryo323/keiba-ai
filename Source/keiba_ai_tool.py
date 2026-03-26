# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 01:02:31 2021

@author: RYO
"""

from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
import getinfo
import preprocess
import racedb
import mycalender
import keibaai
import scraping
import re 

class keibaAITestTool(Toplevel):
   
    def call_popup_calender():
        root = Tk()
        root.title("Calendar App")
        mycal = mycalender.MyCalendar(root)
        mycal.pack()
        root.mainloop()
            
    def call_get_race_list(self):
        date = self.entry2.get()
        if re.fullmatch(r'[0-9]{8}',date) == None:
            self.write("日付は8桁の半角数字で入力してください．")
            return
        
        getInfo = getinfo.GetInfo("","")
        race_list = getInfo.get_race_time(date)
    
        root = Tk()
        root.title("raceList")
        tree = ttk.Treeview(root)
        # 列インデックスの作成
        tree["columns"] = (1,2,3,4,5,6,7)
        # 表スタイルの設定(headingsはツリー形式ではない、通常の表形式)
        tree["show"] = "headings"
        # 各列の設定(インデックス,オプション(今回は幅を指定))
        for i in range(0,len(tree["columns"])):
            tree.column(i+1,width=100)
            
        # 各列のヘッダー設定(インデックス,テキスト)
        tree.heading(1,text="place")
        tree.heading(2,text="raceNum")
        tree.heading(3,text="raceName")
        tree.heading(4,text="raceID")
        tree.heading(5,text="startTime")
        tree.heading(6,text="course")
        tree.heading(7,text="headCount")
        #print(race_list)
        
        for race in race_list:
            tree.insert("", "end", values=[race['place'],race['race_num'],race['race_name'],race['race_id'],race['startTime'],race['course'],race['headcount']])
        
        tree.pack()

    def forecast(self):
        race_id = self.entry1.get()
        if re.fullmatch(r'[0-9]{12}',race_id) == None:
            self.write("レースIDは12桁の半角数字で入力してください．")
            return
        pp = preprocess.PreProcess
        getinfo.GetInfo.get_race_card(race_id)
        diff = pp.get_diff_race(race_id)
        
        #if not (len(diff) == 0):
        #    if not ((len(diff) == 1) and ((diff[0] == 0) or (diff[0] == "0"))):
        #rd = racedb.raceDB
        #rd.get_race_result(diff)
        #sc = scraping.Scraping
        #sc.get_race_result(diff)
        pp.join_netkeiba_target(diff)
        pp.calc_agari_rank(diff)
        
        pp.join_pre_race_result(race_id)
        pp.encode_use_LabelEncoder(race_id)
        
        ai = keibaai.KeibaAI
        ai.forecast_race(race_id)

    def write(self, logMessage, state='MESSAGE'):
        self.scrolledText['state'] = NORMAL
        self.scrolledText.insert('end', logMessage+'\n', state)
        self.scrolledText.see(END)
        self.scrolledText['state'] = DISABLED
    
    def __init__(self, master):
        
        master.title('keibaAITestTool')
        self.frame1 = ttk.Frame(master)
        self.frame2 = ttk.Frame(master)
        self.frame3 = ttk.Frame(master)
        
        self.label1 = ttk.Label(self.frame1, text='レースID', width=8)
        self.label2 = ttk.Label(self.frame2, text='日付', width=8)
        
        self.entry1_text = StringVar()
        self.entry2_text = StringVar()
        
        #global entry1,entry2
        self.entry1 = ttk.Entry(self.frame1, textvariable=self.entry1_text)
        self.entry2 = ttk.Entry(self.frame2, textvariable=self.entry2_text)
        
        self.button1 = ttk.Button(self.frame1, text='予想実行', command=self.forecast)
        self.button2 = ttk.Button(self.frame2, text='カレンダー表示', command=keibaAITestTool.call_popup_calender)
        self.button3 = ttk.Button(self.frame2, text='レース一覧取得', command=self.call_get_race_list)
        
        self. scrolledText = scrolledtext.ScrolledText(self.frame3,height=15,state=DISABLED)
        self.frame1.pack(anchor=W)
        self.frame2.pack(anchor=W)
        self.frame3.pack(anchor=W)
        
        #frame1
        self.label1.pack(side=LEFT)
        self.entry1.pack(side=LEFT)
        self.button1.pack(side=LEFT)
        
        #frame2
        self.label2.pack(side=LEFT)
        self.entry2.pack(side=LEFT)
        self.button2.pack(side=LEFT)
        self.button3.pack(side=LEFT)
        
        #frame3
        self.scrolledText.pack()

if __name__ == "__main__":
    root = Tk()
    tool = keibaAITestTool(root)
    root.mainloop()