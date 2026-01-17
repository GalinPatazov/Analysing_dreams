from openai import OpenAI
from django.conf import settings
import requests

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def analyze_dream(dream_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a dream analysis assistant."},
                {"role": "user", "content": dream_text}
            ],
            max_tokens=250
        )
        return response.choices[0].message.content
    except Exception as e:
        print("AI TEXT ERROR:", e)
        return "AI analysis is temporarily unavailable."

def generate_dream_image(dream_text):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"A surrealistic digital art depiction of this dream: {dream_text}",
            size="1024x1024",
            n=1,
        )
        image_url = response.data[0].url
        # Download the image content
        img_data = requests.get(image_url).content
        return img_data
    except Exception as e:
        print("AI IMAGE ERROR:", e)
        return None