#!/usr/bin/env python3
"""
Test: Database Open and Close
Mode: Embedded (FFI)
Description: Tests basic database lifecycle - open and close operations

Uses embedded FFI mode (no server required).
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestDatabaseOpenClose(TestBase):
    def __init__(self):
        super().__init__("FFI - Database Open/Close")
        self.db_path = None
        self.db = None
    
    def setup(self):
        """Setup test database"""
        self.db_path = setup_test_db("./test_db_01")
    
    def execute_tests(self):
        """Execute all test cases"""
        
        # Test 1: Open database
        try:
            self.db = Database.open(self.db_path)
            self.add_result("Open database", True)
        except Exception as e:
            self.add_result("Open database", False, str(e))
            return
        
        # Test 2: Database object exists
        try:
            assert self.db is not None
            self.add_result("Database object created", True)
        except AssertionError as e:
            self.add_result("Database object created", False, str(e))
        
        # Test 3: Close database
        try:
            self.db.close()
            self.add_result("Close database", True)
        except Exception as e:
            self.add_result("Close database", False, str(e))
        
        # Test 4: Context manager
        try:
            with Database.open(self.db_path) as db:
                assert db is not None
            self.add_result("Context manager (with statement)", True)
        except Exception as e:
            self.add_result("Context manager (with statement)", False, str(e))
    
    def teardown(self):
        """Cleanup"""
        cleanup_test_db(self.db_path)


if __name__ == "__main__":
    test = TestDatabaseOpenClose()
    results = test.run()
    
    # Exit with appropriate code
    failed = sum(1 for r in results if not r["passed"])
    sys.exit(0 if failed == 0 else 1)
