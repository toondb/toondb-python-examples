#!/usr/bin/env python3
"""
Test: KV Path Operations
Mode: Embedded (FFI)
Description: Tests hierarchical path-based keys (put_path, get_path, delete_path)
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestKvpathoperations(TestBase):
    def __init__(self):
        super().__init__("FFI - KV Path Operations")
        self.db_path = None
        self.db = None
    
    def setup(self):
        """Setup test database"""
        self.db_path = setup_test_db("./test_db_04")
        self.db = Database.open(self.db_path)

    def execute_tests(self):
        """Execute all test cases"""

        # Test 1: Put path
        try:
            self.db.put_path('users/alice/name', b'Alice Smith')
            self.add_result("Put path", True)
        except Exception as e:
            self.add_result("Put path", False, str(e))

        # Test 2: Get path
        try:
            assert self.db.get_path('users/alice/name') == b'Alice Smith'
            self.add_result("Get path", True)
        except Exception as e:
            self.add_result("Get path", False, str(e))

        # Test 3: Delete path
        try:
            self.db.delete_path('users/alice/name'); assert self.db.get_path('users/alice/name') is None
            self.add_result("Delete path", True)
        except Exception as e:
            self.add_result("Delete path", False, str(e))

        # Test 4: Nested paths
        try:
            self.db.put_path('a/b/c/d', b'deep'); assert self.db.get_path('a/b/c/d') == b'deep'
            self.add_result("Nested paths", True)
        except Exception as e:
            self.add_result("Nested paths", False, str(e))

    def teardown(self):
        """Cleanup"""
        if self.db:
            self.db.close()
        cleanup_test_db(self.db_path)


if __name__ == "__main__":
    test = TestKvpathoperations()
    results = test.run()
    
    failed = sum(1 for r in results if not r["passed"])
    sys.exit(0 if failed == 0 else 1)
