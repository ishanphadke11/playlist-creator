import streamlit as st
import requests

st.title("Spotify Playlist Creator")

st.markdown("### Authenticate with Spotify")
if st.button("Login with Spotify"):
    st.markdown("[Click here to login with Spotify](https://83c758cfffee.ngrok-free.app/login)")

st.markdown("### Create a Playlist")
topic = st.text_input("Enter a topic: ")
language = st.text_input("Enter language: ")

if st.button("Generate Playlist"):
    response = requests.post("https://83c758cfffee.ngrok-free.app/generate_playlist", json={
        "topic": topic,
        "language": language
    })

    if response.status_code == 200:
        playlist_url = response.json()['playlist_url']
        st.success("Playlist created!")
        st.markdown(f"[Playlist] ({playlist_url})")
    else:
        st.error("Something went wrong")