# insidertradingscraper


Download insider trading data to a SQL Server database. 


insidertradingscraper can be automatically setup using docker-compose through [docker-insidertradingscraper](https://github.com/trietnguyenjhu/docker-insidertradingscraper). Alternatively, the apps requires [datsup](https://github.com/trietnguyenjhu/datsup) and [dbadapter](https://github.com/trietnguyenjhu/dbadapter) packages. The dir should be arranged in the following manner


    +-- datsup
    |   +-- ...
    +-- dbadapter
    |   +-- ...
    +-- insidertradingscraper (working dir)
    |   +-- insiderScraper
    |       +-- ...
    |   +-- settings.ini
    |   +-- README.md
    |   +-- ...


The following modes are available through the command line interface (CLI):

    python insiderScraper/app.py --create-tables --confirm-reset
    python insiderScraper/app.py --update-tickers amzn fb msft
    python insiderScraper/app.py --auto-update [--filter-db]
    python insiderScraper/app.py --date-range 080119 082819
    python insiderScraper/app.py --oldest-updates 100


settings.ini should be setup and located in the default working directory (insidertradingscraper) prior to running:

    [auth]
    host: hostName
    database: databaseName 
    user: userName
    password: password

The database structure can be viewed in ERD.txt