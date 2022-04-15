from argparse import ArgumentParser
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import Spotify
import os
from tqdm import tqdm
import json

OUTPUT_DIRECTORY = "playlist_data"

os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

def read_track_ids(tracks):
    track_ids = []
    while True:
        for item in tracks['items']:
            if 'track' in item:
                track = item['track']
            else:
                track = item
            try:
                track_ids.append(track["id"])
            except KeyError:
                print(u'Skipping track {0} by {1} (local only?)'.format(
                    track['name'], track['artists'][0]['name']))
        # 1 page = 50 results
        # check if there are more pages
        if tracks['next']:
            tracks = sp.next(tracks)
        else:
            break
    return track_ids


def read_playlist(playlist_id):
    results = sp.playlist(playlist_id,
                          fields='tracks,next,name')
    tracks = results['tracks']
    return read_track_ids(tracks)

parser = ArgumentParser()

parser.add_argument("--playlist_id", type=str, required=True)

args = parser.parse_args()

credentials = SpotifyClientCredentials(
    client_id=os.environ["SPOTIFY_CLIENT_ID"],
    client_secret=os.environ["SPOTIFY_CLIENT_SECRET"])
sp = Spotify(client_credentials_manager=credentials)

PLAYLIST_ID = args.playlist_id

spotify_ids = read_playlist(PLAYLIST_ID)

track_meta_data = []
track_audio_features = []
for track_id in tqdm(spotify_ids):
    track_meta_data.append(sp.track(track_id))
    track_audio_features.append(sp.audio_features(track_id)[0])

with open(f"{OUTPUT_DIRECTORY}/{PLAYLIST_ID}-meta-data.json", 'w') as f:
    json.dump(track_meta_data, f, indent=4)

with open(f"{OUTPUT_DIRECTORY}/{PLAYLIST_ID}-audio-features.json", 'w') as f:
    json.dump(track_audio_features, f, indent=4)
print("Done!")