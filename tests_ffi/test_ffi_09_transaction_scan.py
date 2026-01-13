#!/usr/bin/env python3
"""Test: Transaction Scan | Mode: FFI | Desc: Scan in transaction"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestTransactionscan(TestBase):
    def __init__(self):
        super().__init__("FFI - Transaction Scan")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_09")
        self.db = Database.open(self.db_path)

    def execute_tests(self):
        try:
            self.db.put(b'a1', b'x')
            self.add_result("Setup", True)
        except Exception as e:
            self.add_result("Setup", False, str(e))
        try:
            with self.db.transaction() as txn: list(txn.scan_prefix(b'a1'))
            self.add_result("Scan", True)
        except Exception as e:
            self.add_result("Scan", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestTransactionscan()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
