"""main interface"""
import sys
import os

sys.path.append(os.path.join('..'))  # link to support libraries
from datsup import log
from datsup import settings
from dbadapter import adapter

import setupDatabase as setupDb
import updateTickers
import cli
import dataManipulation as manip
import dateRange
import oldestUpdate
from exceptions import InvalidModeError

SQLSERVERFLAG = True
SCHEMA = 'insiderTrading.'


def main():

    args = cli.getArgs()
    logger = log.LogManager('insiderScraper.log')

    # setup database connection
    credentials = settings.readConfig('settings.ini')['auth']

    with adapter.SQLServer(credentials) as database:
        # mode selection
        if args.create_tables and args.confirm_reset:  # -c --confirm-reset
            setupDb.run(database)
        elif args.create_tables:
            raise InvalidModeError(
                'Must set --confirm-reset to reintialize tables')
        else:
            if args.update_tickers:  # -u
                tickerList = args.update_tickers
            elif args.auto_update:  # -a
                tickerList = manip.processTickerCSV(
                    os.path.join('data', 'tickers082219.csv'))
                tickerList = manip.filterTickersFromCSV(
                    tickerList, os.path.join('data', 'elimTickers.csv'))
                if args.filter_db:  # [-f]
                    tickerList = manip.filterTickersFromDb(tickerList, database)
            elif args.date_range:  # -d
                tickerList = dateRange.getTickers(args.date_range)
            elif args.oldest_updates:  # -o
                tickerList = oldestUpdate.getTickers(
                    database, args.oldest_updates[0])
            else:
                raise InvalidModeError('Invalid mode')
            updateTickers.run(database, logger, tickerList)


if __name__ == '__main__':
    main()
