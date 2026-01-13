#!/usr/bin/env python3
"""Test: Compression | Mode: FFI | Desc: Data compression

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestCompression(TestBase):
    def __init__(self):
        super().__init__("FFI - Compression")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_39")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            large_data = b'x' * 10000; self.db.put(b'compressed', large_data); retrieved = self.db.get(b'compressed'); assert len(retrieved) == len(large_data)
            self.add_result("Compress", True)
        except Exception as e:
            self.add_result("Compress", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestCompression()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
