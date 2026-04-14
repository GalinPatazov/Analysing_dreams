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
                {"role": "system", "content": "You are a dream analysis assistant. Be helpful and non-judgmental."},
                {"role": "user", "content": dream_text},
            ],
            max_tokens=250,
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


def generate_dream_image(dream_text: str):
    """
    1) Ask GPT to convert the dream into a safe visual prompt (keeps meaning, removes disallowed content)
    2) Generate image from that prompt
    3) If still blocked, use a generic fallback
    """
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
                        "- Keep the dream's main symbols, mood, setting.\n"
                        "- Remove/avoid: nudity, sexual content, minors, self-harm, graphic violence, blood/gore.\n"
                        "- Do NOT include real people, celebrities, or identifying details.\n"
                        "- Do NOT include any text to be written in the image.\n"
                        "- Output ONLY the final image prompt, 2-4 sentences."
                    )
                },
                {"role": "user", "content": dream_text}
            ],
            max_tokens=300,
        )
        safe_visual_prompt = prompt_resp.choices[0].message.content.strip()
    except Exception as e:
        print("PROMPT REWRITE ERROR:", e)
        safe_visual_prompt = None

    # Add a safety wrapper always
    if safe_visual_prompt:
        final_prompt = (
            "Surreal dreamlike digital illustration, PG-13. "
            "No text, no captions, no logos, no watermarks. "
            "No nudity. No blood or injuries. "
            "Do not depict real people.\n"
            f"Scene: {safe_visual_prompt}"
        )
    else:
        # If rewrite failed, fallback to a mild wrapper of the original
        final_prompt = (
            "Surreal dreamlike digital illustration, PG-13. "
            "No text, no captions, no logos. No nudity. No gore. "
            "Do not depict real people.\n"
            f"Scene: {dream_text[:600]}"
        )

    # Step B: Try to generate using rewritten prompt
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=final_prompt,
            size="1024x1024",
            n=1,
        )
        image_url = response.data[0].url
        return requests.get(image_url, timeout=30).content

    except Exception as e:
        print("AI IMAGE ERROR (dream-based attempt):", e)

        # Step C: Only now use generic fallback (last resort)
        fallback_prompt = (
            "Surreal abstract dreamscape digital illustration: floating islands, moonlit clouds, "
            "impossible architecture, soft fog, cinematic lighting, highly detailed. "
            "No people. No text. No logos. PG-13."
        )
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=fallback_prompt,
                size="1024x1024",
                n=1,
            )
            image_url = response.data[0].url
            return requests.get(image_url, timeout=30).content
        except Exception as e2:
            print("AI IMAGE ERROR (fallback):", e2)
            return None