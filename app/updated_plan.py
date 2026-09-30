from google import genai

from .config import (
    GEMINI_API_KEY,
    GEMINI_WORKOUT_MODEL
)


def _get_client():
    if not GEMINI_API_KEY:
        return None

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


def update_demo_plan(
    original_plan: str,
    feedback: str
) -> str:
    """
    Basic local fallback when Gemini is unavailable.
    """

    return f"""
UPDATED FITBUDDY PLAN

The following feedback was received:

{feedback}

The original plan is retained below.

-----------------------------
ORIGINAL PLAN
-----------------------------

{original_plan}

-----------------------------
LOCAL UPDATE
-----------------------------

Suggested adjustment based on your feedback:

- Review the requested change before starting.
- Keep training intensity manageable.
- Add recovery when needed.
- Maintain correct exercise technique.
- Progress gradually instead of making sudden increases.
- Keep at least one recovery/rest day when appropriate.

This local update is a demonstration because the Gemini API
is not currently configured.
"""


def update_workout_plan(
    original_plan: str,
    feedback: str
) -> str:
    """
    Use Gemini to revise the original workout plan based
    on user feedback.
    """

    client = _get_client()

    if client is None:
        return update_demo_plan(
            original_plan,
            feedback
        )

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Below is the user's existing 7-day workout plan.

---------------- ORIGINAL PLAN ----------------

{original_plan}

---------------- USER FEEDBACK ----------------

{feedback}

-------------------------------------------------

Create an updated version of the workout plan.

Rules:

1. Preserve the useful structure of the original plan.
2. Apply the user's feedback where it is reasonable.
3. Keep exactly 7 days.
4. Maintain warm-up, workout and cooldown/recovery sections.
5. Include sets, repetitions or durations.
6. Add rest days when the feedback requests additional recovery.
7. Add cardio when the feedback requests more cardio.
8. Do not recommend dangerous training.
9. Do not guarantee results.
10. Keep the revised plan practical.
11. Clearly indicate what has changed.
12. End with safety/recovery notes.

Return the complete updated 7-day plan.
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_WORKOUT_MODEL,
            contents=prompt
        )

        text = getattr(response, "text", None)

        if text:
            return text.strip()

        return update_demo_plan(
            original_plan,
            feedback
        )

    except Exception as exc:
        return (
            "Gemini could not update the plan.\n\n"
            f"Technical message: {exc}\n\n"
            + update_demo_plan(
                original_plan,
                feedback
            )
        )