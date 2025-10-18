"""Setup vector store with AxleWave documents."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import DOCS_DIR, VECTOR_STORE_DIR
from utils.document_loader import load_axlewave_documents
from utils.vector_store import AxleWaveVectorStore


def setup_vectorstore():
    """Initialize vector store with documents."""
    print("🚀 Setting up AxleWave Vector Store...\n")
    
    # Load documents
    print("📄 Loading documents...")
    documents = load_axlewave_documents(DOCS_DIR)
    print(f"✓ Loaded {len(documents)} documents\n")
    
    # Initialize vector store
    print("🗄️  Initializing ChromaDB...")
    vector_store = AxleWaveVectorStore(VECTOR_STORE_DIR)
    vector_store.create_collection()
    
    # Add documents
    print("\n📊 Adding documents to vector store...")
    vector_store.add_documents(documents)
    
    # Test query
    print("\n🧪 Testing retrieval...")
    test_queries = [
        "What does AxleWave do?",
        "Who are the target customers?",
        "What are the key features?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = vector_store.query(query, n_results=2)
        if results:
            print(f"✓ Found {len(results)} relevant chunks")
            print(f"  Preview: {results[0][:150]}...")
    
    print("\n✅ Vector store setup complete!")
    print(f"📍 Location: {VECTOR_STORE_DIR}")
    
    return vector_store


if __name__ == "__main__":
    try:
        setup_vectorstore()
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
