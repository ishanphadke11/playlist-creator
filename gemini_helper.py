import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def build_prompt(custom_prompt):
    return f"""You are a playlist curator. The user has written a simple prompt from which they want
            a playlist created. Here is that prompt: {custom_prompt}. I want you to only suggest songs that fit the user's request exactly.
            Do not include any songs from unrelated genres. If the user has not specified a number of songs, 
            include 15 songs. If the user has specified a number of songs, give exactly that many songs. 
            Focus on well known tracks in the category. Once you have created your song list, go through your list one by one 
            to make sure each song truly fits the prompt. Format songs as 'Song Title - Artist'."""


def generate_song_list(custom_prompt):
    """
    Generate a list of songs using Gemini. Ensures no empty entries.
    Also does a self-check to remove irrelevant songs.
    """

    prompt = build_prompt(custom_prompt)
    response = model.generate_content(prompt)

    raw_lines = response.text.split("\n")
    songs = [line.strip() for line in raw_lines if line.strip()]

    print("[DEBUG] Raw Gemini response:")
    print(response.text)

    # Verification step: Re-check with Gemini
    verification_prompt = f"""
    User prompt: {custom_prompt}
    Here is the list of songs I generated: {songs}.
    Please return ONLY the songs that actually fit the prompt. 
    Keep the same format 'Song - Artist'. Do not add any explanation, just the final verified list.
    """
    verification_response = model.generate_content(verification_prompt)
    verified_lines = verification_response.text.split("\n")
    verified_songs = [line.strip() for line in verified_lines if line.strip()]

    print("[DEBUG] Verified song list:")
    print(verified_songs)

    return verified_songs