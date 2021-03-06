"""Generate sql database operations"""
from datsup.psqladapter import DatabaseManager
import globalconst


SQLSERVERFLAG = globalconst.SQLSERVERFLAG
schema = globalconst.SCHEMA


def removeDuplicateTrades(database):
    """Delete all duplicate trade entries"""
    sql = \
        f"""
            delete from {schema}Trade t1 where exists (
                select 1 from {schema}Trade t2
                where
                    t1.insider_id = t2.insider_id and
                    t1.filingDate = t2.filingDate and
                    t1.price = t2.price and
                    t1.quantity = t2.quantity and
                    t1.trade_id < t2.trade_id
            )
        """
    if SQLSERVERFLAG: sql = "exec sp_deleteDuplicateTrades"
    database.runSQL(sql, verify=True)


def updateLastFilingTimeStamp(database):
    """Full update of the lastFiling field in Company table"""

    sql = \
        f"""
            with t as (
                select insider_id, max(filingDate) insiderLastUpdate
                from {schema}Trade
                group by insider_id
            ), t2 as (
                select max(t.insiderLastUpdate) companyLastUpdate, i.company_id
                from t
                inner join {schema}Insider i on t.insider_id = i.insider_id
                group by i.company_id
            )
            update {schema}Company c
            set lastFiling = (
                select companyLastUpdate
                from t2
                where t2.company_id = c.company_id
            )
        """
    if SQLSERVERFLAG: sql = "exec sp_updateCompanyLastFiling"
    database.runSQL(sql, verify=True)


def updateCompanyLastUpdates(database: DatabaseManager, ticker: str):
    """Update lastUpdate field in Company table with current timestamp"""
    sql = \
        f"""
            update {schema}Company
            set lastUpdated = now()
            where ticker = '{ticker}'
        """
    if SQLSERVERFLAG: sql = sql.replace('now()', 'SYSUTCDATETIME()')
    database.runSQL(sql, verify=True)


def updateInsiderMutables(database, insiderId, sharesOwned, asOfDate):
    """"""
    sql = \
        f"""
            update {schema}Insider
            set
                sharesOwned = {sharesOwned},
                asOfDate = '{asOfDate}'
            where insider_id = {insiderId}
        """
    database.runSQL(sql, verify=True)


def getCurrentFinalDate(database, insiderId):
    """Get the current Insider.finalDate"""
    result = database.getData(
        f'select asOfDate from {schema}Insider where insider_id = {insiderId}')
    return None if result is None else result['asOfDate'].values[0]


def checkSqlString(sql, values):
    """Implement database.cursor.mogrify(sql, params)"""
    unique = "%PARAMETER%"
    sql = sql.replace("?", unique)
    for v in values: sql = sql.replace(unique, repr(v), 1)
    return sql


def setupSqlServerSP(database):
    sql = \
        """
            create procedure sp_deleteDuplicateTrades as
            delete from insiderTrading.Trade
            where trade_id in (
                select max(trade_id)
                from insiderTrading.Trade
                group by filingDate, startingDate, price, quantity, 
                    insider_id, company_id, tradetype_id
                having count(1) > 1
            )

            create procedure sp_updateCompanyLastFiling as
            with t as (
                select insider_id, max(filingDate) insiderLastUpdate
                from insiderTrading.Trade
                group by insider_id
            ), t2 as (
                select max(t.insiderLastUpdate) companyLastUpdate, i.company_id
                from t
                inner join insiderTrading.Insider i on t.insider_id = i.insider_id
                group by i.company_id
            )
            update c 
            set lastFiling = (
                select companyLastUpdate
                from t2
                where t2.company_id = c.company_id
            )
            from insiderTrading.Company c
        """
    database.runSQL(sql, verify=True)