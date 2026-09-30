import os
from pathlib import Path

from dotenv import load_dotenv


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(BASE_DIR / ".env")


# ---------------------------------------------------------
# Application settings
# ---------------------------------------------------------

APP_NAME = os.getenv(
    "APP_NAME",
    "FitBuddy - AI Fitness Plan Generator"
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0"
)


# ---------------------------------------------------------
# Gemini settings
# ---------------------------------------------------------

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
)

# Current Gemini models can be changed from .env.
# Keeping them configurable makes the application easier
# to maintain when model names change.
GEMINI_WORKOUT_MODEL = os.getenv(
    "GEMINI_WORKOUT_MODEL",
    "gemini-3.8-flash"
)

GEMINI_TIP_MODEL = os.getenv(
    "GEMINI_TIP_MODEL",
    "gemini-3.8-flash"
)


# ---------------------------------------------------------
# Database settings
# ---------------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'fitbuddy.db'}"
)


# ---------------------------------------------------------
# Admin settings
# ---------------------------------------------------------

ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "admin"
)

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    "fitbuddy123"
)