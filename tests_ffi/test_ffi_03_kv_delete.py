#!/usr/bin/env python3
"""
Test: KV Delete Operations
Mode: Embedded (FFI)
Description: Tests key deletion operations

Tests delete functionality and verification.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestKVDelete(TestBase):
    def __init__(self):
        super().__init__("FFI - KV Delete")
        self.db_path = None
        self.db = None
    
    def setup(self):
        """Setup test database"""
        self.db_path = setup_test_db("./test_db_03")
        self.db =  Database.open(self.db_path)
        
        # Pre-populate with data
        self.db.put(b"delete_me", b"value")
        self.db.put(b"keep_me", b"value")
    
    def execute_tests(self):
        """Execute all test cases"""
        
        # Test 1: Delete existing key
        try:
            self.db.delete(b"delete_me")
            value = self.db.get(b"delete_me")
            assert value is None, f"Expected None after delete, got {value}"
            self.add_result("Delete existing key", True)
        except Exception as e:
            self.add_result("Delete existing key", False, str(e))
        
        # Test 2: Other keys unaffected
        try:
            value = self.db.get(b"keep_me")
            assert value == b"value", f"Other keys should be unaffected"
            self.add_result("Other keys unaffected by delete", True)
        except Exception as e:
            self.add_result("Other keys unaffected by delete", False, str(e))
        
        # Test 3: Delete non-existent key (should not error)
        try:
            self.db.delete(b"never_existed")
            self.add_result("Delete non-existent key (no error)", True)
        except Exception as e:
            self.add_result("Delete non-existent key (no error)", False, str(e))
        
        # Test 4: Re-add after delete
        try:
            self.db.put(b"delete_me", b"new_value")
            value = self.db.get(b"delete_me")
            assert value == b"new_value"
            self.add_result("Re-add after delete", True)
        except Exception as e:
            self.add_result("Re-add after delete", False, str(e))
    
    def teardown(self):
        """Cleanup"""
        if self.db:
            self.db.close()
        cleanup_test_db(self.db_path)


if __name__ == "__main__":
    test = TestKVDelete()
    results = test.run()
    
    failed = sum(1 for r in results if not r["passed"])
    sys.exit(0 if failed == 0 else 1)
