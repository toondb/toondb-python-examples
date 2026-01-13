#!/usr/bin/env python3
"""
Test: Basic KV Put/Get Operations
Mode: Embedded (FFI)
Description: Tests basic key-value put and get operations

Uses embedded FFI mode with bytes keys and values.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestKVPutGet(TestBase):
    def __init__(self):
        super().__init__("FFI - KV Put/Get")
        self.db_path = None
        self.db = None
    
    def setup(self):
        """Setup test database"""
        self.db_path = setup_test_db("./test_db_02")
        self.db = Database.open(self.db_path)
    
    def execute_tests(self):
        """Execute all test cases"""
        
        # Test 1: Simple put
        try:
            self.db.put(b"key1", b"value1")
            self.add_result("Put single key-value", True)
        except Exception as e:
            self.add_result("Put single key-value", False, str(e))
        
        # Test 2: Simple get
        try:
            value = self.db.get(b"key1")
            assert value == b"value1", f"Expected b'value1', got {value}"
            self.add_result("Get existing key", True)
        except Exception as e:
            self.add_result("Get existing key", False, str(e))
        
        # Test 3: Get non-existent key
        try:
            value = self.db.get(b"nonexistent")
            assert value is None, f"Expected None, got {value}"
            self.add_result("Get non-existent key returns None", True)
        except Exception as e:
            self.add_result("Get non-existent key returns None", False, str(e))
        
        # Test 4: Overwrite existing key
        try:
            self.db.put(b"key1", b"new_value")
            value = self.db.get(b"key1")
            assert value == b"new_value", f"Expected b'new_value', got {value}"
            self.add_result("Overwrite existing key", True)
        except Exception as e:
            self.add_result("Overwrite existing key", False, str(e))
        
        # Test 5: Multiple keys
        try:
            self.db.put(b"key2", b"value2")
            self.db.put(b"key3", b"value3")
            
            val1 = self.db.get(b"key1")
            val2 = self.db.get(b"key2")
            val3 = self.db.get(b"key3")
            
            assert val1 == b"new_value"
            assert val2 == b"value2"
            assert val3 == b"value3"
            self.add_result("Multiple keys independent", True)
        except Exception as e:
            self.add_result("Multiple keys independent", False, str(e))
    
    def teardown(self):
        """Cleanup"""
        if self.db:
            self.db.close()
        cleanup_test_db(self.db_path)


if __name__ == "__main__":
    test = TestKVPutGet()
    results = test.run()
    
    failed = sum(1 for r in results if not r["passed"])
    sys.exit(0 if failed == 0 else 1)
