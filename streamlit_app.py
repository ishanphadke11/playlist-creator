import streamlit as st
import requests

BASE_URL = "https://playlist-creator-ndda.onrender.com"

st.title("🎵 Spotify Playlist Creator")

# Check authentication status
try:
    auth_response = requests.get(f"{BASE_URL}/check_auth")
    if auth_response.status_code == 200:
        auth_data = auth_response.json()
        if auth_data.get("authenticated"):
            st.success("✅ You are authenticated with Spotify!")
        else:
            st.warning("⚠️ You need to authenticate with Spotify first.")
    else:
        st.warning("⚠️ Could not check authentication status.")
except:
    st.error("❌ Could not connect to authentication server.")

st.markdown("### Step 1: Authenticate with Spotify")
if st.button("🎧 Login with Spotify"):
    st.markdown(f"[Click here to login with Spotify]({BASE_URL}/login)")
    st.info("🔄 After logging in, refresh this page to see your authentication status!")

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
                st.success("🎉 Playlist created!")
                st.markdown(f"[🎵 Open Playlist]({playlist_url})")
            elif response.status_code == 401:
                st.error("⚠️ Please authenticate with Spotify first! Click the login button above.")
            else:
                st.error("❌ Something went wrong. Please try again.")
    else:
        st.error("📝 Please enter both topic and language")