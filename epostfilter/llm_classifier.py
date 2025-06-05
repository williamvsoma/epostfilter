import epostfilter.config as cfg
import ollama
from pydantic import BaseModel
from enum import Enum

SYSTEM_PROMPT = (
    "You are a **high-precision** email spam filter.\n"
    "Output *only* valid JSON that matches exactly this schema:\n"
    '{"result": "spam" | "not spam", "confidence": float}\n'
    "Think privately; do **not** include your reasoning in the reply."
)

class is_spam(str, Enum):
    spam = 'spam'
    not_spam = 'not spam'

class ResultModel(BaseModel):
    result: is_spam

def spam_classifier(txt) -> bool:
    response = ollama.chat(
        model=cfg.llm_model, 
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': txt},
        ], 
        format=ResultModel.model_json_schema(), 
        options={
            'temperature': 0.0, 
            'top_k': 1,
            }
    ) 
    response = ResultModel.model_validate_json(response['message']['content'])
    return response.result.value == 'spam'