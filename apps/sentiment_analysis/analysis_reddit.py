import pathlib

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import apps.sentiment_analysis.analysis_reddit_buzz as tab1
import apps.sentiment_analysis.analysis_reddit_buzz as tab2
import id_factory as idf
from app import app
from assets.styles import tab_selected_style, tab_style

# ----------------------------------------------------- Setup ----------------------------------------------------- #

# Initialising id factory
id_start = idf.init_id('analysis_reddit')

# get relative data folder
PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("../datasets").resolve()  # Change path to datasets

colors = {"background": "#272B30", "text": "#FFFFFF"}

# ------------------------------------------------------ Layout ------------------------------------------------------ #

layout = dbc.Container([

    # Header
    dbc.Row([
        dbc.Col([
            html.H2("Reddit Analysis",
                    className='text-center text-white font-weight-normal p-4')
        ]),
    ]),

    # Create 2 tabs for the company/candlestick specific search
    dbc.Row([
        dbc.Col([
            dcc.Tabs(id=idf.gen_id(id_start, 'tabs'),
                     value='tab-1',
                     children=[
                         dcc.Tab(label='buzz screener', value='tab-1', style=tab_style,
                                 selected_style=tab_selected_style),
                         dcc.Tab(label='undefined screener', value='tab-2', style=tab_style,
                                 selected_style=tab_selected_style),
                     ],
                     colors={
                         "border": "grey",
                         "background": "272B30"},
                     ),
        ], align='center'),
    ]),

    # Create a placeholder for tabs content
    dbc.Row([
        dbc.Col([
            html.Div(id=idf.gen_id(id_start, 'tabs-content'))
        ], align='center')
    ])

])


# ---------------------------------------------------- Callbacks ---------------------------------------------------- #

# Callback for updating tabs
@app.callback(
    [
        Output(component_id=idf.gen_id(id_start, 'tabs-content'), component_property='children')
    ],
    [
        Input(component_id=idf.gen_id(id_start, 'tabs'), component_property='value')
    ]
)
def render_content(tab):

    # Return tabs accordingly
    if tab == 'tab-1':
        return [
            tab1.layout
        ]
    elif tab == 'tab-2':
        return [
            html.Div([
                tab2.layout
            ])
        ]
