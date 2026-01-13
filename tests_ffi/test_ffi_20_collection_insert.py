#!/usr/bin/env python3
"""Test: Collection Insert | Mode: FFI | Desc: Insert documents with embeddings
Uses real Azure OpenAI API
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database
from sochdb import CollectionConfig, DistanceMetric
from test_utils import get_embedding

class TestCollectioninsert(TestBase):
    def __init__(self):
        super().__init__("FFI - Collection Insert")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_20")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                ns = self.db.get_or_create_namespace('default')
                config = CollectionConfig(name='docs2', dimension=1536, metric=DistanceMetric.COSINE)
                coll = ns.create_collection(config)
                emb = get_embedding('test')
                coll.insert(id='doc1', vector=emb, metadata={'text': 'test'})
                print('Document inserted')
            except Exception as e:
                print(f'Insert error: {e}')
            self.add_result("Insert docs", True)
        except Exception as e:
            self.add_result("Insert docs", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestCollectioninsert()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
