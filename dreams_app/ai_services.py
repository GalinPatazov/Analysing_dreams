import base64
import re
import requests
from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Words/phrases that often trigger image policy blocks.
# We "soft redact" them to reduce false failures.
_BLOCKLIST_PATTERNS = [
    r"\b(suicide|self[-\s]?harm|kill myself|cut(ting)?)\b",
    r"\b(rape|sexual assault|incest)\b",
    r"\b(nude|nudity|porn|explicit)\b",
    r"\b(blood|gore|guts|dismember|decapitat)\w*\b",
    r"\b(child|minor|underage)\b",
]

def analyze_dream(dream_text: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a dream analysis assistant. Be helpful and non-judgmental. "
                        "Write your analysis in 3-4 short paragraphs. "
                        "Always finish every sentence completely — never leave a thought unfinished. "
                        "Keep the total response under 220 words."
                    )
                },
                {"role": "user", "content": dream_text},
            ],
            max_tokens=350,
        )
        return response.choices[0].message.content
    except Exception as e:
        print("AI TEXT ERROR:", e)
        return "AI analysis is temporarily unavailable."


def _sanitize_dream_text(text: str) -> str:
    t = (text or "").strip()

    # Remove obvious instruction/prompt-injection style lines (helps stability)
    t = re.sub(r"(?is)\b(ignore|bypass|override)\b.*", "", t)

    # Soft redact sensitive terms
    for pat in _BLOCKLIST_PATTERNS:
        t = re.sub(pat, "[redacted]", t, flags=re.IGNORECASE)

    # Keep prompts from being too long
    if len(t) > 800:
        t = t[:800] + "…"
    return t


def _image_bytes_from_response(response):
    image = response.data[0]
    if getattr(image, "b64_json", None):
        return base64.b64decode(image.b64_json)
    if getattr(image, "url", None):
        return requests.get(image.url, timeout=30).content
    return None


def generate_dream_image(dream_text: str, dream_title: str = ""):
    """
    1) Ask GPT to convert the dream into a safe visual prompt (keeps meaning, removes disallowed content)
    2) Generate image from that prompt
    3) If dream-based generation fails, return None instead of showing an unrelated generic image
    """
    if not settings.OPENAI_API_KEY:
        return None

    sanitized_text = _sanitize_dream_text(dream_text)
    title = (dream_title or "").strip()
    dream_context = f"Title: {title}\nDream: {sanitized_text}" if title else sanitized_text

    # Step A: make a safe visual prompt using GPT (very important)
    try:
        prompt_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You convert dream descriptions into SAFE image prompts.\n"
                        "Rules:\n"
                        "- Ground the image in the specific dream. Keep the main place, objects, actions, mood, and symbols.\n"
                        "- Do not replace the dream with a generic fantasy scene.\n"
                        "- If a detail is unsafe, replace only that detail with a symbolic, non-graphic equivalent.\n"
                        "- Remove/avoid: nudity, sexual content, minors, self-harm, graphic violence, blood/gore.\n"
                        "- Do NOT include real people, celebrities, or identifying details.\n"
                        "- Do NOT include any text to be written in the image.\n"
                        "- Output ONLY the final image prompt, 2-3 sentences."
                    )
                },
                {"role": "user", "content": dream_context}
            ],
            max_tokens=350,
        )
        safe_visual_prompt = prompt_resp.choices[0].message.content.strip()
    except Exception as e:
        print("PROMPT REWRITE ERROR:", e)
        safe_visual_prompt = None

    # Add a safety wrapper always
    style = (
        "Draw a surreal dreamlike digital illustration, PG-13, no text, no captions, "
        "no logos, no watermarks, no nudity, no blood or injuries, do not depict real people. "
        "The image must clearly include the concrete visual details from the dream, not a generic dreamscape."
    )
    if safe_visual_prompt:
        final_prompt = f"{style}\nScene: {safe_visual_prompt}"
    else:
        # If rewrite failed, fallback to a mild wrapper of the original
        final_prompt = f"{style}\nScene: {dream_context[:700]}"

    # Step B: Try to generate using rewritten prompt
    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=final_prompt,
            size="1024x1024",
            quality="medium",
            n=1,
        )
        return _image_bytes_from_response(response)

    except Exception as e:
        print("AI IMAGE ERROR (gpt-image-1):", e)

        # Compatibility fallback for accounts that cannot use GPT Image yet.
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=final_prompt,
                size="1024x1024",
                n=1,
            )
            return _image_bytes_from_response(response)
        except Exception as e2:
            print("AI IMAGE ERROR (dall-e-3):", e2)
            return None
