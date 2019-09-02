"""main interface"""
import sys
import os
sys.path.append(os.path.join('..'))  # link to datsup
from datsup import log
from datsup import psqladapter as psql
from datsup import settings

import setupDatabase as setupDb
import updateTickers
import cli
import dataManipulation as manip
import dateRange
import oldestUpdate
from exceptions import InvalidModeError


def main():

    args = cli.getArgs()
    logger = log.LogManager('insiderScraper.log')

    # setup database connection
    config = settings.readConfig('settings.ini')
    db = psql.DatabaseManager(
        config['auth']['host'],
        config['auth']['database'],
        config['auth']['user'],
        config['auth']['password'])

    # mode selection
    if args.create_tables and args.confirm_reset:  # -c --confirm-reset
        setupDb.run(db)
    else:
        if args.update_tickers:  # -u
            tickerList = args.update_tickers
        elif args.auto_update:  # -a
            tickerList = manip.processTickerCSV(
                os.path.join('data', 'tickers082219.csv'))
            tickerList = manip.filterTickersFromCSV(
                tickerList, os.path.join('data', 'elimTickers.csv'))
            if args.filter_db:  # [-f]
                tickerList = manip.filterTickersFromDb(tickerList, db)
        elif args.date_range:  # -d
            tickerList = dateRange.getTickers(args.date_range)
        elif args.oldest_updates:  # -o
            tickerList = oldestUpdate.getTickers(db, args.oldest_updates[0])
        else:
            raise InvalidModeError('Invalid mode')

        try:
            updateTickers.run(db, logger, tickerList)
        except Exception:
            db.close()
            raise
    db.close()


if __name__ == '__main__':
    main()
