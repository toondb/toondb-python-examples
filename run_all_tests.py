#!/usr/bin/env python3
"""
Master Test Runner for SochDB Testing Suite

Runs all FFI and/or gRPC tests and generates comprehensive summary.
"""

import os
import sys
import json
import argparse
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Import after ensuring path
sys.path.insert(0, os.path.dirname(__file__))
from test_utils import save_test_results, load_test_results


def discover_tests(directory: str) -> List[str]:
    """Discover all test files in directory"""
    test_files = []
    if not os.path.exists(directory):
        return test_files
    
    for file in sorted(os.listdir(directory)):
        if file.startswith("test_") and file.endswith(".py"):
            test_files.append(os.path.join(directory, file))
    
    return test_files


def run_test_file(test_file: str) -> Dict[str, Any]:
    """Run a single test file and capture results"""
    import subprocess
    
    start_time = time.time()
    
    try:
        # Run test file
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per test
        )
        
        execution_time = (time.time() - start_time) * 1000  # ms
        
        return {
            "file": os.path.basename(test_file),
            "passed": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time_ms": execution_time
        }
    except subprocess.TimeoutExpired:
        return {
            "file": os.path.basename(test_file),
            "passed": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": "Test timeout (5 minutes exceeded)",
            "execution_time_ms": 300000
        }
    except Exception as e:
        return {
            "file": os.path.basename(test_file),
            "passed": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "execution_time_ms": 0
        }


def generate_summary(ffi_results: List[Dict], grpc_results: List[Dict], output_file: str):
    """Generate markdown summary report"""
    
    total_tests = len(ffi_results) + len(grpc_results)
    ffi_passed = sum(1 for r in ffi_results if r["passed"])
    grpc_passed = sum(1 for r in grpc_results if r["passed"])
    total_passed = ffi_passed + grpc_passed
    
    total_time = sum(r["execution_time_ms"] for r in ffi_results + grpc_results)
    
    summary = f"""# SochDB Testing Suite - Final Summary

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Overview

- **Total Tests:** {total_tests}
- **Passed:** {total_passed} ({total_passed/total_tests*100:.1f}%)
- **Failed:** {total_tests - total_passed} ({(total_tests - total_passed)/total_tests*100:.1f}%)
- **Total Execution Time:** {total_time/1000:.2f}s

---

## FFI (Embedded Mode) Tests

- **Total:** {len(ffi_results)}
- **Passed:** {ffi_passed}
- **Failed:** {len(ffi_results) - ffi_passed}
- **Success Rate:** {ffi_passed/len(ffi_results)*100 if ffi_results else 0:.1f}%

### FFI Test Results

"""
    
    for result in ffi_results:
        status = "✓" if result["passed"] else "✗"
        time_str = f"{result['execution_time_ms']:.0f}ms"
        summary += f"- {status} `{result['file']}` ({time_str})\n"
    
    summary += f"""
---

## gRPC (Server Mode) Tests

- **Total:** {len(grpc_results)}
- **Passed:** {grpc_passed}
- **Failed:** {len(grpc_results) - grpc_passed}
- **Success Rate:** {grpc_passed/len(grpc_results)*100 if grpc_results else 0:.1f}%

### gRPC Test Results

"""
    
    for result in grpc_results:
        status = "✓" if result["passed"] else "✗"
        time_str = f"{result['execution_time_ms']:.0f}ms"
        summary += f"- {status} `{result['file']}` ({time_str})\n"
    
    # Failed tests details
    failed_tests = [r for r in ffi_results + grpc_results if not r["passed"]]
    if failed_tests:
        summary += "\n---\n\n## Failed Tests Details\n\n"
        for result in failed_tests:
            summary += f"### {result['file']}\n\n"
            summary += f"**Exit Code:** {result['exit_code']}\n\n"
            if result["stderr"]:
                summary += f"**Error:**\n```\n{result['stderr'][:500]}\n```\n\n"
    
    # Write summary
    with open(output_file, 'w') as f:
        f.write(summary)
    
    return summary


def main():
    parser = argparse.ArgumentParser(description='Run SochDB test suite')
    parser.add_argument(
        '--mode',
        choices=['ffi', 'grpc', 'all'],
        default='all',
        help='Test mode to run'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("SochDB Testing Suite - Master Runner")
    print("="*80)
    print()
    
    ffi_results = []
    grpc_results = []
    
    # Run FFI tests
    if args.mode in ['ffi', 'all']:
        print("Running FFI (Embedded Mode) Tests...")
        print("-"*80)
        
        ffi_tests = discover_tests('tests_ffi')
        for i, test_file in enumerate(ffi_tests, 1):
            print(f"\n[{i}/{len(ffi_tests)}] Running {os.path.basename(test_file)}...")
            result = run_test_file(test_file)
            ffi_results.append(result)
            
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            print(f"{status} - {result['execution_time_ms']:.0f}ms")
            
            if args.verbose and result["stdout"]:
                print(result["stdout"])
            
            if not result["passed"] and result["stderr"]:
                print(f"Error: {result['stderr'][:200]}")
        
        # Save FFI results
        save_test_results(ffi_results, 'test_results/ffi_results.json')
        print(f"\nFFI Results: {sum(1 for r in ffi_results if r['passed'])}/{len(ffi_results)} passed")
    
    # Run gRPC tests
    if args.mode in ['grpc', 'all']:
        print("\n\nRunning gRPC (Server Mode) Tests...")
        print("-"*80)
        
        grpc_tests = discover_tests('tests_grpc')
        
        if not grpc_tests:
            print("No gRPC tests found (or server not available)")
        else:
            for i, test_file in enumerate(grpc_tests, 1):
                print(f"\n[{i}/{len(grpc_tests)}] Running {os.path.basename(test_file)}...")
                result = run_test_file(test_file)
                grpc_results.append(result)
                
                status = "✓ PASS" if result["passed"] else "✗ FAIL"
                print(f"{status} - {result['execution_time_ms']:.0f}ms")
                
                if args.verbose and result["stdout"]:
                    print(result["stdout"])
                
                if not result["passed"] and result["stderr"]:
                    print(f"Error: {result['stderr'][:200]}")
            
            # Save gRPC results
            save_test_results(grpc_results, 'test_results/grpc_results.json')
            print(f"\ngRPC Results: {sum(1 for r in grpc_results if r['passed'])}/{len(grpc_results)} passed")
    
    # Generate summary
    print("\n\nGenerating Summary Report...")
    print("-"*80)
    
    summary = generate_summary(ffi_results, grpc_results, 'test_results/summary.md')
    print(summary)
    
    # Exit with appropriate code
    total_failed = sum(1 for r in ffi_results + grpc_results if not r["passed"])
    sys.exit(0 if total_failed == 0 else 1)


if __name__ == "__main__":
    main()
