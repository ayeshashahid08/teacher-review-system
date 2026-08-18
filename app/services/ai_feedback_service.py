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
from google import genai
from google.genai.errors import ServerError, ClientError
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Primary model and fallback model during high-demand spikes
PRIMARY_MODEL = "gemini-3.6-flash"
FALLBACK_MODEL = "gemini-2.5-pro"


def generate_ai_feedback(mcq_summary: str, remarks_summary: str) -> str:
    prompt = f"""You are writing a short performance feedback summary for a teacher's monthly review.

MCQ score breakdown for this month (percentage of maximum marks per category):
{mcq_summary}

Observer remarks collected this month:
{remarks_summary}

Write a feedback summary that is STRICTLY between 80 and 100 words. It must:
- Summarize the teacher's strong points based on the data above
- Identify specific, actionable points of improvement the teacher can act on
- Be written in a constructive, professional tone addressed to the teacher
- Not invent facts not supported by the data above

Return only the feedback text, no headings, no preamble."""

    models_to_try = [PRIMARY_MODEL, FALLBACK_MODEL]

    for model in models_to_try:
        # Retry up to 2 times per model if high demand hits
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return response.text.strip()
            except ServerError as e:
                # Catch 503 Overloaded errors and wait briefly before retrying/falling back
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    time.sleep(2)
                    continue
                raise e
            except ClientError as e:
                raise e

    raise RuntimeError("All configured Gemini models are currently experiencing high demand. Please try again in a moment.")


def generate_ai_feedback_with_retry(mcq_summary: str, remarks_summary: str, max_attempts: int = 2) -> str:
    for _ in range(max_attempts):
        feedback = generate_ai_feedback(mcq_summary, remarks_summary)
        word_count = len(feedback.split())
        if 75 <= word_count <= 105:
            return feedback
    return feedback