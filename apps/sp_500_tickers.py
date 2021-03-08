import os
import pathlib
import pickle
from datetime import datetime as dt
from datetime import timedelta as td

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import requests
import talib
# import yahoo_fin.stock_info as yf
import yfinance as yf
from dash.dependencies import Input, Output
import bs4 as bs
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import requests
from pathlib import Path

import id_factory as idf
from app import app

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets/sp500").resolve()  # Change path to datasets

### Retrieving S&P500 List
# # Webscraping Function
# resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
#
# # Define bs object
# soup = bs.BeautifulSoup(resp.text, 'lxml')
#
# # Find table info
# table = soup.find('table', {'class': 'wikitable sortable'})
#
# tickers = []
#
# # Iterate through the rows, and extracts the first table data (column)
# for row in table.findAll('tr')[1:]:
#     ticker = row.findAll('td')[0].text
#
#     # Replace dot(.) with hyphen(-) (different naming convention)
#     ticker = row.findAll('td')[0].text.strip().replace('.', '-')
#
#     # Replace newline character at the end of each webscrape
#     new_ticker = ticker.replace('\n', '')
#
#     tickers.append(new_ticker)
#
# # Dump pickle file
# with open(str(DATA_PATH)+'/sp500_companies', 'wb') as f:
#     pickle.dump(tickers, f)

tickers = pd.read_pickle((str(DATA_PATH) + '/sp500_companies'))

start = dt.now() - td(100)
end = dt.now()

print(len(tickers))
count = 0

for ticker in tickers:
    # df = yf.get_data(ticker, start_date=start, end_date=end, interval="1d")
    df = yf.download(ticker, start=start, end=end)
    df.to_csv(str(DATA_PATH) + '/stocks_dfs/{}.csv'.format(ticker))
    count += 1
    print(count)
print("Done")
