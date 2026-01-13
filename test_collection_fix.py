#!/usr/bin/env python3
"""
Test script to verify Collection.insert bug fix
"""
import os
import sys
import shutil

# Add SDK to path

from sochdb import Database
from sochdb import CollectionConfig, DistanceMetric

TEST_DB = "/tmp/test_collection_fix_db"

def cleanup():
    if os.path.exists(TEST_DB):
        shutil.rmtree(TEST_DB)

def test_collection_insert():
    cleanup()
    
    print("=" * 60)
    print("Testing Collection.insert Fix")
    print("=" * 60)
    
    # Open database
    db = Database.open(TEST_DB)
    print("✓ Database opened")
    
    # Create namespace
    ns = db.get_or_create_namespace("default")
    print("✓ Namespace created")
    
    # Create collection
    config = CollectionConfig(name="test", dimension=128, metric=DistanceMetric.COSINE)
    col = ns.create_collection(config)
    print("✓ Collection created")
    
    # Test: Count before insert
    count_before = col.count()
    print(f"  Count before insert: {count_before}")
    assert count_before == 0, f"Expected 0, got {count_before}"
    
    # Test: Insert
    vector = [0.1] * 128
    metadata = {"text": "hello world", "category": "test"}
    col.insert(id="doc1", vector=vector, metadata=metadata)
    print("✓ Insert completed (no exception)")
    
    # Test: Count after insert
    count_after = col.count()
    print(f"  Count after insert: {count_after}")
    assert count_after == 1, f"Expected 1, got {count_after}"
    print("✓ Count is correct!")
    
    # Test: Get document
    doc = col.get("doc1")
    print(f"  Retrieved document: {doc is not None}")
    assert doc is not None, "Expected document, got None"
    assert doc["id"] == "doc1", f"Wrong id: {doc['id']}"
    assert doc["metadata"]["text"] == "hello world", "Wrong metadata"
    assert len(doc["vector"]) == 128, "Wrong vector length"
    print("✓ Get returns correct document!")
    
    # Test: Insert second document
    col.insert(id="doc2", vector=[0.2] * 128, metadata={"text": "goodbye"})
    assert col.count() == 2, "Expected 2 documents"
    print("✓ Second insert works!")
    
    # Test: Delete
    deleted = col.delete("doc1")
    assert deleted == True, "Delete should return True"
    assert col.count() == 1, "Expected 1 after delete"
    print("✓ Delete works!")
    
    # Test: Get deleted document
    deleted_doc = col.get("doc1")
    assert deleted_doc is None, "Deleted doc should be None"
    print("✓ Get returns None for deleted doc!")
    
    # Cleanup
    db.close()
    cleanup()
    
    print()
    print("=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_collection_insert()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
