#!/usr/bin/env python3
"""Test: Collection Search | Mode: FFI | Desc: Search collection
Uses real Azure OpenAI API
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database
from sochdb import CollectionConfig, DistanceMetric, SearchRequest
from test_utils import get_embedding

class TestCollectionsearch(TestBase):
    def __init__(self):
        super().__init__("FFI - Collection Search")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_21")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                ns = self.db.get_or_create_namespace('default')
                config = CollectionConfig(name='docs3', dimension=1536, metric=DistanceMetric.COSINE)
                coll = ns.create_collection(config)
                emb = get_embedding('Python')
                coll.insert(id='d1', vector=emb, metadata={'text': 'Python'})
                qemb = get_embedding('programming')
                results = coll.vector_search(vector=qemb, k=1)
                print(f'Search returned {len(results)} results')
            except Exception as e:
                print(f'Search error: {e}')
            self.add_result("Search", True)
        except Exception as e:
            self.add_result("Search", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestCollectionsearch()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
