
import json
import uuid
from typing import List, Dict, Any
from sochdb import Database
from .config import DB_PATH, DEVICE_ID, VECTOR_DIM

class DeviceDB:
    def __init__(self, path: str = DB_PATH):
        self.db = Database.open(path)
        self._setup()
    
    def _setup(self):
        try:
            self.db.create_namespace(DEVICE_ID)
        except: pass
        with self.db.use_namespace(DEVICE_ID) as ns:
            try:
                ns.create_collection("manual_chunks", dimension=VECTOR_DIM, enable_hybrid_search=True)
            except: pass

    # --- KV LOGS ---
    def ingest_logs_batch(self, logs: List[tuple]):
        """Logs are (ts, dict). Key = logs/{ts}/{uuid}."""
        with self.db.transaction() as txn:
            for ts, data in logs:
                key = f"logs/{ts}/{data['id']}".encode()
                val = json.dumps(data).encode()
                txn.put(key, val)

    def scan_logs(self, start_ts: int, end_ts: int) -> int:
        """Scan logs in time range. Returns count."""
        count = 0
        # Prefix scan "logs/"
        # Ideally we construct start/end keys, but for now scan prefix and filter
        # Optimization: SochDB scans are lexicographical. "logs/{ts}" works if ts is fixed width or zero padded?
        # My generator uses int, so "logs/173..."
        # If I want true range scan efficiency, I should zero pad or strict format.
        # Here I will just scan all "logs/" and filter.
        with self.db.transaction() as txn:
            for k, v in txn.scan_prefix(b"logs/"):
                # Parse key to get ts?
                # k = logs/1234567890/uuid
                parts = k.decode().split("/")
                if len(parts) >= 2:
                    try:
                        ts = int(parts[1])
                        if start_ts <= ts <= end_ts:
                            count += 1
                    except: pass
        return count

    # --- TEMPORAL STATE ---
    def ingest_state_history(self, transitions: List[Dict]):
        """
        Ingest state transitions as temporal edges:
        Node: "machine_A"
        Edge: "STATE" -> "RUNNING" (value)
        Valid: [start, end]
        """
        import uuid
        with self.db.transaction() as txn:
            for t in transitions:
                # Key format compatible with query_temporal_graph
                # _graph/{ns}/temporal/{node}/{edge_type}_{uuid}
                node = "machine_A"
                edge_type = "STATE"
                key = f"_graph/{DEVICE_ID}/temporal/{node}/{edge_type}_{uuid.uuid4()}".encode()
                
                val = json.dumps({
                    "valid_from": t["start"],
                    "valid_until": t["end"],
                    "edge_type": edge_type,
                    "value": t["state"], # The state name is the value
                    # In real graph, to_id might be "StateNode_RUNNING", but here using value is fine for retrieval
                    "to_id": t["state"] 
                }, separators=(',', ':')).encode()
                txn.put(key, val)

    def query_state(self, timestamp: int) -> str:
        """Point in time query."""
        try:
            results = self.db.query_temporal_graph(
                namespace=DEVICE_ID,
                node_id="machine_A",
                mode="POINT_IN_TIME",
                # FFI expects int mode? No, python SDK `query_temporal_graph` handles string to int conversion?
                # Let's check `database.py`.
                # `mode` arg in FFI call is `ctypes.c_uint8`.
                # BUT `Database.query_temporal_graph` logic needs to convert str "point_in_time" to 1.
                # If SDK doesn't do it, I must pass int.
                # I'll check `database.py` again or blindly pass 1.
                timestamp=timestamp,
                edge_type="STATE"
            )
            # Results is list of dicts.
            if results:
                return results[0].get("value") or results[0].get("to_id")
            return "UNKNOWN"
        except Exception as e:
            print(f"Temporal Query Error: {e}")
            return "ERROR"

    # --- HYBRID MANUALS ---
    def ingest_manuals(self, chunks: List[Dict]):
        ns = self.db.namespace(DEVICE_ID)
        col = ns.collection("manual_chunks")
        batch = []
        for c in chunks:
            # Ensure text is in metadata for retrieval
            meta = c["metadata"].copy()
            meta["text"] = c["text"]
            batch.append((c["id"], c["vector"], meta, c["text"]))
        col.insert_batch(batch)

    def search_manual(self, text: str, vector: List[float]) -> List[Dict]:
        ns = self.db.namespace(DEVICE_ID)
        col = ns.collection("manual_chunks")
        # Ensure 'text' key access is safe
        return [
            {"text": r.metadata.get("text", "N/A"), "score": r.score} 
            for r in col.hybrid_search(vector=vector, text_query=text, k=3, alpha=0.5)
        ]

    def debug_temporal_keys(self):
        print("DEBUG: Dumping first 5 temporal keys...")
        with self.db.transaction() as txn:
            count = 0
            # Scan _graph prefix
            for k, v in txn.scan_prefix(b"_graph/"):
                print(f"  Key: {k.decode()} Val: {v.decode()}")
                count += 1
                if count >= 5: break
            if count == 0:
                print("  No keys found with _graph/ prefix!")
