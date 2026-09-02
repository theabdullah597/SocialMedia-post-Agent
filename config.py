import os
from dotenv import load_dotenv
load_dotenv()
LLM_API_KEY=os.getenv('GEMINI_API_KEY')
QDRANT_URL=os.getenv('QDRANT_URL')
QDRANT_API_KEY=os.getenv('QDRANT_API_KEY')
TAVILY_API_KEY=os.getenv('TAVIlY_API_KEY')
if LLM_API_KEY:
    print("LLM API key set")
else:
    raise ValueError('LLM_API_KEY environment variable not set')


if QDRANT_URL:
    print("QDRANT URL set")
else:
    raise ValueError('QDRANT_URL environment variable not set')

if QDRANT_API_KEY:
    print("QDRANT API key set")
else:
    raise ValueError('QDRANT_API_KEY environment variable not set')

if TAVILY_API_KEY:
    print("TAVILY API key set")
else:
    raise ValueError('TAVILY_API_KEY environment variable not set')
