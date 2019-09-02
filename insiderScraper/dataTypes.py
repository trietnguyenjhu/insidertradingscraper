from pandas import DataFrame


class Company:
    def __init__(self, name, ticker, cik, sector, subSector, industry):
        self.name = name
        self.ticker = ticker
        self.cik = cik
        self.sector = sector
        self.subSector = subSector
        self.industry = industry


class Insider:
    def __init__(self, name, title, company, sharesOwned):
        self.name = name
        self.title = title
        self.company = company
        self.sharesOwned = sharesOwned


class Trades:
    def __init__(self, table: DataFrame, company: Company):

        self.table = table
        self.company = company
