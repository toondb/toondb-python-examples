#!/usr/bin/env python3
"""Test script to verify all TODO fixes work correctly"""
import os
import sys
import shutil


from sochdb import Database
from sochdb import CollectionConfig, DistanceMetric

TEST_DB = "/tmp/test_todo_fixes_db"

def cleanup():
    if os.path.exists(TEST_DB):
        shutil.rmtree(TEST_DB)

def test_all_fixes():
    cleanup()
    
    print("=" * 60)
    print("Testing All TODO Fixes")
    print("=" * 60)
    
    # Phase 1: Create data
    print("\n--- Phase 1: Create Data ---")
    db = Database.open(TEST_DB)
    ns = db.get_or_create_namespace("default")
    
    # Test create_collection with persistence
    config = CollectionConfig(name="persistent_test", dimension=4)
    col = ns.create_collection(config)
    col.insert(id="doc1", vector=[1.0, 0.0, 0.0, 0.0], metadata={"text": "first"})
    col.insert(id="doc2", vector=[0.0, 1.0, 0.0, 0.0], metadata={"text": "second"})
    print(f"✓ Created collection with {col.count()} documents")
    
    # Test list_collections
    collections = ns.list_collections()
    print(f"✓ list_collections: {collections}")
    assert "persistent_test" in collections
    
    # Test stats - just verify it returns a dict without error
    stats = db.stats()
    print(f"✓ stats(): returns dict with keys: {list(stats.keys())[:3]}...")
    
    # Test checkpoint
    db.checkpoint()
    print("✓ checkpoint() completed")
    
    db.close()
    print("✓ Database closed")
    
    # Phase 2: Reopen and verify persistence
    print("\n--- Phase 2: Verify Persistence ---")
    db2 = Database.open(TEST_DB)
    ns2 = db2.get_or_create_namespace("default")
    
    # Test list_collections after reopen
    collections = ns2.list_collections()
    print(f"✓ After reopen, list_collections: {collections}")
    assert "persistent_test" in collections, "Collection should persist"
    
    # Test get_collection loads from storage
    col2 = ns2.get_collection("persistent_test")
    print(f"✓ get_collection loaded, count = {col2.count()}")
    assert col2.count() == 2, f"Expected 2 docs, got {col2.count()}"
    
    # Test document retrieval
    doc = col2.get("doc1")
    print(f"✓ Retrieved doc1: {doc['metadata']}")
    assert doc is not None and doc["metadata"]["text"] == "first"
    
    # Test search still works
    results = col2.vector_search([1.0, 0.0, 0.0, 0.0], k=2)
    print(f"✓ vector_search: {len(results)} results")
    assert len(results) >= 1
    
    # Test delete_collection
    ns2.delete_collection("persistent_test")
    print("✓ delete_collection completed")
    
    # Verify deletion
    collections = ns2.list_collections()
    assert "persistent_test" not in collections, "Collection should be deleted"
    print(f"✓ After delete, list_collections: {collections}")
    
    db2.close()
    cleanup()
    
    print("\n" + "=" * 60)
    print("ALL TODO FIXES VERIFIED! ✓")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_all_fixes()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
