# Get Spotify links given YouTube links 

import youtube_dl 
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
import os

class LinkConverter:
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

    def get_spotify_id(self, yt_link):
        yt_info = self.get_yt_info(yt_link)
        if(yt_info == None):
            return "Video Unavailable" 
        artistname, trackname = yt_info
        res = self.sp.search(q=f'artist:{artistname.split(",")[0]} track:{trackname}', type='track')

        if(res['tracks']['total']==0):
            res = self.sp.search(trackname, limit = 10)
            for i in res['tracks']['items']:
                if(i['name'].lower() == trackname.lower()):
                    artists = [j['name'] for j in i['artists']]
                    for target in artistname.split(','):
                        for candidate in artists:
                            if(target.lower() == candidate.lower()):
                                return i['id']
        else:
            try:
                return res['tracks']['items'][0]['id']
            except:
                return None 
