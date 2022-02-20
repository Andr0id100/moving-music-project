import os
import praw
from pymongo import MongoClient
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--post_link", type=str, required=True)
args = parser.parse_args()

def process_comments(comment_thread):
    processed_comments = []
    print()
    for (i, x) in enumerate(comment_thread):
        print(f"{i+1}/{len(comment_thread)}")
    
        if type(x) is praw.models.MoreComments:
            processed_comments.extend(process_comments(x.comments()))
            continue
    
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
        processed_comments.append(document)
    return processed_comments

POST_LINK = args.post_link

reddit = praw.Reddit(client_id=os.environ["REDDIT_CLIENT_ID"],
                     client_secret=os.environ["REDDIT_SECRET"], user_agent=os.environ["REDDIT_USER_AGENT"])
client = MongoClient()
db = client["mmt_project"]

submission = reddit.submission(url=POST_LINK)
# Delete existing collection for the thread
db.drop_collection(submission.id)
thread_collection = db[submission.id]

comments = submission.comments.list()
flattened_comments = process_comments(comments)
thread_collection.insert_many(flattened_comments)
    