#!/usr/bin/env python3
"""Test script for Collection search methods"""
import os
import sys
import shutil


from sochdb import Database
from sochdb import CollectionConfig, DistanceMetric

TEST_DB = "/tmp/test_search_db"

def cleanup():
    if os.path.exists(TEST_DB):
        shutil.rmtree(TEST_DB)

def test_search():
    cleanup()
    
    print("=" * 60)
    print("Testing Collection Search Methods")
    print("=" * 60)
    
    db = Database.open(TEST_DB)
    ns = db.get_or_create_namespace("default")
    
    # Create collection with hybrid search enabled
    config = CollectionConfig(
        name="docs", 
        dimension=4,  # Small for testing
        metric=DistanceMetric.COSINE,
        enable_hybrid_search=True,
        content_field="text"
    )
    col = ns.create_collection(config)
    
    # Insert test documents
    col.insert(id="doc1", vector=[1.0, 0.0, 0.0, 0.0], metadata={"text": "Python programming language", "category": "tech"})
    col.insert(id="doc2", vector=[0.9, 0.1, 0.0, 0.0], metadata={"text": "Machine learning with Python", "category": "tech"})
    col.insert(id="doc3", vector=[0.0, 1.0, 0.0, 0.0], metadata={"text": "Cooking recipes", "category": "food"})
    col.insert(id="doc4", vector=[0.0, 0.9, 0.1, 0.0], metadata={"text": "Healthy food recipes", "category": "food"})
    
    print(f"✓ Inserted {col.count()} documents")
    
    # Test 1: Vector search
    print("\n--- Vector Search ---")
    query_vec = [1.0, 0.0, 0.0, 0.0]  # Should match doc1, doc2
    results = col.vector_search(query_vec, k=3)
    print(f"  Query: {query_vec}")
    print(f"  Results: {len(results)} found")
    for r in results:
        print(f"    - {r.id}: score={r.score:.4f}, metadata={r.metadata}")
    
    assert len(results) >= 2, f"Expected at least 2 results, got {len(results)}"
    assert results[0].id == "doc1", f"Expected doc1 first, got {results[0].id}"
    print("✓ Vector search works!")
    
    # Test 2: Vector search with filter
    print("\n--- Vector Search with Filter ---")
    results = col.vector_search(query_vec, k=3, filter={"category": "tech"})
    print(f"  Filter: category=tech")
    print(f"  Results: {len(results)} found")
    for r in results:
        print(f"    - {r.id}: score={r.score:.4f}")
    
    assert all(r.id in ["doc1", "doc2"] for r in results), "Filter should only return tech docs"
    print("✓ Filter works!")
    
    # Test 3: Keyword search  
    print("\n--- Keyword Search ---")
    results = col.keyword_search("Python", k=3)
    print(f"  Query: 'Python'")
    print(f"  Results: {len(results)} found")
    for r in results:
        print(f"    - {r.id}: score={r.score:.4f}")
    
    assert len(results) >= 2, "Should find Python docs"
    print("✓ Keyword search works!")
    
    # Test 4: Hybrid search
    print("\n--- Hybrid Search ---")
    query_vec = [0.0, 1.0, 0.0, 0.0]  # Points to food docs
    results = col.hybrid_search(query_vec, text_query="recipes", k=3)
    print(f"  Vector: {query_vec}")
    print(f"  Text: 'recipes'")
    print(f"  Results: {len(results)} found")
    for r in results:
        print(f"    - {r.id}: score={r.score:.4f}")
    
    assert len(results) >= 2, "Should find food docs"
    print("✓ Hybrid search works!")
    
    db.close()
    cleanup()
    
    print("\n" + "=" * 60)
    print("ALL SEARCH TESTS PASSED! ✓")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_search()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
