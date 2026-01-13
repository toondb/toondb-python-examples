#!/usr/bin/env python3
"""Test: gRPC Errors | Mode: gRPC | Desc: Error handling via gRPC
REQUIRES: sochdb-grpc server running on localhost:50051

"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from test_utils import TestBase
from sochdb import SochDBClient

class TestGrpcerrorhandling(TestBase):
    def __init__(self):
        super().__init__("gRPC - gRPC Errors")
        self.client = None
    def setup(self):
        try:
            self.client = SochDBClient("localhost:50051")
        except Exception as e:
            print(f"gRPC server not available: {e}")
            self.client = None
    def execute_tests(self):
        if not self.client:
            self.add_result("Server check", False, "gRPC server not running")
            return
        self.add_result("Connect to server", True)
        # Add specific gRPC tests here
    def teardown(self):
        if self.client: self.client.close()

if __name__ == "__main__":
    test = TestGrpcerrorhandling()
    sys.exit(0 if all(r["passed"] for r in test.run()) else 1)
