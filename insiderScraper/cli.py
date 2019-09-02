"""Add CLI options"""
import argparse


def getArgs():
    """Parse CLI args"""
    parser = argparse.ArgumentParser(
        description='Insider trading data collector')

    parser.add_argument(
        '-c',
        '--create-tables',
        action='store_true',
        help='setup database')

    parser.add_argument(
        '--confirm-reset',
        action='store_true',
        help='confirm reset with -c'
    )

    parser.add_argument(
        '-u',
        '--update-tickers',
        nargs='+',
        help='update data - must specify company tickers')

    parser.add_argument(
        '-a',
        '--auto-update',
        action='store_true',
        help='update data automatically based on the tickers csv file'
    )

    parser.add_argument(
        '-f',
        '--filter-db',
        action='store_true',
        help='filter out tickers already in db - use with -a'
    )

    parser.add_argument(
        '-d',
        '--date-range',
        nargs='+',
        help='update data based on companies filings within a date range'
    )

    parser.add_argument(
        '-o',
        '--oldest-updates',
        nargs='+',
        help='update data based on the oldest updated companies'
    )

    args = parser.parse_args()
    return args
