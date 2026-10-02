import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

sys.path.append(str(Path(__file__).resolve().parent))

from data.profile import candidate_profile
from schemas.match_schema import MatchResult

load_dotenv()

my_api_key = os.getenv('GROQ_API_KEY')
if not my_api_key:
    raise ValueError("API KEY MISSING")

client = Groq(api_key=my_api_key)
model = 'openai/gpt-oss-20b'

structured_llm = llm.with_structured_output(MatchResult)
