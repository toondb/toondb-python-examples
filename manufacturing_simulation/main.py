
import os
import shutil
import time
import numpy as np
from .config import DB_PATH, NUM_EVENTS, ERROR_CODES, VECTOR_DIM
from .data_gen import DataGenerator
from .db_ops import DeviceDB

def run_simulation():
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        
    print("=== Manufacturing Device Brain (IoT) ===")
    
    # Setup
    db = DeviceDB(DB_PATH)
    gen = DataGenerator()
    
    # 1. Generate Data
    logs = gen.generate_telemetry()
    transitions = gen.generate_states()
    manuals = gen.generate_manuals()
    
    # 2. Ingest
    print("\n[Ingestion & Throughput]")
    
    # Logs (KV)
    start_t = time.time()
    db.ingest_logs_batch(logs)
    dur = time.time() - start_t
    print(f"Ingested {len(logs)} logs in {dur:.2f}s ({len(logs)/dur:.1f} events/sec)")
    
    # State (Temporal)
    db.ingest_state_history(transitions)
    print(f"Ingested {len(transitions)} state transitions.")
    
    # Manuals (Hybrid)
    db.ingest_manuals(manuals)
    print(f"Ingested {len(manuals)} manual chunks.")

    # Debug Keys
    db.debug_temporal_keys()
    
    # 3. Time-Travel Correctness
    print("\n[State Reconstruction Test]")
    correct = 0
    total_checks = 10
    
    # Pick random points within transition windows
    import random
    check_points = []
    for _ in range(total_checks):
        t = random.choice(transitions)
        # Point = random time between start and end
        mid = random.randint(t["start"], t["end"])
        expected = t["state"]
        check_points.append((mid, expected))
        
    for ts, expected in check_points:
        actual = db.query_state(ts)
        match = "PASS" if actual == expected else f"FAIL (Got {actual})"
        if actual == expected: correct += 1
        print(f"T={ts}: Expected {expected} -> {match}")
        
    print(f"Correctness: {correct}/{total_checks}")
    
    # 4. Hybrid Search (Error Codes)
    print("\n[Manual Search Test]")
    target_code = "E142"
    target_text = ERROR_CODES[target_code]
    
    query = f"What does error {target_code} mean?"
    # Use vector for target_code (simulating embedding of query)
    vec = (gen.error_vectors[target_code] + np.random.randn(VECTOR_DIM)*0.01).tolist()
    
    results = db.search_manual(query, vec)
    found = False
    print(f"Query: '{query}'")
    for r in results:
        txt = r["text"]
        print(f"  - [{r['score']:.4f}] {txt[:60]}...")
        if target_code in txt:
            found = True
            
    if found:
        print("PASS: Found relevant manual chunk.")
    else:
        print("FAIL: Did not find manual chunk.")

    print("\nSimulation Complete.")

if __name__ == "__main__":
    run_simulation()
