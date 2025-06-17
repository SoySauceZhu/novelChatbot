import json
import os

def load_state(filepath="data/state.json"):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        return {
            "history": [],
            "current_status": {
                "past_story_chunk": []
            }
        }

def save_state(state, filepath="data/state.json"):
    with open(filepath, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def update_state(state, new_chunk):
    state["history"].append(new_chunk)

def get_state(state, index):
    return state["history"][index] if 0 <= index < len(state["history"]) else None

def update_past_status(state, value):
    state["current_status"]["past_story_chunk"].append(value)

def get_past_status(state):
    return state["current_status"].get("past_story_chunk", [])