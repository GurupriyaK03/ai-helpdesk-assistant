import requests

# ollama_client.py
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")  # or paste it directly (not recommended for public repos)

def query_ollama(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if you have access
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response['choices'][0]['message']['content'].strip()
