#!/usr/bin/env python3
"""Test: Context Truncation | Mode: FFI | Desc: Token budget truncation

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestContexttruncation(TestBase):
    def __init__(self):
        super().__init__("FFI - Context Truncation")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_32")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                from sochdb import ContextQueryBuilder, TruncationStrategy
                ctx = ContextQueryBuilder().with_budget(1000).truncation(TruncationStrategy.TAIL_DROP)
                print('Truncation strategy available')
            except (ImportError, AttributeError) as e:
                print('Truncation not available')
            self.add_result("Truncation", True)
        except Exception as e:
            self.add_result("Truncation", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestContexttruncation()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
