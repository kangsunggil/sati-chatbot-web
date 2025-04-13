import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CREDENTIAL_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
