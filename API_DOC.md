# Chatbot Micro-Service API Documentation

This micro-service exposes endpoints for interactive story generation, memory search, and state management. It is built with FastAPI and can be run locally or deployed as a container.

## Getting Started

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
2. **Start the service:**
   ```sh
   uvicorn app:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.

3. **Interactive API docs:**
   Visit `http://127.0.0.1:8000/docs` for Swagger UI.

---

## API Endpoints

### 1. Continue Story
- **POST** `/continue_story`
- **Description:** Generate the next story chunk based on user input and memory.
- **Request Body:**
  ```json
  {
    "user_input": "<your story input>"
  }
  ```
- **Response:**
  ```json
  {
    "story": "<generated story chunk>"
  }
  ```

### 2. Search Memory
- **POST** `/memory/search`
- **Description:** Search for similar memories in the story history.
- **Request Body:**
  ```json
  {
    "query": "<search text>"
  }
  ```
- **Response:**
  ```json
  {
    "results": ["<memory1>", "<memory2>", ...]
  }
  ```

### 3. Get State
- **GET** `/state`
- **Description:** Retrieve the current story state/history.
- **Response:**
  ```json
  {
    "history": [...],
    "current_status": { ... }
  }
  ```

### 4. Update State
- **POST** `/state`
- **Description:** Add a new story chunk to the state/history.
- **Request Body:**
  ```json
  {
    "new_chunk": "<story chunk>"
  }
  ```
- **Response:**
  ```json
  { "status": "ok" }
  ```

---

## Notes
- All endpoints accept and return JSON.
- The service uses OpenAI API and sentence-transformers for story generation and memory search.
- Data is persisted in the `data/` directory.

---

## Example Usage (Python)

```python
import requests

# Continue story
resp = requests.post('http://127.0.0.1:8000/continue_story', json={"user_input": "你的故事输入"})
print(resp.json())

# Search memory
resp = requests.post('http://127.0.0.1:8000/memory/search', json={"query": "关键词"})
print(resp.json())

# Get state
resp = requests.get('http://127.0.0.1:8000/state')
print(resp.json())

# Update state
resp = requests.post('http://127.0.0.1:8000/state', json={"new_chunk": "新故事片段"})
print(resp.json())
```

---

For more details, see the code in `app.py` or use the interactive docs at `/docs`.
