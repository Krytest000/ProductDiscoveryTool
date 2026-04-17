import os
import anthropic

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def analyze_pain_points(reviews: list[dict]) -> list[dict]:
    """
    Send cleaned reviews to Claude and get back structured pain point categories.

    Returns a list of dicts:
        [{"category": str, "description": str, "count": int, "quotes": [str, ...]}, ...]
    """
    if not reviews:
        return []

    texts = "\n---\n".join(
        f"[Rating: {r['rating']}★] {r['text']}" for r in reviews[:200]
    )

    prompt = f"""You are a product analyst. Below are user reviews of a mobile app.

Identify the TOP 5 most common pain points. For each:
1. Give it a short category name (3–5 words)
2. Write one sentence describing the pattern
3. Estimate how many of the reviews mention it (as a number)
4. Pick 2–3 verbatim short quotes that best illustrate it

Respond ONLY with valid JSON in this exact format:
[
  {{
    "category": "...",
    "description": "...",
    "count": 12,
    "quotes": ["...", "..."]
  }}
]

Reviews:
{texts}"""

    client = _get_client()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
