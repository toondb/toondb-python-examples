#!/usr/bin/env python3
"""
Test: Transaction Rollback
Mode: Embedded (FFI)
Description: Tests automatic transaction rollback on exception
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestTransactionrollback(TestBase):
    def __init__(self):
        super().__init__("FFI - Transaction Rollback")
        self.db_path = None
        self.db = None
    
    def setup(self):
        """Setup test database"""
        self.db_path = setup_test_db("./test_db_08")
        self.db = Database.open(self.db_path)

    def execute_tests(self):
        """Execute all test cases"""

        # Test 1: Rollback on exception
        try:
            try:
                with self.db.transaction() as txn:
                    txn.put(b'rollback_key', b'should_not_exist')
                    raise ValueError('test')
            except ValueError:
                pass
            assert self.db.get(b'rollback_key') is None
            self.add_result("Rollback on exception", True)
        except Exception as e:
            self.add_result("Rollback on exception", False, str(e))

    def teardown(self):
        """Cleanup"""
        if self.db:
            self.db.close()
        cleanup_test_db(self.db_path)


if __name__ == "__main__":
    test = TestTransactionrollback()
    results = test.run()
    
    failed = sum(1 for r in results if not r["passed"])
    sys.exit(0 if failed == 0 else 1)
