import streamlit as st
import requests
import time

BASE_URL = "https://playlist-creator-ndda.onrender.com"

st.set_page_config(page_title="Spotify Playlist Creator", page_icon="🎵")
st.title("Spotify Playlist Creator")

if "auth_id" not in st.session_state:
    st.session_state.auth_id = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Step 1: Login
st.markdown("### Step 1: Authenticate with Spotify")
if st.button("Login with Spotify"):
    r = requests.get(f"{BASE_URL}/start_auth", timeout=10)
    if r.ok:
        obj = r.json()
        auth_id = obj["auth_id"]
        auth_url = obj["auth_url"]
        st.session_state.auth_id = auth_id

        # Open Spotify login in a new tab immediately
        st.markdown(
            f"""
            <script>
                window.open("{auth_url}", "_blank");
            </script>
            """,
            unsafe_allow_html=True
        )

        with st.spinner("Waiting for you to finish Spotify login in the other tab..."):
            for _ in range(60):
                s = requests.get(f"{BASE_URL}/auth_status", params={"auth_id": auth_id}, timeout=5)
                if s.ok and s.json().get("authenticated"):
                    st.success("Authenticated with Spotify!")
                    st.session_state.authenticated = True
                    break
                time.sleep(1)
            else:
                st.warning("Timed out waiting for Spotify login.")
    else:
        st.error("Failed to start authentication.")


# Step 2: Create playlist
st.markdown("### Step 2: Create a Playlist")
custom_prompt = st.text_area("Enter your prompt: ")

if st.button("Generate Playlist"):
    if not custom_prompt.strip():
        st.error("Please enter a prompt")
    elif not st.session_state.authenticated:
        st.error("Please authenticate with Spotify first!")
    else:
        with st.spinner("Creating playlist..."):
            payload = {
                "custom_prompt": custom_prompt,
                "auth_id": st.session_state.auth_id
            }
            resp = requests.post(f"{BASE_URL}/generate_playlist", json=payload, timeout=30)
            if resp.ok:
                playlist_url = resp.json()["playlist_url"]
                st.success("Playlist created!")
                st.markdown(f"[Open Playlist]({playlist_url})")
            elif resp.status_code == 401:
                st.error("Not authenticated with Spotify.")
            else:
                st.error("Something went wrong.")
