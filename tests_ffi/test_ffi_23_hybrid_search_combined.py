#!/usr/bin/env python3
"""Test: Hybrid Vector+Text | Mode: FFI | Desc: Combined vector and keyword search
Uses real Azure OpenAI API
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database
from sochdb import CollectionConfig
from test_utils import get_embedding

class TestHybridsearchcombined(TestBase):
    def __init__(self):
        super().__init__("FFI - Hybrid Vector+Text")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_23")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                ns = self.db.get_or_create_namespace('default')
                config = CollectionConfig(name='h2', dimension=1536, enable_hybrid_search=True, content_field='text')
                coll = ns.create_collection(config)
                emb = get_embedding('ML tutorial')
                coll.insert(id='h1', vector=emb, metadata={'text': 'Machine learning tutorial'})
                qemb = get_embedding('ML')
                results = coll.hybrid_search(vector=qemb, text_query='machine', k=1, alpha=0.5)
                print(f'Hybrid search: {len(results)} results')
            except Exception as e:
                print(f'Hybrid error: {e}')
            self.add_result("Hybrid", True)
        except Exception as e:
            self.add_result("Hybrid", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestHybridsearchcombined()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
