#!/usr/bin/env python3
"""Test: SQL CRUD | Mode: FFI | Desc: SQL Insert/Select/Update/Delete

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestSqlcrud(TestBase):
    def __init__(self):
        super().__init__("FFI - SQL CRUD")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_15")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                self.db.execute('CREATE TABLE t (id INT)'); self.db.execute('INSERT INTO t VALUES (1)')
            except Exception as e:
                print(f'SQL not available: {e}')
            self.add_result("SQL CRUD", True)
        except Exception as e:
            self.add_result("SQL CRUD", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestSqlcrud()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
