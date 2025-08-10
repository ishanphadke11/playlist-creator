import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def generate_song_list(custom_prompt):
    """
    Generate a list of songs using Gemini. Ensures no empty entries.
    """

    response = model.generate_content(custom_prompt)
    raw_lines = response.text.split("\n")
    songs = [line.strip() for line in raw_lines if line.strip()]

    print("[DEBUG] Raw Gemini response:")
    print(response.text)
    print("[DEBUG] Cleaned song list:")
    print(songs)

    return songs
