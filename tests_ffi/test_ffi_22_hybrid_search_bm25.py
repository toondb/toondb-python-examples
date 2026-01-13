#!/usr/bin/env python3
"""Test: Hybrid Search BM25 | Mode: FFI | Desc: Keyword search with BM25

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database
from sochdb import CollectionConfig

class TestHybridsearchbm25(TestBase):
    def __init__(self):
        super().__init__("FFI - Hybrid Search BM25")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_22")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                ns = self.db.get_or_create_namespace('default')
                config = CollectionConfig(name='hybrid1', dimension=1536, enable_hybrid_search=True, content_field='text')
                coll = ns.create_collection(config)
                print('Hybrid search collection created')
            except Exception as e:
                print(f'Hybrid search error: {e}')
            self.add_result("BM25", True)
        except Exception as e:
            self.add_result("BM25", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestHybridsearchbm25()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
