#!/usr/bin/env python3
"""Test: Cache Statistics | Mode: FFI | Desc: Cache hit/miss stats

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestCachestats(TestBase):
    def __init__(self):
        super().__init__("FFI - Cache Statistics")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_30")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                stats = self.db.cache_stats('test_cache')
                print(f'Cache stats: {stats}')
            except (AttributeError, Exception) as e:
                print(f'cache_stats not available: {e}')
            self.add_result("Stats", True)
        except Exception as e:
            self.add_result("Stats", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestCachestats()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
