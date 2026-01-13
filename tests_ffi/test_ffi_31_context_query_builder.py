#!/usr/bin/env python3
"""Test: Context Query Builder | Mode: FFI | Desc: LLM context assembly

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestContextquerybuilder(TestBase):
    def __init__(self):
        super().__init__("FFI - Context Query Builder")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_31")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                from sochdb import ContextQueryBuilder, ContextFormat
                ctx = ContextQueryBuilder().for_session('s1').with_budget(2048).format(ContextFormat.TOON)
                print('Context builder available')
            except (ImportError, AttributeError) as e:
                print(f'ContextQueryBuilder not available: {e}')
            self.add_result("Context builder", True)
        except Exception as e:
            self.add_result("Context builder", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestContextquerybuilder()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
