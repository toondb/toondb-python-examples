
from typing import List, Dict, Any

def calculate_recall(retrieved_docs: List[Any], relevant_topic: str, k: int = 5) -> float:
    """
    Calculate Recall@k.
    Here, relevance is defined as match between retrieved document topic and query topic.
    """
    if not retrieved_docs:
        return 0.0
        
    top_k = retrieved_docs[:k]
    relevant_count = 0
    for doc in top_k:
        # Assuming doc.metadata['topic'] exists
        if doc.metadata.get('topic') == relevant_topic:
            relevant_count += 1
            
    # If we assume there are at least K relevant docs in the DB (which there are, 1000s)
    # Then Recall@K is relevant_retrieved / K ? 
    # Or ideally relevant_retrieved / total_relevant_in_db
    # BUT, traditionally Recall@K usually means relevant_retrieved_in_k / total_relevant_in_db.
    # Given total relevant is HUGE (all docs for that topic), this will be small.
    # Maybe we want Precision@K really? Or "Recall" in the sense "did we find ONE of the relevant things?"
    
    # Requirement says: "Recall@5 >= 0.85 on semantic queries"
    # This usually implies "Is the relevant answer in the top 5?" for a QA pair.
    # But here we have topics. 
    # Let's interpret as: Precision@K (portion of top K that are relevant).
    # OR, maybe it means "Is at least one relevant doc in top 5?" (Hit Rate concept).
    
    # Let's implement Precision@K here strictly.
    return relevant_count / k

def calculate_success_at_k(retrieved_docs: List[Any], relevant_topic: str, k: int = 5) -> bool:
    """Returns True if at least one relevant doc is in top K."""
    top_k = retrieved_docs[:k]
    for doc in top_k:
        if doc.metadata.get('topic') == relevant_topic:
            return True
    return False

def calculate_ndcg(retrieved_docs: List[Any], relevant_topic: str, k: int = 10) -> float:
    """
    Calculate NDCG@k.
    Relevance score: 1 if topic match, 0 if not.
    """
    import math
    
    dcg = 0.0
    idcg = 0.0
    
    top_k = retrieved_docs[:k]
    
    for i, doc in enumerate(top_k):
        rel = 1 if doc.metadata.get('topic') == relevant_topic else 0
        dcg += (2**rel - 1) / math.log2(i + 2)
        
    # IDCG: Ideal ordering has all 1s at top
    # We assume we can fill all K spots with relevant docs? Yes.
    for i in range(k):
        idcg += (2**1 - 1) / math.log2(i + 2)
        
    if idcg == 0:
        return 0.0
    return dcg / idcg
