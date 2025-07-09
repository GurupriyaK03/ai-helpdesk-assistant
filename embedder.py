import os
import fitz  # PyMuPDF
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from utils import chunk_text

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_and_index(role, pdf_path, index_dir="vector_stores"):
    # Extract file name without extension
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Read PDF and extract text
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text() for page in doc])
    chunks = chunk_text(text)

    # Generate embeddings
    embeddings = model.encode(chunks)

    # Create FAISS index and add embeddings
    index = faiss.IndexFlatL2(384)
    index.add(embeddings)

    # Save index and chunks with unique names based on file
    os.makedirs(index_dir, exist_ok=True)
    index_path = os.path.join(index_dir, f"{role}_{base}.index")
    chunk_path = os.path.join(index_dir, f"{role}_{base}_chunks.pkl")

    faiss.write_index(index, index_path)
    with open(chunk_path, "wb") as f:
        pickle.dump(chunks, f)
