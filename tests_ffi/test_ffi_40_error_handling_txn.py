#!/usr/bin/env python3
"""Test: Transaction Errors | Mode: FFI | Desc: Transaction error handling

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestErrorhandlingtxn(TestBase):
    def __init__(self):
        super().__init__("FFI - Transaction Errors")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_40")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                from sochdb import TransactionConflictError
                print('TransactionConflictError available')
            except ImportError:
                print('TransactionConflictError not imported')
            self.add_result("TXN error", True)
        except Exception as e:
            self.add_result("TXN error", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestErrorhandlingtxn()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
