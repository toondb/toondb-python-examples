#!/usr/bin/env python3
"""
Test: Stats and Checkpoint
Mode: Embedded (FFI)
Description: Tests database statistics and checkpoint operations
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestStatscheckpoint(TestBase):
    def __init__(self):
        super().__init__("FFI - Stats and Checkpoint")
        self.db_path = None
        self.db = None
    
    def setup(self):
        """Setup test database"""
        self.db_path = setup_test_db("./test_db_06")
        self.db = Database.open(self.db_path)

    def execute_tests(self):
        """Execute all test cases"""

        # Test 1: Get stats
        try:
            stats = self.db.stats(); assert isinstance(stats, dict)
            self.add_result("Get stats", True)
        except Exception as e:
            self.add_result("Get stats", False, str(e))

        # Test 2: Stats has keys
        try:
            stats = self.db.stats(); assert 'keys_count' in stats or 'transactions_committed' in stats
            self.add_result("Stats has keys", True)
        except Exception as e:
            self.add_result("Stats has keys", False, str(e))

        # Test 3: Checkpoint
        try:
            ts = self.db.checkpoint(); print(f'Checkpoint: {ts}')
            self.add_result("Checkpoint", True)
        except Exception as e:
            self.add_result("Checkpoint", False, str(e))

    def teardown(self):
        """Cleanup"""
        if self.db:
            self.db.close()
        cleanup_test_db(self.db_path)


if __name__ == "__main__":
    test = TestStatscheckpoint()
    results = test.run()
    
    failed = sum(1 for r in results if not r["passed"])
    sys.exit(0 if failed == 0 else 1)
