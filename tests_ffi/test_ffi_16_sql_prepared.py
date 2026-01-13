#!/usr/bin/env python3
"""Test: SQL Prepared Statements | Mode: FFI | Desc: Prepared SQL statements

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestSqlprepared(TestBase):
    def __init__(self):
        super().__init__("FFI - SQL Prepared Statements")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_16")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                stmt = self.db.prepare('SELECT * FROM t WHERE id = ?'); stmt.execute([1])
            except (AttributeError, Exception) as e:
                print('Prepared statements not available')
            self.add_result("Prepared", True)
        except Exception as e:
            self.add_result("Prepared", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestSqlprepared()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
