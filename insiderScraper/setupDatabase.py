import globalconst

schema = globalconst.SCHEMA

def run(database):
    """Drop all tables and recreate"""

    # drop tables
    dropTables = 'Trade TradeType Insider Company Industry'.split()
    dropTables = [f'{schema}{x}' for x in dropTables]
    for table in dropTables:
        database.dropTableIfExists(table, verify=True)

    database.createTable(
        table=f'{schema}TradeType',
        dataVars=dict(
            code='char(1)',
            type='varchar(20)'),
        foreignKeys=dict()
    )

    database.createTable(
        table=f'{schema}Industry',
        dataVars=dict(
            name='varchar(100)',
            sector='varchar(100)',
            subSector='varchar(100)'),
        foreignKeys=dict()
    )

    database.createTable(
        table=f'{schema}Company',
        dataVars=dict(
            name='varchar(100)',
            ticker='varchar(20)',
            cik='numeric',
            lastUpdated='datetime2',
            lastFiling='datetime2'),
        foreignKeys=dict(
            industry_id=f'{schema}Industry')
    )

    database.createTable(
        table=f'{schema}Insider',
        dataVars=dict(
            name='varchar(100)',
            title='varchar(100)',
            sharesOwned='numeric',
            asOfDate='datetime2'),
        foreignKeys=dict(
            company_id=f'{schema}Company')
    )

    database.createTable(
        table=f'{schema}Trade',
        dataVars=dict(
            filingDate='datetime2',
            startingDate='date',
            price='float',
            quantity='numeric'),
        foreignKeys=dict(
            insider_id=f'{schema}Insider',
            company_id=f'{schema}Company',
            tradetype_id=f'{schema}TradeType')
    )
