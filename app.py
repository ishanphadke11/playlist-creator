from flask import Flask, request, redirect, session, jsonify, make_response
from spotify_helper import sp_oauth, get_spotify_client, create_playlist, search_and_add_tracks
from gemini_helper import generate_song_list
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SPOTIFY_CLIENT_SECRET")

# Configure session for cross-origin
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = False

@app.route('/')
def home():
    return "🎵 Spotify Playlist Creator API is running! Use /login to authenticate with Spotify."

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Updated callback route
@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "No authorization code received"}), 400
    
    try:
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        
        # Return token as JSON instead of HTML
        return jsonify({
            "status": "success",
            "access_token": access_token,
            "token_preview": access_token[:20] + "..."
        })
    except Exception as e:
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 400

@app.route('/check_auth')
def check_auth():
    token_info = session.get('token_info')
    if token_info:
        return jsonify({
            "authenticated": True, 
            "message": "You are authenticated!",
            "token_preview": token_info['access_token'][:20] + "..."
        })
    else:
        return jsonify({"authenticated": False, "message": "Not authenticated"})

@app.route('/generate_playlist', methods=['POST', 'OPTIONS'])
def generate_playlist():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response
    
    data = request.json
    topic = data['topic']
    language = data['language']
    playlist_name = f"{topic} Songs"
    
    token_info = session.get('token_info')
    if not token_info:
        response = jsonify({"error": "Not authenticated"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 401
    
    try:
        sp = get_spotify_client(token_info)
        user_id = sp.me()['id']
        songs = generate_song_list(topic, language)
        playlist_id, playlist_url = create_playlist(sp, user_id, playlist_name)
        search_and_add_tracks(sp, playlist_id, songs)
        
        response = jsonify({"playlist_url": playlist_url})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    except Exception as e:
        response = jsonify({"error": f"Playlist creation failed: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)