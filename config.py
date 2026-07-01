import os
from dotenv import load_dotenv
load_dotenv()

try:
    GROQ_API_KEY = os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not present in .env file")
    GROQ_MODEL = os.getenv("GROQ_MODEL")
    if not GROQ_MODEL:
        raise ValueError("GROQ_MODEL is not present in .env file")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    if not JIRA_API_TOKEN:
        raise ValueError("JIRA_API_TOKEN  is not present in .env file")
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
    if not JIRA_BASE_URL:
        raise ValueError("JIRA_BASE_URL is not present in the .env file")
    JIRA_EMAIL=os.getenv("JIRA_EMAIL")
    if not JIRA_EMAIL:
        raise ValueError("JIRA_EMAIL in not present in .env file")
except Exception as e:
    raise ValueError(f"Error occur while loading ENVIRONMENT FILES {e}")

print("loaded the config.py")