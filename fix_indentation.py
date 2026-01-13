#!/usr/bin/env python3
"""
Script to fix indentation errors in generated test files.

The test generator created files where the code inside execute_tests()
is not properly indented. This script fixes all such files.
"""

import os
import re

def fix_test_file(filepath):
    """Fix indentation issues in a test file."""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Pattern: After "def execute_tests(self):", followed by "try:", 
    # then another "try:" without proper indentation
    # We need to properly indent the inner try-except block
    
    lines = content.split('\n')
    fixed_lines = []
    in_execute_tests = False
    found_first_try = False
    indent_level = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detect execute_tests method
        if 'def execute_tests(self):' in line:
            in_execute_tests = True
            found_first_try = False
            fixed_lines.append(line)
            i += 1
            continue
        
        # If we're in execute_tests and find the outer try
        if in_execute_tests and not found_first_try and line.strip() == 'try:':
            found_first_try = True
            fixed_lines.append(line)
            i += 1
            continue
        
        # If we found the outer try and now see an inner try without proper indent
        if in_execute_tests and found_first_try and line.strip().startswith('try:'):
            # This is the problematic inner try - it should be indented
            # Skip this and the following except, and grab the actual test code
            i += 1  # Skip the "try:"
            
            # Collect all lines until we find "except" at the same level
            test_code_lines = []
            while i < len(lines):
                current = lines[i]
                if current.strip().startswith('except'):
                    # Skip the except block
                    i += 1
                    # Skip lines in the except block
                    while i < len(lines) and (lines[i].startswith('    ') or lines[i].strip().startswith('print')):
                        i += 1
                    break
                else:
                    # This is actual test code that needs to be properly indented
                    test_code_lines.append(current)
                    i += 1
            
            # Now add the test code with proper indentation (8 spaces for being inside try)
            for test_line in test_code_lines:
                if test_line.strip():  # Only process non-empty lines
                    # Remove any existing leading whitespace and add proper indent
                    stripped = test_line.lstrip()
                    fixed_lines.append('            ' + stripped)
                else:
                    fixed_lines.append('')
            
            # Look for add_result line which should be at the right level
            continue
        
        # Detect end of execute_tests
        if in_execute_tests and line.strip() and not line.startswith(' ') and 'def ' in line:
            in_execute_tests = False
            found_first_try = False
        
        fixed_lines.append(line)
        i += 1
    
    fixed_content = '\n'.join(fixed_lines)
    
    # Write back
    with open(filepath, 'w') as f:
        f.write(fixed_content)
    
    return True


def main():
    """Fix all test files with indentation issues."""
    
    test_files = [
        # Query Builder
        'test_ffi_12_query_builder_basic.py',
        'test_ffi_13_query_builder_filters.py',
        # SQL
        'test_ffi_14_sql_create_table.py',
        'test_ffi_15_sql_crud.py',
        'test_ffi_16_sql_prepared.py',
        'test_ffi_17_table_schema.py',
        'test_ffi_18_index_policies.py',
        # Collections
        'test_ffi_19_collection_create.py',
        'test_ffi_20_collection_insert.py',
        'test_ffi_21_collection_search.py',
        # Hybrid Search
        'test_ffi_22_hybrid_search_bm25.py',
        'test_ffi_23_hybrid_search_combined.py',
        # Graph
        'test_ffi_24_graph_node_properties.py',
        'test_ffi_25_graph_get_neighbors.py',
        'test_ffi_26_graph_find_path.py',
        # Temporal
        'test_ffi_27_temporal_query_range.py',
        'test_ffi_28_temporal_end_edge.py',
        # Cache
        'test_ffi_29_cache_ttl.py',
        'test_ffi_30_cache_stats.py',
        # Context
        'test_ffi_31_context_query_builder.py',
        'test_ffi_32_context_truncation.py',
        # WAL
        'test_ffi_33_wal_checkpoint.py',
        'test_ffi_34_wal_recovery.py',
        # Format
        'test_ffi_35_format_toon.py',
        'test_ffi_36_format_json.py',
        # Tracing
        'test_ffi_37_tracing_start.py',
        'test_ffi_38_tracing_span.py',
        # Error Handling
        'test_ffi_40_error_handling_txn.py',
        'test_ffi_41_error_handling_db.py',
        # Vector Index
        'test_ffi_42_vector_index_batch.py',
        'test_ffi_43_vector_index_search_params.py',
    ]
    
    tests_dir = 'tests_ffi'
    fixed_count = 0
    
    for filename in test_files:
        filepath = os.path.join(tests_dir, filename)
        if os.path.exists(filepath):
            try:
                fix_test_file(filepath)
                print(f"✓ Fixed {filename}")
                fixed_count += 1
            except Exception as e:
                print(f"✗ Error fixing {filename}: {e}")
        else:
            print(f"⚠ File not found: {filepath}")
    
    print(f"\nFixed {fixed_count}/{len(test_files)} files")


if __name__ == '__main__':
    main()
