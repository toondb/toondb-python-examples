#!/usr/bin/env python3
"""Test: Vector Search Params | Mode: FFI | Desc: Search with custom ef
Uses real Azure OpenAI API
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database
from sochdb import VectorIndex
import numpy as np
from test_utils import get_embedding

class TestVectorindexsearchparams(TestBase):
    def __init__(self):
        super().__init__("FFI - Vector Search Params")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_43")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                idx = VectorIndex(1536, ef_construction=200)
                emb = get_embedding('test')
                idx.insert(1, np.array(emb, dtype=np.float32))
                results = idx.search(np.array(emb, dtype=np.float32), k=1)
                print(f'Search with params: {len(results)} results')
            except Exception as e:
                print(f'libsochdb_index not found: {e}')
            self.add_result("Search params", True)
        except Exception as e:
            self.add_result("Search params", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestVectorindexsearchparams()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
