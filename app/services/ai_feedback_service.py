# import os
# from google import genai
# from app.core.config import settings

# client = genai.Client(api_key=settings.GEMINI_API_KEY)

# # Use gemini-1.5-pro for feedback quality/cost balance.
# # Swap to gemini-1.0-pro if you're generating hundreds of these a month and want lower cost.
# MODEL_NAME = "gemini-1.5-pro"


# def generate_ai_feedback(mcq_summary: str, remarks_summary: str) -> str:
#     """
#     mcq_summary: plain text like "Lesson planning: 82%\nClassroom management: 65%\n..."
#     remarks_summary: concatenated general_observation + remarks_suggestions text from the month's observations
#     """
#     prompt = f"""You are writing a short performance feedback summary for a teacher's monthly review.

# MCQ score breakdown for this month (percentage of maximum marks per category):
# {mcq_summary}

# Observer remarks collected this month:
# {remarks_summary}

# Write a feedback summary that is STRICTLY between 80 and 100 words. It must:
# - Summarize the teacher's strong points based on the data above
# - Identify specific, actionable points of improvement the teacher can act on
# - Be written in a constructive, professional tone addressed to the teacher
# - Not invent facts not supported by the data above

# Return only the feedback text, no headings, no preamble."""

#     response = client.messages.create(
#         model=MODEL_NAME,
#         max_tokens=300,
#         messages=[{"role": "user", "content": prompt}],
#     )

#     feedback_text = response.content[0].text.strip()
#     return feedback_text

# def generate_ai_feedback_with_retry(mcq_summary: str, remarks_summary: str, max_attempts: int = 2) -> str:
#     for _ in range(max_attempts):
#         feedback = generate_ai_feedback(mcq_summary, remarks_summary)
#         word_count = len(feedback.split())
#         if 75 <= word_count <= 105:  # small buffer around the 80-100 target
#             return feedback
#     return feedback  # return last attempt even if slightly off, rather than fail the whole report


import time
from typing import Union, List, Dict, Any
from google import genai
from google.genai.errors import ServerError, ClientError
from app.core.config import settings

# Initialize Gemini client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

PRIMARY_MODEL = "gemini-3.6-flash"
FALLBACK_MODEL = "gemini-2.5-pro"


def build_structured_mcq_summary(mcq_items: Union[str, List[Union[Dict[str, Any], Any]]]) -> str:
    """
    Pre-processes raw MCQ response data into structured performance tiers.
    """
    if isinstance(mcq_items, str):
        return mcq_items

    strengths = []
    moderate = []
    needs_improvement = []

    for item in mcq_items:
        if isinstance(item, dict):
            text = item.get("question_text", "")
            score = item.get("response_percentage", 0)
        else:
            text = getattr(item, "question_text", "")
            score = getattr(item, "response_percentage", 0)

        if score >= 85:
            strengths.append(f"- {text} (Score: {score}%)")
        elif score >= 50:
            moderate.append(f"- {text} (Score: {score}%)")
        else:
            needs_improvement.append(f"- {text} (CRITICAL LOW Score: {score}%)")

    lines = []
    if strengths:
        lines.append("TOP STRENGTHS (85%+ ONLY):\n" + "\n".join(strengths))
    else:
        lines.append("TOP STRENGTHS (85%+ ONLY):\n- None identified this month.")

    if moderate:
        lines.append("MODERATE / AVERAGE PERFORMANCE (50% - 84%):\n" + "\n".join(moderate))

    if needs_improvement:
        lines.append("SERIOUS WEAKNESSES / NEEDS IMMEDIATE IMPROVEMENT (Below 50%):\n" + "\n".join(needs_improvement))

    return "\n\n".join(lines)


def generate_ai_feedback(mcq_summary: Union[str, List[Any]], remarks_summary: str) -> str:
    """
    Generates structured, factual teacher review feedback strictly using
    pre-processed performance tiers and observer remarks.
    """
    formatted_mcq = build_structured_mcq_summary(mcq_summary)

    prompt = f"""You are writing a short, factual performance feedback summary for a teacher's monthly review.

MCQ EVALUATION DATA:
{formatted_mcq}

OBSERVER REMARKS:
{remarks_summary}

STRICT CONSTRAINTS (VIOLATIONS ARE UNACCEPTABLE):
1. ACCURACY RULE FOR PREPARATION & LOW SCORES: 
   - Look at the score for "Enters fully prepared for the class" and other items.
   - If a category is listed under 'SERIOUS WEAKNESSES' (e.g. 25%), you MUST NOT praise it. NEVER say "excellent preparation", "great prep", or "well prepared" if preparation scored below 85%.
   - You MUST explicitly call out low-scoring items (like coming to class unprepared) as primary areas needing improvement.
2. NO GENERIC FLATTERY:
   - Do NOT use fluffy words like "excellent", "outstanding", or "exceptional" unless referring specifically to a 100% item.
3. PRAISE RULE: Restrict praise ONLY to items under 'TOP STRENGTHS (85%+ ONLY)'.
4. IMPROVEMENT RULE: Focus constructive feedback directly on items under 'SERIOUS WEAKNESSES' and negative observer remarks.
5. WORD COUNT: STRICTLY between 80 and 100 words.
6. FORMAT: Plain text only. Direct tone addressed to the teacher ("You..."). No headings, no preamble.

Write the feedback summary:"""

    models_to_try = [PRIMARY_MODEL, FALLBACK_MODEL]

    for model in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return response.text.strip()
            except ServerError as e:
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    time.sleep(2)
                    continue
                raise e
            except ClientError as e:
                raise e

    raise RuntimeError("All configured Gemini models are currently experiencing high demand. Please try again in a moment.")


def generate_ai_feedback_with_retry(mcq_summary: Union[str, List[Any]], remarks_summary: str, max_attempts: int = 2) -> str:
    for _ in range(max_attempts):
        feedback = generate_ai_feedback(mcq_summary, remarks_summary)
        word_count = len(feedback.split())
        if 75 <= word_count <= 105:
            return feedback
    return feedback