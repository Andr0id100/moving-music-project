from pymongo import MongoClient
import re
import pygsheets 
import pandas as pd
from argparse import ArgumentParser
from spotipy.oauth2 import SpotifyClientCredentials
from get_links import SpotifyFinder
import os 

credentials = SpotifyClientCredentials(
        client_id=os.environ["SPOTIFY_ID"],
        client_secret=os.environ["SPOTIFY_SECRET"])

sf = SpotifyFinder(credentials)

parser = ArgumentParser()
parser.add_argument("--post_id", type=str, required=True)
args = parser.parse_args()

# THREAD_ID = "1cot2h"
# EXPORT_FILE = THREAD_ID + "_v2" + ".csv"
# THREAD_ID = "rmfow"
# EXPORT_FILE = THREAD_ID + "_v1" + ".csv"

POST_ID = args.post_id
EXPORT_FILE = f"{POST_ID}.csv"

# Source: https://stackoverflow.com/questions/19377262/regex-for-youtube-url
# regex_pattern = "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"

# Source: https://www.geeksforgeeks.org/python-check-url-string/
#url_pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
url_pattern = r'\(.*?\)'
x_by_pattern = r"((?:\w+ ){1,4})by ((?:\w+ ?){1,4})"
x_dash_pattern = r"((?:\w+ ){1,4})- ((?:\w+ ?){1,4})"

gs_client = pygsheets.authorize(service_file=os.environ["GS_CRED_PATH"])
sh = gs_client.open('test')
wks = sh.sheet1 

client = MongoClient()
db = client["mmt_project"]
thread_collection = db[POST_ID]

total = thread_collection.count_documents({})

comments = thread_collection.find({}, {"_id": 0})

filtered_data = []

count = 0
for i, comment in enumerate(comments):
    count+=1 

total = 0 

def write_to_sheet(data):
    df = pd.DataFrame(data).assign(post_id=[POST_ID for _ in data])
    df.to_csv(EXPORT_FILE, index=False)
    print("Exported to", EXPORT_FILE)
    wks.set_dataframe(df, (1,1))

comments = thread_collection.find({}, {"_id": 0})
for i, comment in enumerate(comments):
    print(f'{i}/{count} - {total}', end='\r', flush=True)    

    if((i+1)%5000 == 0):
        write_to_sheet(filtered_data)

    match = False 
    # Just checking Youtube for now
    # yout for youtube.com and youtu.be
    if "yout" in comment["body"]:
        print('here')
        matches = re.findall(url_pattern, comment["body"])
        # String that had "yout" as part of text and not URL
        if len(matches) == 0:
            continue
        for url in matches:
            url = url[1:-1]
            # Filtering out non youtube links
            if ("youtube" not in url) and ("youtu.be" not in url):
                #print(f"Dropping URL {url}")
                continue
            spotify_id = sf.id_from_yt(url.lstrip().rstrip())
            filtered_data.append({
                "url": url,
                "author": comment["author"],
                "comment_id": comment["comment_id"],
                "upvotes": comment["upvotes"], 
                "spotify_id": spotify_id,
                "song_match": None, 
                "artist_match": None,
            })
            total+=1
            match = True

    if(not(match)): 
        x_by_match = re.findall(x_by_pattern, comment['body'])
        x_dash_match = re.findall(x_dash_pattern, comment['body'])
        match = False 

        if(len(x_by_match)):
            artist = x_by_match[0][1].lstrip().rstrip()
            track = x_by_match[0][0].lstrip().rstrip()
            match = True

        elif(len(x_dash_match)):
            artist = x_dash_match[0][1].lstrip().rstrip()
            track = x_dash_match[0][0].lstrip().rstrip()
            match = True

        if(match):
            spotify_id = sf.id_from_info(artist, track)
            if(not(spotify_id)):
                spotify_id = sf.id_from_info(track, artist)
            if(spotify_id):
                filtered_data.append({
                    "url": None,
                    "author": comment["author"],
                    "comment_id": comment["comment_id"],
                    "upvotes": comment["upvotes"], 
                    "spotify_id": spotify_id,
                    "song_match": track, 
                    "artist_match": artist,
                })
                total+=1

write_to_sheet(filtered_data)