"""
Similarity Checker for Document Intelligence
Compares documents using cosine similarity
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict, Any
from collections import defaultdict

class SimilarityChecker:
    def __init__(self, config, embedding_engine):
        self.config = config
        self.embedding_engine = embedding_engine
        self.threshold = config.SIMILARITY_THRESHOLD
    
    def compare_documents(self, doc1_text: str, doc2_text: str) -> float:
        """
        Compare two documents using cosine similarity
        
        Args:
            doc1_text: First document text
            doc2_text: Second document text
            
        Returns:
            Similarity score between 0 and 1
        """
        emb1 = self.embedding_engine.get_embedding(doc1_text)
        emb2 = self.embedding_engine.get_embedding(doc2_text)
        
        # Calculate cosine similarity
        similarity = cosine_similarity([emb1], [emb2])[0][0]
        
        return float(similarity)
    
    def compare_with_all(self, target_text: str, reference_texts: List[str]) -> List[float]:
        """
        Compare target text with multiple reference texts
        
        Args:
            target_text: Text to compare
            reference_texts: List of reference texts
            
        Returns:
            List of similarity scores
        """
        if not reference_texts:
            return []
        
        # Get target embedding
        target_emb = self.embedding_engine.get_embedding(target_text)
        
        # Get reference embeddings
        ref_embs = self.embedding_engine.get_batch_embeddings(reference_texts)
        
        # Calculate similarities
        similarities = []
        for ref_emb in ref_embs:
            sim = cosine_similarity([target_emb], [ref_emb])[0][0]
            similarities.append(float(sim))
        
        return similarities
    
    def find_most_similar(self, target_text: str, reference_texts: List[str], top_k: int = 3) -> List[Tuple[int, float]]:
        """
        Find most similar documents to target
        
        Args:
            target_text: Text to compare
            reference_texts: List of reference texts
            top_k: Number of top matches to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        similarities = self.compare_with_all(target_text, reference_texts)
        
        # Get top k indices
        if len(similarities) <= top_k:
            indices = list(range(len(similarities)))
        else:
            indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [(idx, similarities[idx]) for idx in indices]
    
    def detect_anomalies(self, texts: List[str], threshold: float = None) -> List[Tuple[int, float]]:
        """
        Detect anomalous documents that are too different from others
        
        Args:
            texts: List of document texts
            threshold: Similarity threshold (default from config)
            
        Returns:
            List of (index, avg_similarity) for anomalies
        """
        if len(texts) < 3:
            return []
        
        if threshold is None:
            threshold = self.threshold
        
        # Get all embeddings
        embeddings = self.embedding_engine.get_batch_embeddings(texts)
        
        # Calculate centroid
        centroid = np.mean(embeddings, axis=0)
        
        # Calculate similarity to centroid
        similarities = []
        for emb in embeddings:
            sim = cosine_similarity([emb], [centroid])[0][0]
            similarities.append(float(sim))
        
        # Find anomalies
        anomalies = []
        for i, sim in enumerate(similarities):
            if sim < threshold:
                anomalies.append((i, sim))
        
        return anomalies
    
    def calculate_document_set_consistency(self, texts: List[str]) -> Dict[str, Any]:
        """
        Calculate overall consistency of a document set
        
        Args:
            texts: List of document texts
            
        Returns:
            Dictionary with consistency metrics
        """
        if len(texts) < 2:
            return {
                "consistency_score": 1.0,
                "pairwise_similarities": [],
                "mean_similarity": 1.0,
                "std_similarity": 0.0,
                "min_similarity": 1.0,
                "max_similarity": 1.0
            }
        
        # Get embeddings
        embeddings = self.embedding_engine.get_batch_embeddings(texts)
        
        # Calculate pairwise similarities
        pairwise_sims = []
        n = len(embeddings)
        
        for i in range(n):
            for j in range(i+1, n):
                sim = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
                pairwise_sims.append(float(sim))
        
        # Calculate statistics
        mean_sim = np.mean(pairwise_sims) if pairwise_sims else 1.0
        std_sim = np.std(pairwise_sims) if pairwise_sims else 0.0
        min_sim = min(pairwise_sims) if pairwise_sims else 1.0
        max_sim = max(pairwise_sims) if pairwise_sims else 1.0
        
        # Overall consistency score (can be used in document scoring)
        consistency_score = mean_sim * (1 - std_sim)  # Penalize high variance
        
        return {
            "consistency_score": float(consistency_score),
            "pairwise_similarities": pairwise_sims,
            "mean_similarity": float(mean_sim),
            "std_similarity": float(std_sim),
            "min_similarity": float(min_sim),
            "max_similarity": float(max_sim),
            "num_comparisons": len(pairwise_sims)
        }
    
    def check_field_consistency(self, extracted_fields: List[Dict[str, Any]]) -> List[str]:
        """
        Check consistency of extracted fields across multiple documents
        
        Args:
            extracted_fields: List of extracted field dictionaries
            
        Returns:
            List of mismatch flags
        """
        mismatch_flags = []
        
        if len(extracted_fields) < 2:
            return mismatch_flags
        
        # Check amounts
        amounts = [f.get('amounts', []) for f in extracted_fields]
        if amounts and all(amounts):
            # Flatten and compare
            all_amounts = [a for sublist in amounts for a in sublist]
            if len(set(all_amounts)) > 1:
                mismatch_flags.append("amount_mismatch_across_docs")
        
        # Check diagnosis codes
        diagnoses = [f.get('diagnosis_codes', []) for f in extracted_fields]
        if diagnoses and all(diagnoses):
            all_diag = [d for sublist in diagnoses for d in sublist]
            if len(set(all_diag)) > 1:
                mismatch_flags.append("diagnosis_mismatch_across_docs")
        
        # Check procedure codes
        procedures = [f.get('procedure_codes', []) for f in extracted_fields]
        if procedures and all(procedures):
            all_proc = [p for sublist in procedures for p in sublist]
            if len(set(all_proc)) > 1:
                mismatch_flags.append("procedure_mismatch_across_docs")
        
        # Check provider names
        providers = [f.get('provider_name') for f in extracted_fields if f.get('provider_name')]
        if len(providers) > 1 and len(set(providers)) > 1:
            mismatch_flags.append("provider_mismatch_across_docs")
        
        return mismatch_flags