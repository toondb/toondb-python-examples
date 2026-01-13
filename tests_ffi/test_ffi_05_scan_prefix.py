#!/usr/bin/env python3
"""
Test: Prefix Scanning
Mode: Embedded (FFI)
Description: Tests scan_prefix for efficient prefix-based iteration
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestScanprefix(TestBase):
    def __init__(self):
        super().__init__("FFI - Prefix Scanning")
        self.db_path = None
        self.db = None
    
    def setup(self):
        """Setup test database"""
        self.db_path = setup_test_db("./test_db_05")
        self.db = Database.open(self.db_path)

    def execute_tests(self):
        """Execute all test cases"""

        # Test 1: Scan prefix setup
        try:
            for i in range(5): self.db.put(f'logs/{i:03d}'.encode(), f'entry{i}'.encode())
            self.add_result("Scan prefix setup", True)
        except Exception as e:
            self.add_result("Scan prefix setup", False, str(e))

        # Test 2: Scan with prefix
        try:
            results = list(self.db.scan_prefix(b'logs/')); assert len(results) == 5
            self.add_result("Scan with prefix", True)
        except Exception as e:
            self.add_result("Scan with prefix", False, str(e))

        # Test 3: Prefix isolation
        try:
            self.db.put(b'other/1', b'x'); logs = list(self.db.scan_prefix(b'logs/'));  assert len(logs) == 5
            self.add_result("Prefix isolation", True)
        except Exception as e:
            self.add_result("Prefix isolation", False, str(e))

    def teardown(self):
        """Cleanup"""
        if self.db:
            self.db.close()
        cleanup_test_db(self.db_path)


if __name__ == "__main__":
    test = TestScanprefix()
    results = test.run()
    
    failed = sum(1 for r in results if not r["passed"])
    sys.exit(0 if failed == 0 else 1)
