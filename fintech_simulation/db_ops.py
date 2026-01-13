
import json
import time
import uuid
import random
from typing import Dict, Any, List, Optional
from sochdb import Database, DatabaseError, TransactionError

class FintechDB:
    def __init__(self, path: str):
        self.db = Database.open(path)
        self._init_schema()

    def _init_schema(self):
        """Setup hybrid search collection for policies."""
        try:
            self.db.create_namespace("bank_ops")
        except: pass
        
        with self.db.use_namespace("bank_ops") as ns:
            try:
                ns.create_collection("policy_docs", dimension=1536, enable_hybrid_search=True)
            except: pass

    # --- SQL Table Simulation (KV) ---
    def _get_row(self, txn, table: str, pk: str) -> Optional[Dict]:
        key = f"table/{table}/{pk}".encode()
        data = txn.get(key)
        return json.loads(data) if data else None

    def _put_row(self, txn, table: str, pk: str, data: Dict):
        key = f"table/{table}/{pk}".encode()
        txn.put(key, json.dumps(data).encode())

    # --- Core Workflows ---
    
    def ingest_policies(self, policies: List[Dict]):
        ns = self.db.namespace("bank_ops")
        col = ns.collection("policy_docs")
        batch = []
        for p in policies:
            batch.append((p["id"], p["vector"], p, p["text"]))
        col.insert_batch(batch)

    def create_dispute(self, dispute: Dict):
        """Non-transactional setup helper."""
        with self.db.transaction() as txn:
            self._put_row(txn, "disputes", dispute["id"], dispute)
    
    def process_dispute(self, agent_id: str, dispute_id: str, new_status: str, justification: str) -> str:
        """
        Transactional update:
        1. Read dispute
        2. Check policy (simulated)
        3. Update dispute
        4. Add ledger entry
        5. Log audit
        """
        # Retry loop for SSI
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with self.db.transaction() as txn:
                    # 1. READ
                    dispute = self._get_row(txn, "disputes", dispute_id)
                    if not dispute:
                        return "NOT_FOUND"
                    
                    # Simulate conflict window
                    time.sleep(0.01) 
                    
                    # 2. LOGIC
                    current_status = dispute.get("status", "new")
                    if current_status == new_status:
                        return "NO_OP"

                    # 3. WRITE UPDATES
                    dispute["status"] = new_status
                    dispute["last_updated_by"] = agent_id
                    dispute["updated_at"] = time.time()
                    self._put_row(txn, "disputes", dispute_id, dispute)

                    # 4. LEDGER
                    ledger_entry = {
                        "id": str(uuid.uuid4()),
                        "dispute_id": dispute_id,
                        "type": "STATUS_CHANGE",
                        "old": current_status,
                        "new": new_status,
                        "amount": dispute.get("amount", 0)
                    }
                    self._put_row(txn, "ledger", ledger_entry["id"], ledger_entry)

                    # 5. AUDIT (Append only log)
                    audit_entry = {
                        "timestamp": time.time(),
                        "actor": agent_id,
                        "action": "UPDATE_DISPUTE",
                        "resource": dispute_id,
                        "justification": justification
                    }
                    # Audit key: audit/{timestamp}_{uuid}
                    audit_key = f"audit/{audit_entry['timestamp']}_{uuid.uuid4()}".encode()
                    txn.put(audit_key, json.dumps(audit_entry).encode())
                
                # If we get here, commit succeeded
                return "SUCCESS"

            except (TransactionError, DatabaseError) as e:
                # SochDB might raise DatabaseError on put if txn is aborted eagerly
                err_msg = str(e).lower()
                if "conflict" in err_msg or "serialization" in err_msg or "failed to put" in err_msg:
                    print(f"Conflict/Error detected for {agent_id}, retrying ({attempt+1}/{max_retries})... Error: {e}")
                    time.sleep(random.uniform(0.05, 0.1)) # Backoff
                    continue
                raise e
        
        return "CONFLICT_GIVEUP"

    def get_audit_trail(self) -> List[Dict]:
        """Scan audit logs."""
        logs = []
        with self.db.transaction() as txn:
            # Use scan_prefix for 'audit/'
            for k, v in txn.scan_prefix(b"audit/"):
                logs.append(json.loads(v))
        return sorted(logs, key=lambda x: x["timestamp"])

    def get_ledger(self) -> List[Dict]:
        rows = []
        with self.db.transaction() as txn:
            for k, v in txn.scan_prefix(b"table/ledger/"):
                rows.append(json.loads(v))
        return rows
    
    def get_dispute(self, dispute_id: str) -> Optional[Dict]:
        with self.db.transaction() as txn:
            return self._get_row(txn, "disputes", dispute_id)

