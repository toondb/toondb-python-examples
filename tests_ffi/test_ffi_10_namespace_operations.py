#!/usr/bin/env python3
"""
Test: Namespace Operations
Mode: Embedded (FFI)
Description: Tests namespace-scoped KV operations
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestNamespaceoperations(TestBase):
    def __init__(self):
        super().__init__("FFI - Namespace Operations")
        self.db_path = None
        self.db = None
    
    def setup(self):
        """Setup test database"""
        self.db_path = setup_test_db("./test_db_10")
        self.db = Database.open(self.db_path)

        # Pre-create namespace
        try:
            self.db.create_namespace('tenant1')
        except:
            pass

    def execute_tests(self):
        """Execute all test cases"""

        # Test 1: Namespace put/get
        try:
            with self.db.use_namespace('tenant1') as ns: ns.put('key1', b'val1'); assert ns.get('key1') == b'val1'
            self.add_result("Namespace put/get", True)
        except Exception as e:
            self.add_result("Namespace put/get", False, str(e))

        # Test 2: Namespace isolation
        try:
            with self.db.use_namespace('tenant1') as ns: ns.put('isolated', b'x'); assert self.db.get(b'isolated') is None
            self.add_result("Namespace isolation", True)
        except Exception as e:
            self.add_result("Namespace isolation", False, str(e))

    def teardown(self):
        """Cleanup"""
        if self.db:
            self.db.close()
        cleanup_test_db(self.db_path)


if __name__ == "__main__":
    test = TestNamespaceoperations()
    results = test.run()
    
    failed = sum(1 for r in results if not r["passed"])
    sys.exit(0 if failed == 0 else 1)
