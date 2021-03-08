import dash_bootstrap_components as dbc
import dash_html_components as html

import id_factory as idf
from app import app

id_start = idf.init_id('homepage')

layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H2("STOCKSTOCKSTOCKS", className='text-center text-white font-weight-normal p-4')
        ])
    ]),

    dbc.Row([
        html.H5('Stockstockstocks provides a variety of powerful indicators used to aid people in making investment '
                'decisions.',
                className='text-center text-white font-weight-normal p-4'),
    ]),


    dbc.Row([
        dbc.Col([
            dbc.Card(
                [
                    dbc.CardImg(src=app.get_asset_url('fundamental_analysis.png'),
                                style={'height': '70%', 'width': '70%'}, className='center', top=True),
                    dbc.CardBody(
                        [
                            html.H4("Fundamental Analysis", className="text-white"),
                            html.P(
                                "Measures a security's intrinsic value through economic and financial factors.",
                                className="card-text",
                            ),
                            html.Br(),
                            html.Br(),
                            html.Br(),
                            dbc.Button("Read More", color="primary"),
                        ]
                    ),
                ]
            )
        ]),

        dbc.Col([
            dbc.Card(
                [
                    dbc.CardImg(src=app.get_asset_url('technical_analysis.png'),
                                style={'height': '70%', 'width': '70%'}, className='center', top=True),
                    dbc.CardBody(
                        [
                            html.H4("Technical Analysis", className="text-white"),
                            html.P(
                                "Used to predict price movement from analysing historical technical data.",
                            ),
                            html.Div(
                                "• Candlestick Patterns",
                            ),
                            html.Div(
                                "• Statistical Indicators",
                            ),
                            html.Br(),
                            dbc.Button("Read More", color="primary"),
                        ]
                    ),
                ]
            )
        ]),

        dbc.Col([
            dbc.Card(
                [
                    dbc.CardImg(src=app.get_asset_url('sentiment_analysis.png'),
                                style={'height': '70%', 'width': '70%'}, className='center', top=True),
                    dbc.CardBody(
                        [
                            html.H4("Sentiment Analysis", className="text-white"),
                            html.P(
                                "Analyses sentiment trends to infer correlation with stock performance.",
                            ),
                            html.Div(
                                "• User Sentiments",
                            ),
                            html.Div(
                                "• Keyword Sentiments",
                            ),
                            html.Br(),
                            dbc.Button("Read More", color="primary"),
                        ]
                    ),
                ]
            )
        ])
    ]),
])
