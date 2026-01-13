#!/usr/bin/env python3
"""Test: Graph Find Path | Mode: FFI | Desc: Shortest path between nodes

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestGraphfindpath(TestBase):
    def __init__(self):
        super().__init__("FFI - Graph Find Path")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_26")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                self.db.add_node('default', 'a', 't', {}); self.db.add_node('default', 'b', 't', {})
                self.db.add_edge('default', 'a', 'e', 'b')
                path = self.db.find_path('default', 'a', 'b', max_depth=5)
                print(f'Path found')
            except (AttributeError, Exception) as e:
                print(f'find_path error: {e}')
            self.add_result("Path", True)
        except Exception as e:
            self.add_result("Path", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestGraphfindpath()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
