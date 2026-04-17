import os
import anthropic

PERSONAS = [
    {
        "id": "natalia",
        "name": "Natalia",
        "age": 24,
        "city": "Poznań",
        "role": "Marketing specialist / student lifestyle",
        "apps": ["BLIK", "Revolut", "mBank"],
        "archetype": "Impatient Mobile User",
        "traits": [
            "Fast actions, very low patience",
            '"If it takes more than 5 seconds, I get annoyed"',
            "Skips steps, acts quickly",
            "High trust for popular apps, doesn't read details",
        ],
    },
    {
        "id": "kacper",
        "name": "Kacper",
        "age": 29,
        "city": "Warsaw",
        "role": "Frontend developer",
        "apps": ["Revolut", "Zen", "Apple Pay"],
        "archetype": "Analytical Early Adopter",
        "traits": [
            "Optimizes finances, tracks everything",
            "Notices inefficiencies",
            "Cares about fees, automation, integrations",
            "Low trust in institutions, high trust in tech",
        ],
    },
    {
        "id": "ola",
        "name": "Ola",
        "age": 22,
        "city": "Kraków",
        "role": "Student, active social life",
        "apps": ["BLIK", "Revolut"],
        "archetype": "Social Spender",
        "traits": [
            "Group payments, spontaneous spending",
            "Avoids awkward money situations",
            "Prefers simple split & request flows",
            "High trust if app is popular",
        ],
    },
    {
        "id": "michal",
        "name": "Michał",
        "age": 34,
        "city": "Wrocław",
        "role": "Logistics specialist",
        "apps": ["bank app", "BLIK"],
        "archetype": "Cautious User",
        "traits": [
            "Double-checks everything",
            "Needs clarity and confirmation",
            "Afraid of making mistakes",
            "Low trust, fear of fraud",
        ],
    },
    {
        "id": "karolina",
        "name": "Karolina",
        "age": 31,
        "city": "Gdańsk",
        "role": "Freelance graphic designer",
        "apps": ["Revolut", "PayPal", "bank apps"],
        "archetype": "Freelancer (Chaotic Finances)",
        "traits": [
            "Irregular income, multi-currency",
            "Struggles with organization",
            "Values flexibility and simplicity",
            "Trusts tools, less so institutions",
        ],
    },
]

PERSONA_MAP = {p["id"]: p for p in PERSONAS}

SIMULATION_INSTRUCTIONS = """You will simulate a specific user persona testing a product feature.

You MUST:
- Think independently as this persona
- Speak in first person
- Reflect their personality, habits, and limitations
- NOT behave like a UX expert
- Avoid generic answers — be specific, emotional, and sometimes imperfect
- Occasionally misunderstand things (real users do this)

For this persona, walk through the feature and respond in this exact format:

### Persona: {name} ({age}, {city}) — {archetype}

**Context:**
[Briefly describe where you are and what you're doing when you try this feature]

**What I do:**
[Numbered steps — walk through the flow as this persona]

**Thoughts & reactions:**
[Real-time thoughts, emotions, confusion, satisfaction]

**Frustrations:**
[Specific friction: UI, wording, timing, trust issues]

**Would I continue or quit?**
[Would you abandon the flow? When and why?]

**What would make it better (for me):**
[Suggestions that reflect this persona's personality — NOT generic UX advice]"""

SUMMARY_INSTRUCTIONS = """Based on the persona feedback above, write a concise summary in this format:

## Summary

### Common patterns across personas:
- [bullet points]

### Where personas react differently:
- [bullet points]

### Top 3 critical UX risks:
1. ...
2. ...
3. ..."""


def build_persona_prompt(persona: dict, feature_description: str) -> str:
    traits_text = "\n".join(f"  - {t}" for t in persona["traits"])
    apps_text = ", ".join(persona["apps"])
    instructions = SIMULATION_INSTRUCTIONS.format(
        name=persona["name"],
        age=persona["age"],
        city=persona["city"],
        archetype=persona["archetype"],
    )
    return f"""{instructions}

---

**Your persona:**
- Name: {persona["name"]}, {persona["age"]}, {persona["city"]}
- Role: {persona["role"]}
- Apps used: {apps_text}
- Archetype: {persona["archetype"]}
- Key traits:
{traits_text}

---

**Feature to evaluate:**
{feature_description}"""


_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def simulate_persona(persona: dict, feature_description: str) -> str:
    prompt = build_persona_prompt(persona, feature_description)
    client = _get_client()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def generate_summary(all_feedback: list[dict]) -> str:
    combined = "\n\n---\n\n".join(
        f"**{fb['name']}:** {fb['response']}" for fb in all_feedback
    )
    prompt = f"{combined}\n\n---\n\n{SUMMARY_INSTRUCTIONS}"
    client = _get_client()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()
