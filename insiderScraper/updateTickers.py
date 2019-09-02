import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import re
import time
import random
from io import StringIO
import datetime

from datsup import nanhandler as nan
from datsup import log
from datsup import fileio
from dataTypes import Company, Trades
from exceptions import NoDataError
import sql


def run(database, logger: log.LogManager, tickers: np.ndarray):
    """Main update logic"""
    count = 0
    random.shuffle(tickers)

    for ticker in tickers:
        now = datetime.datetime.now()
        print(f'{now.month:02.0f}/{now.day:02.0f}/{now.year:02.0f} ' +
              f'{now.hour:02.0f}:{now.minute:02.0f}:{now.second:02.0f} - ' +
              f'Downloading {ticker.strip().upper()} - {count}/{len(tickers)}')

        page = 1
        flagNextPage = True

        while flagNextPage and page < 10:  # for > 1000 trade entries
            try:
                rawData = download(generateUrl(ticker, page))
            except NoDataError as e:
                fileio.appendLine('data/elimTickers.csv', ticker)
                logger.logError(e)
            else:
                data = process(rawData)
                insertToDb(database, data)
            page += 1

            # detect last page for ticker
            if len(rawData.table) != 1000: flagNextPage = False

            # page refresh delay - to decrease traffic frequency
            time.sleep(random.random()*10)

        # batch delay - to decrease traffic frequency
        count += 1
        if count % 8 == 0:
            sTime = random.random()*20
            print(f'{now.month:02.0f}/{now.day:02.0f}/{now.year:02.0f} ' +
                f'{now.hour:02.0f}:{now.minute:02.0f}:{now.second:02.0f} - ' +
                f'Sleeping for {sTime:02.1f}s')
            time.sleep(sTime)

    sql.updateLastFilingTimeStamp(database)  # update Company.lastFiling


def generateUrl(ticker: str, page: int) -> str:
    return "http://openinsider.com/screener?s=" + ticker + \
        "&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=" +\
        "1&xs=1&xa=1&xd=1&xg=1&xf=1&xm=1&xx=1&xc=1&xw=1&vl=&vh=&ocl=&och=&s" +\
        "ic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=" +\
        f"&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page={page}"


def download(url: str) -> dict:
    """Download and map raw data"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    table = pd.read_html(str(soup.findAll('table', {'class': 'tinytable'})))[0]

    if len(table.columns) != 16:  # unable to download error handling
        ticker = re.findall(
            r'(?<=http://openinsider.com/screener\?s=)\w+', url)[0]
        raise NoDataError(f'Unable to find data for {ticker.upper()}')

    table = table.drop(['X', '1d', '1w', '1m', '6m'], axis=1)
    table.columns = [
        'filingDate', 'startingDate', 'ticker', 'insiderName',
        'insiderTitle', 'tradeType', 'price', 'quantity',
        'sharesOwned', 'changeInSharesOwned', 'value']

    companyInfo = soup.find('div', {'id': 'subjectDetails'}).text.split(' - ')

    name = soup.find('div', {'class': 'h1title'}).text.split(
        ' - ')[1].strip().replace("'", "''")
    ticker = soup.find('div', {'class': 'h1title'}).text.split(
        ' - ')[0].strip().replace("'", "''")
    sector = companyInfo[0].strip().replace("'", "''")
    subSector = companyInfo[1].strip().replace("'", "''")
    industry = companyInfo[2].strip().replace("'", "''")
    cik = re.findall(r'\d+', ''.join(companyInfo))[0]

    company = Company(name, ticker, cik, sector, subSector, industry)
    rawTrades = Trades(table, company)

    return rawTrades


def process(rawTrades: Trades):
    """Clean raw data"""
    rawTrades.table['price'] = rawTrades.table['price'].map(
        lambda x: x.strip('$').replace(',', ''))
    rawTrades.table['quantity'] = rawTrades.table['quantity'].map(
        lambda x: str(x).strip('+').replace(',', ''))

    # ' must be '' for queries
    rawTrades.table['insiderName'] = rawTrades.table['insiderName'].map(
        lambda x: str(x).replace("'", "''"))
    rawTrades.table['insiderTitle'] = rawTrades.table['insiderTitle'].map(
        lambda x: str(x).replace("'", "''"))

    rawTrades.table = nan.replaceDefects(
        rawTrades.table,
        'insiderName',
        {'See "Remarks" below.': 'null'})

    return rawTrades


def insertToDb(database, data: Trades):
    """Map data structure to database"""
    # process industry
    selectSql = \
        f"""
            select industry_id
            from industry
            where name = '{data.company.industry}'
        """
    insertSql = \
        f"""
            insert into industry (name, sector, subSector)
            values (
                '{data.company.industry}',
                '{data.company.sector}',
                '{data.company.subSector}')
        """
    industryId = database.queryId(selectSql, insertSql)

    # process company
    selectSql = \
        f"""
            select company_id
            from company
            where cik = {data.company.cik}
        """
    insertSql = \
        f"""
            insert into company (name, ticker, cik, industry_id)
            values (
                '{data.company.name}',
                '{data.company.ticker}',
                {data.company.cik},
                {industryId})
        """
    companyId = database.queryId(selectSql, insertSql)
    sql.updateCompanyLastUpdates(database, data.company.ticker)

    for insider in data.table['insiderName'].unique():
        insiderWorkingData = data.table[data.table['insiderName'] == insider]
        insiderTitle = insiderWorkingData['insiderTitle'].iloc[0]

        insiderWorkingData['filingDate'] = pd.to_datetime(
            insiderWorkingData['filingDate']).copy()

        finalDate = max(insiderWorkingData['filingDate'])
        finalSharesOwned = insiderWorkingData[
            insiderWorkingData['filingDate'] == finalDate]['sharesOwned'].values[0]
        finalDate = str(finalDate)

        # convert col back to string for psycopg2 copy_from
        insiderWorkingData['filingDate'] = insiderWorkingData['filingDate'].map(
            lambda x: str(x)).copy()

        selectSql = \
            f"""
                select insider_id
                from insider
                where name = '{insider}' and company_id = {companyId}
            """
        insertSql = \
            f"""
                insert into insider (
                    name, title, company_id
                )
                values (
                    '{insider}', '{insiderTitle}', {companyId}
                )
            """
        insiderId = database.queryId(selectSql, insertSql)

        # update insider sharesOwned and asOfDate
        currentFinalDate = sql.getCurrentFinalDate(database, insiderId)
        if currentFinalDate is None or \
            currentFinalDate < np.datetime64(finalDate):
            sql.updateInsiderMutables(
                database, insiderId, finalSharesOwned, finalDate)

        for tradeType in insiderWorkingData['tradeType'].unique():
            tradeTypeWorkingData = insiderWorkingData[
                insiderWorkingData['tradeType'] == tradeType]
            tradeTypeCode = tradeType.split(' - ')[0].strip()
            tradeTypeType = tradeType.split(' - ')[1].strip()
            selectSql = \
                f"""
                    select tradetype_id
                    from tradetype
                    where code = '{tradeTypeCode}'
                """
            insertSql = \
                f"""
                    insert into TradeType (code, type)
                    values ('{tradeTypeCode}', '{tradeTypeType}')
                """
            tradeTypeId = database.queryId(selectSql, insertSql)

            tradeTypeWorkingData = tradeTypeWorkingData[[
                'filingDate', 'startingDate', 'price', 'quantity']]
            tradeTypeWorkingData['insider_id'] = insiderId
            tradeTypeWorkingData['tradetype_id'] = tradeTypeId

            #   reorder columns to match with db columns ordering
            tradeTypeWorkingData = tradeTypeWorkingData[[
                'insider_id', 'tradetype_id', 'filingDate',
                'startingDate', 'price', 'quantity']]

            # https://stackoverflow.com/questions/1869973/recreating-postgres-copy-directly-in-python
            f = StringIO()
            ioWriteString = '\n'.join([
                '\t'.join(list(map(str, x))) for x in tradeTypeWorkingData.values])
            f.write(ioWriteString)
            f.seek(0)

            database.cursor.copy_from(f, 'Trade', columns=(
                'insider_id', 'tradetype_id', 'filingDate',
                'startingDate', 'price', 'quantity'))
            database.commit()
    sql.removeDuplicateTrades(database)
