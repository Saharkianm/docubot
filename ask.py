"""
ask.py — DocuBot's brain: retrieval + generation, fully local.

1. Retrieve relevant doc chunks from Chroma (search by meaning)
2. Build a prompt that forces the model to use ONLY those chunks
3. Send the prompt to a local Ollama model and print the answer

No API key, no internet needed after the models are downloaded.
"""

import json
import urllib.request
import chromadb

# Change this to compare models. Use the exact name from `ollama list`.
MODEL = "phi3"   # try "gemma:2b" or "gemma2:2b" too

OLLAMA_URL = "http://localhost:11434/api/chat"

# ---- Connect to your vector database ----
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="fastapi_docs")


def retrieve(question, n_results=4):
    """Get the most relevant doc chunks for a question."""
    results = collection.query(query_texts=[question], n_results=n_results)
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    return list(zip(chunks, sources))


def build_prompt(question, retrieved_chunks):
    """Wrap the chunks in strict instructions so the answer stays grounded."""
    context_text = ""
    for chunk, source in retrieved_chunks:
        context_text += f"[Source: {source}]\n{chunk}\n\n"

    return f"""You are DocuBot, a helpful assistant that answers questions about FastAPI using only the documentation excerpts provided below.

Rules:
- Only answer using the information in the excerpts below.
- If the excerpts don't contain the answer, say "I don't have enough information in the docs to answer that."
- Mention which source file the information came from.
- Keep the answer short and clear.

Documentation excerpts:
{context_text}

User question: {question}

Answer:"""


def call_ollama(prompt):
    """Send the prompt to the local Ollama server and return the reply text."""
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,   # wait for the full answer instead of streaming
    }).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    # Small local models can be slow on CPU, so allow up to 5 minutes
    with urllib.request.urlopen(request, timeout=300) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["message"]["content"]


def ask(question):
    """Full pipeline: retrieve -> build prompt -> ask the local model."""
    retrieved = retrieve(question)
    prompt = build_prompt(question, retrieved)
    return call_ollama(prompt)


if __name__ == "__main__":
    print(f"DocuBot is ready (model: {MODEL}). Type a question, or 'quit' to exit.\n")
    while True:
        question = input("You: ")
        if question.lower() in ("quit", "exit"):
            break
        try:
            print("\n(thinking... small models can take a while)\n")
            print(f"DocuBot: {ask(question)}\n")
        except Exception as e:
            print(f"\nError: {e}")
            print("Is Ollama running? Try `ollama list` in another cmd window.")
            print(f"Is the model name '{MODEL}' exactly what `ollama list` shows?\n")