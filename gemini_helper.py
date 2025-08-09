import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_song_list(prompt, language):
    model = genai.GenerativeModel('gemini-1.5-flash')
    full_prompt = f"Generate a list of 15 songs related to the topic ' {prompt} ' in ' {language} '. Just return the song name and artist in each line."
    response = model.generate_content(full_prompt)
    return response.text.splitlines()