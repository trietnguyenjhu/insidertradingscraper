import re
import pandas as pd
import numpy as np

from datsup.psqladapter import DatabaseManager
from datsup import datahandling as dh

import globalconst

schema = globalconst.SCHEMA

def processTickerCSV(path: str):
    """Filter out non-equity tickers"""
    rawTickers = pd.read_csv(path)
    tickers = rawTickers[rawTickers['ticker'].map(
            lambda x: len(re.findall('[\^\.]', x)) == 0)]['ticker'].values
    return np.unique(tickers)


def filterTickersFromCSV(
    tickers: np.ndarray, filterFilePath: str) -> np.ndarray:
    """Filter out tickers from file"""
    fArray = pd.read_csv(filterFilePath)['ticker'].values
    tickers = dh.filterArray(tickers, fArray)
    return tickers


def filterTickersFromDb(tickers: np.array, database: DatabaseManager):
    """Filter out tickers already in database"""
    fDf = database.getData(
        f'select ticker from {schema}Company')
    if fDf is not None:
        tickers = dh.filterArray(tickers, fDf['ticker'].values)
    return tickers
