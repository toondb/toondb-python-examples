#!/usr/bin/env python3
"""Test script for semantic cache fix"""
import os
import sys
import shutil


from sochdb import Database

TEST_DB = "/tmp/test_cache_fix_db"

def cleanup():
    if os.path.exists(TEST_DB):
        shutil.rmtree(TEST_DB)

def test_cache():
    cleanup()
    
    print("=" * 60)
    print("Testing Semantic Cache Fix")
    print("=" * 60)
    
    db = Database.open(TEST_DB)
    
    # Test cache put
    print("\n--- Cache Put ---")
    embedding1 = [1.0, 0.0, 0.0, 0.0]  # Normalized 4-dim vector
    db.cache_put(
        cache_name="llm_cache",
        key="What is Python?",
        value="Python is a programming language.",
        embedding=embedding1,
        ttl_seconds=3600
    )
    print("✓ cache_put completed")
    
    # Put a second entry
    embedding2 = [0.0, 1.0, 0.0, 0.0]
    db.cache_put(
        cache_name="llm_cache",
        key="What is JavaScript?",
        value="JavaScript is a scripting language.",
        embedding=embedding2,
        ttl_seconds=3600
    )
    print("✓ Second cache_put completed")
    
    # Test cache get - exact match
    print("\n--- Cache Get (Exact Match) ---")
    result = db.cache_get(
        cache_name="llm_cache",
        query_embedding=[1.0, 0.0, 0.0, 0.0],  # Exact match to embedding1
        threshold=0.9
    )
    print(f"  Query: [1.0, 0.0, 0.0, 0.0]")
    print(f"  Result: {result}")
    assert result == "Python is a programming language.", f"Expected Python answer, got: {result}"
    print("✓ Exact match cache hit!")
    
    # Test cache get - similar query
    print("\n--- Cache Get (Similar Query) ---")
    result = db.cache_get(
        cache_name="llm_cache",
        query_embedding=[0.95, 0.1, 0.0, 0.0],  # Very similar to embedding1
        threshold=0.85
    )
    print(f"  Query: [0.95, 0.1, 0.0, 0.0]")
    print(f"  Result: {result}")
    assert result == "Python is a programming language.", f"Expected Python answer, got: {result}"
    print("✓ Similar query cache hit!")
    
    # Test cache get - different cache name (miss)
    print("\n--- Cache Get (Wrong Cache Name) ---")
    result = db.cache_get(
        cache_name="other_cache",
        query_embedding=[1.0, 0.0, 0.0, 0.0],
        threshold=0.85
    )
    print(f"  Result: {result}")
    assert result is None, "Should be cache miss"
    print("✓ Cache miss for wrong cache name!")
    
    # Test cache get - below threshold (miss)
    print("\n--- Cache Get (Below Threshold) ---")
    result = db.cache_get(
        cache_name="llm_cache",
        query_embedding=[0.5, 0.5, 0.5, 0.5],  # Low similarity
        threshold=0.9
    )
    print(f"  Query: [0.5, 0.5, 0.5, 0.5] (low similarity)")
    print(f"  Result: {result}")
    assert result is None, "Should be cache miss below threshold"
    print("✓ Cache miss below threshold!")
    
    # Count cache hits
    hits = 0
    for _ in range(5):
        r = db.cache_get("llm_cache", [1.0, 0.0, 0.0, 0.0], 0.85)
        if r: hits += 1
    print(f"\n--- Hit Rate Test: {hits}/5 ({hits*20}%) ---")
    
    db.close()
    cleanup()
    
    print("\n" + "=" * 60)
    print("ALL CACHE TESTS PASSED! ✓")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_cache()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
