from sochdb import Database
import shutil
import time

def test_keyword_ffi():
    db_path = "./test_kw_db"
    try:
        shutil.rmtree(db_path)
    except:
        pass
        
    db = Database.open(db_path)
    ns = db.get_or_create_namespace("test_ns")
    col = ns.create_collection("test_col", dimension=2, enable_hybrid_search=True)
    
    # Insert doc
    col.insert(
        id="doc1",
        vector=[0.1, 0.1],
        metadata={"text": "Hello world this is Python"}
    )
    
    # 1. Search via Python wrapper (which uses FFI now)
    print("Searching for 'python'...")
    res = col.keyword_search(query="python")
    print(f"Results for 'python': {len(res.results)}")
    for r in res.results:
        print(r)

    # 2. Search for 'MISSING'
    print("Searching for 'missing'...")
    res = col.keyword_search(query="missing")
    print(f"Results for 'missing': {len(res.results)}")

    # 3. Direct FFI call check
    print("Direct FFI Check:")
    ffi_res = db.ffi_collection_keyword_search("test_ns", "test_col", "python")
    print(f"Direct FFI result: {ffi_res}")
    
    # Debug: Inspect Raw Data
    print("\nRaw Data Scan:")
    prefix = f"test_ns/collections/test_col/vectors/".encode()
    with db.transaction() as txn:
        for k, v in txn.scan_prefix(prefix):
            print(f"Key: {k.decode()}")
            print(f"Val: {v.decode()}")

if __name__ == "__main__":
    test_keyword_ffi()
