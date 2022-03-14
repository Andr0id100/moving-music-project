# Use Reddit API to scrape
# all comments from the link of a thread

import os
import praw
from pymongo import MongoClient

THREAD_LINK = "https://www.reddit.com/r/Music/comments/1cot2h/what_is_the_most_moving_song_you_have_ever_heard/"

reddit = praw.Reddit(client_id=os.environ["REDDIT_CLIENT_ID"],
                     client_secret=os.environ["REDDIT_SECRET"], user_agent=os.environ["REDDIT_USER_AGENT"])
                     
client = MongoClient(os.environ["MONGO_URL"])
db = client.get_database("mmt-project")
#collection = db.mmt_data 

submission = reddit.submission(url=THREAD_LINK)
# Delete existing collection for the thread
db.drop_collection(submission.id)
thread_collection = db[submission.id]

comments = submission.comments.list()

for (i, x) in enumerate(comments):
    print(f"{i}/{len(comments)}")
    body = x.body
    score = x.score
    if x.author is None:
        author = ""
    else:
        author = x.author.name
    document = {
        "body": body,
        "author": author,
        "score":score, 
        "comment_id": x.id
    }
    thread_collection.insert_one(document)