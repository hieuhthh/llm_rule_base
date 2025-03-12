from dotenv import load_dotenv
load_dotenv()
from google import genai
from google.genai import types
import os

# pip install --upgrade --user google-genai

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)
model = "gemini-2.0-flash-001"
# model = "gemini-2.0-flash-lite"

def ask_gemini(prompt):
    generate_content_config = types.GenerateContentConfig(
        temperature=0.1,
        top_p=0.9,
        top_k=40,
        max_output_tokens=4096,
        response_mime_type="text/plain",
    )
    response = client.models.generate_content(
        model=model,
        contents=[
            prompt,
        ],
        config=generate_content_config,
    )
    response = response.text
    response = response.strip()
    return response

if __name__ == '__main__':
    prompt = "Who are you?"
    response = ask_gemini(prompt)
    print(response)
