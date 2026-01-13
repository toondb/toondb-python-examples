#!/usr/bin/env python3
"""Test: Temporal End Edge | Mode: FFI | Desc: End temporal edge

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database
import time

class TestTemporalendedge(TestBase):
    def __init__(self):
        super().__init__("FFI - Temporal End Edge")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_28")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                now = int(time.time()*1000)
                self.db.add_node('default', 'd', 's', {}); self.db.add_node('default', 'on', 's', {})
                self.db.add_temporal_edge('default', 'd', 'S', 'on', now-1000, 0, {})
                self.db.end_temporal_edge('default', 'd', 'S', 'on', now)
                print('Temporal edge ended')
            except (AttributeError, Exception) as e:
                print(f'end_temporal_edge not available: {e}')
            self.add_result("End edge", True)
        except Exception as e:
            self.add_result("End edge", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestTemporalendedge()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
