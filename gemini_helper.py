import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def build_prompt(custom_prompt):
    return f"""You are a playlist curator. The user has written a simple prompt from which they want
a playlist created. Here is that prompt: {custom_prompt}. Only suggest songs that fit the prompt exactly.
If no number of songs is specified, include 15 songs. Focus on well-known tracks in the category.
Format each line as: 'Song Title' only (no artist)."""


def generate_song_list(custom_prompt):
    """
    Generate a list of song titles using Gemini and verify them.
    Removes any empty entries and ensures songs fit the prompt.
    """
    # Step 1: Initial generation
    prompt = build_prompt(custom_prompt)
    response = model.generate_content(prompt)

    raw_lines = response.text.split("\n")
    songs = [line.strip().strip('"') for line in raw_lines if line.strip()]

    print("[DEBUG] Gemini initial song titles:")
    print(songs)

    # Step 2: Verification
    verification_prompt = f"""
        User prompt: {custom_prompt}
        Here is the list of songs I generated: {songs}.
        Please return ONLY the songs that actually fit the prompt. 
        Keep the same format 'Song Title' only (no artist). 
        Do not include any unrelated songs. Do not add explanations.
        """
    verification_response = model.generate_content(verification_prompt)
    verified_lines = verification_response.text.split("\n")
    verified_songs = [line.strip().strip('"') for line in verified_lines if line.strip()]

    print("[DEBUG] Verified song list:")
    print(verified_songs)

    return verified_songs
