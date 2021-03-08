import datetime
import json
import sqlite3

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from unidecode import unidecode
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import twitter_credentials
from app import app

analyser = SentimentIntensityAnalyzer()

conn = sqlite3.connect('twitter.db')
c = conn.cursor()


def create_table():
    try:
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL)")
        c.execute("CREATE INDEX fast_unix ON sentiment(unix)")
        c.execute("CREATE INDEX fast_tweet ON sentiment(tweet)")
        c.execute("CREATE INDEX fast_sentiment ON sentiment(sentiment)")
        conn.commit()
    except Exception as e:
        print(str(e))


class TwitterStreamer():

    def stream_tweets(self, hash_tag_list):
        # Handles twitter authentication and the connection to the Twitter Streaming API

        try:
            listener = StdOutListener()

            auth = OAuthHandler(twitter_credentials.API_Key, twitter_credentials.API_Secret_Key)
            auth.set_access_token(twitter_credentials.Access_Token, twitter_credentials.Access_Token_Secret)

            stream = Stream(auth, listener)

            stream.filter(track=hash_tag_list)
        except Exception as e:
            print(str(e))


class StdOutListener(StreamListener):

    def on_data(self, raw_data):
        try:
            data = json.loads(raw_data)
            tweet = unidecode(data['text'])
            time_ms = data['timestamp_ms']
            time_datetime = datetime.datetime.fromtimestamp(int(data['timestamp_ms'])/1000.0)
            time_datetime = str(time_datetime)[:10]
            vs = analyser.polarity_scores(tweet)
            sentiment = vs['compound']
            print(time_datetime, tweet, sentiment)

            return tweet

            # c.execute("INSERT INTO sentiment(unix, tweet, sentiment) VALUES (?, ?, ?)",
            #           (time_datetime, tweet, sentiment))
            #
            # conn.commit()
            # time.sleep(1)

        except KeyError as e:
            print(str(e))

        return True

    def on_error(self, status_code):
        print(status_code)


layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div(id='text'),
            dcc.Interval(id='update',
                         interval=1*1000)
        ])
    ])
])


@app.callback(
    Output('text', 'children'),
    [Input('update', 'n_intervals')]
)
def update_text(input_data):

    # # Run this to populate the table
    create_table()

    # hash_tags = ['stockmarket', 'investing']
    hash_tags = ['stockmarket', 'investing', 'stocks', 'trading', 'money']

    twitter_streamer = TwitterStreamer()

    while True:
        return twitter_streamer.stream_tweets(hash_tags)


tweets = api.user