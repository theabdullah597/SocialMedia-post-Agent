import os
from dotenv import load_dotenv
load_dotenv()
LLM_API_KEY=os.getenv('GEMINI_API_KEY')
if LLM_API_KEY:
    print("LLM API key set")
else:
    raise ValueError('LLM_API_KEY environment variable not set')