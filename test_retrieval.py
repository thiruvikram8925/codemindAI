
from modules.code_loader import load_code_files
from modules.code_chunker import create_chunks
from modules.embeddings import (
    load_embedding_model,
    generate_embeddings
)
from modules.vector_store import (
    create_faiss_index,
    search_similar_chunks
)

# Step 1: Load project files
documents = load_code_files("extracted_project")

print("Total files:", len(documents))

# Step 2: Create code chunks
chunks = create_chunks(documents)

print("Total chunks:", len(chunks))

if not chunks:
    print("No code chunks found. Upload a project first.")
    raise SystemExit

# Step 3: Load embedding model
model = load_embedding_model()

# Step 4: Generate embeddings
texts = [chunk["text"] for chunk in chunks]

embeddings = generate_embeddings(texts, model)

print("Embeddings generated:", embeddings.shape)

# Step 5: Create FAISS database
index = create_faiss_index(embeddings)

# Step 6: Search for relevant code
query = input("\nAsk something about your code: ")

results = search_similar_chunks(
    query,
    model,
    index,
    chunks,
    top_k=3
)

# Step 7: Display results
print("\n========== SEARCH RESULTS ==========")

for i, result in enumerate(results, start=1):

    chunk = result["chunk"]

    print("\nResult:", i)
    print("Similarity:", round(result["score"], 4))
    print("File:", chunk["file"])
    print("Function/Class:", chunk["name"])
    print("Code:\n", chunk["text"])
