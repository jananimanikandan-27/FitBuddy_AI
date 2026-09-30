from google import genai

from .config import (
    GEMINI_API_KEY,
    GEMINI_WORKOUT_MODEL
)


def _get_client():
    """
    Create Gemini client.

    Returns None when no API key is configured.
    """
    if not GEMINI_API_KEY:
        return None

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


def generate_demo_workout(
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str
) -> str:
    """
    Local fallback plan used when Gemini API is not configured.
    """

    return f"""
FITBUDDY - SAMPLE 7-DAY FITNESS PLAN

User:
Name: {name}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Intensity: {intensity}

IMPORTANT:
This is a demonstration plan because a Gemini API key
has not been configured yet.

DAY 1 - FULL BODY
Warm-up:
- 5-10 minutes brisk walking
- Arm circles
- Bodyweight squats

Main Workout:
- Bodyweight Squats: 3 x 12
- Push-ups: 3 x 8-12
- Dumbbell Rows: 3 x 10
- Glute Bridges: 3 x 12
- Plank: 3 x 30 seconds

Cooldown:
- 5 minutes light stretching

DAY 2 - CARDIO + CORE
Warm-up:
- 5 minutes walking

Main Workout:
- Brisk Walk/Jog: 20-30 minutes
- Mountain Climbers: 3 x 20
- Dead Bug: 3 x 10
- Plank: 3 x 30 seconds

Cooldown:
- Light stretching

DAY 3 - UPPER BODY
Warm-up:
- 5-10 minutes

Main Workout:
- Push-ups: 3 x 8-12
- Dumbbell Shoulder Press: 3 x 10
- Dumbbell Row: 3 x 10
- Biceps Curl: 3 x 12
- Triceps Extension: 3 x 12

Cooldown:
- Shoulder and arm stretches

DAY 4 - ACTIVE RECOVERY
- 20-30 minutes easy walking
- Mobility exercises
- Light stretching

DAY 5 - LOWER BODY
Warm-up:
- 5-10 minutes

Main Workout:
- Squats: 3 x 12
- Lunges: 3 x 10 each leg
- Romanian Deadlift: 3 x 10
- Calf Raises: 3 x 15
- Glute Bridge: 3 x 12

Cooldown:
- Lower-body stretching

DAY 6 - CARDIO + CORE
Warm-up:
- 5 minutes walking

Main Workout:
- Jogging/Walking: 25-30 minutes
- Bicycle Crunches: 3 x 15
- Leg Raises: 3 x 10
- Plank: 3 x 30-45 seconds

Cooldown:
- Light stretching

DAY 7 - REST AND RECOVERY
- Rest
- Gentle walking if desired
- Mobility
- Adequate sleep

GENERAL GUIDELINES
- Start at a manageable intensity.
- Maintain proper exercise technique.
- Increase difficulty gradually.
- Stay hydrated.
- Prioritize balanced meals and adequate protein.

This is general fitness information and is not medical advice.
"""


def generate_workout_gemini(
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str
) -> str:
    """
    Generate a personalized 7-day workout plan using Gemini.
    """

    client = _get_client()

    if client is None:
        return generate_demo_workout(
            name,
            age,
            weight,
            goal,
            intensity
        )

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a personalized 7-day fitness plan.

User information:
Name: {name}
Age: {age}
Weight: {weight} kg
Fitness goal: {goal}
Workout intensity: {intensity}

Requirements:

1. Generate exactly 7 days.
2. Clearly label Day 1 through Day 7.
3. Include a warm-up for training days.
4. Include the main workout.
5. Include exercise names.
6. Include sets and repetitions or duration.
7. Include reasonable rest intervals.
8. Include cooldown or recovery guidance.
9. Include rest or active recovery where appropriate.
10. Adapt the difficulty to the requested intensity.
11. Make the plan appropriate for the stated fitness goal.
12. Do not promise medical or guaranteed results.
13. Avoid dangerous extreme training.
14. Keep the plan easy to understand.
15. Do not ask the user questions.
16. End with general safety guidance.

Format:

DAY 1 - [FOCUS]

Warm-up:
...

Main Workout:
1. Exercise - sets x reps
2. Exercise - sets x reps

Rest:
...

Cooldown:
...

Repeat the same structure through DAY 7.

At the end include:

IMPORTANT NOTES:
- Progressive overload
- Recovery
- Hydration
- Balanced nutrition
- Proper exercise technique

The response should be plain text and easy to display on a web page.
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_WORKOUT_MODEL,
            contents=prompt
        )

        text = getattr(response, "text", None)

        if text:
            return text.strip()

        return generate_demo_workout(
            name,
            age,
            weight,
            goal,
            intensity
        )

    except Exception as exc:
        return (
            "Gemini could not generate the plan right now.\n\n"
            f"Technical message: {exc}\n\n"
            "A local demonstration plan is shown below.\n\n"
            + generate_demo_workout(
                name,
                age,
                weight,
                goal,
                intensity
            )
        )