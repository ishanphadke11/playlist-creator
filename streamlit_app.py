import streamlit as st
import requests
from urllib.parse import urlencode

BASE_URL = "https://playlist-creator-ndda.onrender.com"
SPOTIFY_CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
REDIRECT_URI = st.secrets["SPOTIFY_REDIRECT_URI"]

# Spotify authentication URL builder
def get_auth_url():
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "playlist-modify-public",
        "show_dialog": "true"
    }
    return f"https://accounts.spotify.com/authorize?{urlencode(params)}"

st.title("🎵 Spotify Playlist Creator")

# Store token in session state
if "spotify_token" not in st.session_state:
    st.session_state.spotify_token = None

# Step 1: Authentication
st.markdown("### Step 1: Authenticate with Spotify")
if st.button("🎧 Login with Spotify"):
    auth_url = get_auth_url()
    st.markdown(f"[Click here to login with Spotify]({auth_url})")
    st.info("After logging in, you'll be redirected to a page with your access token. Copy the whole token value and paste it below.")

# Token input
token_input = st.text_input("Paste Spotify Access Token Here", key="token_input")

if token_input:
    st.session_state.spotify_token = token_input
    st.success("✅ Token saved! You can now create playlists")

# Step 2: Playlist Creation
st.markdown("### Step 2: Create a Playlist")
topic = st.text_input("Enter a topic:")
language = st.text_input("Enter language:")

if st.button("🎵 Generate Playlist"):
    if not st.session_state.spotify_token:
        st.error("⚠️ Please authenticate first!")
    elif not topic or not language:
        st.error("📝 Please enter both topic and language")
    else:
        with st.spinner("Creating playlist..."):
            response = requests.post(
                f"{BASE_URL}/generate_playlist",
                json={
                    "topic": topic,
                    "language": language,
                    "token": st.session_state.spotify_token  # Send token directly
                }
            )
            
            if response.status_code == 200:
                playlist_url = response.json().get('playlist_url')
                st.success("🎉 Playlist created!")
                st.markdown(f"[🎵 Open Playlist]({playlist_url})")
            else:
                error = response.json().get("error", "Unknown error")
                st.error(f"❌ Playlist creation failed: {error}")