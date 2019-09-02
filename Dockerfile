from python:3-slim
workdir /insider_rds
run pip3 install --trusted-host pypi.python.org -r requirements.txt

run python insiderScraper/app.py -a -f
