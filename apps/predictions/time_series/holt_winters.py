import pathlib
from datetime import datetime as dt
from datetime import timedelta as td

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import requests
import yfinance as yf
import plotly.graph_objects as go

from statsmodels.tsa.holtwinters import ExponentialSmoothing
import numpy as np

from dash.dependencies import Input, Output, State

import id_factory as idf
from app import app

# ----------------------------------------------------- Setup ----------------------------------------------------- #

# Initialising id factory
id_start = idf.init_id('holt_winters')

# Retrieve path
PATH = pathlib.Path(__file__).parent.parent.parent
DATA_PATH = PATH.joinpath("../datasets").resolve()  # Change path to datasets

colors = {"background": "#272B30", "text": "#FFFFFF"}
# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

df_holt_winters = pd.read_csv(DATA_PATH.joinpath("holt_winters.csv"))

# ------------------------------------------------------ Layout ------------------------------------------------------ #

layout = dbc.Container([

    html.Br(),

    dbc.Row([
        html.H5('The Holt-Winters Exponential Smoothing model for forecasting '
                'models 3 aspects of a time series - the average, trends and seasonality.'
                'There are two methods, namely the additive method that accounts for seasonality '
                'linearly, and the multiplicative methods that accounts for an increasing '
                'seasonal variation over time.',
                className='text-center text-white font-weight-normal p-4'),
    ]),

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

    ], justify='center', no_gutters=True),

    html.Br(),

    # Process
    dbc.Row([
        dbc.Col([
            html.Button(id=idf.gen_id(id_start, 'button_input'), n_clicks=0, children='Show Info')
        ]),
    ]),

    html.Br(),

    # Placeholder for graph
    dbc.Row([
        dbc.Col([
            dbc.Spinner([
                html.Div(id=idf.gen_id(id_start, 'graph'), children=[])
            ])
        ])
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id="indicator_type_plot",
                columns=[
                    {"name": i, "id": i} for i in df_holt_winters.columns
                ],
                data=df_holt_winters.to_dict('records'),
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

                style_cell_conditional=[
                    {'if': {'column_id': 'Plot Type'},
                     'width': '20%'},
                    {'if': {'column_id': 'Behaviour'},
                     'width': '80%'},
                ],

                style_as_list_view=True,
            )
        ]),

    ]),
    html.Br(),
    html.Br(),
    html.Br(),
])


# ---------------------------------------------------- Callbacks ---------------------------------------------------- #

@app.callback(
    [
        Output(component_id=idf.gen_id(id_start, 'graph'), component_property='children'),
    ],
    [
        Input(component_id=idf.gen_id(id_start, 'button_input'), component_property='n_clicks')
    ],
    [
        State(component_id=idf.gen_id(id_start, 'companies'), component_property='value')
    ]
)
def update_info(n, input_data):
    start = dt.now() - td(365 * 5)
    end = dt.now()

    try:
        # Webscraping live data
        df = yf.download(input_data, start=start, end=end)  # Download stock data

        # Gets all tickers from yahoo finance
        url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(input_data)
        result = requests.get(url).json()

        # Checks if ticker entered exists, breaks once found
        name = 'NULL'
        for x in result['ResultSet']['Result']:
            if x['symbol'] == input_data.upper():
                name = x['name']
            break

        # If name is NULL, then return Ticker Not Found Error
        if name == 'NULL':
            return [html.H5("Please enter a valid ticker/input parameter", style={"testDecoration": "underline"},
                            className='text-center text-white font-weight-lighter')]

        N_test = 253  # Specifies the number of trading days in a year

        # Splits the 5 year data set to train and test split
        test = df.iloc[:N_test]['Adj Close']  # Uses the first 1 year to test (currently not in use)
        train = df.iloc[N_test:]  # Use the last 4 years of data to train

        try:
            # Builds the Holt-Winters Machine Learning Model for additive model
            hw = ExponentialSmoothing(train['Adj Close'], trend='add', seasonal='add', seasonal_periods=253)
            res_hw = hw.fit()

            # Builds the Holt-Winters Machine Learning Model for multiplicative model
            hw_2 = ExponentialSmoothing(train['Adj Close'], trend='add', seasonal='mul', seasonal_periods=253)
            res_hw_2 = hw_2.fit()

        except:
            # If insufficient historical data, choose to not train and return
            return [html.H5("Insufficient historical data (5 years)", style={"testDecoration": "underline"},
                            className='text-center text-white font-weight-lighter')]

        # Creates a list of daily dates ranging from today to 1 year into the future
        predict_date = pd.date_range(start=end, periods=365).normalize()

        # Create a dataframe with date and predicted adjusted close forecast 1 year into the future
        df_temp = {'Date': predict_date, 'Adj Close': res_hw.forecast(365)}
        df_prediction = pd.DataFrame(df_temp)
        df_prediction = df_prediction.set_index('Date')

        df_temp_2 = {'Date': predict_date, 'Adj Close': res_hw_2.forecast(365)}
        df_prediction_2 = pd.DataFrame(df_temp_2)
        df_prediction_2 = df_prediction_2.set_index('Date')

        # Concatenates the existing dataset with the forecasted dataset
        frames = [train, df_prediction]
        df_final_additive = pd.concat(frames)

        frames = [train, df_prediction_2]
        df_final_multiplicative = pd.concat(frames)

        # Optional Code to calculate RMSE and MSE
        def rmse(y, t):
            return np.sqrt(np.mean((y - t) ** 2))

        def mae(y, t):
            return np.mean(np.abs(y - t))

        # Additive
        # print("Train RMSE:", rmse(train['Adj Close'], res_hw.fittedvalues))
        # print("Test RMSE:", rmse(test['Adj Close'], res_hw.forecast(N_test).reset_index()))
        #
        # print("Train MAE:", mae(train['Adj Close'], res_hw.fittedvalues))
        # print("Test MAE:", mae(test['Adj Close'], res_hw.forecast(N_test).reset_index()))

        # Multiplicative
        # print("Train RMSE:", rmse(train['Adj Close'], res_hw_2.fittedvalues))
        # print("Test RMSE:", rmse(test['Adj Close'], res_hw.forecast(N_test).reset_index()))
        #
        # print("Train MAE:", mae(train['Adj Close'], res_hw_2.fittedvalues))
        # print("Test MAE:", mae(test['Adj Close'], res_hw.forecast(N_test).reset_index()))

        graphs = []  # Define list of graphs to be plotted

        # Appends the various graphs into a list of go objects
        graphs.append(go.Scatter(
            x=list(df_final_additive.index),
            y=list(df_final_additive['Adj Close']),
            name='Additive'.upper())
        )

        graphs.append(go.Scatter(
            x=list(df_final_multiplicative.index),
            y=list(df_final_multiplicative['Adj Close']),
            name='Multiplicative'.upper())
        )

        graphs.append(go.Scatter(
            x=list(df.index),
            y=list(df['Adj Close']),
            name='Original'.upper())
        )

        # Stores final figure into 'figure'
        figure = go.Figure(
            data=graphs,
            layout={
                "height": 700,
                # "width": 1000,
                "showlegend": True,
                "plot_bgcolor": colors["background"],
                "paper_bgcolor": colors["background"],
                "font": {"color": colors["text"]},
            }
        )

        # Creates time ranges for graph
        figure.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                activecolor="blue",
                bgcolor=colors["background"],
                buttons=list(
                    [
                        dict(count=1, label="1D", step="day", stepmode="backward"),
                        dict(count=5, label="5D", step="day", stepmode="backward"),
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(count=5, label="5Y", step="year", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(label="Max", step="all"),
                    ]
                ),
            ),
        )

        fig = dcc.Graph(id='stock_graph',
                        figure=figure)

        return [fig]

    except:

        if input_data == '':
            # Returns no graph if no input
            return ['']
        else:
            # Returns invalid ticker if ticker does not exist
            return [html.H5("Please enter a valid ticker/input parameter", style={"testDecoration": "underline"},
                            className='text-center text-white font-weight-lighter')]
