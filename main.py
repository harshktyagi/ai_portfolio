import os
import json
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine import evaluate_match, stream_evaluate
from schemas.match_schema import MatchResult
from util.parser import text_extractor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return {}

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

@app.post('/evaluate-stream')
def evaluate_stream(payload: EvaluateRequest):
    try:
        return StreamingResponse(
            stream_evaluate(
                user_input=payload.user_input,
                chat_history=payload.chat_history
            ),
            media_type="text/plain"
        )

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