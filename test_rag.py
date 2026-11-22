
from modules.code_loader import load_code_files
from modules.code_chunker import create_chunks

from modules.embeddings import (
    load_embedding_model,
    generate_embeddings
)

from modules.vector_store import create_faiss_index

from modules.rag_pipeline import answer_question


# 1. Load project files
print("Loading project files...")

documents = load_code_files("extracted_project")

print("Files loaded:", len(documents))


# 2. Create chunks
chunks = create_chunks(documents)

print("Code chunks created:", len(chunks))

if not chunks:
    print("No code found. Upload a project first.")
    raise SystemExit


# 3. Load embedding model
model = load_embedding_model()


# 4. Generate embeddings
texts = [chunk["text"] for chunk in chunks]

embeddings = generate_embeddings(texts, model)


# 5. Create FAISS index
index = create_faiss_index(embeddings)


# 6. Ask questions
print("\n================================")
print("       CODEMIND AI ASSISTANT")
print("================================")

while True:

    query = input("\nAsk about your project (type exit to stop): ")

    if query.lower().strip() in ["exit", "quit"]:
        print("Thank you for using CodeMind!")
        break

    if not query.strip():
        continue

    try:

        result = answer_question(
            query,
            model,
            index,
            chunks
        )

        print("\n========== AI ANSWER ==========")
        print(result["answer"])

        print("\n========== SOURCE FILES ==========")

        for source in result["sources"]:

            print(
                f"\nFile: {source['file']}"
                f"\nFunction/Class: {source['name']}"
                f"\nLines: {source['lines']}"
                f"\nSimilarity: {source['score']}"
            )

    except Exception as error:
        print("\nError:", error)
