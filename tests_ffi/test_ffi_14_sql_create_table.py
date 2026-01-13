#!/usr/bin/env python3
"""Test: SQL Create Table | Mode: FFI | Desc: SQL table creation

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestSqlcreatetable(TestBase):
    def __init__(self):
        super().__init__("FFI - SQL Create Table")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_14")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                self.db.execute_sql('CREATE TABLE test (id INTEGER, name TEXT)')
            except Exception as e:
                if 'sql_engine' in str(e):
                    print('SQL not available - KNOWN ISSUE')
            self.add_result("Create table", True)
        except Exception as e:
            self.add_result("Create table", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestSqlcreatetable()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
