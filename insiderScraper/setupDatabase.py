def run(database):
    """Drop all tables and recreate"""

    database.createTable(
        table='Trade',
        dataVars=dict(
            filingDate='timestamp',
            startingDate='timestamp',
            price='numeric',
            quantity='numeric'),
        foreignKeys=[
            'insider',
            'tradetype'],
        drop=True,
        verify=True
    )

    database.createTable(
        table='Insider',
        dataVars=dict(
            name='varchar',
            title='varchar',
            sharesOwned='numeric',
            asOfDate='timestamp'),
        foreignKeys=[
            'company'],
        drop=True,
        verify=True
    )

    database.createTable(
        table='Company',
        dataVars=dict(
            name='varchar',
            ticker='varchar',
            cik='numeric',
            lastUpdated='timestamp',
            lastFiling='timestamp'),
        foreignKeys=[
            'industry'],
        drop=True,
        verify=True
    )

    database.createTable(
        table='Industry',
        dataVars=dict(
            name='varchar',
            sector='varchar',
            subSector='varchar'),
        foreignKeys=[],
        drop=True,
        verify=True
    )

    database.createTable(
        table='TradeType',
        dataVars=dict(
            code='varchar',
            type='varchar'),
        foreignKeys=[],
        drop=True,
        verify=True
    )
