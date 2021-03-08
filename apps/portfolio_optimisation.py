import dash_bootstrap_components as dbc
import dash_html_components as html

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
from scipy.optimize import linprog

import plotly.graph_objects as go
import plotly.express as px

import numpy as np
from dash.dependencies import Input, Output, State

import id_factory as idf
from app import app

# ----------------------------------------------------- Setup ----------------------------------------------------- #

# Initialising id factory
id_start = idf.init_id('portfolio_optimisation')

colors = {"background": "#272B30", "text": "#FFFFFF"}
# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

# Retrieve path
PATH = pathlib.Path(__file__).parent.parent

# ------------------------------------------------------ Layout ------------------------------------------------------ #

layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H2("Portfolio Optimisation", className='text-center text-white font-weight-normal p-4')
        ]),
    ]),

    dbc.Col([
        dbc.Row([
            html.H5('Learn how to build a portfolio and how diversification affects risk and returns.',
                    className='text-center text-white font-weight-normal p-4'),
        ]),

        dbc.Row([
            html.Div(
                "• Visualise Risk-Return plots of multiple companies",
                className='text-center text-white font-weight-normal'
            ),
        ]),

        dbc.Row([
            html.Div(
                "• Optimise portfolios through min/max return (LP), min variance (QP)",
                className='text-center text-white font-weight-normal'
            ),
        ]),

        dbc.Row([
            html.Div(
                "• Manage risk through the Sharpe Ratio",
                className='text-center text-white font-weight-normal'
            ),
        ]),
    ]),

    html.Br(),

    # Ticker entry box
    dbc.Row([
        dbc.Col([
            dbc.Row([
                html.Div("Companies (separated with a comma ','):", className='text-white')
            ]),
            dbc.Row([
                dbc.Input(id=idf.gen_id(id_start, 'companies'), value='AAPL, TSLA, SBUX, WMT', type='text',
                          bs_size='md')
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
    # Remove any whitespaces
    input_data = input_data.replace(" ", "")

    # Create list by splitting at ','
    companies = input_data.split(",")

    # print(companies)

    # Create list to store company names
    companies_names = [""] * len(companies)
    # print(companies_names)

    # Create list to store index of non-existent companies
    wrong_ticker = []

    # Retrieve company full name
    i = 0
    while i < len(companies):

        try:
            temp = yf.Ticker(companies[i])
            companies_names[i] = temp.info['longName']
            i += 1
        except:
            wrong_ticker.append(companies[i])  # Append to list
            companies.pop(i)  # Remove companies that do not exist
            companies_names.pop(i)  # Remove one index from original name list

    if not companies_names:  # No existing company, return
        print('oof')
        return ['']

    start = dt.now() - td(365)
    end = dt.now()

    # Webscraping live data
    df = yf.download(companies[0], start=start, end=end)  # Download stock data
    # print(df)

    # Create a dataframe with date and predicted adjusted close forecast 1 year into the future
    df = df.filter(['Adj Close'])  # Filter only column with adjusted close
    df.columns = [str(companies[0])]  # Change column name to ticker of first company
    # print(df)

    if len(companies) > 1:
        for i in range(1, len(companies)):

            df_temp = yf.download(companies[i], start=start, end=end)  # Download stock data
            df_temp = df_temp.filter(['Adj Close'])  # Filter column
            df_temp.columns = [str(companies[i])]  # Change name to ticker

            df = df.join(df_temp)  # Join the rows while maintaining index

            # df = df.append({str(companies[i]): df_temp['Adj Close']}, ignore_index=True)

    # print(df)

    # If NA values present, use forward filling
    if df.isna().sum().sum() != 0:
        df = df.fillna(method='ffill', inplace=True)

    # Create empty returns dataframe, index gotten from initial df (less one row)
    returns = pd.DataFrame(index=list(df.index.values)[1:])  # Create returns dataframe, index gotten from initial df

    # Get return values using percentage change
    for company in companies:
        current_returns = df[company].pct_change()
        returns[company] = current_returns.iloc[1:] * 100  # Convert to percentage (x100)

    mean_return = returns.mean()  # Mean
    cov = returns.cov()  # Covariance

    cov_np = cov.to_numpy()  # Convert to numpy array for indexing

    # Predict multi-asset returns
    N = 1000  # Number of generated portfolios
    D = len(mean_return)  # Number of assets
    returns = np.zeros(N)  # Empty arrays to store returns and risks
    risks = np.zeros(N)
    random_weights = []
    for i in range(N):
        rand_range = 1.0
        # Generate random vector w
        w = np.random.random(D) * rand_range - rand_range / 2  # with short-selling
        w[-1] = 1 - w[:-1].sum()  # Ensures that w sums to 1
        np.random.shuffle(w)  # Shuffle to remove bias towards the last value
        random_weights.append(w)
        ret = mean_return.dot(w)  # Calculate return and risk
        risk = np.sqrt(w.dot(cov_np).dot(w))
        returns[i] = ret  # Assign to array
        risks[i] = risk

    # Predict single-asset returns
    single_asset_returns = np.zeros(D)  # Create empty arrays
    single_asset_risks = np.zeros(D)
    for i in range(D):
        ret = mean_return[i]  # Calculate returns and risk
        risk = np.sqrt(cov_np[i, i])

        single_asset_returns[i] = ret  # Assign to array
        single_asset_risks[i] = risk

    # Set A_eq and B_eq for linprog function minimization
    A_eq = np.ones((1, D))
    b_eq = np.ones(1)

    ### NOTE: The bounds are by default (0, None) unless otherwise specified.
    # bounds = None
    # bounds = [(-0.5, None)] * D
    bounds = [(0, None)] * D

    # minimize
    res = linprog(mean_return, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
    min_return = res.fun
    print(res)

    # maximize
    res = linprog(-mean_return, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
    max_return = -res.fun  # Need to negate as we optimized the negative of the return
    print(res)

    print(min_return)
    print(max_return)


    graphs = []  # Define list of graphs to be plotted

    # Appends the various graphs into a list of go objects

    graphs.append(go.Scatter(
        x=list(risks),
        y=list(returns),
        name='Multi-Assets'.upper(),
        mode='markers',
        opacity=0.5
        )
    )

    for i in range(len(companies)):
        graphs.append(go.Scatter(
            x=[single_asset_risks[i]],
            y=[single_asset_returns[i]],
            name=companies_names[i].upper(),
            mode='markers')
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

    figure.update_layout(
        title={
            'text': "Markowitz Bullet",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    figure.update_xaxes(title_text='Risk (%)')
    figure.update_yaxes(title_text='1D Returns (%)')

    fig = dcc.Graph(id='stock_graph',
                    figure=figure)

    return [fig]
