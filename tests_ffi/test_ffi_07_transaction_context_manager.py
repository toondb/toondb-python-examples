#!/usr/bin/env python3
"""
Test: Transaction Context Manager
Mode: Embedded (FFI)
Description: Tests transaction context manager pattern
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestTransactioncontextmanager(TestBase):
    def __init__(self):
        super().__init__("FFI - Transaction Context Manager")
        self.db_path = None
        self.db = None
    
    def setup(self):
        """Setup test database"""
        self.db_path = setup_test_db("./test_db_07")
        self.db = Database.open(self.db_path)

    def execute_tests(self):
        """Execute all test cases"""

        # Test 1: Context manager put
        try:
            with self.db.transaction() as txn: txn.put(b'tx1', b'val1')
            self.add_result("Context manager put", True)
        except Exception as e:
            self.add_result("Context manager put", False, str(e))

        # Test 2: Auto-commit verified
        try:
            assert self.db.get(b'tx1') == b'val1'
            self.add_result("Auto-commit verified", True)
        except Exception as e:
            self.add_result("Auto-commit verified", False, str(e))

        # Test 3: Read own writes
        try:
            with self.db.transaction() as txn: txn.put(b'tx2', b'val2'); assert txn.get(b'tx2') == b'val2'
            self.add_result("Read own writes", True)
        except Exception as e:
            self.add_result("Read own writes", False, str(e))

    def teardown(self):
        """Cleanup"""
        if self.db:
            self.db.close()
        cleanup_test_db(self.db_path)


if __name__ == "__main__":
    test = TestTransactioncontextmanager()
    results = test.run()
    
    failed = sum(1 for r in results if not r["passed"])
    sys.exit(0 if failed == 0 else 1)
