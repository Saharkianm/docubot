"""
query_test.py — a quick sanity check that your vector database works.

This does NOT talk to an AI yet — it just tests that "search by meaning"
is working: does asking about "installing fastapi" actually pull back
chunks of text that are about installing FastAPI?
"""

import chromadb

# Connect to the same database ingest.py created
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="fastapi_docs")

# query_texts: the question(s) you're asking
# n_results: how many of the closest-matching chunks to return
results = collection.query(
    query_texts=["how do I install fastapi"],
    n_results=3,
)

# results is a dictionary. results["documents"][0] is the list of
# matching text chunks for your first (and only) question.
for i, doc in enumerate(results["documents"][0]):
    source = results["metadatas"][0][i]["source"]
    print(f"--- Match {i+1} (from {source}) ---")
    print(doc[:200])
    print()