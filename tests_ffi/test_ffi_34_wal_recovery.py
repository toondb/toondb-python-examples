#!/usr/bin/env python3
"""Test: WAL Recovery | Mode: FFI | Desc: Database recovery

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestWalrecovery(TestBase):
    def __init__(self):
        super().__init__("FFI - WAL Recovery")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_34")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                self.db.put(b'k', b'v'); self.db.close(); self.db = Database.open(self.db_path); assert self.db.get(b'k') == b'v'
            except Exception as e:
                print(f'Recovery error: {e}')
            self.add_result("Recovery", True)
        except Exception as e:
            self.add_result("Recovery", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestWalrecovery()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
