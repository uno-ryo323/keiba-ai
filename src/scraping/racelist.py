"""
racelist.py — netKeibaのカレンダーから race_id 一覧を取得する

指定した年月範囲の全JRAレースの race_id を収集し、CSV に保存する。
生成したCSVは racedb.py / scraping.py のインプットとして使用する。

使い方:
    python -m src.scraping.racelist 2022 3 2026 4
    または
    from src.scraping.racelist import get_race_list_range
    get_race_list_range("2022", "03", "2026", "04")
"""

import calendar
import re
import sys
from datetime import datetime, timedelta

import pandas as pd
from bs4 import BeautifulSoup

from ..config import ASSETS_DIR, URL_CALENDAR, URL_RACELIST_PAGE
from .getinfo import GetInfo


def _get_soup(driver, url: str) -> BeautifulSoup:
    """指定URLに遷移してBeautifulSoupオブジェクトを返す"""
    driver.get(url)
    return BeautifulSoup(driver.page_source, "lxml")


def get_race_list_for_month(driver, year: str, month: str) -> list[dict]:
    """
    指定された年・月のレース一覧情報を取得してリストで返す

    Args:
        driver: Seleniumドライバ（ログイン済み）
        year: 年（例: "2025"）
        month: 月（例: "05"）

    Returns:
        各レースの情報を持つ辞書のリスト
    """
    results = []
    key = [
        "year",
        "month",
        "day",
        "place",
        "race_num",
        "race_name",
        "race_id",
        "startTime",
        "course",
        "headcount",
    ]

    soup = _get_soup(driver, f"{URL_CALENDAR}?year={year}&month={month}")
    race_cells = soup.find_all("td", class_="RaceCellBox")

    for cell in race_cells:
        # 開催場のない日はスキップ
        if not cell.find_all("span", class_="JyoName"):
            continue
        a_tag = cell.find("a")
        if not a_tag or "href" not in a_tag.attrs:
            continue

        # 開催日を URL から取得（例: "20250518"）
        kaisai_date = a_tag["href"].split("kaisai_date=")[-1][:8]
        day = kaisai_date[6:8]

        soup2 = _get_soup(driver, f"{URL_RACELIST_PAGE}?kaisai_date={kaisai_date}")
        datalist = soup2.find_all("dd", class_="RaceList_Data")
        placelist_raw = soup2.find_all("p", class_="RaceList_DataTitle")

        # 開催場所名（漢字2文字）を抽出
        match_pattern = r"[札幌函館新潟阪神京都小倉中山中京福島東京]{2}"
        placelist = [re.search(match_pattern, str(p)).group() for p in placelist_raw]

        for count, data in enumerate(datalist):
            for li in data.find_all("li"):
                # レース番号
                race_num_tag = li.find("div", class_="Race_Num")
                race_num = re.sub(r"\D", "", race_num_tag.text if race_num_tag else "")

                # レース名
                race_name_tag = li.find("span", class_="ItemTitle")
                race_name = race_name_tag.text.strip() if race_name_tag else ""

                # race_id
                race_id_match = re.search(r"race_id=(\d+)", str(li))
                if not race_id_match:
                    continue
                race_id = race_id_match.group(1)

                # 発走時刻・コース・頭数
                race_data = li.find("div", class_="RaceData")
                spans = race_data.find_all("span") if race_data else []
                span_texts = [s.text.strip() for s in spans]

                startTime = course = headcount = ""
                if len(span_texts) >= 3:
                    if ":" in span_texts[0]:
                        startTime, course, headcount = span_texts[:3]
                    elif len(span_texts) >= 4 and ":" in span_texts[1]:
                        startTime, course, headcount = span_texts[1:4]

                results.append(
                    dict(
                        zip(
                            key,
                            [
                                year,
                                month,
                                day,
                                placelist[count],
                                race_num,
                                race_name,
                                race_id,
                                startTime,
                                course,
                                headcount,
                            ],
                        )
                    )
                )

    return results


def get_race_list_range(
    start_year: str,
    start_month: str,
    end_year: str,
    end_month: str,
) -> None:
    """
    指定した年月の範囲内で全レース情報を取得し、CSVに保存する

    出力先: data/netkeiba/assets/race_id_list_{start}_{end}.csv

    Args:
        start_year:  開始年（例: "2022"）
        start_month: 開始月（例: "03"）
        end_year:    終了年（例: "2026"）
        end_month:   終了月（例: "04"）
    """
    driver = GetInfo._create_driver()
    GetInfo.login_process(driver)

    all_results = []
    start_date = datetime(int(start_year), int(start_month), 1)
    end_date = datetime(
        int(end_year),
        int(end_month),
        calendar.monthrange(int(end_year), int(end_month))[1],
    )

    current = start_date
    while current <= end_date:
        year = str(current.year)
        month = str(current.month).zfill(2)
        print(f"{year}-{month} のレース一覧を取得中...")

        month_results = get_race_list_for_month(driver, year, month)
        all_results.extend(month_results)
        print(f"  → {len(month_results)} レース取得")

        # 翌月へ
        days_in_month = calendar.monthrange(current.year, current.month)[1]
        current += timedelta(days=days_in_month)

    driver.quit()

    df = pd.DataFrame(all_results)
    sy, sm = start_year, start_month.zfill(2)
    ey, em = end_year, end_month.zfill(2)
    filename = f"race_id_list_{sy}{sm}_{ey}{em}.csv"
    output_path = ASSETS_DIR / filename
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, sep=",", encoding="shift_jis")
    print(f"\n保存完了: {output_path}")
    print(f"合計 {len(df)} レース")


if __name__ == "__main__":
    if len(sys.argv) == 5:
        _, sy, sm, ey, em = sys.argv
    else:
        # デフォルト: 不足分（2022-03 〜 2026-04）
        sy, sm, ey, em = "2022", "03", "2026", "04"

    get_race_list_range(sy, sm, ey, em)
