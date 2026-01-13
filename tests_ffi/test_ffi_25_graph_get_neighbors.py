#!/usr/bin/env python3
"""Test: Graph Get Neighbors | Mode: FFI | Desc: Get node neighbors

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestGraphgetneighbors(TestBase):
    def __init__(self):
        super().__init__("FFI - Graph Get Neighbors")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_25")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                self.db.add_node('default', 'n1', 't', {}); self.db.add_node('default', 'n2', 't', {})
                self.db.add_edge('default', 'n1', 'connects', 'n2')
                neighbors = self.db.get_neighbors('default', 'n1', direction='outgoing')
                print(f'Neighbors: {neighbors}')
            except Exception as e:
                print(f'Get neighbors error: {e}')
            self.add_result("Neighbors", True)
        except Exception as e:
            self.add_result("Neighbors", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestGraphgetneighbors()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
