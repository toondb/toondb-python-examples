#!/usr/bin/env python3
"""Test: WAL Checkpoint | Mode: FFI | Desc: WAL checkpointing

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase, setup_test_db, cleanup_test_db
from sochdb import Database


class TestWalcheckpoint(TestBase):
    def __init__(self):
        super().__init__("FFI - WAL Checkpoint")
        self.db_path = self.db = None
    def setup(self):
        self.db_path = setup_test_db("./test_db_33")
        self.db = Database.open(self.db_path)
    def execute_tests(self):
        try:
            ts = self.db.checkpoint(); print(f'Checkpoint: {ts}')
            self.add_result("Checkpoint", True)
        except Exception as e:
            self.add_result("Checkpoint", False, str(e))
    def teardown(self):
        if self.db: self.db.close()
        cleanup_test_db(self.db_path)

if __name__ == "__main__":
    test = TestWalcheckpoint()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
