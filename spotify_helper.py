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
    Search Spotify for each song title and add the most popular result to the playlist.
    Returns the list of actually added tracks (title + artists).
    """
    final_tracks = []

    for song in songs:
        song = song.strip()
        if not song:
            continue

        try:
            query = f'track:"{song}"'
            print(f"[DEBUG] Searching Spotify for: {query}")
            result = sp.search(q=query, limit=5, type="track")
            tracks = result.get("tracks", {}).get("items", [])

            if tracks:
                # Pick most popular track
                best = max(tracks, key=lambda t: t.get("popularity", 0))
                sp.playlist_add_items(playlist_id, [best["id"]])
                track_info = f"{best['name']} - {', '.join([a['name'] for a in best['artists']])}"
                final_tracks.append(track_info)
                print(f"[INFO] Added: {track_info}")
            else:
                print(f"[WARN] No results for: {song}")

        except Exception as e:
            print(f"[ERROR] Failed to add {song}: {e}")

    return final_tracks


def create_playlist(sp, user_id, name):
    playlist = sp.user_playlist_create(user=user_id, name=name, public=True)
    print(f"[INFO] Created playlist: {playlist['external_urls']['spotify']}")
    return playlist['id'], playlist['external_urls']['spotify']