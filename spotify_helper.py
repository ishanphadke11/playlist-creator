import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import google.generativeai as genai

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

def search_and_add_tracks(sp, playlist_id, songs):
    """
    Improved Spotify search logic.
    - Tries exact match first
    - Falls back to partial match
    - Tries multiple results
    """
    for entry in songs:
        entry = entry.strip()
        if not entry:
            print("[WARN] Skipping empty song entry")
            continue

        try:
            print(f"[DEBUG] Searching for: {entry}")
            
            # First attempt: full query
            result = sp.search(q=entry, limit=3, type="track")
            tracks = result.get("tracks", {}).get("items", [])
            
            # If no result, try splitting into song and artist
            if not tracks and " - " in entry:
                song, artist = entry.split(" - ", 1)
                print(f"[DEBUG] Secondary search: song={song}, artist={artist}")
                result = sp.search(q=f"track:{song} artist:{artist}", limit=3, type="track")
                tracks = result.get("tracks", {}).get("items", [])

            if tracks:
                # Pick the most popular track from the results
                best_match = max(tracks, key=lambda t: t.get("popularity", 0))
                sp.playlist_add_items(playlist_id, [best_match["id"]])
                print(f"[INFO] Added: {best_match['name']} by {best_match['artists'][0]['name']}")
            else:
                print(f"[WARN] No results for: {entry}")

        except Exception as e:
            print(f"[ERROR] Failed to search/add {entry}: {e}")


def create_playlist(sp, user_id, name):
    playlist = sp.user_playlist_create(user=user_id, name=name, public=True)
    print(f"[INFO] Created playlist: {playlist['external_urls']['spotify']}")
    return playlist['id'], playlist['external_urls']['spotify']