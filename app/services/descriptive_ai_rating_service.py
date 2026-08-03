import os
import json
from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL_NAME = "gemini-1.5-pro"


def rate_descriptive_section(strengths: str, areas_of_improvement: str, suggestions_recommendations: str) -> dict:
    prompt = f"""You are rating the descriptive section of a teacher classroom observation. The observer wrote these three notes:

STRENGTHS:
{strengths}

AREAS OF IMPROVEMENT:
{areas_of_improvement}

SUGGESTIONS / RECOMMENDATIONS:
{suggestions_recommendations}

Read all three together as one whole submission to understand context, then score each of the three individually on a scale of 0 to 3:
0 = missing, blank, or not meaningful
1 = vague or generic, lacks specifics
2 = specific and relevant, reasonably detailed
3 = specific, detailed, and clearly actionable/evidence-based

Respond with ONLY valid JSON, no markdown fences, no preamble, in this exact shape:
{{"strengths_score": <0-3 number>, "improvement_score": <0-3 number>, "suggestions_score": <0-3 number>, "rationale": "<one sentence explaining the scores>"}}"""

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text.strip()
    raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        raise ValueError(f"AI rating response was not valid JSON: {raw_text}")

    for key in ("strengths_score", "improvement_score", "suggestions_score"):
        parsed[key] = max(0, min(3, float(parsed[key])))  # clamp in case the model drifts outside 0-3

    parsed["total_score"] = parsed["strengths_score"] + parsed["improvement_score"] + parsed["suggestions_score"]
    return parsed