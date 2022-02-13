# Use Reddit API to scrape
# all comments from the link of a thread

import os
import praw
from pymongo import MongoClient

THREAD_LINK = "https://www.reddit.com/r/Music/comments/1cot2h/what_is_the_most_moving_song_you_have_ever_heard/"

reddit = praw.Reddit(client_id=os.environ["REDDIT_CLIENT_ID"],
                     client_secret=os.environ["REDDIT_SECRET"], user_agent=os.environ["REDDIT_USER_AGENT"])
client = MongoClient()
db = client["mmt_project"]

submission = reddit.submission(url=THREAD_LINK)
# Delete existing collection for the thread
db.drop_collection(submission.id)
thread_collection = db[submission.id]

comments = submission.comments.list()

for (i, x) in enumerate(comments):
    print(f"{i}/{len(comments)}")
    body = x.body
    if x.author is None:
        author = ""
    else:
        author = x.author.name
    document = {
        "body": body,
        "author": author,
        "comment_id": x.id,
        "upvotes": x.ups
    }
    thread_collection.insert_one(document)
    