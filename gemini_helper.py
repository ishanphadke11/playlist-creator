import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def generate_song_list(topic: str, language: str):
    """
    Generate a list of songs using Gemini. Ensures no empty entries.
    """
    full_prompt = (
        f"Generate a playlist of 10 songs about '{topic}' in {language}. "
        "Return one song per line in the format: Song Name - Artist."
    )

    response = model.generate_content(full_prompt)
    raw_lines = response.text.split("\n")
    songs = [line.strip() for line in raw_lines if line.strip()]

    print("[DEBUG] Raw Gemini response:")
    print(response.text)
    print("[DEBUG] Cleaned song list:")
    print(songs)

    return songs
