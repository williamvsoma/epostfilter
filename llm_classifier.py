import config as cfg
import ollama
from pydantic import BaseModel
from enum import Enum

class is_spam(str, Enum):
    spam = 'spam'
    not_spam = 'not spam'

class ResultModel(BaseModel):
    result: is_spam

def spam_classifier(txt) -> bool:
    prompt = f'classify the following email as spam or not spam. Classify as smap only if you are confident: {txt}'
    response = ollama.chat(model=cfg.llm_model, messages=[
        {
            'role': 'user',
            'content': prompt,
        },
        ], format=ResultModel.model_json_schema(), options={'temperature':0.0, 'top_k':1}
    ) 
    response = ResultModel.model_validate_json(response['message']['content'])
    return response.result.value == 'spam'