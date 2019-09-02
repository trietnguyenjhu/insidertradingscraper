"""Generate sql database operations"""
from datsup.psqladapter import DatabaseManager


def removeDuplicateTrades(database):
    """Delete all duplicate trade entries"""
    sql = \
        """
            delete from trade t1 where exists (
                select 1 from trade t2
                where
                    t1.insider_id = t2.insider_id and
                    t1.filingDate = t2.filingDate and
                    t1.price = t2.price and
                    t1.quantity = t2.quantity and
                    t1.trade_id < t2.trade_id
            )
        """
    database.runSQL(sql, verify=True)


def updateLastFilingTimeStamp(database):
    """Full update of the lastFiling field in Company table"""

    sql = \
        """
            with t as (
                select insider_id, max(filingDate) insiderLastUpdate
                from trade
                group by insider_id
            ), t2 as (
                select max(t.insiderLastUpdate) companyLastUpdate, i.company_id
                from t
                inner join insider i on t.insider_id = i.insider_id
                group by i.company_id
            )
            update company c
            set lastFiling = (
                select companyLastUpdate
                from t2
                where t2.company_id = c.company_id
            )
        """
    database.runSQL(sql, verify=True)


def updateCompanyLastUpdates(database: DatabaseManager, ticker: str):
    """Update lastUpdate field in Company table with current timestamp"""
    sql = \
        f"""
            update company
            set lastUpdated = now()
            where ticker = '{ticker}'
        """
    database.runSQL(sql, verify=True)


def updateInsiderMutables(database, insiderId, sharesOwned, asOfDate):
    """"""
    sql = \
        f"""
            update insider
            set
                sharesOwned = {sharesOwned},
                asOfDate = '{asOfDate}'
            where insider_id = {insiderId}
        """
    database.runSQL(sql, verify=True)


def getCurrentFinalDate(database, insiderId):
    """Get the current Insider.finalDate"""
    return database.getData(
        f'select asOfDate from insider where insider_id = {insiderId}')[
            'asofdate'].values[0]
