from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request
)

from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash
)
from .gemini_generator import (
    generate_workout_gemini
)
from .models import User, WorkoutPlan
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "FitBuddy"
        }
    )


# ---------------------------------------------------------
# GENERATE WORKOUT
# ---------------------------------------------------------

@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(
    request: Request,

    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),

    db: Session = Depends(get_db)
):
    # Validate using Pydantic
    try:
        user_data = UserInput(
            user_id=user_id.strip(),
            name=name.strip(),
            age=age,
            weight=weight,
            goal=goal.strip(),
            intensity=intensity.lower().strip()
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "title": "FitBuddy",
                "error": f"Invalid input: {exc}"
            },
            status_code=400
        )

    # -----------------------------------------------------
    # Generate AI content
    # -----------------------------------------------------

    workout_plan = generate_workout_gemini(
        name=user_data.name,
        age=user_data.age,
        weight=user_data.weight,
        goal=user_data.goal,
        intensity=user_data.intensity
    )

    nutrition_tip = generate_nutrition_tip_with_flash(
        user_data.goal
    )

    # -----------------------------------------------------
    # Save/update user
    # -----------------------------------------------------

    user = db.execute(
        select(User).where(
            User.user_id == user_data.user_id
        )
    ).scalar_one_or_none()

    if user:
        user.name = user_data.name
        user.age = user_data.age
        user.weight = user_data.weight
        user.goal = user_data.goal
        user.intensity = user_data.intensity
    else:
        user = User(
            user_id=user_data.user_id,
            name=user_data.name,
            age=user_data.age,
            weight=user_data.weight,
            goal=user_data.goal,
            intensity=user_data.intensity
        )

        db.add(user)

    db.commit()

    # -----------------------------------------------------
    # Save plan
    # -----------------------------------------------------

    plan = db.execute(
        select(WorkoutPlan)
        .where(
            WorkoutPlan.user_id == user_data.user_id
        )
    ).scalar_one_or_none()

    if plan:
        plan.original_plan = workout_plan
        plan.updated_plan = None
        plan.nutrition_tip = nutrition_tip
        plan.feedback = None
        plan.updated_at = None
    else:
        plan = WorkoutPlan(
            user_id=user_data.user_id,
            original_plan=workout_plan,
            nutrition_tip=nutrition_tip
        )

        db.add(plan)

    db.commit()

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "title": "Your FitBuddy Plan",
            "user": user,
            "plan": plan,
            "message": "Your 7-day workout plan has been generated successfully."
        }
    )


# ---------------------------------------------------------
# FEEDBACK / UPDATE PLAN
# ---------------------------------------------------------

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(
    request: Request,

    user_id: str = Form(...),
    feedback: str = Form(...),

    db: Session = Depends(get_db)
):
    try:
        feedback_data = FeedbackRequest(
            user_id=user_id.strip(),
            feedback=feedback.strip()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid feedback: {exc}"
        )

    user = db.execute(
        select(User).where(
            User.user_id == feedback_data.user_id
        )
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    plan = db.execute(
        select(WorkoutPlan)
        .where(
            WorkoutPlan.user_id == feedback_data.user_id
        )
    ).scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Workout plan not found."
        )

    # Use the latest version as the basis for the next update.
    current_plan = (
        plan.updated_plan
        if plan.updated_plan
        else plan.original_plan
    )

    new_plan = update_workout_plan(
        original_plan=current_plan,
        feedback=feedback_data.feedback
    )

    plan.updated_plan = new_plan
    plan.feedback = feedback_data.feedback
    plan.updated_at = datetime.utcnow()

    db.commit()

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "title": "Updated FitBuddy Plan",
            "user": user,
            "plan": plan,
            "message": "Your workout plan has been updated based on your feedback."
        }
    )


# ---------------------------------------------------------
# VIEW ALL USERS
# ---------------------------------------------------------

@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db)
):
    users = db.execute(
        select(User).order_by(
            User.created_at.desc()
        )
    ).scalars().all()

    user_records = []

    for user in users:

        plan = db.execute(
            select(WorkoutPlan)
            .where(
                WorkoutPlan.user_id == user.user_id
            )
        ).scalar_one_or_none()

        user_records.append(
            {
                "user": user,
                "plan": plan
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "title": "All Users",
            "records": user_records
        }
    )


# ---------------------------------------------------------
# API - GENERATE WORKOUT
# ---------------------------------------------------------

@router.post(
    "/api/generate-workout"
)
def api_generate_workout(
    user_data: UserInput,
    db: Session = Depends(get_db)
):
    workout_plan = generate_workout_gemini(
        name=user_data.name,
        age=user_data.age,
        weight=user_data.weight,
        goal=user_data.goal,
        intensity=user_data.intensity
    )

    nutrition_tip = generate_nutrition_tip_with_flash(
        user_data.goal
    )

    user = db.execute(
        select(User).where(
            User.user_id == user_data.user_id
        )
    ).scalar_one_or_none()

    if user:
        user.name = user_data.name
        user.age = user_data.age
        user.weight = user_data.weight
        user.goal = user_data.goal
        user.intensity = user_data.intensity
    else:
        user = User(
            user_id=user_data.user_id,
            name=user_data.name,
            age=user_data.age,
            weight=user_data.weight,
            goal=user_data.goal,
            intensity=user_data.intensity
        )

        db.add(user)

    db.commit()

    plan = db.execute(
        select(WorkoutPlan)
        .where(
            WorkoutPlan.user_id == user_data.user_id
        )
    ).scalar_one_or_none()

    if plan:
        plan.original_plan = workout_plan
        plan.updated_plan = None
        plan.nutrition_tip = nutrition_tip
        plan.feedback = None
        plan.updated_at = None
    else:
        plan = WorkoutPlan(
            user_id=user_data.user_id,
            original_plan=workout_plan,
            nutrition_tip=nutrition_tip
        )

        db.add(plan)

    db.commit()

    return {
        "message": "Workout plan generated successfully.",
        "user_id": user_data.user_id,
        "workout_plan": workout_plan,
        "nutrition_tip": nutrition_tip
    }


# ---------------------------------------------------------
# API - NUTRITION TIP
# ---------------------------------------------------------

@router.get(
    "/api/nutrition-tip"
)
def api_nutrition_tip(
    goal: str
):
    return {
        "goal": goal,
        "nutrition_tip": generate_nutrition_tip_with_flash(
            goal
        )
    }


# ---------------------------------------------------------
# API - UPDATE PLAN
# ---------------------------------------------------------

@router.post(
    "/api/update-plan/{user_id}"
)
def api_update_plan(
    user_id: str,
    feedback: str = Form(...),
    db: Session = Depends(get_db)
):
    plan = db.execute(
        select(WorkoutPlan)
        .where(
            WorkoutPlan.user_id == user_id
        )
    ).scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Workout plan not found."
        )

    current_plan = (
        plan.updated_plan
        if plan.updated_plan
        else plan.original_plan
    )

    updated = update_workout_plan(
        current_plan,
        feedback
    )

    plan.updated_plan = updated
    plan.feedback = feedback
    plan.updated_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Workout plan updated successfully.",
        "user_id": user_id,
        "updated_plan": updated
    }


# ---------------------------------------------------------
# API - GET USER
# ---------------------------------------------------------

@router.get(
    "/api/users/{user_id}"
)
def api_get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(
            User.user_id == user_id
        )
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    plan = db.execute(
        select(WorkoutPlan)
        .where(
            WorkoutPlan.user_id == user_id
        )
    ).scalar_one_or_none()

    return {
        "user": {
            "user_id": user.user_id,
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity
        },
        "plan": {
            "original_plan": plan.original_plan
            if plan else None,
            "updated_plan": plan.updated_plan
            if plan else None,
            "nutrition_tip": plan.nutrition_tip
            if plan else None,
            "feedback": plan.feedback
            if plan else None
        }
        if plan else None
    }