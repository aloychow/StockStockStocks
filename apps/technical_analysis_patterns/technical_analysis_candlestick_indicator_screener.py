import glob
import pathlib

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import talib
from dash.dependencies import Input, Output

import id_factory as idf
from app import app

# ----------------------------------------------------- Setup ----------------------------------------------------- #

# Initialising id factory
id_start = idf.init_id('technical_analysis_candlestick_indicator_screener')

# Retrieve path
PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("../datasets").resolve()  # Change path to datasets

# Importing candlestick pattern dataset
candlestick_patterns = str(DATA_PATH) + '/candlestick_patterns/candlestick_patterns.csv'
patterns = pd.read_csv(candlestick_patterns, header=None, index_col=0, squeeze=True).to_dict()

# Read all preexisting dataset paths
datasets = glob.glob(str(DATA_PATH) + "/sp500/stocks_dfs/*.csv")

# Creates an array of company names by reading from path and slicing
company_names = []
length_of_path = len(str(DATA_PATH) + "/sp500/stocks_dfs/")

for dataset in datasets:
    company_names.append(dataset[length_of_path:-4])

# # To get company names from ticker (very slow)
# company_dict = {}
#
# for company in company_names:
#
#     # Gets all tickers from yahoo finance
#     url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(company)
#     result = requests.get(url).json()
#
#     # Checks if ticker entered exists, breaks once found (get Name)
#     for x in result['ResultSet']['Result']:
#         if x['symbol'] == company.upper():
#             name = x['name']
#             company_dict[company] = name
#             print(name)
#             break

# ------------------------------------------------------ Layout ------------------------------------------------------ #

layout = dbc.Container([

    html.Br(),

    # Candlestick dropdown selection
    dbc.Row([
        dbc.Col([
            dbc.Row([
                html.Div("Candlestick Pattern:", className='text-white')
            ]),
            dbc.Row([
                dcc.Dropdown(id=idf.gen_id(id_start, 'pattern'),
                             style={"width": "100%"},
                             className='',
                             options=[{'label': patterns[pattern], 'value': pattern} for pattern in patterns],
                             multi=False,
                             value='CDL2CROWS',
                             clearable=False,
                             placeholder="Select indicators"
                             )
            ], style={"width": "90%"})
        ]),

        # Show less dropdown selection
        dbc.Col([
            dbc.Row([
                html.Div("Show Less:", className='text-white')
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
            ], style={"width": "90%"})
        ])
    ], justify='center', no_gutters=True),

    html.Br(),

    dbc.Spinner([  # Create spinner as data reading is slow

        # Placeholder for datatable
        dbc.Row([
            dbc.Col([
                html.Div(id=idf.gen_id(id_start, 'table'))
            ])
        ]),
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
    ],
    [
        Input(component_id=idf.gen_id(id_start, 'pattern'), component_property='value'),
        Input(component_id=idf.gen_id(id_start, 'show_less'), component_property='value')
    ]
)
def update_patterns(pattern, option):
    counter = 0  # Count number of bearish/bullish
    table = pd.DataFrame(columns=['Symbol', 'Company', 'Pattern', 'Signal'])  # Create empty dataframe to populate

    pattern_function = getattr(talib, pattern)  # Call candlestick identifier function

    for i in range(len(datasets)):
        df = pd.read_csv(datasets[i])  # Read each dataset (company)

        try:  # Try to run candlestick pattern test

            # Retrieve result from function
            result = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])

            # Get company name from list created at beginning
            company = company_names[i]

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
                table = table.append({'Symbol': company,
                                      # 'Company': company_dict[company],
                                      'Company': company,
                                      'Pattern': patterns[pattern],
                                      'Signal': signal}, ignore_index=True)

            # If show less, append only if pattern is not neutral
            elif option == 'yes':
                if last != 0:
                    counter += 1  # Ensures at least one row present
                    table = table.append({'Symbol': company,
                                          # 'Company': company_dict[company],
                                          'Company': company,
                                          'Pattern': patterns[pattern],
                                          'Signal': signal}, ignore_index=True)

        except:

            # Error checking
            print('failed')

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
        page_size=10,
        sort_action="native",
        sort_mode="single",
    )

    # If show less and no values, return no pattern message
    if counter == 0 and option == 'yes':
        return [html.Div('No pattern detected', className='text-center')]
    # Else, return the table
    else:
        return [signal_table]
