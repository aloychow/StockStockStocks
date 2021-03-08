import dash_html_components as html
import dash_bootstrap_components as dbc

from assets.styles import SIDEBAR_STYLE

sidebar = html.Div(
    [
        html.H5("STOCKSTOCKSTOCKS", className="text-center text-white"),
        html.Hr(style={
            'background-color': 'white'
        }),
        # html.P(
        #     "Table of Contents", className="lead"
        # ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/apps/homepage"),
                
                dbc.NavLink("Portfolio Optimisation", href="/apps/portfolio_optimisation"),
                
                dbc.DropdownMenu([
                    dbc.NavLink("Candlestick Patterns",
                                href="/apps/technical_analysis_patterns/technical_analysis_candlesticks",
                                active="exact"),
                    dbc.NavLink("Statistical Indicators",
                                href="/apps/technical_analysis_patterns/technical_analysis_indicators",
                                active="exact")],
                    label="Technical Indicators",
                    nav=True,
                ),

                dbc.DropdownMenu([
                    dbc.NavLink("Reddit", href="/apps/sentiment_analysis/analysis_reddit"),
                    dbc.NavLink("Twitter", href="/apps/sentiment_analysis/sentiment_analysis_twitter"),
                ],
                    label="Sentiment Analysis",
                    nav=True,
                ),

                dbc.DropdownMenu([
                    dbc.NavLink("Time Series Forecasting", href="/apps/predictions/time_series/time_series_forecasting"),
                    # dbc.NavLink("ARIMA", href="/apps/sentiment_analysis/sentiment_analysis_twitter"),
                ],
                    label="Machine Learning",
                    nav=True,
                )
            ],
            vertical=True,
            # pills=True,
            # style="#44484A"
        ),
    ],
    style=SIDEBAR_STYLE,
)
