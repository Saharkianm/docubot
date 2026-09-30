"""
test_chunking.py — inspect how your docs get chunked, with no
embeddings or LLM involved. Just the chunking logic on its own.

This lets you SEE:
- how many chunks each file produces
- whether chunks cut off mid-sentence awkwardly
- whether the overlap is actually working (chunk boundaries share text)
"""

import glob
from ingest import chunk_text

doc_files = glob.glob("docs/**/*.md", recursive=True)
print(f"Found {len(doc_files)} files\n")

total_chunks = 0

for filepath in doc_files:
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    total_chunks += len(chunks)
    print(f"{filepath}: {len(text)} chars -> {len(chunks)} chunks")

print(f"\nTotal chunks across all files: {total_chunks}")

# ---- Look closely at ONE file's chunks ----
# Change this to inspect a different file
target_file = doc_files[0] if doc_files else None

if target_file:
    print(f"\n--- Detailed view of: {target_file} ---\n")
    with open(target_file, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        print(f"[Chunk {i}] ({len(chunk)} chars)")
        print(chunk)
        print("-" * 50)
