import traceback
from flask import Flask, request, redirect, jsonify, make_response
from dotenv import load_dotenv
from datetime import timedelta
import os
import uuid
import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import google.generativeai as genai
from spotify_helper import get_spotify_client, search_and_add_tracks, create_playlist
from gemini_helper import generate_song_list

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not found in environment variables.")

print(f"[DEBUG] GOOGLE_API_KEY loaded: {API_KEY[:5]}...")  # mask for logs

genai.configure(api_key=API_KEY)


app = Flask(__name__)
app.secret_key = os.getenv("SPOTIFY_CLIENT_SECRET")

# Session config
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = False

# In-memory token store: auth_id -> token_info
_tokens_by_authid = {}

# Configure Spotify OAuth
scope = "playlist-modify-public"
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
print(f"[DEBUG] Using redirect URI: {redirect_uri}")

sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=redirect_uri,
    scope=scope,
    show_dialog=True
)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# Routes
@app.route('/')
def home():
    return "Spotify Playlist Creator API is running"

@app.route('/start_auth')
def start_auth():
    auth_id = uuid.uuid4().hex
    auth_url = sp_oauth.get_authorize_url(state=auth_id)
    _tokens_by_authid[auth_id] = None
    return jsonify({"auth_id": auth_id, "auth_url": auth_url})

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code:
        return jsonify({"error": "No authorization code received"}), 400
    try:
        token_info = sp_oauth.get_access_token(code)
        if state:
            _tokens_by_authid[state] = token_info
        return f"""
        <html>
        <body>
          <h2>Authentication complete — you can close this tab.</h2>
          <script>
            if (window.opener) {{
              window.opener.postMessage({{type: 'spotify_auth_complete', auth_id: '{state}'}}, '*');
            }}
          </script>
        </body>
        </html>
        """
    except Exception as e:
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 400

@app.route('/auth_status')
def auth_status():
    auth_id = request.args.get('auth_id')
    if not auth_id:
        return jsonify({"authenticated": False}), 400
    token_info = _tokens_by_authid.get(auth_id)
    if token_info:
        # Refresh token if expired
        expires_at = token_info.get("expires_at")
        if expires_at and expires_at < time.time():
            try:
                token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
                _tokens_by_authid[auth_id] = token_info
            except Exception:
                return jsonify({"authenticated": False})
        return jsonify({"authenticated": True})
    return jsonify({"authenticated": False})

@app.route('/generate_playlist', methods=['POST', 'OPTIONS'])
def generate_playlist_route():
    if request.method == 'OPTIONS':
        resp = make_response()
        resp.headers.add("Access-Control-Allow-Origin", "*")
        resp.headers.add('Access-Control-Allow-Headers', "*")
        resp.headers.add('Access-Control-Allow-Methods', "*")
        return resp

    try:
        data = request.json
        prompt = data.get("custom_prompt").strip()
        auth_id = data.get('auth_id')

        print(f"[DEBUG] Incoming playlist request: {prompt}, auth_id={auth_id}")

        if not prompt:
            return jsonify({"error": "Missing prompt"}), 400

        token_info = _tokens_by_authid.get(auth_id)
        if not token_info:
            return jsonify({"error": "Not authenticated"}), 401

        sp = get_spotify_client(token_info)
        user_id = sp.me().get('id')
        print(f"[DEBUG] Spotify user_id: {user_id}")

        # Gemini step
        print("Calling generate song list")
        songs = generate_song_list(prompt)
        print(f"[DEBUG] Gemini returned songs: {songs}")

        if not songs:
            return jsonify({"error": "Gemini returned no songs"}), 500

        playlist_id, playlist_url = create_playlist(sp, user_id, f"Custom Playlist")
        print(f"[DEBUG] Created playlist: {playlist_id} - {playlist_url}")

        search_and_add_tracks(sp, playlist_id, songs)
        print(f"[DEBUG] Added {len(songs)} songs to playlist")

        resp = jsonify({"playlist_url": playlist_url})
        resp.headers.add("Access-Control-Allow-Origin", "*")
        return resp

    except Exception as e:
        print(f"[ERROR] Playlist creation failed: {str(e)}")
        traceback.print_exc()
        resp = jsonify({"error": f"Playlist creation failed: {str(e)}"})
        resp.headers.add("Access-Control-Allow-Origin", "*")
        return resp, 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
