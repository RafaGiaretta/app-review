import os
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SerpApi_Key")
OPENAI_KEY = os.getenv("GPT_Key")
