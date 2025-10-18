"""
Simple in-memory vector store using TF-IDF for semantic search.
"""
from typing import List, Dict, Any
from collections import Counter
import math
import re


class VectorStore:
    """Simple TF-IDF based vector store."""
    
    def __init__(self, collection_name: str = "axlewave_docs", persist_directory: str = "./chroma_db"):
        self.documents = []
        self.metadatas = []
        self.ids = []
        self.idf = {}
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        return re.findall(r'\w+', text.lower())
    
    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Compute term frequency."""
        counter = Counter(tokens)
        total = len(tokens)
        return {term: count / total for term, count in counter.items()}
    
    def _compute_idf(self):
        """Compute inverse document frequency."""
        doc_count = len(self.documents)
        term_doc_count = Counter()
        
        for doc in self.documents:
            tokens = set(self._tokenize(doc))
            term_doc_count.update(tokens)
        
        self.idf = {term: math.log(doc_count / count) for term, count in term_doc_count.items()}
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Compute cosine similarity between two TF-IDF vectors."""
        common_terms = set(vec1.keys()) & set(vec2.keys())
        if not common_terms:
            return 0.0
        
        dot_product = sum(vec1[term] * vec2[term] for term in common_terms)
        mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        
        return dot_product / (mag1 * mag2) if mag1 and mag2 else 0.0
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]] = None, ids: List[str] = None):
        """Add documents to the vector store."""
        if ids is None:
            ids = [f"doc_{len(self.documents) + i}" for i in range(len(documents))]
        
        self.documents.extend(documents)
        self.metadatas.extend(metadatas or [{} for _ in documents])
        self.ids.extend(ids)
        self._compute_idf()
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using TF-IDF."""
        query_tokens = self._tokenize(query)
        query_tf = self._compute_tf(query_tokens)
        query_vec = {term: tf * self.idf.get(term, 0) for term, tf in query_tf.items()}
        
        scores = []
        for i, doc in enumerate(self.documents):
            doc_tokens = self._tokenize(doc)
            doc_tf = self._compute_tf(doc_tokens)
            doc_vec = {term: tf * self.idf.get(term, 0) for term, tf in doc_tf.items()}
            
            similarity = self._cosine_similarity(query_vec, doc_vec)
            scores.append((i, similarity))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for i, score in scores[:n_results]:
            results.append({
                'id': self.ids[i],
                'document': self.documents[i],
                'metadata': self.metadatas[i],
                'distance': 1 - score
            })
        
        return results
    
    def query(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Alias for search method."""
        return self.search(query, n_results)
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks


class AxleWaveVectorStore(VectorStore):
    """AxleWave-specific vector store wrapper."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        super().__init__(persist_directory=persist_directory)
    
    def create_collection(self):
        """Create collection - no-op for in-memory store."""
        pass
