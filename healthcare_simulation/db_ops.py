
import json
import time
from typing import List, Dict, Tuple
from sochdb import Database, DatabaseError
from .config import DB_PATH, VECTOR_DIM

class HospitalDB:
    def __init__(self, path: str = DB_PATH):
        self.db = Database.open(path)
        self._setup()
        
    def _setup(self):
        try:
            self.db.create_namespace("hospital_a")
        except: pass
        
        with self.db.use_namespace("hospital_a") as ns:
            try:
                ns.create_collection("guidelines", dimension=VECTOR_DIM, enable_hybrid_search=True)
            except: pass

    def ingest_chunks(self, chunks: List[Dict]):
        ns = self.db.namespace("hospital_a")
        col = ns.collection("guidelines")
        
        batch = []
        for c in chunks:
            batch.append((c["id"], c["vector"], c["metadata"], c["text"]))
            
            if len(batch) >= 100:
                col.insert_batch(batch)
                batch = []
        if batch:
            col.insert_batch(batch)

    def search(self, query: str, vector: List[float], k: int = 5) -> List[Dict]:
        """Hybrid search combining keyword (acronyms) + vector."""
        ns = self.db.namespace("hospital_a")
        col = ns.collection("guidelines")
        
        results = col.hybrid_search(vector=vector, text_query=query, k=k, alpha=0.5)
        
        return [
            {"id": r.id, "score": r.score, "metadata": r.metadata, "text": r.metadata.get("text", "")} 
            for r in results
        ]

    def cache_lookup(self, query_text: str, vector: List[float]) -> str:
        # Cache key is usually the query text, but lookup is by vector
        return self.db.cache_get("med_qa", vector, threshold=0.9)

    def cache_save(self, query_text: str, answer: str, vector: List[float]):
        self.db.cache_put("med_qa", query_text, answer, vector, ttl_seconds=3600)

    def compare_formats(self, results: List[Dict]) -> Tuple[int, int]:
        """Measure JSON vs TOON size for a result set."""
        # JSON
        json_str = json.dumps(results)
        json_size = len(json_str.encode())
        
        # TOON (Simplified simulation of TOON format)
        # result[N]{cols}: val,val; val,val...
        # Assuming we send [id, topic, score]
        header = f"result[{len(results)}]{{id,topic,score}}:"
        body = ""
        for r in results:
            topic = r["metadata"].get("topic", "")
            body += f"{r['id']},{topic},{r['score']:.4f};"
        
        toon_str = header + body
        toon_size = len(toon_str.encode())
        
        return json_size, toon_size
