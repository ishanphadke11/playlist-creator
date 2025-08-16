import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def generate_song_list(custom_prompt):
    """
    Generate a list of songs using Gemini. Ensures no empty entries.
    """

    prompt = build_prompt(custom_prompt)

    response = model.generate_content(prompt)
    raw_lines = response.text.split("\n")
    songs = [line.strip() for line in raw_lines if line.strip()]

    print("[DEBUG] Raw Gemini response:")
    print(response.text)
    print("[DEBUG] Cleaned song list:")
    print(songs)

    return songs

def build_prompt(custom_prompt):
    return f"""You are a playlist curator. The user has written a simple prompt from which they want
            a playlist created. Here is that prompt: {custom_prompt}. I want you to only suggest songs that fit the user's request exactly
            Do not include any songs from unrelated genres. When you pick a son. If and only if the user has not specified a number of songs, 
            include 15 songs. If the user has specified a number of songs, give excatly that many songs. Focus on well known tracks in the category.
            For example try to exclude songs from artists who are generally not mainstream unless a specific artist is specified. Go throgh your
            list to make sure all songs in the list are related to the prompt entered by the user"""