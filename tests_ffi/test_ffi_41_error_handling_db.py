#!/usr/bin/env python3
"""Test: Database Errors | Mode: FFI | Desc: Database error handling

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestErrorhandlingdb(TestBase):
    def __init__(self):
        super().__init__("FFI - Database Errors")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_41")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            from sochdb import DatabaseError; print('DatabaseError available')
            self.add_result("DB error", True)
        except Exception as e:
            self.add_result("DB error", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestErrorhandlingdb()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
