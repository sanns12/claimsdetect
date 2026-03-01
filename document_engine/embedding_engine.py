"""
Embedding Engine for Document Intelligence
Converts text to vector embeddings using sentence transformers
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import hashlib
import pickle
import os

class EmbeddingEngine:
    def __init__(self, config):
        self.config = config
        self.model_name = config.EMBEDDING_MODEL
        self.model = None
        self.cache = {}  # Simple cache for embeddings
        self.cache_file = "embedding_cache.pkl"
        
        # Load cache if exists
        self._load_cache()
    
    def _load_model(self):
        """Lazy load model to save memory"""
        if self.model is None:
            print(f"📥 Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print("✅ Model loaded successfully")
    
    def _load_cache(self):
        """Load embedding cache from disk"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    self.cache = pickle.load(f)
                print(f"📦 Loaded {len(self.cache)} cached embeddings")
            except:
                self.cache = {}
    
    def _save_cache(self):
        """Save embedding cache to disk"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
        except:
            pass
    
    def _get_text_hash(self, text: str) -> str:
        """Create hash of text for caching"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text
        
        Args:
            text: Input text
            
        Returns:
            numpy array of embeddings
        """
        if not text or len(text.strip()) == 0:
            return np.zeros(384)  # Return zero vector for empty text
        
        # Check cache first
        text_hash = self._get_text_hash(text)
        if text_hash in self.cache:
            return self.cache[text_hash]
        
        # Load model and generate embedding
        self._load_model()
        
        # Generate embedding
        embedding = self.model.encode(text, normalize_embeddings=True)
        
        # Cache it
        self.cache[text_hash] = embedding
        self._save_cache()
        
        return embedding
    
    def get_batch_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts efficiently
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embeddings
        """
        if not texts:
            return []
        
        # Check cache for each text
        uncached_texts = []
        uncached_indices = []
        embeddings = [None] * len(texts)
        
        for i, text in enumerate(texts):
            if not text or len(text.strip()) == 0:
                embeddings[i] = np.zeros(384)
            else:
                text_hash = self._get_text_hash(text)
                if text_hash in self.cache:
                    embeddings[i] = self.cache[text_hash]
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            self._load_model()
            new_embeddings = self.model.encode(uncached_texts, normalize_embeddings=True)
            
            # Cache and assign
            for idx, text, emb in zip(uncached_indices, uncached_texts, new_embeddings):
                text_hash = self._get_text_hash(text)
                self.cache[text_hash] = emb
                embeddings[idx] = emb
            
            self._save_cache()
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        self._load_model()
        return self.model.get_sentence_embedding_dimension()
    
    def clear_cache(self):
        """Clear embedding cache"""
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print("🧹 Embedding cache cleared")