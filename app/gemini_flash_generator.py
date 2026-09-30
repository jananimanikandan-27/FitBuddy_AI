from google import genai

from .config import (
    GEMINI_API_KEY,
    GEMINI_TIP_MODEL
)


def _get_client():
    if not GEMINI_API_KEY:
        return None

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


def generate_demo_tip(goal: str) -> str:
    """
    Local fallback nutrition/recovery tip.
    """

    goal_lower = goal.lower()

    if "loss" in goal_lower or "fat" in goal_lower:
        return (
            "For a fat-loss goal, focus on balanced meals with "
            "adequate protein, vegetables, whole-food carbohydrates "
            "and healthy fats. Maintain a sustainable calorie deficit "
            "rather than using extreme restriction."
        )

    if "muscle" in goal_lower or "gain" in goal_lower:
        return (
            "For muscle gain, include a protein-rich food in your "
            "regular meals and combine it with sufficient calories, "
            "carbohydrates, hydration and recovery."
        )

    return (
        "For general wellness, focus on balanced meals, adequate "
        "protein, fruits and vegetables, hydration and consistent sleep."
    )


def generate_nutrition_tip_with_flash(goal: str) -> str:
    """
    Generate a concise nutrition or recovery tip with Gemini.
    """

    client = _get_client()

    if client is None:
        return generate_demo_tip(goal)

    prompt = f"""
You are FitBuddy's nutrition and recovery assistant.

The user's fitness goal is:
{goal}

Give ONE concise, practical nutrition or recovery tip.

Requirements:
- 80-120 words maximum.
- Use simple language.
- Make it relevant to the fitness goal.
- Include a practical example where useful.
- Do not prescribe medical treatment.
- Do not recommend dangerous diets.
- Do not promise guaranteed results.
- Focus on sustainable healthy habits.

Return only the tip.
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_TIP_MODEL,
            contents=prompt
        )

        text = getattr(response, "text", None)

        if text:
            return text.strip()

        return generate_demo_tip(goal)

    except Exception as exc:
        return (
            generate_demo_tip(goal)
            + "\n\n"
            + f"(AI tip unavailable: {exc})"
        )