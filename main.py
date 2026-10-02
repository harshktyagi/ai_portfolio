import os
import json
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from engine import evaluate_match
from schemas.match_schema import MatchResult
from util.parser import text_extractor

app = FastAPI()

@app.get('/')
def health_check():
    return {'status' : 'online', 'message' : 'AI PORTFOLIO API up and running!'}

class EvaluateRequest(BaseModel):
    user_input : str
    chat_history : list[dict[str, str]] | None = []

@app.post('/evaluate', response_model = MatchResult)
def evaluate_text(payload: EvaluateRequest):
    try:
        result = evaluate_match(
            user_input = payload.user_input,
            chat_history = payload.chat_history
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/evaluate-file')
async def evaluate_file(file : UploadFile = File(...), chat_history_str : str | None = Form(default = '[]')):
    try:
        chat_history = json.loads(chat_history_str)

        temp_file_path = f'temp{file.filename}'
        with open(temp_file_path, 'wb') as f:
            f.write(await file.read())

            extracted_text = text_extractor(temp_file_path)

            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

            if not extracted_text:
                raise HTTPException(status_code=400, detail="Unable to extract text from file.")

            result = evaluate_match(
                user_input=extracted_text,
                chat_history=chat_history
            )
            return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    