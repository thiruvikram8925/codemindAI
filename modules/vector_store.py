
import faiss
import numpy as np


def create_faiss_index(embeddings):

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    print("FAISS vector database created!")
    print("Total vectors:", index.ntotal)

    return index


def search_similar_chunks(
    query,
    model,
    index,
    chunks,
    top_k=3
):

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype=np.float32
    )

    total_chunks = len(chunks)
    top_k = min(top_k, total_chunks)

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        results.append({
            "score": float(score),
            "chunk": chunks[idx]
        })

    return results
