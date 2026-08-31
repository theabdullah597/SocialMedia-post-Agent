import os
from dotenv import load_dotenv
load_dotenv()
LLM_API_KEY=os.getenv('LLM_API_KEY')
if not LLM_API_KEY:
    raise ValueError('LLM_API_KEY environment variable not set')