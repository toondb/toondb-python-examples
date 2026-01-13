
import threading
import time
import shutil
import os
from config import DB_PATH, NUM_DISPUTES, POLICY_DOCS
from db_ops import FintechDB

def run_concurrent_test(db: FintechDB, dispute_id: str):
    print(f"\n[Concurrent Test] Agents attacking Dispute {dispute_id}...")
    
    results = []
    
    def agent_worker(agent_name, new_status, justification):
        res = db.process_dispute(agent_name, dispute_id, new_status, justification)
        results.append((agent_name, res))
        print(f"  -> Agent {agent_name} finished: {res}")

    t1 = threading.Thread(target=agent_worker, args=("Agent_A", "resolved", "Customer provided proof"))
    t2 = threading.Thread(target=agent_worker, args=("Agent_B", "rejected", "Policy violation"))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    return results

def run_simulation():
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        
    print("=== Fintech Copilot Transaction Simulation ===")
    db = FintechDB(DB_PATH)
    
    # 1. Ingest Policies
    print("Ingesting Policies...")
    db.ingest_policies(POLICY_DOCS)
    
    # 2. Seed Disputes
    print(f"Seeding {NUM_DISPUTES} disputes...")
    target_dispute_id = "dsp_001"
    
    for i in range(NUM_DISPUTES):
        d_id = f"dsp_{i:03d}"
        amount = 100 + (i * 10)
        db.create_dispute({
            "id": d_id,
            "reason": "goods_not_received",
            "amount": amount,
            "status": "new",
            "customer": f"cust_{i}"
        })

    # 3. Concurrent Updates (Adversarial Case)
    # Both read "new", one tries to set "resolved", other "rejected"
    # SochDB SSI should force one to retry
    results = run_concurrent_test(db, target_dispute_id)
    
    # Verify State
    final_dispute = db.get_dispute(target_dispute_id)
    print(f"\n[Verification] Final State for {target_dispute_id}:")
    print(f"  Status: {final_dispute['status']}")
    print(f"  Last Updated By: {final_dispute['last_updated_by']}")
    
    # Check Ledger
    ledger = db.get_ledger()
    related_ledger = [l for l in ledger if l["dispute_id"] == target_dispute_id]
    print(f"  Ledger Entries for ID: {len(related_ledger)}")
    for l in related_ledger:
        print(f"    - {l['old']} -> {l['new']} (Type: {l['type']})")
        
    # Check Audit
    audit = db.get_audit_trail()
    related_audit = [a for a in audit if a["resource"] == target_dispute_id]
    print(f"  Audit Logs for ID: {len(related_audit)}")
    for a in related_audit:
        print(f"    - [{a['actor']}] {a['action']} : {a['justification']}")

    # 4. Correctness Check
    # If both succeeded (one via retry), we should have 2 state changes in history?
    # Actually, process_dispute logic:
    # Read status. If status == new_status, return NO_OP.
    # T1: New -> Resolved.
    # T2: New -> Rejected.
    # If T1 commits first, Status=Resolved.
    # T2 retries. Reads Status=Resolved.
    # Logic: If T2 still wants to set Rejected, it overwrites Resolved -> Rejected.
    # So we expect 2 ledger entries: New->Resolved, Resolved->Rejected.
    # UNLESS logic checks "if status != new" and aborts?
    # My logic: `if current_status == new_status: NO_OP`.
    # So T2 (Rejected) != Resolved. It proceeds.
    # So we expect 2 updates.
    
    assert len(related_ledger) == 2, f"Expected 2 ledger entries, got {len(related_ledger)}"
    assert len(related_audit) == 2, f"Expected 2 audit logs, got {len(related_audit)}"
    print("\n[SUCCESS] Correctness Verified: ACID transactions ensured no lost updates.")
    
    # 5. Volume Test (Throughput)
    print("\n[Volume Test] Processing remaining disputes...")
    start_t = time.time()
    processed = 0
    for i in range(1, NUM_DISPUTES): # Skip 0 (already done)
        d_id = f"dsp_{i:03d}"
        db.process_dispute("Agent_Batch", d_id, "resolved", "Auto-resolve")
        processed += 1
    duration = time.time() - start_t
    tps = processed / duration
    print(f"Processed {processed} transactions in {duration:.2f}s ({tps:.1f} txn/sec)")
    
    print("\nSimulation Complete.")

if __name__ == "__main__":
    run_simulation()
