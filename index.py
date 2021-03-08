import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app, server

# Connect to app pages (in apps)
from apps import homepage
from apps import portfolio_optimisation
from apps.technical_analysis_patterns import technical_analysis_candlestick, technical_analysis_indicators
from apps.sentiment_analysis import sentiment_analysis_twitter, analysis_reddit
from apps.predictions.time_series import time_series_forecasting

from assets.styles import CONTENT_STYLE
from sidebar import sidebar

## ---------- Creating layout using dash and bootstrap ---------- ##
app.layout = dbc.Container([
    html.Div([
        dcc.Location(id='url', refresh=False),

        sidebar,

        # Store page layout here
        html.Div(id='page-content', children=[])
    ], style=CONTENT_STYLE)
])


## ---------- Callback section: connecting components ---------- ##

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/homepage':
        return homepage.layout
    if pathname == '/apps/portfolio_optimisation':
        return portfolio_optimisation.layout
    if pathname == '/apps/technical_analysis_patterns/technical_analysis_candlesticks':
        return technical_analysis_candlestick.layout
    if pathname == '/apps/technical_analysis_patterns/technical_analysis_indicators':
        return technical_analysis_indicators.layout
    if pathname == '/apps/sentiment_analysis/analysis_reddit':
        return analysis_reddit.layout
    if pathname == '/apps/sentiment_analysis/sentiment_analysis_twitter':
        return sentiment_analysis_twitter.layout
    if pathname == '/apps/predictions/time_series/time_series_forecasting':
        return time_series_forecasting.layout
    else:
        return technical_analysis_indicators.layout  # Main page


if __name__ == '__main__':
    app.run_server(debug=False, port=3000)
