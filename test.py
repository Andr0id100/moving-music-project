from pymongo import MongoClient
import re
import pandas as pd
from argparse import ArgumentParser
from spotipy.oauth2 import SpotifyClientCredentials
from get_links import SpotifyFinder
import os

parser = ArgumentParser()
parser.add_argument("--post_id", type=str, required=True)
args = parser.parse_args()

# THREAD_ID = "1cot2h"
# EXPORT_FILE = THREAD_ID + "_v2" + ".csv"
# THREAD_ID = "rmfow"
# EXPORT_FILE = THREAD_ID + "_v1" + ".csv"

POST_ID = args.post_id
EXPORT_FILE = f"{POST_ID}.csv"

credentials = SpotifyClientCredentials(
        client_id=os.environ["SPOTIFY_ID"],
        client_secret=os.environ["SPOTIFY_SECRET"])

sf = SpotifyFinder(credentials)

# Source: https://stackoverflow.com/questions/19377262/regex-for-youtube-url
# regex_pattern = "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"

# Source: https://www.geeksforgeeks.org/python-check-url-string/
url_pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
x_by_pattern = r"((?:\w+ ){1,4})by ((?:\w+ ?){1,4})"
x_dash_pattern = r"((?:\w+ ){1,4})- ((?:\w+ ?){1,4})"

client = MongoClient()
db = client["mmt_project"]
thread_collection = db[POST_ID]

comments = thread_collection.find({}, {"_id": 0})

filtered_data = []

for comment in comments[:100]:
    # Just checking Youtube for now
    # yout for youtube.com and youtu.be
    matches = re.findall(x_by_pattern, comment["body"])
    if(len(matches)):
        print(matches) 
        print(sf.id_from_info(matches[0][1].lstrip().rstrip(), matches[0][0].lstrip().rstrip()))