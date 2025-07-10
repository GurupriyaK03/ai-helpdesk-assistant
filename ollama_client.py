import openai
import os
import request
openai.api_key = "your-api-key"  # Set this securely!

def query_ollama(prompt):
    client = openai.OpenAI()  # New client-based usage

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or gpt-4
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
