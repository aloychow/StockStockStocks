import dash
import pycountry
import plotly

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_table

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import pandas_datareader.data as web

from datetime import datetime, timedelta

import csv

import pathlib
from app import app

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

## ---------- Importing data into csv file format (companies) ---------- ##

# df_companies = pd.read_csv(DATA_PATH.joinpath("companies_sorted.csv"))
# # df_companies = pd.read_csv("datasets/companies_sorted.csv")
# df_companies = df_companies[['name', 'year founded', 'industry', 'current employee estimate', 'size range', 'country']]
#
# df_companies = df_companies.dropna()
#
# df_companies = df_companies[df_companies['size range'] == '10001+']
#
# #Removing countries with non-existent country code (according to wiki)
# my_list = ['czechia', 'south korea', 'taiwan', 'venezuela', 'russia', 'iran', 'vietnam','palestine', 'macau', 'syria', 'tanzania',
#             'sint maarten', 'moldova', 'democratic republic of the congo', 'bolivia', 'libya', 'bolivia', 'british virgin islands',
#             'côte d’ivoire', 'macedonia', 'laos', 'curaçao', 'bolivia', 'Åland islands', 'kosovo', 'caribbean netherlands',
#             'south sudan', 'são tomé and príncipe', 'brunei', 'saint martin', 'micronesia', 'saint helena', 'north korea',
#             'republic of the congo', 'u.s. virgin islands', 'nan', '']
#
# df_companies = df_companies.loc[~df_companies.country.isin(my_list)]
#
# #print(df_companies['country'])
# dic = {}
# country_list = []
#
# with open(DATA_PATH.joinpath("wikipedia-iso-country-codes.csv")) as f:
#     file= csv.DictReader(f, delimiter=',')
#     for line in file:
#         dic[line['English short name lower case'].lower()] = line['Alpha-3 code']
#
# countries = df_companies['country']
#
# for country in countries:
#     try:
#         country_list.append(dic[country])
#     except Exception as e:
#         print(e)
#
# print(len(country_list))
# print(len(df_companies))
# # print(df_companies)
#
# df_companies.insert(5, "iso", country_list, True)
# df_companies = df_companies.round(decimals=0)
#
# df_companies = df_companies[['name', 'year founded', 'industry', 'current employee estimate', 'country','iso']]
#
# df_companies.to_csv(DATA_PATH.joinpath('companies_sorted_short.csv'))

## ---------- Continuation ---------- ##

df_companies = pd.read_csv(DATA_PATH.joinpath("companies_sorted_short.csv"))

# df_companies = pd.read_csv("datasets/companies_sorted_short.csv")
df_companies = df_companies.drop(df_companies.columns[0], axis=1)
df_companies["name"] = df_companies.name.str.upper()
df_companies["industry"] = df_companies.industry.str.title()
df_companies["country"] = df_companies.country.str.title()

# Create list of years with companies founded (to dynamically update dropdown)
year_list = df_companies["year founded"]
year_list = list(dict.fromkeys(year_list))
year_list.sort(reverse=True)
year_list.insert(0, 'All')

# print(df_companies[:15])
# print(year_list)

## ---------- Creating layout using dash and bootstrap ---------- ##

layout = dbc.Container([
    # dbc.Row(dbc.Col(
    #     dbc.Spinner(children=[dcc.Graph(id="loading_map",figure={})],
    #     size="lg", color="primary", type="border", fullscreen=False),
    #     width={'size': 12, 'offset': 0})
    # ),
    dbc.Row([
        dbc.Col(html.H1("Company History", className='text-center text-primary, p-4'),
                width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id="company_year", style={"testDecoration": "underline", "width": "40%"}, className='pt-4',
                         options=[
                             {'label': year, 'value': year} for year in year_list
                         ],
                         multi=False,
                         value=year_list[0],
                         clearable=False,
                         placeholder="Select a year"
                         ),
            dbc.Spinner(children=[dcc.Graph(id="my_company_map",
                                            figure={},
                                            )], size="lg", color="primary", type="border", fullscreen=False)
        ],  # width={'size':5, 'offset':0}
            xs=12, sm=12, md=12, lg=12, xl=12)
    ], no_gutters=False, justify='center', align="center"),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id="company_table",
                columns=[
                    # {"name": i, "id": i}
                    # if i != "iso"
                    # else {"name": i, "id": i, "hidden": True}
                    # for i in df_companies.columns

                    {'name': 'Company', 'id': "name", 'type': 'text', 'editable': False},
                    {'name': 'Year Founded', 'id': "year founded", 'type': 'numeric', 'editable': False},
                    {'name': 'Sector/Industry', 'id': "industry", 'type': 'text', 'editable': False},
                    {'name': 'Current Employees', 'id': "current employee estimate", 'type': 'numeric',
                     'editable': False},
                    {'name': 'Country of Origin', 'id': "country", 'type': 'text', 'editable': False},

                ],
                data=df_companies.to_dict('records'),
                sort_action="native",
                sort_mode="multi",
                page_current=0,
                page_size=10,
                page_action="native",
                style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold', 'border': '1px solid grey'},
                style_table={'overflowX': 'scroll'},

                style_cell={'padding': '10px'},
                style_cell_conditional=[{
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['name', 'industry', 'country', 'iso']
                ],
                style_data_conditional=[{
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }],
                style_as_list_view=True,

                # tooltip_delay=1000,
                # tooltip_header=[{'name': 'Name of company',
                #                 'year founded': 'Year company was established/founded',
                #                 'industry': 'Industry company belongs to',
                #                 'size range': 'Size range of company defined by total staff/number of employees',
                #                 'country': 'Country in which company resides',
                #                 'iso': 'Iso-3 code of country'}],
            )
        ], xs=12, sm=12, md=12, lg=12, xl=12)
    ], no_gutters=False, justify='center'),

    dbc.Row([
        dbc.Col(
            html.H6("The company data has been retrieved up till 2017 from Kaggle datasets, and may not be updated.",
                    className='text-center text-primary, font-weight-lighter, p-4'),
            width=12)
    ])

], fluid=True)


## ---------- Callback section: connecting components ---------- ##

# Company Map
@app.callback(
    [Output('company_table', 'data'),
     Output('my_company_map', 'figure')],
    [Input('company_year', 'value')]
)
def update_graph(year_slctd):
    # container = "Year Selected: {}".format(year_slctd)

    # Filter by year
    dff = df_companies.copy()
    mask = dff['year founded'] == year_slctd

    if len(dff[mask]) != 0:
        # Plotly Express
        fig = px.choropleth(
            data_frame=dff[mask],
            locations="iso",
            color="country",
            hover_name="country",
            projection="natural earth",
            title="Companies Founded by Year",
            color_continuous_scale="Aggrnyl"
        )

        fig.update_layout(title=dict(font=dict(size=28), x=0.5, xanchor='center'),
                          margin=dict(l=60, r=60, t=50, b=50),
                          paper_bgcolor='rgba(0,0,0,0)'
                          )

        # fig = go.Figure(data=go.Choropleth(
        #     locations="iso",
        #     colorscale="Blues",

        # ))

        data = dff[mask].to_dict('records')
        return data, fig

    elif year_slctd == 'All':
        fig = px.choropleth(
            data_frame=dff,
            locations="iso",
            color="country",
            hover_name="country",
            projection="natural earth",
            title="Companies Founded by Year",
            color_continuous_scale="Aggrnyl"
        )

        # print(dff[mask])

        fig.update_layout(title=dict(font=dict(size=28), x=0.5, xanchor='center'),
                          margin=dict(l=60, r=60, t=50, b=50),
                          paper_bgcolor='rgba(0,0,0,0)'
                          )
        data = dff.to_dict('records')

        return data, fig

    else:
        fig = px.choropleth(
            data_frame=dff[mask],
            locations="iso",
            color="country",
            hover_name="country",
            projection="natural earth",
            title="Companies Founded by Year",
            color_continuous_scale="Aggrnyl"
        )

        # print(dff[mask])

        fig.update_layout(title=dict(font=dict(size=28), x=0.5, xanchor='center'),
                          margin=dict(l=60, r=60, t=50, b=50),
                          paper_bgcolor='rgba(0,0,0,0)'
                          )
        data = dff.to_dict('records')
        return dff[mask], fig
