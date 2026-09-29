from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ask import retrieve, build_prompt, call_ollama

app = FastAPI(title="DocuBot API")

# Allow your chat webpage (running on file:// or a different port)
# to send requests to this API. In a real product you'd restrict
# allow_origins to your actual website's address instead of "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def health_check():
    return {"status": "DocuBot is running"}


@app.post("/chat")
def chat(request: ChatRequest):
    retrieved = retrieve(request.question)
    prompt = build_prompt(request.question, retrieved)
    answer = call_ollama(prompt)

    # Only show sources if the model actually used them to answer.
    # This is a simple heuristic: check for the model's own refusal phrase.
    if "don't have enough information" in answer.lower():
        sources = []
    else:
        sources = sorted({source for _, source in retrieved})
        
    return {"answer": answer, "sources": sources}