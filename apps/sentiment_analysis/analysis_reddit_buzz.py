import glob
import pathlib

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime as dt
from datetime import timedelta as td
import yahoo_fin.stock_info as yf
from plotly.subplots import make_subplots

from dash.dependencies import Input, Output

import id_factory as idf
from app import app

# ----------------------------------------------------- Setup ----------------------------------------------------- #

# Initialising id factory
id_start = idf.init_id('analysis_reddit_buzz')

# Retrieve path
PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("../datasets").resolve()  # Change path to datasets

# Set colours
colors = {"background": "#272B30", "text": "#FFFFFF"}
# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

# Importing datasets
df_reddit_mentions_sum = pd.read_csv(str(DATA_PATH) + '/reddit/reddit_mentions_sum.csv')
df_reddit_mentions_daily = pd.read_csv(str(DATA_PATH) + '/reddit/reddit_mentions_daily.csv')

# Renaming Columns
df_reddit_mentions_sum = df_reddit_mentions_sum.rename(columns={"num_mentions": "Mentions", "stock_ticker": "Ticker", "stock_name": "Company"})
df_reddit_mentions_daily = df_reddit_mentions_daily.rename(columns={"num_mentions": "Mentions", "stock_ticker": "Ticker", "stock_name": "Company", "dt": "Date"})

# Getting Unique Tickers
ticker_list = df_reddit_mentions_sum['Ticker']

# ------------------------------------------------------ Layout ------------------------------------------------------ #

layout = dbc.Container([

    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Row([
                html.Div("Company Ticker:", className='text-white')
            ]),
            dbc.Row([
                dcc.Dropdown(id=idf.gen_id(id_start, 'company'),
                             style={"width": "100%"},
                             className='',
                             options=[{'label': ticker, 'value': ticker} for ticker in ticker_list],
                             multi=False,
                             value=ticker_list[0],
                             clearable=False,
                             placeholder="Select company"
                             )
            ], style={"width": "20%"})
        ])
    ]),

    html.Br(),

    # Placeholder for Graph
    dbc.Row([
        dbc.Col([
            html.Div(id=idf.gen_id(id_start, 'graph'))
        ])
    ]),

    html.Br(),

    dbc.Row([
        html.H5('These are the most popular tickers mentioned in the last 7 days, in the 4 main stocks subreddit - '
                'WallstreetBets, Stockmarket, Stocks & Investing.',
                className='text-center text-white font-weight-normal p-4'),
    ]),

    # Create a datatable from the dataframe
    dash_table.DataTable(
        id=idf.gen_id(id_start, "df_reddit_mentions_sum"),
        columns=[
            {"name": i, "id": i} for i in df_reddit_mentions_sum.columns
        ],
        data=df_reddit_mentions_sum.to_dict('records'),
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
        page_size=10,
        sort_action="native",
        sort_mode="single",
    ),

    html.Br(),

])


# ---------------------------------------------------- Callbacks ---------------------------------------------------- #

# Callback for updating of graphs
@app.callback(
    [
        Output(component_id=idf.gen_id(id_start, 'graph'), component_property='children'),
    ],
    [
        Input(component_id=idf.gen_id(id_start, 'company'), component_property='value'),
    ]
)
def update_reddit_company(company):

    start = dt.now() - td(5)
    end = dt.now()
    df_stock_prices = yf.get_data(company, start_date=start, end_date=end, interval="1d")

    df_daily = df_reddit_mentions_daily[df_reddit_mentions_daily['Ticker'] == company]

    figure = make_subplots(specs=[[{"secondary_y": True}]])

    figure.add_trace(
        go.Scatter(
            x=list(df_daily['Date']),
            y=list(df_daily['Mentions']),
            name='Post Count'),
        secondary_y=False,
    )

    figure.add_trace(
        go.Scatter(x=list(df_stock_prices.index),
                   y=list(df_stock_prices.close),
                   name="Stock Price",
                   ),
        secondary_y=True,
    )

    figure.update_yaxes(title_text="Post Count", secondary_y=False)
    figure.update_yaxes(title_text="Stock Price", secondary_y=True)

    figure.update_layout(
        title={
            'text': 'Sentiment Trend',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        # width=800,
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font={'color': colors["text"]}
    )

    # Creates time ranges for graph
    figure.update_xaxes(
        rangeslider_visible=True,
    )

    fig = dcc.Graph(id='stock_graph',
                    figure=figure)

    return [fig]
