import pathlib
from datetime import datetime as dt
from datetime import timedelta as td

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import requests
import talib
import yfinance as yf
from dash.dependencies import Input, Output

import id_factory as idf
from app import app

# ----------------------------------------------------- Setup ----------------------------------------------------- #

# Initialising id factory
id_start = idf.init_id('technical_analysis_candlestick_company_screener')

# Retrieve path
PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("../datasets").resolve()  # Change path to datasets

# Importing candlestick pattern dataset
candlestick_patterns = str(DATA_PATH) + '/candlestick_patterns/candlestick_patterns.csv'
patterns = pd.read_csv(candlestick_patterns, header=None, index_col=0, squeeze=True).to_dict()

# ------------------------------------------------------ Layout ------------------------------------------------------ #

layout = dbc.Container([

    html.Br(),

    # Ticker entry box
    dbc.Row([
        dbc.Col([
            dbc.Row([
                html.Div("Company:", className='text-white')
            ]),
            dbc.Row([
                dbc.Input(id=idf.gen_id(id_start, 'companies'), value='AAPL', type='text', bs_size='md')
            ], style={"width": "90%"})
        ]),

        # Show less dropdown selection
        dbc.Col([
            dbc.Row([
                html.Div("Show less:", className='text-white')
            ]),
            dbc.Row([
                dcc.Dropdown(id=idf.gen_id(id_start, 'show_less'),
                             style={"width": "100%"},
                             className='',
                             options=[
                                 {'label': 'Yes', 'value': 'yes'},
                                 {'label': 'No', 'value': 'no'},
                             ],
                             multi=False,
                             value='yes',
                             clearable=False,
                             placeholder="Select indicators"
                             )
            ])
        ])
    ], justify='center', no_gutters=True),

    html.Br(),

    # Placeholder for datatable
    dbc.Row([
        dbc.Col([
            html.Div(id=idf.gen_id(id_start, 'table'))
        ])
    ]),

    html.Br(),

    # Placeholder for graph
    dbc.Row([
        dbc.Col([
            html.Div(id=idf.gen_id(id_start, 'graph'), children=[])
        ])
    ]),
    html.Br(),
    html.Br(),
    html.Br(),
])


# ---------------------------------------------------- Callbacks ---------------------------------------------------- #

# Callback for updating of candlestick patterns
@app.callback(
    [
        Output(component_id=idf.gen_id(id_start, 'table'), component_property='children'),
        Output(component_id=idf.gen_id(id_start, 'graph'), component_property='children')
    ],
    [
        Input(component_id=idf.gen_id(id_start, 'companies'), component_property='value'),
        Input(component_id=idf.gen_id(id_start, 'show_less'), component_property='value')
    ]
)
def update_patterns(companies, option):
    counter = 0  # Count number of bearish/bullish
    start = dt.now() - td(365 * 2)  # start date
    end = dt.now()  # end date

    table = pd.DataFrame(columns=['Symbol', 'Company', 'Pattern', 'Signal'])  # Create empty dataframe

    graphs = []  # Create list of graphs

    df = yf.download(companies, start=start, end=end)  # Download stock data

    # Gets all tickers from yahoo finance
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(companies)
    result = requests.get(url).json()

    # Checks if ticker entered exists, breaks once found (get Name)
    for x in result['ResultSet']['Result']:
        if x['symbol'] == companies.upper():
            name = x['name']
            graphs.append(html.Img(src=("https://finviz.com/chart.ashx?t={}&ty=c&ta=1&p=d&s=l".format(companies)),
                                   style={'width': '100%'}))

        break

    # For all patterns, run through each
    for pattern in patterns:

        pattern_function = getattr(talib, pattern)  # Call candlestick identifier function
        try:  # Try to run candlestick pattern test

            # Retrieve result from function
            result = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])

            # Get the current result (last available trading day)
            last = result.tail().values[0]

            # Append pattern type
            if last == 100:
                signal = 'Bullish'
            elif last == 200:
                signal = 'Bullish with confirmation'
            elif last == -100:
                signal = 'Bearish'
            elif last == -200:
                signal = 'Bearish with confirmation'
            else:
                signal = 'Neutral'

            # If show all, append regardless
            if option == 'no':
                table = table.append(
                    {'Symbol': companies, 'Company': name, 'Pattern': patterns[pattern], 'Signal': signal},
                    ignore_index=True)

            # If show less, append only if pattern is not neutral
            elif option == 'yes':
                if last != 0:
                    counter += 1
                    table = table.append(
                        {'Symbol': companies, 'Company': name, 'Pattern': patterns[pattern], 'Signal': signal},
                        ignore_index=True)

        except:

            # Error checking
            pass

    # Create a datatable from the dataframe
    signal_table = dash_table.DataTable(
        id="table",
        columns=[
            {"name": i, "id": i} for i in table.columns
        ],
        data=table.to_dict('records'),
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'fontWeight': 'bold',
        },

        style_table={'overflowX': 'scroll'},

        style_cell={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white',
            'padding': '10px',
            'textAlign': 'left',
        },
        style_as_list_view=True,
    )

    # If no such company
    if len(companies) == 0:
        return ['', '']

    # If no patterns but company exist
    elif counter == 0 and option == 'yes':
        return ['', graphs]

    # Else, return the table and graph
    else:
        return [signal_table, graphs]
