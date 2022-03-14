from concurrent.futures import thread
from pymongo import MongoClient
import re
import pandas as pd
import os 
import pygsheets 
from spotipy.oauth2 import SpotifyClientCredentials
from get_links import LinkConverter

credentials = SpotifyClientCredentials(
        client_id=os.environ["SPOTIFY_ID"],
        client_secret=os.environ["SPOTIFY_SECRET"])

THREAD_ID = "1cot2h"
EXPORT_FILE = THREAD_ID + "_v1" + ".csv"
# Source: https://stackoverflow.com/questions/19377262/regex-for-youtube-url
# regex_pattern = "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"

lc = LinkConverter(credentials)
# Source: https://www.geeksforgeeks.org/python-check-url-string/
url_pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

client = MongoClient(os.environ["MONGO_URL"])
db = client.get_database("mmt-project")
thread_collection = db[THREAD_ID]

comments = thread_collection.find({}, {"_id": 0})

filtered_data = []

for comment in comments:
    # Just checking Youtube for now
    # yout for youtube.com and youtu.be
    if "yout" in comment["body"]:
        matches = re.findall(url_pattern, comment["body"])

        # String that had "yout" as part of text and not URL
        if len(matches) == 0:
            continue
        for url in matches:
            url = url[0]
            # Filtering out non youtube links
            if ("youtube" not in url) and ("youtu.be" not in url):
                print(f"Dropping URL {url}")
                continue
            
            spot_id = lc.get_spotify_id(url)

            filtered_data.append({
                "yt_url": url,
                "spot_id": spot_id,
                "author": comment["author"],
                "comment_id": comment["comment_id"],
                "score": comment["score"]
            })
print()

df = pd.DataFrame(filtered_data)
gs_client = pygsheets.authorize(service_file=os.environ["GS_CRED_PATH"])
sh = gs_client.open('test')
wks = sh.sheet1 
wks.set_dataframe(df, (1,1))
df.to_csv(EXPORT_FILE, index=False)
print("Exported to", EXPORT_FILE)
