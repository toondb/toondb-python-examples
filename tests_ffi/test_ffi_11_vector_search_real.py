#!/usr/bin/env python3
"""
Test: Vector Search with Real Azure OpenAI Embeddings
Mode: Embedded (FFI)
Description: Tests VectorIndex with real embeddings from Azure OpenAI

This test uses the REAL Azure OpenAI API - no mocking!
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from test_utils import TestBase, get_embedding, SAMPLE_TEXTS, SAMPLE_QUERIES
from sochdb import VectorIndex
import numpy as np


class TestVectorSearchReal(TestBase):
    def __init__(self):
        super().__init__("FFI - Vector Search (Real Azure OpenAI)")
        self.index = None
        self.embeddings = []
    
    def setup(self):
        """Setup - Get embeddings from Azure OpenAI"""
        print("\n  Getting embeddings from Azure OpenAI...")
        for i, text in enumerate(SAMPLE_TEXTS[:3]):
            emb = get_embedding(text)
            self.embeddings.append(emb)
            print(f"    ✓ Got embedding for doc{i} (dim={len(emb)})")
        
        # Create vector index
        self.index = VectorIndex(dimension=1536, max_connections=16)
    
    def execute_tests(self):
        """Execute all test cases"""
        
        # Test 1: Insert vectors
        try:
            for i, emb in enumerate(self.embeddings):
                self.index.insert(i, np.array(emb, dtype=np.float32))
            self.add_result(f"Insert {len(self.embeddings)} vectors", True)
        except Exception as e:
            self.add_result(f"Insert {len(self.embeddings)} vectors", False, str(e))
            return
        
        # Test 2: Search with real query
        try:
            query_text = SAMPLE_QUERIES[0]  # "What is Python?"
            print(f"\n  Searching for: '{query_text}'")
            
            query_emb = get_embedding(query_text)
            print(f"    ✓ Got query embedding (dim={len(query_emb)})")
            
            results = self.index.search(np.array(query_emb, dtype=np.float32), k=2)
            
            assert len(results) > 0, "Should return results"
            
            # Results are (id, distance) tuples
            top_id, top_dist = results[0]
            
            print(f"    ✓ Top result: doc{top_id} (distance={top_dist:.4f})")
            print(f"      Text: '{SAMPLE_TEXTS[top_id]}'")
            
            # The Python document should be most relevant
            assert top_id == 0, f"Expected Python doc (id=0), got id={top_id}"
            
            self.add_result("Search with real query (correct result)", True, f"Found doc{top_id}")
        except Exception as e:
            self.add_result("Search with real query", False, str(e))
        
        # Test 3: Search multiple queries
        try:
            for query in SAMPLE_QUERIES[:2]:
                query_emb = get_embedding(query)
                results = self.index.search(np.array(query_emb, dtype=np.float32), k=1)
                assert len(results) > 0
            
            self.add_result("Multiple query searches", True)
        except Exception as e:
            self.add_result("Multiple query searches", False, str(e))
    
    def teardown(self):
        """Cleanup"""
        # VectorIndex is in-memory only, no cleanup needed
        pass


if __name__ == "__main__":
    test = TestVectorSearchReal()
    results = test.run()
    
    failed = sum(1 for r in results if not r["passed"])
    sys.exit(0 if failed == 0 else 1)
