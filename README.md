# Log RAG Operations

## Local Setup

### Environment Setup

1. Create the environment: `python3.11 -m venv .venv` (alternatively `python3 -m venv .venv`)

2. Activate the environment: `source .venv/bin/activate`

3. Upgrade & install:
```
pip install --upgrade pip
pip install -r requirements.txt
```

4. Verify (optional)
```
python3.11 -c src/env_test.py
```

### Ollama (LLM) Setup

1. Pull llama3: `ollama pull llama3`

2. The Embedding model for turning text into vectors: `ollama pull nomic-embed-text`