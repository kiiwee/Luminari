import html2text
from bs4 import BeautifulSoup
import requests
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import utils as utils
import json
from openai import OpenAI

function_caller = utils.FunctionCaller()

# Create the functions metadata
functions_metadata = function_caller.create_functions_metadata()

# Create the system prompt
system_prompt = utils.prompt_beginning + \
    f"<tools> {json.dumps(functions_metadata, indent=4)} </tools>" + \
    utils.system_prompt_end

class Query(BaseModel):
    query: str


client = OpenAI(
    # This is the default and can be omitted
    api_key='sk-xxx',
    base_url='http://127.0.0.1:4200/v1'
)

app = FastAPI(title="Luminari API",
              version="0.0.1",
              description="A simple api server using FastAPI interface and Pydantic data validation")


def search(query):
    url = "http://localhost:8080/search"
    params = {
        'q': query,
        'format': 'json',
        'language': 'en',
    }
    response = requests.get(url, params=params, cookies={'lang;': 'en'})
    return response.json()


def get_text_from_url(results):
    res_l = []
    for result in results:

        url = result.get('url')
        if 'medium.com' in url:
            url = 'https://freedium.cfd/'+url
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        text = [p.text for p in soup.find_all(
            ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]

        ai_res = {}
        ai_res['url'] = url
        ai_res['title'] = result.get('title')
        ai_res['content'] = result.get('content')
        ai_res['text'] = text

        res_l.append(ai_res)

    return res_l


@app.post("/tool_response")
async def get_tool_response(query: Query):
    messages = [
        {'role': 'system', 'content': system_prompt,
         },
        {'role': 'user', 'content': query.query}
    ]
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="hermes",
        temperature=0,
    )
    messages,function_calls_json=utils.get_func_response(chat_completion,messages)
    messages,urls=utils.call_functions(messages,function_calls_json,function_caller)
    return messages,urls


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,port=4201 )