from dataclasses import dataclass
import pandas as pd


@dataclass
class Company:
    name: str
    ticker: str
    cik: str
    sector: str
    subSector: str
    industry: str


@dataclass
class Trades:
    table: pd.DataFrame
    company: Company
