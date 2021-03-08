import pathlib
from datetime import datetime as dt
from datetime import timedelta as td

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objects as go
import requests
import yahoo_fin.stock_info as yf
from dash.dependencies import Input, Output
from stockstats import StockDataFrame as Sdf

import id_factory as idf
from app import app

id_start = idf.init_id('technical_analysis_pattern')

# get relative data folder
PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

colors = {"background": "#272B30", "text": "#FFFFFF"}
# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

df_indicator_type_plot = pd.read_csv(DATA_PATH.joinpath("indicator_plot_type.csv"))
df_indicator_type = pd.read_csv(DATA_PATH.joinpath("indicator_type.csv"))
df_indicator_category = pd.read_csv(DATA_PATH.joinpath("indicator_category.csv"))

layout = dbc.Container(
    [
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("Statistical Indicators", className='text-center text-white font-weight-normal p-4')
            ])
        ]),

        # Ticker
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    html.Div("Ticker Symbol:", className='text-white')
                ]),
                dbc.Row([
                    dbc.Input(id='ticker_input', value='AAPL', type='text', bs_size='md')
                ])
            ])
        ]),

        html.Br(),

        # Graph type
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    html.Div("Graph Type:", className='text-white')
                ]),
                dbc.Row([
                    dcc.Dropdown(id='graph_type',
                                 style={"width": "100%"},
                                 className='',
                                 options=[
                                     {'label': 'Line Graph', 'value': 'line'},
                                     {'label': 'Area Graph', 'value': 'area'},
                                     {'label': 'Candlestick Graph', 'value': 'candle'},
                                     {'label': 'Bar Graph', 'value': 'ohlc'}
                                 ],
                                 multi=False,
                                 value='line',
                                 clearable=False,
                                 placeholder="Select graph type"
                                 )
                ], style={"width": "90%"})
            ]),

            # Indicators
            dbc.Col([
                dbc.Row([
                    html.Div("Indicators:", className='text-white')
                ]),
                dbc.Row([
                    dcc.Dropdown(id='indicators',
                                 style={"width": "100%"},
                                 className='',
                                 options=[
                                     {'label': 'Moving Average', 'value': 'ma'},
                                     {'label': 'Bollinger Bands', 'value': 'bb'},
                                     {'label': 'RSI', 'value': 'rsi'},
                                     {'label': 'MACD', 'value': 'macd'}
                                 ],
                                 multi=True,
                                 value='line',
                                 clearable=False,
                                 placeholder="Select indicators"
                                 )
                ])
            ])
        ], justify='center', no_gutters=True),

        html.Br(),
        html.Br(),

        # Moving Averages
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    html.Div(id='ma_header')
                ])
            ])
        ], no_gutters=True),

        dbc.Row([

            dbc.Col([
                dbc.Row([
                    html.Div(id='ma_moving_average_type_header'),
                ]),
                dbc.Row([
                    html.Div(id='ma_moving_average_type')
                ])
            ], width=3),

            dbc.Col([
                dbc.Row([
                    html.Div(id='ma_moving_average_header_1'),
                ]),
                dbc.Row([
                    html.Div(id='ma_moving_average_1')
                ])
            ], width=2),

            dbc.Col([
                dbc.Row([
                    html.Div(id='ma_moving_average_header_2'),
                ]),

                dbc.Row([
                    html.Div(id='ma_moving_average_2')
                ]),
            ], width=2),

            dbc.Col([
                dbc.Row([
                    html.Div(id='ma_moving_average_header_3'),
                ]),

                dbc.Row([
                    html.Div(id='ma_moving_average_3')
                ]),
            ], width=2),
        ], justify='left', no_gutters=True),

        html.Br(),

        # Bollinger Bands
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    html.Div(id='bb_header')
                ])
            ])
        ], no_gutters=True),

        dbc.Row([
            dbc.Col([
                dbc.Row([
                    html.Div(id='bb_moving_average_header'),
                ]),
                dbc.Row([
                    html.Div(id='bb_moving_average')
                ])
            ], width=3),

            dbc.Col([
                dbc.Row([
                    html.Div(id='bb_standard_deviation_header'),
                ]),

                dbc.Row([
                    html.Div(id='bb_standard_deviation')
                ]),
            ], width=4),
        ], justify='left', no_gutters=True),

        html.Br(),
        html.Br(),
        html.Br(),

        # Ticker name
        dbc.Row([
            dbc.Col([
                html.Div(id='ticker_name')
            ], width=12),
        ]),

        # Graph
        dbc.Row([
            dbc.Col([
                html.Div(id='ticker_graph_output')
            ], style={'display': 'inline-block', 'width': '100%'})
        ]),

        # Writeup

        dbc.Row([
            html.Div('Technical Indicators are mathematics calculations done on the stocks past patterns, '
                     'such as price, volume. These indicators can be categorised accordingly, to provide technical '
                     'information to identify trends and make predictions in terms of stock price movements.',
                     className='text-center text-white font-weight-normal p-4')
        ]),

        html.Br(),

        dbc.Row([
            dbc.Col([
                dash_table.DataTable(
                    id="indicator_type_plot",
                    columns=[
                        {"name": i, "id": i} for i in df_indicator_type_plot.columns
                    ],
                    data=df_indicator_type_plot.to_dict('records'),
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

        dbc.Row([
            dbc.Col([
                dash_table.DataTable(
                    id="indicator_type",
                    columns=[
                        {"name": i, "id": i} for i in df_indicator_type.columns
                    ],
                    data=df_indicator_type.to_dict('records'),
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
                        {'if': {'column_id': 'Indicator Type'},
                         'width': '20%'},
                        {'if': {'column_id': 'Significance'},
                         'width': '80%'},
                    ],

                    style_as_list_view=True,
                )
            ]),

        ]),

        html.Br(),

        dbc.Row([
            dbc.Col([
                dash_table.DataTable(
                    id="indicator_category",
                    columns=[
                        {"name": i, "id": i} for i in df_indicator_category.columns
                    ],
                    data=df_indicator_category.to_dict('records'),
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
                        {'if': {'column_id': 'Category'},
                         'width': '20%'},
                        {'if': {'column_id': 'Significance'},
                         'width': '80%'},
                    ],

                    style_as_list_view=True,
                )
            ]),
        ]),

        html.Br(),
        html.Br(),
        html.Br(),

    ],

    style={'backgroundColor': colors["background"]}
)


# Callbacks

# Moving Averages
@app.callback(
    [
        Output(component_id='ma_header', component_property='children'),
        Output(component_id='ma_moving_average_type_header', component_property='children'),
        Output(component_id='ma_moving_average_header_1', component_property='children'),
        Output(component_id='ma_moving_average_header_2', component_property='children'),
        Output(component_id='ma_moving_average_header_3', component_property='children'),
        Output(component_id='ma_moving_average_type', component_property='children'),
        Output(component_id='ma_moving_average_1', component_property='children'),
        Output(component_id='ma_moving_average_2', component_property='children'),
        Output(component_id='ma_moving_average_3', component_property='children')
    ],
    [
        Input(component_id='indicators', component_property='value')
    ]
)
def update_ma(indicator):
    if 'ma' in indicator:

        header = html.Div("Moving Averages", className='text-white font-weight-bold')
        header_ma = html.Div("Type:", className='text-white mr-3 pt-1')
        header_ma_1 = html.Div("Period 1:", className='text-white mr-3 pt-1')
        header_ma_2 = html.Div("Period 2:", className='text-white mr-3 pt-1')
        header_ma_3 = html.Div("Period 3:", className='text-white mr-3 pt-1')

        input_ma_type = dcc.Dropdown(id="ma_type",
                                     style={"width": 150},
                                     className='',
                                     options=[
                                         {'label': 'Simple', 'value': 'sma'},
                                         {'label': 'Exponential', 'value': 'ema'},
                                     ],
                                     multi=False,
                                     value='sma',
                                     clearable=False,
                                     )

        input_ma_1 = dbc.Input(
            id="ma_input_1", type="number", value=15,
            min=1, max=200, step=1,
            bs_size="sm",
            # size=20,
            style={'width': 80}
        )

        input_ma_2 = dbc.Input(
            id="ma_input_2", type="number", value=50,
            min=1, max=200, step=1,
            bs_size="sm",
            # size=20,
            style={'width': 80}
        )

        input_ma_3 = dbc.Input(
            id="ma_input_3", type="number", value=100,
            min=1, max=200, step=1,
            bs_size="sm",
            # size=20,
            style={'width': 80}
        )

        return [header, header_ma, header_ma_1, header_ma_2, header_ma_3, input_ma_type, input_ma_1, input_ma_2,
                input_ma_3]
    else:

        input_ma_type = html.Div(id="ma_type")
        input_ma_1 = html.Div(id="ma_input_1")
        input_ma_2 = html.Div(id="ma_input_2")
        input_ma_3 = html.Div(id="ma_input_3")

        return ["", "", "", "", "", input_ma_type, input_ma_1, input_ma_2, input_ma_3]


# Bollinger Bands
@app.callback(
    [
        Output(component_id='bb_header', component_property='children'),
        Output(component_id='bb_moving_average_header', component_property='children'),
        Output(component_id='bb_standard_deviation_header', component_property='children'),
        Output(component_id='bb_moving_average', component_property='children'),
        Output(component_id='bb_standard_deviation', component_property='children')
    ],
    [
        Input(component_id='indicators', component_property='value')
    ]
)
def update_bb(indicator):
    if 'bb' in indicator:

        header = html.Div("Bollinger Bands", className='text-white font-weight-bold')
        header_ma = html.Div("Moving Average:", className='text-white mr-3 pt-1')
        header_sd = html.Div("Standard Deviation:", className='text-white mr-3 pt-1')

        input_ma = dbc.Input(
            id="ma_input", type="number", value=20,
            min=1, max=200, step=1,
            bs_size="sm",
            # size=20,
            style={'width': 80}
        )

        input_sd = dbc.Input(
            id="sd_input", type="number", value=2,
            min=1, max=200, step=1,
            bs_size="sm",
            # size=20,
            style={'width': 80}
        )

        return [header, header_ma, header_sd, input_ma, input_sd]
    else:

        input_ma = html.Div(id="ma_input")
        input_sd = html.Div(id="sd_input")

        return ["", "", "", input_ma, input_sd]


@app.callback(
    [
        Output(component_id='ticker_name', component_property='children'),
        Output(component_id='ticker_graph_output', component_property='children')
    ],
    [
        Input(component_id='ticker_input', component_property='value'),
        Input(component_id='graph_type', component_property='value'),
        Input(component_id='indicators', component_property='value'),

        # Moving Averages Input
        Input(component_id='ma_type', component_property='value'),
        Input(component_id='ma_input_1', component_property='value'),
        Input(component_id='ma_input_2', component_property='value'),
        Input(component_id='ma_input_3', component_property='value'),

        # Bollinger Bands Input
        Input(component_id='ma_input', component_property='value'),
        Input(component_id='sd_input', component_property='value'),
    ]
)
def update_graph(
        input_data, graph, indicator,

        # Moving Averages
        ma_type, ma_1, ma_2, ma_3,

        # Bollinger bands
        bb_ma, bb_sd
):

    start = dt.now() - td(365 * 2)
    end = dt.now()

    try:
        # Webscraping live data
        df = yf.get_data(input_data, start_date=start, end_date=end, interval="1d")
        # df = web.DataReader(input_data, 'yahoo', start=start, end=end)
        # df.reset_index(inplace=True, drop=False)

        # print(df)

        stock = Sdf(df)

        # Gets all tickers from yahoo finance
        url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(input_data)
        result = requests.get(url).json()

        # Checks if ticker entered exists, breaks once found
        for x in result['ResultSet']['Result']:
            if x['symbol'] == input_data.upper():
                name = x['name']
            break

        graphs = []  # Define list of graphs to be plotted
        # graphs = make_subplots(specs=[[{"secondary_y": True}]])

        # Plot base Graphs
        # Line graph
        if graph == 'line':

            # graphs.add_trace(
            #     go.Scatter(
            #         x=list(df.index),
            #         y=list(df.close),
            #         name="Line"
            #     )
            # )

            graphs.append(go.Scatter(
                x=list(df.index),
                y=list(df.close),
                name="Line"
            ))

        # Area graph
        elif graph == 'area':

            graphs.append(go.Scatter(
                x=list(df.index),
                y=list(df.close),
                fill="tozeroy",
                name="Area"
            ))

        # Candlestick graph
        elif graph == 'candle':

            graphs.append(go.Candlestick(
                x=df.index,
                open=df.open,
                high=df.high,
                low=df.low,
                close=df.close,
                name="Candlestick"
            ))

        # Bar graph
        elif graph == 'ohlc':

            graphs.append(go.Ohlc(
                x=df.index,
                open=df.open,
                high=df.high,
                low=df.low,
                close=df.close,
                name="Bar"
            ))

        # Checks for simple moving average indicator selection (SMA)
        if 'ma' in indicator:
            if ma_type == 'sma':

                list_ma_1 = stock['close_' + str(ma_1) + '_sma']
                list_ma_2 = stock['close_' + str(ma_2) + '_sma']
                list_ma_3 = stock['close_' + str(ma_3) + '_sma']

            elif ma_type == 'ema':
                list_ma_1 = stock['close_' + str(ma_1) + '_ema']
                list_ma_2 = stock['close_' + str(ma_2) + '_ema']
                list_ma_3 = stock['close_' + str(ma_3) + '_ema']

            graphs.append(go.Scatter(
                x=list(df.index),
                y=list(list_ma_1),
                name=str(ma_1) + str(ma_type.upper())
            ))

            graphs.append(go.Scatter(
                x=list(df.index),
                y=list(list_ma_2),
                name=str(ma_2) + str(ma_type.upper())
            ))

            graphs.append(go.Scatter(
                x=list(df.index),
                y=list(list_ma_3),
                name=str(ma_3) + str(ma_type.upper())
            ))

        # Checks for bollinger bands
        if 'bb' in indicator:
            Sdf.BOLL_PERIOD = bb_ma
            Sdf.BOLL_STD_TIMES = bb_sd
            stock = Sdf(df)

            bb = stock['boll']
            upper_band = stock['boll_ub']
            lower_band = stock['boll_lb']

            # print(upper_band)

            graphs.append(go.Scatter(
                x=list(df.index),
                y=list(lower_band),
                name='BB Lower Bound' + ' (' + str(bb_sd) + 'SD)'
            ))

            graphs.append(go.Scatter(
                x=list(df.index),
                y=list(upper_band),
                name='BB Upper Bound' + ' (' + str(bb_sd) + 'SD)',
                fill='tonexty',
                fillcolor='rgba(245, 188, 66, 0.2)'
            ))

            graphs.append(go.Scatter(
                x=list(df.index),
                y=list(bb),
                name=str(bb_ma) + 'SMA'
            ))

        # Checks for relative strength index selection (RSI)
        if 'rsi' in indicator:
            rsi_6 = stock['rsi_6']
            rsi_12 = stock['rsi_12']

            graphs.append(go.Scatter(
                x=list(df.index),
                y=list(rsi_6),
                name="RSI 6 Day"
            ))

            graphs.append(go.Scatter(
                x=list(df.index),
                y=list(rsi_12),
                name="RSI 12 Day"
            ))

        # Checks for moving average convergence divergence (MACD)
        if 'macd' in indicator:
            macd = stock['macd']  # MACD
            signal = stock['macds']  # MACD signal line
            hist = stock['macdh']  # MACD histogram

            graphs.append(go.Scatter(
                x=list(df.index),
                y=list(macd),
                name='MACD'
            ))

            graphs.append(go.Scatter(
                x=list(df.index),
                y=list(signal),
                name='Signal'
            ))

            graphs.append(go.Scatter(
                x=list(df.index),
                y=list(hist),
                line=dict(color="royalblue", width=2, dash="dot"),
                name='Histogram'
            ))

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

        # Creates the graph to be returned
        fig = dcc.Graph(id='stock_graph',
                        figure=figure)

        ticker = name.upper() + " (" + input_data.upper() + ")"
        return [html.H5(ticker, className='text-center text-white font-weight-normal'), fig]

    except:
        if input_data == '':
            # Returns no graph if no input
            return ['', '']
        else:
            # Returns invalid ticker if ticker does not exist
            return [html.H5("Please enter a valid ticker/input parameter", style={"testDecoration": "underline"},
                            className='text-center text-white font-weight-lighter'), ""]
