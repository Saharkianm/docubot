<<<<<<< HEAD
# docubot
=======
# DocuBot — Local RAG Assistant for FastAPI Docs

DocuBot answers questions about FastAPI using only its official documentation,
grounding every answer in retrieved source text instead of relying on the
model's general training knowledge. If the docs don't cover something, it
says so instead of guessing.

The entire system runs **locally with no external API calls** — embeddings,
retrieval, and generation all happen on-device. This makes it suitable for
scenarios where sending data to a third-party API isn't an option (privacy
requirements, restricted network access, air-gapped environments).

## How it works

```
User question
     │
     ▼
[1] Embed the question (Chroma's local embedding model)
     │
     ▼
[2] Retrieve top-N most relevant doc chunks (vector similarity search)
     │
     ▼
[3] Build a prompt: question + retrieved chunks + strict grounding rules
     │
     ▼
[4] Local LLM (via Ollama, e.g. phi3 / gemma2:2b) generates an answer
     │
     ▼
Answer + source citations returned to the user
```

## Tech stack

- **Python** — core pipeline
- **ChromaDB** — local vector database for storing and searching document embeddings
- **Ollama** — runs open-weight LLMs (phi3, gemma2:2b) fully on-device
- **FastAPI** — serves the pipeline as a REST API (`POST /chat`)
- **Vanilla HTML/JS** — lightweight chat frontend, decoupled from the backend

## Features

- Answers grounded strictly in the provided documentation
- Refuses to answer out-of-scope questions instead of hallucinating
- Returns source file citations for every grounded answer
- Fully offline after initial model download — no API key, no per-query cost
- Swappable local models (tested with phi3 and gemma2:2b) to compare
  speed/quality tradeoffs

## Setup

```bash
# 1. Install Ollama (https://ollama.com) and pull a model
ollama pull phi3

# 2. Create a virtual environment and install dependencies
python -m venv venv
venv\Scripts\activate          # Windows
pip install chromadb fastapi uvicorn

# 3. Ingest the documentation into the vector database
python ingest.py

# 4. Start the API
uvicorn api:app --reload

# 5. Serve the chat UI
python -m http.server 5500
# then open http://127.0.0.1:5500/chat.html
```

## Example

**Q: How do I install FastAPI?**
> Grounded answer with citation to `docs/tutorial/index.md`

**Q: What is the capital of France?**
> "I don't have enough information in the docs to answer that."
> (correctly refuses — this isn't in the FastAPI documentation)

## Why fully local instead of a hosted API?

This was a deliberate design choice, not just a workaround: many real-world
deployments (regulated industries, air-gapped networks, cost-sensitive
environments) cannot send user data to external AI APIs. Building and
debugging a fully local pipeline — from embeddings to generation — demonstrates
the same engineering skills as a hosted-API version, applied to a genuinely
harder constraint.

## Possible improvements

- Conversation memory across turns
- Structured (JSON) model output instead of parsing free text for refusals
- Larger/quantized local models for better answer quality
- Chunking strategy tuning (semantic chunking instead of fixed-size)

## Author

Built by Sahar as a hands-on project for learning Forward Deployed
Engineering: taking an existing system (FastAPI + its docs) and building a
working, client-usable tool on top of it under real infrastructure
constraints.
>>>>>>> d10eecd0 (Initial commit)
