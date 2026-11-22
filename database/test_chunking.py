
from modules.code_loader import load_code_files
from modules.code_chunker import create_chunks

PROJECT_FOLDER = "extracted_project"

# Step 1: Load source files
documents = load_code_files(PROJECT_FOLDER)

print("\n========== LOADED FILES ==========")

print("Total files:", len(documents))

for doc in documents:
    print(doc["file"])

# Step 2: Generate chunks
chunks = create_chunks(documents)

print("\n========== GENERATED CHUNKS ==========")

print("Total chunks:", len(chunks))

# Step 3: Display chunks
for i, chunk in enumerate(chunks, start=1):

    print("\n------------------------------")

    print("Chunk:", i)
    print("File:", chunk["file"])
    print("Name:", chunk["name"])
    print("Type:", chunk["type"])
    print("Lines:", chunk["start_line"], "-", chunk["end_line"])

    print("\nCode:")
    print(chunk["text"])
