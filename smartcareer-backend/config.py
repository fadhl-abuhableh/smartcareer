import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'models/gemini-1.5-flash-8b')

# Rate Limiting and Cache Configuration
CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 86400))  # 24 hours in seconds
MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 60))

# MySQL DB config (same as in app.py)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'smartcareer_db')
}

# AI Service Configuration
MAX_REQUESTS_PER_MINUTE = 60  # Maximum number of requests per minute
CACHE_TIMEOUT = 3600  # Cache timeout in seconds (1 hour)
MAX_CACHE_SIZE = 1000  # Maximum number of cached responses

# Fallback responses for when the AI service fails
FALLBACK_RESPONSES = {
    'resume_feedback': {
        "general": "We're currently unable to provide personalized resume feedback. Please try again later.",
        "strengths": "• Unable to analyze strengths at this time\n• Please try again later",
        "improvements": "• Unable to suggest improvements at this time\n• Please try again later"
    },
    'career_advice': {
        "certifications": "We're currently unable to provide certification recommendations. Please try again later.",
        "skills": "We're currently unable to provide skill recommendations. Please try again later.",
        "tips": "• Unable to provide tips at this time\n• Please try again later"
    },
    'detailed_roadmap': [
        {
            "title": "Junior Data Analyst",
            "description": "Learn Python, SQL, and data visualization. Build dashboards and analyze data. Create a portfolio with 2-3 data analysis projects."
        },
        {
            "title": "Senior Data Analyst",
            "description": "Master advanced analytics, statistical modeling, and data pipeline design. Lead data projects and mentor junior analysts."
        },
        {
            "title": "Data Science Team Lead",
            "description": "Drive data strategy, manage analytics teams, and implement ML solutions. Collaborate with stakeholders on high-impact projects."
        }
    ]
}

# Model Configuration
DEFAULT_MODEL = 'models/gemini-1.5-flash-8b'
FALLBACK_MODEL = 'models/gemma-3-4b-it'

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' 