# insidertradingscraper


Download insider trading data to a SQL Server database. 


insidertradingscraper requires [datsup](https://github.com/trietnguyenjhu/datsup) and [dbadapter](https://github.com/trietnguyenjhu/dbadapter) packages . The dir should be arranged in the following manner


    +-- datsup
    |   +-- ...
    +-- dbadapter
    |   +-- ...
    +-- insidertradingscraper
    |   +-- src
    |   +-- settings.ini
    |   +-- README.md
    |   +-- ...


To run from the CLI:

    python insiderScraper/app.py --create-tables --confirm-reset
    python insiderScraper/app.py --update-tickers amzn fb msft
    python insiderScraper/app.py --auto-update [--filter-db]
    python insiderScraper/app.py --date-range 080119 082819
    python insiderScraper/app.py --oldest-updates 100


settings.ini should be setup prior to running: 

    [auth]
    host: hostName
    database: databaseName 
    user: userName
    password: password

The database structure can be viewed in ERD.txt