# import psaw
# from psaw import PushshiftAPI
import pathlib

import praw
import pandas as pd

import datetime as dt

# api = PushshiftAPI()
#
# start_time = int(dt.datetime(2021, 1, 30).timestamp())
#
# submissions = list(api.search_submissions(after=start_time,
#                                           subreddit='wallstreetbets',
#                                           filter=['url', 'author', 'title', 'subreddit'],
#                                           limit=10))
# for submission in submissions:
#     print(submission)

# Retrieve path
PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("../datasets").resolve()  # Change path to datasets

reddit = praw.Reddit(client_id='cfsrsyk9xPOBBw',
                     client_secret='8oy7adJQblmB558fD0JTU5qM2qvwLQ',
                     user_agent='subSentiment')

# day_end_epoch = dt.now().timestamp()
# day_start_epoch = day_end_epoch - 60
url = "https://api.pushshift.io/reddit/{}/search?limit=1000&sort=desc&author={}&before="

with open(str(DATA_PATH) + '/reddit/subreddits.txt') as f:
    for line in f:
        subreddit = reddit.subreddit(line.strip())

        posts = []

        for post in subreddit.new(limit=10):
            # print(post.title)
            # print(post.score)

            posts.append([post.title,
                          # post.score,
                          # post.upvote_ratio,
                          # 'https://www.reddit.com' + post.permalink,
                          post.subreddit,
                          post.url,
                          # post.comments,
                          post.author,
                          # post.selftext,
                          dt.datetime.fromtimestamp(post.created)
                          # post.created
                          ])

            df = pd.DataFrame(posts, columns=['title',
                                              # 'score',
                                              # 'upvote_ratio',
                                              # 'permalink',
                                              'subreddit',
                                              'url',
                                              # 'num_comments',
                                              'author',
                                              # 'body',
                                              'created'
                                              ]
                              )
            print('ok')

            words = post.title.split()

            cashtags = list(set(filter(lambda word: word.lower().startswith("$"), words)))

            if len(cashtags) > 0 :
                print(cashtags)

        df.to_csv(str(DATA_PATH) + '/reddit/reddit_posts.csv')
        print(df)
