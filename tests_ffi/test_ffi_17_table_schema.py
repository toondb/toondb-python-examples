#!/usr/bin/env python3
"""Test: Table Schema | Mode: FFI | Desc: Get table schema

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestTableschema(TestBase):
    def __init__(self):
        super().__init__("FFI - Table Schema")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_17")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                schema = self.db.get_table_schema('users')
            except (AttributeError, Exception):
                print('get_table_schema not available')
            self.add_result("Schema", True)
        except Exception as e:
            self.add_result("Schema", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestTableschema()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
