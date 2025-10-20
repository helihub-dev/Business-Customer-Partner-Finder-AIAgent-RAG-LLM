# -*- coding: utf-8 -*-
"""Setup vector store with AxleWave documents."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import DOCS_DIR, VECTOR_STORE_DIR
from utils.document_loader import load_axlewave_documents
from utils.vector_store import VectorStore


def setup_vectorstore():
    """Initialize vector store with documents."""
    print("Setting up AxleWave Vector Store...")
    
    # Initialize vector store
    print("Initializing Vector Store...")
    vector_store = VectorStore(persist_directory=str(VECTOR_STORE_DIR))
    
    # Check if already populated
    if vector_store.is_populated():
        print("Vector store already populated, skipping document loading")
        print("Location: {}".format(VECTOR_STORE_DIR))
        return vector_store
    
    # Load documents
    print("Loading documents from all formats (docx, pdf, xlsx, pptx)...")
    documents = load_axlewave_documents(DOCS_DIR)
    print("Loaded {} documents".format(len(documents)))
    for doc in documents:
        print("  - {} ({})".format(doc['filename'], doc['type']))
    
    # Chunk and add documents
    print("Chunking and adding documents...")
    all_chunks = []
    all_metadata = []
    
    for doc in documents:
        chunks = vector_store.chunk_text(doc['content'], chunk_size=500, overlap=50)
        all_chunks.extend(chunks)
        all_metadata.extend([{
            'source': doc['filename'],
            'type': doc['type']
        } for _ in chunks])
        print("  {} chunks from {}".format(len(chunks), doc['filename']))
    
    print("Adding {} chunks to vector store...".format(len(all_chunks)))
    vector_store.add_documents(
        documents=all_chunks,
        metadatas=all_metadata
    )
    
    # Test query
    print("Testing retrieval...")
    test_queries = [
        "What does AxleWave do?",
        "Who are the target customers?",
        "What are the key features?"
    ]
    
    for query in test_queries:
        print("\nQuery: {}".format(query))
        results = vector_store.query(query, n_results=2)
        if results:
            # Handle both string and dict results
            if isinstance(results[0], dict):
                preview = results[0]['document'][:150]
            else:
                preview = results[0][:150]
            print("Found {} relevant chunks".format(len(results)))
            print("  Preview: {}...".format(preview))
    
    print("\nVector store setup complete!")
    print("Location: {}".format(VECTOR_STORE_DIR))
    
    return vector_store


if __name__ == "__main__":
    try:
        setup_vectorstore()
    except Exception as e:
        print("Setup failed: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)

