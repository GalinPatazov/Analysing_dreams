from openai import OpenAI

client = OpenAI()

def analyze_dream(dream_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a dream analysis assistant."},
                {"role": "user", "content": dream_text},
            ],
            max_tokens=200,
        )

        return response.choices[0].message.content

    except Exception:
        return "AI analysis is currently unavailable. Please try again later."
