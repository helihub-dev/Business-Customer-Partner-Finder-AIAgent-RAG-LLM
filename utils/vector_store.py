"""Vector store using ChromaDB with semantic embeddings."""
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer


class VectorStore:
    """Vector store using ChromaDB with semantic embeddings."""
    
    def __init__(self, collection_name: str = "axlewave_docs", persist_directory: str = "./data/vector_store"):
        """Initialize ChromaDB with sentence transformers."""
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        try:
            self.collection = self.client.get_collection(name=collection_name)
            count = self.collection.count()
            print("Loaded existing ChromaDB collection with {} documents".format(count))
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print("Created new ChromaDB collection")
    
    def is_populated(self) -> bool:
        """Check if collection has documents."""
        return self.collection.count() > 0
    
    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None):
        """Add documents with semantic embeddings."""
        if not documents:
            return
        
        if ids is None:
            ids = ["doc_{}".format(i) for i in range(len(documents))]
        
        if metadatas is None:
            metadatas = [{"source": "axlewave"} for _ in documents]
        
        embeddings = self.embedding_model.encode(documents, show_progress_bar=False).tolist()
        
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(self, query: str, n_results: int = 5) -> List[str]:
        """Query with semantic search."""
        query_embedding = self.embedding_model.encode([query], show_progress_bar=False).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        return results['documents'][0] if results['documents'] else []
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search with full result details."""
        query_embedding = self.embedding_model.encode([query], show_progress_bar=False).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        formatted_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })
        
        return formatted_results
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def reset(self):
        """Clear the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except:
            pass
