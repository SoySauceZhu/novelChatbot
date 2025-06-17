from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai
import yaml
import os
from memory import init_index, add_memory, search_memory, save_index, get_embedding
from state import load_state, save_state, update_state, get_state, update_past_status, get_past_status
from prompt import build_story_continuation_prompt, build_summary_prompt, build_story_system_prompt, build_summary_system_prompt
import shutil
import re

app = FastAPI()

# Load config and initialize once
config = yaml.safe_load(open("config.yaml", "r"))
api_key = config["openai_api_key"]
base_url = config["base_url"]
model = config["model"]

os.makedirs("data", exist_ok=True)
index = init_index()
state = load_state()
client = openai.OpenAI(api_key=api_key, base_url=base_url)
story_system_prompt = build_story_system_prompt()
summary_system_prompt = build_summary_system_prompt()

class ContinueStoryRequest(BaseModel):
    user_input: str

@app.post("/continue_story")
def continue_story(req: ContinueStoryRequest):
    user_input = req.user_input
    # Search memory
    if index.ntotal > 0:
        I, D = search_memory(index, user_input)
        memory_texts = [get_state(state, i) for i in I if i < len(state["history"])]
    else:
        memory_texts = []
    last_story_chunk = ""
    for i in range(len(get_past_status(state))):
        if i >= 3:
            break
        last_story_chunk += get_past_status(state)[i] + "\n"
    # Build prompt
    prompt = build_story_continuation_prompt(memory_texts, last_story_chunk, user_input)
    # Call OpenAI
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": story_system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    result = response.choices[0].message.content
    # Save state
    update_state(state, result)
    update_past_status(state, result)
    save_state(state)
    add_memory(index, user_input)
    save_index(index)
    return {"story": result}

@app.get("/state")
def get_current_state():
    return state

@app.post("/state")
def update_current_state(new_chunk: str):
    update_state(state, new_chunk)
    save_state(state)
    return {"status": "ok"}

@app.post("/memory/search")
def memory_search(query: str):
    if index.ntotal > 0:
        I, D = search_memory(index, query)
        memory_texts = [get_state(state, i) for i in I if i < len(state["history"])]
    else:
        memory_texts = []
    return {"results": memory_texts}
