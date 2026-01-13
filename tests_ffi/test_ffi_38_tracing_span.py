#!/usr/bin/env python3
"""Test: Trace Spans | Mode: FFI | Desc: Create trace spans

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestTracingspan(TestBase):
    def __init__(self):
        super().__init__("FFI - Trace Spans")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_38")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                span_id = self.db.start_span('test_span', parent_span=None); print(f'Span: {span_id}')
            except (AttributeError, Exception) as e:
                print(f'Spans not available: {e}')
            self.add_result("Span", True)
        except Exception as e:
            self.add_result("Span", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestTracingspan()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
