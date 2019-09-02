from datsup.psqladapter import DatabaseManager


def getTickers(database: DatabaseManager, noTickers):
    sql = \
        f"""
            select ticker
            from company
            order by lastUpdated asc
            limit {str(noTickers)}
        """
    tickers = database.getData(sql)['ticker'].values
    return tickers
