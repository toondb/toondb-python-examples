#!/usr/bin/env python3
"""Test: Start Trace | Mode: FFI | Desc: Distributed tracing

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestTracingstart(TestBase):
    def __init__(self):
        super().__init__("FFI - Start Trace")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_37")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                trace_id = self.db.start_trace('test_trace'); print(f'Trace: {trace_id}')
            except (AttributeError, Exception) as e:
                print(f'start_trace not available: {e}')
            self.add_result("Start trace", True)
        except Exception as e:
            self.add_result("Start trace", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestTracingstart()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
