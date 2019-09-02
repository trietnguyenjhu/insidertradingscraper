import sys
sys.path.append('../')
sys.path.append('insiderScraper/')

from insiderScraper.dataManipulation import processTickerCSV
from datsup import log
from datsup import fileio
from insiderScraper.exceptions import NoDataException


def test_processTickersCSV():
    data = processTickerCSV('data/tickers082219.csv')
    assert len(data) != 0
    assert data[0] == 'DDD'


def test_logger():
    logFilePath = 'etc/insiderScraper.log'
    logger = log.LogManager(logFilePath)
    pretestLines = fileio.countLines(logFilePath)
    try:
        raise NoDataException('Unable to download MSFT')
    except NoDataException as error:
        logger.logError(error)

    postTestLines = fileio.countLines(logFilePath)

    assert postTestLines == pretestLines + 1

    fileio.deleteLastLine(logFilePath)
