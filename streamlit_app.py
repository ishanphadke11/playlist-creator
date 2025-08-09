import streamlit as st
import requests

# Your actual Render URL
BASE_URL = "https://playlist-creator-ndda.onrender.com"

st.title("🎵 Spotify Playlist Creator")
st.markdown("### Step 1: Authenticate with Spotify")

if st.button("🎧 Login with Spotify"):
    st.markdown(f"[Click here to login with Spotify]({BASE_URL}/login)")

st.markdown("### Step 2: Create a Playlist")
topic = st.text_input("Enter a topic:")
language = st.text_input("Enter language:")

if st.button("🎵 Generate Playlist"):
    if topic and language:
        with st.spinner("Creating playlist..."):
            response = requests.post(f"{BASE_URL}/generate_playlist", json={
                "topic": topic,
                "language": language
            })
            
            if response.status_code == 200:
                playlist_url = response.json()['playlist_url']
                st.success("Playlist created!")
                st.markdown(f"[🎵 Open Playlist]({playlist_url})")
            elif response.status_code == 401:
                st.error("Please authenticate with Spotify first!")
            else:
                st.error("Something went wrong")
    else:
        st.error("Please enter both topic and language")