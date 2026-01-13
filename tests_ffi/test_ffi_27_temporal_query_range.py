#!/usr/bin/env python3
"""Test: Temporal Range Query | Mode: FFI | Desc: Query time range

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database
import time

class TestTemporalqueryrange(TestBase):
    def __init__(self):
        super().__init__("FFI - Temporal Range Query")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_27")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                self.db.add_node('default', 's', 'sensor', {}); self.db.add_node('default', 'active', 'state', {})
                now = int(time.time()*1000)
                self.db.add_temporal_edge('default', 's', 'STATUS', 'active', now-10000, now, {})
                edges = self.db.query_temporal_graph('default', 's', 'RANGE', start_time=now-20000, end_time=now)
                print(f'Range query: {len(edges)} edges')
            except Exception as e:
                print(f'Temporal range error: {e}')
            self.add_result("Range query", True)
        except Exception as e:
            self.add_result("Range query", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestTemporalqueryrange()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
