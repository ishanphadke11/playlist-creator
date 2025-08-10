import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_song_list(prompt, language):
    print(f"[DEBUG] Calling Gemini with prompt='{prompt}', language='{language}'")
    model = genai.GenerativeModel('gemini-1.5-flash')
    full_prompt = (
        f"Generate exactly 15 songs about '{prompt}' in '{language}'. "
        "Return them in the format: Song Name - Artist Name, one per line. "
        "No numbering, no extra commentary."
    )
    response = model.generate_content(full_prompt)

    print(f"[DEBUG] Gemini raw response: {getattr(response, 'text', None)}")

    if not hasattr(response, "text") or not response.text:
        return []

    songs = [line.strip() for line in response.text.splitlines() if line.strip()]
    return songs

