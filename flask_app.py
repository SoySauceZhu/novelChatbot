from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import yaml
import os
from memory import init_index, add_memory, search_memory, save_index, get_embedding
from state import load_state, save_state, update_state, get_state, update_past_status, get_past_status
from prompt import build_story_continuation_prompt, build_summary_prompt, build_story_system_prompt, build_summary_system_prompt
import logging

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

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

@app.route('/continue_story', methods=['POST'])
def continue_story():
    data = request.get_json()
    user_input = data.get('user_input', '')
    logger.info(f"Received user input: {user_input}")
    # Search memory
    if index.ntotal > 0:
        I, D = search_memory(index, user_input)
        memory_texts = [get_state(state, i) for i in I if i < len(state["history"])]
        logger.info(f"Memory search results: {memory_texts}")
    else:
        memory_texts = []
        logger.info("No memory found, starting fresh.")
    last_story_chunk = ""
    for i in range(len(get_past_status(state))):
        if i >= 3:
            break
        last_story_chunk += get_past_status(state)[i] + "\n"
    logger.info(f"Last story chunk: {last_story_chunk}")
    # Build prompt
    prompt = build_story_continuation_prompt(memory_texts, last_story_chunk, user_input)
    logger.info(f"Prompt sent to OpenAI: {prompt}")
    # Call OpenAI
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": story_system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    result = response.choices[0].message.content
    logger.info(f"OpenAI response: {result}")
    # Save state
    update_state(state, result)
    update_past_status(state, result)
    save_state(state)
    add_memory(index, user_input)
    save_index(index)
    logger.info("State and memory updated.")
    return jsonify({"story": result})

@app.route('/state', methods=['GET'])
def get_current_state():
    logger.info("State requested.")
    return jsonify(state)

@app.route('/state', methods=['POST'])
def update_current_state():
    new_chunk = request.get_json(force=True)
    logger.info(f"Updating state with new chunk: {new_chunk}")
    update_state(state, new_chunk)
    save_state(state)
    return jsonify({"status": "ok"})

@app.route('/memory/search', methods=['POST'])
def memory_search():
    data = request.get_json()
    query = data.get('query', '')
    logger.info(f"Memory search for query: {query}")
    if index.ntotal > 0:
        I, D = search_memory(index, query)
        memory_texts = [get_state(state, i) for i in I if i < len(state["history"])]
    else:
        memory_texts = []
    logger.info(f"Memory search results: {memory_texts}")
    return jsonify({"results": memory_texts})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
