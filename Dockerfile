FROM python:3.7.4-slim-buster

WORKDIR /root/Projects/insiderScraper/
COPY insidertradingscraper/requirements.txt .

# MSSQL ODBC - doesn't inclue bcp and sqlcmd
RUN apt-get update &&\
    apt-get install -y gnupg curl g++
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update &&\
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev
RUN pip install -r requirements.txt

COPY insidertradingscraper /root/Projects/insiderScraper/
COPY datsup /root/Projects/datsup/
COPY dbadapter /root/Projects/dbadapter/

RUN apt-get install -y git
