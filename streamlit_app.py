from flask import Flask, request, redirect, session, jsonify
from spotify_helper import sp_oauth, get_spotify_client, create_playlist, search_and_add_tracks
from gemini_helper import generate_song_list
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SPOTIFY_CLIENT_SECRET")

# Configure session
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

@app.route('/')
def home():
    return "🎵 Spotify Playlist Creator API is running! Use /login to authenticate with Spotify."

@app.route('/debug')
def debug():
    """Debug route to check session data"""
    return jsonify({
        "session_data": dict(session),
        "has_token": 'token_info' in session,
        "session_id": request.cookies.get('session')
    })

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "No authorization code received"}), 400
    
    try:
        token_info = sp_oauth.get_access_token(code)
        session['token_info'] = token_info
        session.permanent = True
        return f"Authentication complete! Session saved. <a href='/debug'>Check session</a>"
    except Exception as e:
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 400

@app.route('/done')
def done():
    return "Authentication complete"

@app.route('/check_auth')
def check_auth():
    token_info = session.get('token_info')
    if token_info:
        return jsonify({"authenticated": True, "message": "You are authenticated!"})
    else:
        return jsonify({"authenticated": False, "message": "Not authenticated"})

@app.route('/generate_playlist', methods=['POST'])
def generate_playlist():
    data = request.json
    topic = data['topic']
    language = data['language']
    playlist_name = f"{topic} Songs"
    
    token_info = session.get('token_info')
    if not token_info:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        sp = get_spotify_client(token_info)
        user_id = sp.me()['id']
        songs = generate_song_list(topic, language)
        playlist_id, playlist_url = create_playlist(sp, user_id, playlist_name)
        search_and_add_tracks(sp, playlist_id, songs)
        
        return jsonify({"playlist_url": playlist_url})
    except Exception as e:
        return jsonify({"error": f"Playlist creation failed: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)