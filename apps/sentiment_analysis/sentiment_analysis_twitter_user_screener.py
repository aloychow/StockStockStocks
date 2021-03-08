import re

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
from textblob import TextBlob
from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

import id_factory as idf
import twitter_credentials
from app import app

# ----------------------------------------------------- Setup ----------------------------------------------------- #

# Initialising id factory
id_start = idf.init_id('sentiment_analysis_twitter_user')

colors = {"background": "#272B30", "text": "#FFFFFF"}


# Twitter Client
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


# Authenticator
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.API_Key, twitter_credentials.API_Secret_Key)
        auth.set_access_token(twitter_credentials.Access_Token, twitter_credentials.Access_Token_Secret)
        return auth


# Twitter Streamer
class TwitterStreamer():

    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hashtag_list):
        # Handles twitter authentication and the connection to the Twitter Streaming API
        listener = TwitterListener()

        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        stream.filter(track=hashtag_list)


# Twitter Stream Listener
class TwitterListener(StreamListener):

    def on_data(self, raw_data):
        try:
            # print(raw_data)
            # with open(filename, 'a') as tf:
            #     tf.write(raw_data)
            return True

        except Exception as e:
            print(str(e))

    def on_error(self, status_code):
        if status_code == 420:
            return False
        print(status_code)


class TweetAnalyser():

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyse_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        return analysis.polarity

    def analyse_subjectivity(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        return analysis.subjectivity

    def tweets_to_data_frame(self, tweets):
        # df = pd.DataFrame({'Date': np.array([str(tweet.created_at)[:10] for tweet in tweets])})
        df = pd.DataFrame({'Date': [tweet.created_at for tweet in tweets]})

        df['Tweet'] = np.array([tweet.text for tweet in tweets])
        df['Id'] = np.array([tweet.id for tweet in tweets])
        df['Length'] = np.array([len(tweet.text) for tweet in tweets])
        df['Source'] = np.array([tweet.source for tweet in tweets])
        df['Likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['Retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        # df['Friends'] = np.array([tweet.friends_count for tweet in tweets])

        return df


# ------------------------------------------------------ Layout ------------------------------------------------------ #

layout = dbc.Container([

    html.Br(),

    # Ticker
    dbc.Row([
        dbc.Col([
            dbc.Row([
                html.Div("Twitter Handle:", className='text-white')
            ]),
            dbc.Row([
                dbc.Input(id=idf.gen_id(id_start, 'twitter_handle_input'), value='JoeBiden', type='text', bs_size='md')
            ])
        ])
    ]),

    html.Br(),

    # Graph type
    dbc.Row([
        dbc.Col([
            dbc.Row([
                html.Div("Interval:", className='text-white')
            ]),
            dbc.Row([
                dcc.Dropdown(id=idf.gen_id(id_start, 'interval_type'),
                             style={"width": "100%"},
                             className='',
                             options=[
                                 {'label': 'Daily', 'value': 'daily'},
                                 {'label': 'Individual', 'value': 'individual'},
                             ],
                             multi=False,
                             value='daily',
                             clearable=False,
                             placeholder="Select interval type"
                             )
            ], style={"width": "90%"})
        ]),

        # Indicators
        dbc.Col([
            dbc.Row([
                html.Div("Number of Tweets:", className='text-white')
            ]),
            dbc.Row([
                dcc.Dropdown(id=idf.gen_id(id_start, 'number_tweets'),
                             style={"width": "100%"},
                             className='',
                             options=[
                                 {'label': '20', 'value': 20},
                                 {'label': '100', 'value': 100},
                                 {'label': '1000', 'value': 1000},
                                 {'label': 'All', 'value': -1},

                             ],
                             multi=False,
                             value=1000,
                             clearable=False,
                             placeholder="Select Number"
                             )
            ])
        ])
    ], justify='center', no_gutters=True),

    html.Br(),

    dbc.Row([
        dbc.Col([
            html.Button(id=idf.gen_id(id_start, 'button_input'), n_clicks=0, children='Show Info')
        ])
    ]),

    html.Br(),

    dbc.Spinner([

        html.Div(id=idf.gen_id(id_start, 'name')),
        html.Div(id=idf.gen_id(id_start, 'description')),
        html.Div(id=idf.gen_id(id_start, 'followers_count')),
        html.Div(id=idf.gen_id(id_start, 'friends_count')),
        html.Div(id=idf.gen_id(id_start, 'location')),

        html.Div(id=idf.gen_id(id_start, 'graph')),

    ]),

    dbc.Spinner([
        html.Div(id=idf.gen_id(id_start, 'sentiment')),

        html.Div(id=idf.gen_id(id_start, 'sentiment_score')),

        html.Div(id=idf.gen_id(id_start, 'subjectivity_score')),

        html.Br(),

        html.Div(id=idf.gen_id(id_start, 'table')),

    ]),

])


# ---------------------------------------------------- Callbacks ---------------------------------------------------- #

@app.callback(
    [
        Output(component_id=idf.gen_id(id_start, 'name'), component_property='children'),
        Output(component_id=idf.gen_id(id_start, 'description'), component_property='children'),
        Output(component_id=idf.gen_id(id_start, 'followers_count'), component_property='children'),
        Output(component_id=idf.gen_id(id_start, 'friends_count'), component_property='children'),
        Output(component_id=idf.gen_id(id_start, 'location'), component_property='children'),

        Output(component_id=idf.gen_id(id_start, 'graph'), component_property='children'),
        Output(component_id=idf.gen_id(id_start, 'sentiment'), component_property='children'),
        Output(component_id=idf.gen_id(id_start, 'sentiment_score'), component_property='children'),
        Output(component_id=idf.gen_id(id_start, 'subjectivity_score'), component_property='children'),
        Output(component_id=idf.gen_id(id_start, 'table'), component_property='children')
    ],
    [
        Input(component_id=idf.gen_id(id_start, 'button_input'), component_property='n_clicks')
    ],
    [
        State(component_id=idf.gen_id(id_start, 'twitter_handle_input'), component_property='value'),
        State(component_id=idf.gen_id(id_start, 'number_tweets'), component_property='value'),
        State(component_id=idf.gen_id(id_start, 'interval_type'), component_property='value'),
    ]
)
def update_info(n, handle, number, interval):
    twitter_client = TwitterClient()
    tweet_analyser = TweetAnalyser()
    api = twitter_client.get_twitter_client_api()

    if number == 20:
        no_of_pages = 1
    elif number == 100:
        no_of_pages = 1
    elif number == 1000:
        no_of_pages = 5
    else:
        no_of_pages = 100

    if int(number) <= 200:
        count = int(number)
    else:
        count = 200

    df = pd.DataFrame()

    try:
        name = 'Name: ' + str(api.get_user(handle).name)
        description = 'Bio: ' + str(api.get_user(handle).description)
        followers_count = 'Followers: ' + str(api.get_user(handle).followers_count)
        friends_count = 'Following: ' + str(api.get_user(handle).friends_count)
        location = 'Location: ' + str(api.get_user(handle).location)

        for pages in Cursor(api.user_timeline, screen_name=handle, count=count).pages():
            df = df.append(tweet_analyser.tweets_to_data_frame(pages))

            no_of_pages -= 1

            if no_of_pages <= 0:
                break

        df['Sentiment'] = np.array([tweet_analyser.analyse_sentiment(tweet) for tweet in df['Tweet']])
        df['Subjectivity'] = np.array([tweet_analyser.analyse_subjectivity(tweet) for tweet in df['Tweet']])

    except Exception as e:
        return [html.Div('No such Twitter handle exists', className='text-center'),
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '']


    if interval == 'daily':

        df['Date'] = pd.to_datetime(df['Date']).dt.date

        final_df = df.groupby(['Date'], as_index=False).agg(
            {'Likes': 'sum', 'Length': 'mean', 'Sentiment': 'mean', 'Subjectivity': 'mean'})

        # print(final_df)

        # Uncomment to get count
        # count = df.groupby(['Date'], as_index=False).size().reset_index(name='Count')
        # final_df['Count'] = count['Count']

        # print(final_df)

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces

        fig.add_trace(
            go.Scatter(x=final_df['Date'],
                       y=final_df['Sentiment'],
                       name="Polarity"),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=final_df['Date'],
                       y=final_df['Subjectivity'],
                       name="Subjectivity",
                       ),
            secondary_y=True,
        )

        # Set x-axis title
        # fig.update_xaxes(title_text="Time")

        # Set y-axes titles
        fig.update_yaxes(title_text="Polarity", secondary_y=False)
        fig.update_yaxes(title_text="Subjectivity", secondary_y=True)

    elif interval == 'individual':

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces

        fig.add_trace(
            go.Scatter(x=df['Date'],
                       y=df['Sentiment'],
                       name="Polarity"),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=df['Date'],
                       y=df['Subjectivity'],
                       name="Subjectivity",
                       ),
            secondary_y=True,
        )

        # Set x-axis title
        # fig.update_xaxes(title_text="Time")

        # Set y-axes titles
        fig.update_yaxes(title_text="Polarity", secondary_y=False)
        fig.update_yaxes(title_text="Subjectivity", secondary_y=True)

    fig.update_layout(
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
    fig.update_xaxes(
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

    # Get ratio of tweet sentiments
    sentiment_score = []
    for i in df['Sentiment']:
        if i < 0:
            sentiment_score.append('Negative')
        elif i > 0:
            sentiment_score.append('Positive')
        else:
            sentiment_score.append('Neutral')

    df['Score'] = sentiment_score

    sentiment_df = df.groupby(['Score'], as_index=False).agg({'Sentiment': 'mean'})
    count = df.groupby(['Score'], as_index=False).size().reset_index(name='Count')
    sentiment_df['Count'] = count['Count']
    sentiment_fig = go.Figure(data=[
        go.Pie(
            labels=sentiment_df['Score'],
            values=sentiment_df['Count'],
            hole=.3
        )
    ])

    sentiment_fig.update_layout(
        title={
            'text': 'Sentiment Analysis',
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

    # Get Histogram of tweet sentiment scores
    sentiment_hist = px.histogram(df, x="Sentiment")

    sentiment_hist.update_layout(
        title={
            'text': 'Polarity Histogram',
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

    # Get Histogram of tweet subjectivity scores
    subjectivity_hist = px.histogram(df, x="Subjectivity")

    subjectivity_hist.update_layout(
        title={
            'text': 'Subjectivity Histogram',
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

    # # Get favourite posting platform
    # source_df = df.groupby(['Source'], as_index=False).agg({'Sentiment': 'mean'})
    # count = df.groupby(['Source'], as_index=False).size().reset_index(name='Count')
    # source_df['Count'] = count['Count']
    # source_fig = go.Figure(data=[
    #     go.Pie(
    #         labels=source_df['Source'],
    #         values=source_df['Count'],
    #         hole=.3
    #     )
    # ])
    #
    # source_fig.update_layout(
    #     title={
    #         'text': 'Favourite Platforms',
    #         'y': 0.9,
    #         'x': 0.5,
    #         'xanchor': 'center',
    #         'yanchor': 'top'
    #     },
    #     # width=800,
    #     plot_bgcolor=colors["background"],
    #     paper_bgcolor=colors["background"],
    #     font={'color': colors["text"]}
    # )

    # Create a datatable from the dataframe
    tweets_table = dash_table.DataTable(
        id="table",
        columns=[
            {"name": i, "id": i} for i in df.columns
        ],
        data=df.to_dict('records'),
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

    return [
        html.H6(name, className='text-center text-white font-weight-normal')
        ,
        html.H6(description, className='text-center text-white font-weight-normal')
        ,
        html.H6(followers_count, className='text-center text-white font-weight-normal')
        ,
        html.H6(friends_count, className='text-center text-white font-weight-normal')
        ,
        html.H6(location, className='text-center text-white font-weight-normal')
        ,
        dcc.Graph(
            figure=fig
        ),
        dcc.Graph(
            figure=sentiment_fig
        ),
        dcc.Graph(
            figure=sentiment_hist
        ),
        dcc.Graph(
            figure=subjectivity_hist
        ),
        tweets_table]

