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
    raise ValueError("API KEY is missing")

client = Groq(api_key=my_api_key)
model = 'openai/gpt-oss-20b'

def evaluate_match(user_input: str, chat_history: list[dict[str, str]] = None) -> MatchResult:
    if chat_history is None:
        chat_history = []

    system_prompt = f"""
You are the personal AI Assistant and Portfolio Representative for the candidate.
You are speaking directly to recruiters, hiring managers, and founders evaluating the candidate.

--- CANDIDATE PROFILE ---
{candidate_profile}
-------------------------

Categorize the user's input into ONE of three intents and return a valid JSON object matching this schema:
{MatchResult.model_json_schema()}

--- VOICE & PHRASING RULES ---
- Candidate Identity: Harsh is an aspiring AI Backend Engineer / LLM Engineer transitioning from a data background. DO NOT refer to him as a "Data Analyst" in the present tense. Frame his previous data experience as a supporting foundation for his AI engineering work.
- Name Usage: Refer to him as "Harsh Tyagi" on first mention only. Subsequently, use "Harsh", "he", or "his".

--- INTENT CLASSIFICATION & OUTPUT INSTRUCTIONS ---

INTENT 1: JOB DESCRIPTION OR HIRING REQUIREMENTS
Trigger: The recruiter/user pastes a job description, role description, or set of technical hiring requirements.
Output Rules:
- "match_score": Integer (0-100) reflecting an accurate match between candidate profile and the JD.
- "matching_skills": List of strings detailing skills/tools the candidate possesses that match the JD.
- "missing_skills": List of strings detailing required skills from the JD that the candidate lacks or is weak in.
- "summary": Executive summary highlighting why the candidate is a fit, key strengths relevant to the role, and how their background aligns.

INTENT 2: CANDIDATE PROFILE Q&A
Trigger: The recruiter asks a specific question about the candidate's background, education, projects, skills, or experience (e.g., "What qualifications does he have?", "Where did he study?", "Does he know Python?").
Output Rules:
- "match_score": Set strictly to 0.
- "matching_skills": Set strictly to empty list [].
- "missing_skills": Set strictly to empty list [].
- "summary": Direct, professional answer to the question using specific facts from CANDIDATE PROFILE. Speak in third person ("He holds...", "His experience includes...") or as his AI agent ("Harsh has worked on...").

INTENT 3: CASUAL CHAT, GREETINGS, OR META-QUESTIONS
Trigger: The user greets the bot ("hi", "hello"), asks about the bot itself ("Who made you?", "How do you work?", "What model are you?"), or engages in small talk.
Output Rules:
- "match_score": Set strictly to 0.
- "matching_skills": Set strictly to empty list [].
- "missing_skills": Set strictly to empty list [].
- "summary": Answer the user's specific question naturally before offering assistance. 
  * If asked how/who built the bot: Explain naturally that you were built by Harsh using Python, FastAPI, and Groq's openai/gpt-oss-20b model as a custom portfolio agent to evaluate candidate fit and answer questions about his backend/AI work.
  * Keep it conversational, concise, and direct.

CRITICAL REQUIREMENT:
Output ONLY raw valid JSON. No markdown wrappers or extra commentary outside the JSON payload.
"""
    user_prompt = f"--- USER INPUT ---\n{user_input}"

    messages = [{
        'role': 'system', 
        'content': system_prompt
        }]
    messages.extend(chat_history)
    messages.append({
        'role': 'user', 
        'content': user_prompt
        })

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=messages,
        response_format={
            "type": "json_object"
            }
    )

    raw_json = response.choices[0].message.content

    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": raw_json})

    return MatchResult.model_validate_json(raw_json)


# Test Script
if __name__ == "__main__":
    print("--- Testing engine.py Locally ---\n")
    history = []

    # Test 1: General Greeting
    print("User: Hi! How were you made? Who made you")
    res1 = evaluate_match("Hi! Who are you?", chat_history=history)
    print(f"Bot: {res1.summary}\n")

    # # Test 2: Profile Question
    # print("User: What qualifications does he have?")
    # res2 = evaluate_match("What qualifications does he have?", chat_history=history)
    # print(f"Bot: {res2.summary}\n")

    # # Test 3: Job Description Evaluation
    # print("User: [Pasting JD for Data Analyst/AI Engineer]")
    # sample_jd = "Looking for a Data Analyst proficient in Python, SQL, and LLM APIs."
    # res3 = evaluate_match(sample_jd, chat_history=history)
    # print(f"Match Score: {res3.match_score}%")
    # print(f"Matching Skills: {res3.matching_skills}")
    # print(f"Missing Skills: {res3.missing_skills}")
    # print(f"Summary: {res3.summary}\n")