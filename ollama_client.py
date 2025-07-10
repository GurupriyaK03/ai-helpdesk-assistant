import openai
import os

# Load your OpenAI API key from Streamlit secrets or environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def query_ollama(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=500
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"❌ Error from OpenAI: {str(e)}"
