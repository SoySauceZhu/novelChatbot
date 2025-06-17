from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os


def init_index(dimension=384, index_file="data/memory.index"):
    if not os.path.exists(index_file):
        index = faiss.IndexFlatL2(dimension)
    else:
        index = faiss.read_index(index_file)
    return index


def save_index(index, index_file="data/memory.index"):
    faiss.write_index(index, index_file)


# Load the model once and reuse it
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model


def get_embedding(text):
    model = get_embedding_model()
    embedding = model.encode(text)
    return embedding.reshape(1, -1).astype(np.float32)


def add_memory(index, text):
    vector = get_embedding(text)
    index.add(vector)


def search_memory(index, query, top_k=3):
    """Search for the most similar memories to the query."""
    vector = get_embedding(query)
    D, I = index.search(vector, top_k)
    return I[0], D[0]

def get_all_memories(index):
    if index.ntotal == 0:
        return np.array([])
    return index.reconstruct_n(0, index.ntotal)