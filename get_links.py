# Get Spotify links given YouTube links 

import youtube_dl 
import spotipy 
import pygsheets 
import pandas as pd 
from spotipy.oauth2 import SpotifyClientCredentials
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process 

import os

EXPORT_FILE = "spotify.csv"

credentials = SpotifyClientCredentials(
        client_id=os.environ["SPOTIFY_ID"],
        client_secret=os.environ["SPOTIFY_SECRET"])

class SpotifyFinder:
    def __init__(self, spot_credentials):
        self.ydl = youtube_dl.YoutubeDL()
        self.ydl.params['quiet'] = True
        self.sp = spotipy.Spotify(client_credentials_manager = spot_credentials)
    
    def get_yt_info(self, url):
        try:
            with self.ydl:
                video = self.ydl.extract_info(url, download = False)
                return (video['artist'], video['track'])
        except:
            return None

    def id_from_yt(self, yt_link):
        yt_info = self.get_yt_info(yt_link)
        if(yt_info == None):
            return "Video Unavailable" 
        artist, track = yt_info
        artist = artist.split(",")[0]
        return self.id_from_info(artist, track)

    def id_from_info(self, artistname, trackname):
        # res = self.sp.search(q=f'artist:{artistname} track:{trackname}', type='track')
        # if(res['tracks']['total']==0):
        try:
            res = self.sp.search(trackname, limit = 10)
            for i in res['tracks']['items']:
                track_ratio = fuzz.ratio(i['name'].lower(), trackname.lower())
                if(track_ratio >= 70):
                    artists = [j['name'] for j in i['artists']]
                    for target in artistname.split(','):
                        for candidate in artists:
                            artist_ratio = fuzz.ratio(target.lower(), candidate.lower())
                            if(artist_ratio >= 70):
                                return i['id']
        except:
            return None 
        # else:
        #     try:
        #         return res['tracks']['items'][0]['id']
        #     except:
        #         return None 

if __name__ == "__main__":
    sf = SpotifyFinder(credentials)
    print(sf.id_from_info("death cab for cutie", "i will follow you into the"))
    # data_df = pd.read_csv("data.csv")[["url", "author", "comment_id", "upvotes", "post_id"]]
    # data_df["spotify_id"] = data_df["url"].apply(lambda x: sf.get_spotify_id(x))

    # sh = gs_client.open('test')
    # wks = sh.sheet1 
    # wks.set_dataframe(data_df, (1,1))
    # data_df.to_csv(EXPORT_FILE, index=False)
    # print("Exported to", EXPORT_FILE)
