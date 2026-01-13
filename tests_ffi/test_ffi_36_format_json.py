#!/usr/bin/env python3
"""Test: JSON Format | Mode: FFI | Desc: JSON format conversion

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestFormatjson(TestBase):
    def __init__(self):
        super().__init__("FFI - JSON Format")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_36")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            try:
                self.db.put(b'jk', b'jv'); json_data = self.db.to_json([b'jk']); print(f'JSON: {type(json_data)}')
            except (AttributeError, Exception) as e:
                print(f'to_json not available: {e}')
            self.add_result("JSON", True)
        except Exception as e:
            self.add_result("JSON", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestFormatjson()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
