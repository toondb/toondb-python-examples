#!/usr/bin/env python3
"""
Test: Namespace Creation
Mode: Embedded (FFI)
Description: Tests namespace creation and listing
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestNamespacecreate(TestBase):
    def __init__(self):
        super().__init__("FFI - Namespace Creation")
        self.db_path = None
        self.db = None
    
    def setup(self):
        """Setup test database"""
        self.db_path = setup_test_db("./test_db_09")
        self.db = Database.open(self.db_path)

    def execute_tests(self):
        """Execute all test cases"""

        # Test 1: Create namespace
        try:
            self.db.create_namespace('tenant1')
            self.add_result("Create namespace", True)
        except Exception as e:
            self.add_result("Create namespace", False, str(e))

        # Test 2: List namespaces
        try:
            namespaces = self.db.list_namespaces(); assert 'tenant1' in namespaces
            self.add_result("List namespaces", True)
        except Exception as e:
            self.add_result("List namespaces", False, str(e))

        # Test 3: Get namespace
        try:
            ns = self.db.namespace('tenant1'); assert ns is not None
            self.add_result("Get namespace", True)
        except Exception as e:
            self.add_result("Get namespace", False, str(e))

    def teardown(self):
        """Cleanup"""
        if self.db:
            self.db.close()
        cleanup_test_db(self.db_path)


if __name__ == "__main__":
    test = TestNamespacecreate()
    results = test.run()
    
    failed = sum(1 for r in results if not r["passed"])
    sys.exit(0 if failed == 0 else 1)
