import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

scope = "playlist-modify-public"
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
print(f"[DEBUG] Using redirect URI: {redirect_uri}") # <-- Debug print

sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=redirect_uri,
    scope=scope,
    show_dialog=True
)

def get_spotify_client(token_info):
    return spotipy.Spotify(auth=token_info['access_token'])

def create_playlist(sp, user_id, name):
    playlist = sp.user_playlist_create(user=user_id, name=name, public=True)
    return playlist['id'], playlist['external_urls']['spotify']

def search_and_add_tracks(sp, playlist_id, song_list):
    track_uris = []
    for entry in song_list:
        result = sp.search(q=entry, limit=1, type='track')
        tracks = result.get('tracks', {}).get('items')
        if tracks:
            track_uris.append(tracks[0]['uri'])
    
    if track_uris:
        sp.playlist_add_items(playlist_id, track_uris)