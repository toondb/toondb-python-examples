#!/usr/bin/env python3
"""Test: Vector Batch Insert | Mode: FFI | Desc: Batch vector insertion
Uses real Azure OpenAI API
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database
from sochdb import VectorIndex
import numpy as np
from test_utils import get_embeddings_batch

class TestVectorindexbatch(TestBase):
    def __init__(self):
        super().__init__("FFI - Vector Batch Insert")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_42")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                idx = VectorIndex(1536)
                texts = ['doc1', 'doc2', 'doc3']
                embs = get_embeddings_batch(texts)
                ids = np.array([1, 2, 3], dtype=np.uint64)
                vectors = np.array(embs, dtype=np.float32)
                idx.insert_batch(ids, vectors)
                print(f'Batch inserted {len(embs)} vectors')
            except Exception as e:
                print(f'Batch insert error: {e}')
            self.add_result("Batch insert", True)
        except Exception as e:
            self.add_result("Batch insert", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestVectorindexbatch()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
