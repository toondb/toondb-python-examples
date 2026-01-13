
import json
from typing import List, Dict, Any, Tuple
from sochdb import Database, DatabaseError
from config import DB_PATH, VECTOR_DIM

class ShopDB:
    def __init__(self, path: str = DB_PATH):
        self.db = Database.open(path)
        
    def setup_shop(self):
        """Initialize namespace and collection."""
        try:
            self.db.create_namespace("shop")
        except Exception:
            pass # Ignore if exists

        with self.db.use_namespace("shop") as ns:
            try:
                ns.create_collection(
                    "products", 
                    dimension=VECTOR_DIM,
                    enable_hybrid_search=True # Crucial for SKU search
                )
                print("Created 'products' collection.")
            except Exception as e:
                print(f"Setup note: {e}")

    def ingest_products(self, products: List[Dict]):
        """Ingest product vectors and metadata."""
        ns = self.db.namespace("shop")
        col = ns.collection("products")
        
        batch = []
        for p in products:
            # Combined text for keyword search (Title + SKU + Description)
            content = f"{p['sku']} {p['title']} {p['description']}"
            batch.append((p['id'], p['vector'], p, content))
            
            if len(batch) >= 100:
                col.insert_batch(batch)
                batch = []
        
        if batch:
            col.insert_batch(batch)
            
    def ingest_graph(self, edges: List[Dict]):
        """Ingest graph edges."""
        # Using FFI add_edge
        for edge in edges:
            self.db.add_edge(
                "shop",
                edge["from_id"],
                edge["type"],
                edge["to_id"],
                edge.get("properties")
            )

    def ingest_temporal(self, entries: List[Dict]):
        """Ingest temporal data via direct KV writes (simulating internal storage)."""
        # Format: _graph/{ns}/temporal/{node}/{edge_type}_{uuid} -> JSON
        # This matches what sochdb_query_temporal_graph expects to scan
        import uuid
        
        with self.db.transaction() as txn:
            for entry in entries:
                key = f"_graph/shop/temporal/{entry['node_id']}/{entry['type']}_{uuid.uuid4()}".encode()
                val = json.dumps({
                    "valid_from": int(entry["valid_from"]),
                    "valid_until": int(entry["valid_until"]),
                    "edge_type": entry["type"],
                    "value": entry["value"]
                }).encode()
                txn.put(key, val)

    def hybrid_search(self, text: str, vector: List[float] = None, k: int = 10, alpha: float = 0.5) -> List[Dict]:
        """Run hybrid search."""
        ns = self.db.namespace("shop")
        col = ns.collection("products")
        
        if vector:
            results = col.hybrid_search(vector=vector, text_query=text, k=k, alpha=alpha)
        else:
            results = col.keyword_search(query=text, k=k)
            
        return [
            {"id": r.id, "score": r.score, "metadata": r.metadata} 
            for r in results
        ]

    def get_related(self, product_id: str) -> Dict:
        """Fetch related products via graph traversal."""
        nodes, edges = self.db.traverse("shop", product_id, max_depth=1)
        return {"nodes": nodes, "edges": edges}

    def query_price_history(self, product_id: str, timestamp: int) -> List[Dict]:
        """Query price at specific time."""
        # mode 0 = POINT_IN_TIME
        try:
            # Wrapper around FFI query_temporal_graph if available in SDK
            # checking database.py showed `query_temporal_graph` around line 2000
            # Assuming it's exposed as `query_temporal_graph`
            results = self.db.query_temporal_graph(
                namespace="shop",
                node_id=product_id,
                mode="point_in_time",
                timestamp=timestamp,
                edge_type="PRICE"
            )
            return results
        except AttributeError:
             # Fallback if I misread the SDK or it's named differently
             print("WARN: query_temporal_graph not found on db object")
             return []
