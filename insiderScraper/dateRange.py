"""Implements update by --date-range functionality"""
import pandas as pd
import requests
import numpy as np
from bs4 import BeautifulSoup
import datetime
import time
import random

from datsup import datahandling as dh


def getTickers(dateRange):
    startDate = pd.to_datetime(dateRange[0])
    endDate = pd.to_datetime(dateRange[1])
    tickers = np.array([])
    count = 0
    for date in dh.dateInRange(startDate, endDate):
        now = datetime.datetime.now()

        print(f'{now.month:02.0f}/{now.day:02.0f}/{now.year:02.0f} ' +
            f'{now.hour:02.0f}:{now.minute:02.0f}:{now.second:02.0f} - ' +
            f'Generating tickers - ' +
            f'{count}/{(endDate-startDate).days:.0f}')

        response = requests.get(generateUrl(date))
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            workingTickers = pd.read_html(
                str(soup.find(
                    'table', {'class': 'tinytable'})))[0]['Ticker'].unique()
        except ValueError:  # no data for weekend / holiday
            pass
        tickers = dh.combine(tickers, workingTickers)
        count += 1
        time.sleep(random.random()*10)
    tickers = dh.uniqueValues(tickers)
    return tickers


def generateUrl(date: pd.Timestamp):
    """"""
    url = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=-1&fdr=" +\
        f"{date.month:02.0f}%2F{date.day:02.0f}%2F{date.year:04.0f}+-+" +\
        f"{date.month:02.0f}%2F{date.day:02.0f}%2F{date.year:04.0f}&td=0&td" +\
        "r=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&xa=1&xd=1&xg=1&xf=1&xm=1&xx=1&" +\
        "xc=1&xw=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&isofficer=1" +\
        "&iscob=1&isceo=1&ispres=1&iscoo=1&iscfo=1&isgc=1&isvp=1&isdirector" +\
        "=1&istenpercent=1&isother=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2" +\
        "l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"
    return url
