
import os
import shutil
import time
import uuid
from .config import DB_PATH, TEST_QUERIES, CACHE_PAIRS, VECTOR_DIM, ACRONYMS
from .data_gen import DataGenerator
from .db_ops import HospitalDB

def run_simulation():
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        
    print("=== Healthcare Assistant (Offline/Embedded) ===")
    db = HospitalDB(DB_PATH)
    
    # 1. Generate & Ingest
    gen = DataGenerator()
    chunks = gen.generate_guidelines()
    
    # Enrich metadata with text for display
    for c in chunks:
        c["metadata"]["text"] = c["text"]
        
    start_t = time.time()
    db.ingest_chunks(chunks)
    print(f"Ingested {len(chunks)} chunks in {time.time()-start_t:.2f}s")
    
    # 2. Acronym Search Test (Hybrid)
    print("\n[Acronym Search Test]")
    hits = 0
    total = 0
    
    for q in TEST_QUERIES:
        query_text = q["q"]
        target_acr = q["target"]
        
        # Mock vector for query (using the acronym vector from generator logic)
        # In real app, we'd use an embedder. Here we pick the vector of the target acronym + noise
        base_vec = gen.acronym_vectors[target_acr]
        q_vec = (base_vec + [0.01]*VECTOR_DIM).tolist() # noise handled by numpy usually, but here simple list add fail? 
        # Fix vector math:
        import numpy as np
        q_vec = (gen.acronym_vectors[target_acr] + np.random.randn(VECTOR_DIM)*0.01).tolist()
        
        start_t = time.time()
        results = db.search(query_text, q_vec, k=5)
        latency_ms = (time.time() - start_t) * 1000
        
        # Check recall
        found = False
        for r in results:
            if r["metadata"].get("topic") == target_acr:
                found = True
                break
        
        status = "HIT" if found else "MISS"
        if found: hits += 1
        total += 1
        
        print(f"Q: '{query_text}' -> {status} ({latency_ms:.1f}ms)")
        # Calculate size savings
        j_size, t_size = db.compare_formats(results)
        savings = (1 - t_size/j_size) * 100
        print(f"   Payload: JSON={j_size}b, TOON={t_size}b (Savings: {savings:.1f}%)")

    print(f"Recall: {hits}/{total}")

    # 3. Semantic Cache Test
    print("\n[Semantic Cache Test]")
    for q1, q2 in CACHE_PAIRS:
        # Vector for q1 (mock - random)
        v1 = np.random.randn(VECTOR_DIM).tolist()
        
        # 1st Query: Miss -> Compute -> Save
        print(f"1. Ask: '{q1}'")
        cached = db.cache_lookup(q1, v1)
        if cached:
            print("   -> Unexpected HIT (should be empty)")
        else:
            print("   -> MISS (Computing...)")
            # Simulate "Computing"
            ans = f"Standard protocol for {q1} is 500mg BID."
            db.cache_save(q1, ans, v1)
            
        # 2nd Query: Paraphrase
        print(f"2. Ask: '{q2}' (Paraphrase)")
        # v2 should be similar to v1
        v2 = (np.array(v1) + np.random.randn(VECTOR_DIM)*0.05).tolist() # High similarity
        
        start_t = time.time()
        cached = db.cache_lookup(q2, v2)
        latency_ms = (time.time() - start_t) * 1000
        
        if cached:
            print(f"   -> HIT! content='{cached[:30]}...' ({latency_ms:.2f}ms)")
        else:
            print(f"   -> MISS (Failed to match)")

    print("\nSimulation Complete.")

if __name__ == "__main__":
    run_simulation()
