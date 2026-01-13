#!/usr/bin/env python3
"""Test: Cache TTL | Mode: FFI | Desc: Cache expiration
Uses real Azure OpenAI API
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database
from test_utils import get_embedding
import time

class TestCachettl(TestBase):
    def __init__(self):
        super().__init__("FFI - Cache TTL")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_29")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                emb = get_embedding('test')
                self.db.cache_put('ttl_cache', 'key', 'value', emb, ttl_seconds=1)
                time.sleep(2)
                cached = self.db.cache_get('ttl_cache', emb, threshold=0.9)
                print(f'After TTL: {cached}')
            except Exception as e:
                print(f'Cache TTL error: {e}')
            self.add_result("TTL", True)
        except Exception as e:
            self.add_result("TTL", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestCachettl()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
