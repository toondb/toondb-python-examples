
import numpy as np
import uuid
import sochdb
from sochdb import CollectionConfig, Database
from typing import List, Dict, Any, Tuple
from saas_simulation.config import DB_PATH, ALPHA_VALUES

class SaaSDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.db = Database.open(db_path)

    def setup_tenant(self, tenant_id: str):
        """
        Create namespace and collections for a tenant.
        Collections:
        - kb_docs: hybrid search (vector + bm25)
        - chat_memories: vector only (or hybrid if needed)
        - llm_cache: semantic cache
        """
        ns = self.db.get_or_create_namespace(tenant_id)
        
        # Collection: Knowledge Base
        try:
            config = CollectionConfig(
                name="kb_docs", 
                dimension=1536, 
                enable_hybrid_search=True, 
                content_field="text"
            )
            ns.create_collection(config) 
        except Exception as e:
            # Collection might already exist
            pass

        try:
            # Standard vector collection (assumed no hybrid needed for memory unless specified)
            config = CollectionConfig(name="chat_memories", dimension=1536)
            ns.create_collection(config)
        except:
            pass
            
        try:
            # Cache collection
            config = CollectionConfig(name="llm_responses", dimension=1536)
            ns.create_collection(config)
        except:
            pass

    def ingest_kb(self, tenant_id: str, chunks: List[Dict]):
        ns = self.db.get_or_create_namespace(tenant_id)
        collection = ns.collection("kb_docs")
        
        # Batch insert
        # collection.insert takes (vectors, metadata, ids) or list of objects?
        # Checking typical SDK usage: insert(vectors=..., metadata=..., ids=...)
        # or add(documents=...)
        
        # Let's assume a simplified bulk insert method exists or loop
        # For simulation speed, we'll try to batch if possible.
        
        # Transforming to columns
        ids = [c["id"] for c in chunks]
        vectors = [c["vector"] for c in chunks]
        metadatas = []
        for c in chunks:
            # Flatten or keep as dict? SDK usually takes dict
            # Ensure 'text' field is present for BM25
            meta = c["metadata"].copy()
            meta["text"] = c["text"] 
            
            # Insert individually if batch not supported reliably or for simplicity
            collection.insert(id=c["id"], vector=c["vector"], metadata=meta)

    def ingest_memories(self, tenant_id: str, memories: List[Dict]):
        ns = self.db.get_or_create_namespace(tenant_id)
        collection = ns.collection("chat_memories")
        
        for m in memories:
            meta = m["metadata"].copy()
            meta["text"] = m["text"]
            meta["user_id"] = m["user_id"]
            collection.insert(id=m["id"], vector=m["vector"], metadata=meta)

    def ingest_tickets(self, tenant_id: str, tickets: List[Dict]):
        # Store in KV: ticket state
        import json
        with self.db.transaction() as txn:
            for t in tickets:
                # Key format: tenant_id/tickets/{id}
                key = f"{tenant_id}/tickets/{t['id']}".encode("utf-8")
                value = json.dumps(t).encode("utf-8")
                txn.put(key, value)

    def hybrid_search(self, tenant_id: str, query_text: str, query_vec: List[float], alpha: float = 0.5, k: int = 5):
        """
        Perform hybrid search on kb_docs.
        Alpha: 1.0 = vector only, 0.0 = keyword only
        """
        ns = self.db.get_or_create_namespace(tenant_id)
        collection = ns.collection("kb_docs")
        
        results = collection.hybrid_search(
            vector=query_vec,
            text_query=query_text,
            k=k,
            alpha=0.5
        )
        return results

    def cache_lookup(self, tenant_id: str, query_vec: List[float], threshold: float = 0.7) -> Tuple[bool, Any]:
        """
        Check semantic cache using database-level cache.
        Returns (hit, cached_response)
        """
        cache_name = f"{tenant_id}_responses"
        result = self.db.cache_get(cache_name, query_vec, threshold)
        
        if result is not None:
            return True, result
        return False, None

    def cache_put(self, tenant_id: str, query_vec: List[float], response: str, query_text: str):
        """Store in database-level semantic cache."""
        cache_name = f"{tenant_id}_responses"
        self.db.cache_put(
            cache_name=cache_name,
            key=query_text,
            value=response,
            embedding=query_vec,
            ttl_seconds=3600  # 1 hour TTL
        )

    def close(self):
        self.db.close()
