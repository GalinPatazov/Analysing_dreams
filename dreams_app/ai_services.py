from django.conf import settings
import openai

# Use environment variable from settings
openai.api_key = settings.OPENAI_API_KEY

def analyze_dream(dream_text):
    """Generate AI analysis text using OpenAI"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a dream analysis assistant."},
                {"role": "user", "content": dream_text}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback if API fails
        return f"Mock analysis (AI unavailable): {dream_text[:50]}..."

def generate_dream_image(dream_text):
    try:
        response = openai.images.generate(
            model="gpt-image-1",
            prompt=dream_text,
            size="auto"
        )
        return response.data[0].url
    except Exception:
        return "/static/dreams_app/images/placeholder.png"

