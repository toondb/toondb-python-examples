import time
import cProfile
import pstats
import io
from sochdb import Database, CollectionConfig
from sochdb import SearchRequest

def profile_search():
    print("=== Profiling Search Latency ===")
    
    # 1. Setup DB
    db_path = "./profile_db"
    import shutil
    try:
        shutil.rmtree(db_path)
    except:
        pass
        
    db = Database.open(db_path)
    ns = db.get_or_create_namespace("profile_tenant")
    
    # 2. Ingest Data (Simulate 1000 docs to allow measurable latency)
    print("Ingesting 1000 documents...")
    collection = ns.create_collection("docs", dimension=4, enable_hybrid_search=True, content_field="text")
    
    docs = []
    for i in range(1000):
        docs.append({
            "id": f"doc_{i}",
            "vector": [0.1, 0.2, 0.3, 0.4],
            "metadata": {"text": f"This is document number {i} with some keywords like python, rust, database."},
        })
    
    # Batch insert simulation (loop)
    start_ingest = time.time()
    for d in docs:
        collection.insert(id=d["id"], vector=d["vector"], metadata=d["metadata"])
    print(f"Ingestion took: {time.time() - start_ingest:.4f}s")
    
    # 3. Profile Vector Search (FFI)
    print("\n--- Profiling Vector Search (FFI) ---")
    req = SearchRequest(vector=[0.1, 0.2, 0.3, 0.4], k=10)
    
    start = time.time()
    for _ in range(50):
        _ = collection._vector_search(req) # Call internal method to isolate
    avg_vec = (time.time() - start) / 50 * 1000
    print(f"Avg Vector Search Latency: {avg_vec:.4f} ms")
    
    # 4. Profile Keyword Search (Python)
    print("\n--- Profiling Keyword Search (Python) ---")
    req = SearchRequest(text_query="python database", k=10)
    
    start = time.time()
    for _ in range(50):
        _ = collection._keyword_search(req) # Call internal method to isolate
    avg_key = (time.time() - start) / 50 * 1000
    print(f"Avg Keyword Search Latency: {avg_key:.4f} ms")
    
    # 5. Profile Full Hybrid Search
    print("\n--- Profiling Hybrid Search (End-to-End) ---")
    start = time.time()
    for _ in range(50):
        _ = collection.hybrid_search(vector=[0.1, 0.2, 0.3, 0.4], text_query="python database", k=10)
    avg_hybrid = (time.time() - start) / 50 * 1000
    print(f"Avg Hybrid Search Latency: {avg_hybrid:.4f} ms")
    
    # 6. Detailed cProfile for Keyword Search
    print("\n--- Detailed cProfile: Keyword Search ---")
    pr = cProfile.Profile()
    pr.enable()
    collection._keyword_search(req)
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    print(s.getvalue())

if __name__ == "__main__":
    profile_search()
