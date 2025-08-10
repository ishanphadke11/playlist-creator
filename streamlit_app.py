import streamlit as st
import requests
import time

BASE_URL = "https://playlist-creator-ndda.onrender.com"

st.set_page_config(page_title="Spotify Playlist Creator", page_icon="🎵")
st.title("🎵 Spotify Playlist Creator")

if "auth_id" not in st.session_state:
    st.session_state.auth_id = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Step 1: Login
st.markdown("### Step 1: Authenticate with Spotify")
if st.button("🎧 Login with Spotify"):
    r = requests.get(f"{BASE_URL}/start_auth", timeout=10)
    if r.ok:
        obj = r.json()
        auth_id = obj["auth_id"]
        auth_url = obj["auth_url"]
        st.session_state.auth_id = auth_id
        st.markdown(f'[Click here to log in with Spotify]({auth_url})')
        with st.spinner("Waiting for you to finish Spotify login in the other tab..."):
            for _ in range(60):
                s = requests.get(f"{BASE_URL}/auth_status", params={"auth_id": auth_id}, timeout=5)
                if s.ok and s.json().get("authenticated"):
                    st.success("✅ Authenticated with Spotify!")
                    st.session_state.authenticated = True
                    break
                time.sleep(1)
            else:
                st.warning("⏳ Timed out waiting for Spotify login.")
    else:
        st.error("❌ Failed to start authentication.")

# Step 2: Create playlist
st.markdown("### Step 2: Create a Playlist")
topic = st.text_input("Enter a topic:")
language = st.text_input("Enter language:")

if st.button("🎵 Generate Playlist"):
    if not topic or not language:
        st.error("Please enter both topic and language.")
    elif not st.session_state.authenticated:
        st.error("⚠️ Please authenticate with Spotify first!")
    else:
        with st.spinner("Creating playlist..."):
            payload = {
                "topic": topic,
                "language": language,
                "auth_id": st.session_state.auth_id
            }
            resp = requests.post(f"{BASE_URL}/generate_playlist", json=payload, timeout=30)
            if resp.ok:
                playlist_url = resp.json()["playlist_url"]
                st.success("🎉 Playlist created!")
                st.markdown(f"[Open Playlist]({playlist_url})")
            elif resp.status_code == 401:
                st.error("⚠️ Not authenticated with Spotify.")
            else:
                st.error("❌ Something went wrong.")
