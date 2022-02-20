from pymongo import MongoClient
import re
import pandas as pd
from argparse import ArgumentParser

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
url_pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

client = MongoClient()
db = client["mmt_project"]
thread_collection = db[POST_ID]

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
            
            filtered_data.append({
                "url": url,
                "author": comment["author"],
                "comment_id": comment["comment_id"],
                "upvotes": comment["upvotes"]
            })
print()

df = pd.DataFrame(filtered_data).assign(post_id=[POST_ID for _ in filtered_data])
df.to_csv(EXPORT_FILE, index=False)
print("Exported to", EXPORT_FILE)
