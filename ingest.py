"""
ingest.py — Step 1 of DocuBot

What this file does, in plain English:
1. Walks through your docs/ folder and reads every .md file
2. Cuts each file into small chunks (so we can search by relevant piece, not whole file)
3. Sends each chunk to an embedding model to get its "meaning as numbers"
4. Saves everything into a local Chroma database on your disk

Run it with: python ingest.py
"""

import os
import glob
import chromadb

# ---- Step B: A simple chunking function ----
def chunk_text(text, chunk_size=800, overlap=100):
    """
    Splits text into overlapping chunks.

    chunk_size: how many characters per chunk (roughly ~150-200 words)
    overlap: how many characters repeat between chunks, so we don't
             cut a sentence in half and lose its meaning

    Why overlap? Imagine chunk 1 ends mid-explanation and chunk 2 starts
    right after. If a question needs info from both, overlap helps
    make sure the "connecting" sentence isn't lost.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap  # move forward, but re-include the overlap
    return chunks


def main():
    # ---- Step A: Find all markdown files in docs/ ----
    # glob finds files matching a pattern. "**/*.md" means:
    # "any .md file, in this folder or any subfolder"
    doc_files = glob.glob("docs/**/*.md", recursive=True)
    print(f"Found {len(doc_files)} markdown files")

    # ---- Step C: Read every file, chunk it, and remember where it came from ----
    all_chunks = []       # the actual text pieces
    all_metadata = []      # info about where each chunk came from (for citations later!)
    all_ids = []           # a unique ID for each chunk (Chroma requires this)

    for filepath in doc_files:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadata.append({"source": filepath})   # remember the source file!
            all_ids.append(f"{filepath}::chunk_{i}")

    print(f"Created {len(all_chunks)} chunks total")

    # ---- Step D: Store everything in Chroma ----
    # PersistentClient means it saves to disk (a folder called chroma_db/)
    # instead of disappearing when the script ends.
    client = chromadb.PersistentClient(path="chroma_db")

    # get_or_create_collection = "give me this named bucket, make it if missing"
    # Chroma will automatically embed the text for us using its built-in model.
    collection = client.get_or_create_collection(name="fastapi_docs")

    # add() sends the chunks to be embedded and stored, in batches for speed
    batch_size = 100
    for i in range(0, len(all_chunks), batch_size):
        collection.add(
            documents=all_chunks[i:i + batch_size],
            metadatas=all_metadata[i:i + batch_size],
            ids=all_ids[i:i + batch_size],
        )

    print(f"Done! Stored {collection.count()} chunks in chroma_db/")


if __name__ == "__main__":
    main()