# FitBuddy – AI Fitness Plan Generator

FitBuddy is an AI-powered fitness planning web application.

It generates personalized 7-day workout plans and nutrition/recovery tips.

## Technologies

- Python
- FastAPI
- Jinja2
- SQLAlchemy
- SQLite
- Google Gemini API
- HTML
- CSS

## Features

### 1. Personalized Workout Plan

Users enter:

- Name
- User ID
- Age
- Weight
- Fitness Goal
- Workout Intensity

FitBuddy generates a 7-day plan.

### 2. Nutrition Tip

FitBuddy generates a concise nutrition or recovery tip based on the user's goal.

### 3. Feedback

Users can submit feedback such as:

"Add more cardio."

"Include another rest day."

"Make the workout easier."

The AI generates an updated plan.

### 4. Database

SQLite stores:

- User information
- Original workout plan
- Updated workout plan
- Nutrition tip
- Feedback

### 5. Admin Dashboard

Open:

http://127.0.0.1:8000/view-all-users

The dashboard displays users and their plans.

## Installation

Create virtual environment:

```bash
python -m venv .venv
```
