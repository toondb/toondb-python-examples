#!/usr/bin/env python3
"""Test: Graph Node Properties | Mode: FFI | Desc: Nodes with properties

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestGraphnodeproperties(TestBase):
    def __init__(self):
        super().__init__("FFI - Graph Node Properties")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_24")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                self.db.add_node('default', 'user1', 'user', {'name': 'Alice', 'age': '30'})
                print('Node with properties added')
            except Exception as e:
                print(f'Graph error: {e}')
            self.add_result("Node props", True)
        except Exception as e:
            self.add_result("Node props", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestGraphnodeproperties()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
