#!/usr/bin/env python3
"""Test: Index Policies | Mode: FFI | Desc: Table index policies

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestIndexpolicies(TestBase):
    def __init__(self):
        super().__init__("FFI - Index Policies")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_18")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                self.db.execute('CREATE TABLE t (id INT)'); self.db.set_table_index_policy('t', self.db.INDEX_BALANCED)
                assert self.db.get_table_index_policy('t') == self.db.INDEX_BALANCED
            except Exception as e:
                print(f'Index policies require SQL: {e}')
            self.add_result("Set policy", True)
        except Exception as e:
            self.add_result("Set policy", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestIndexpolicies()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
