# SochDB Testing Suite - Final Summary

**Generated:** 2026-01-09 08:00:23

---

## Overview

- **Total Tests:** 59
- **Passed:** 59 (100.0%)
- **Failed:** 0 (0.0%)
- **Total Execution Time:** 30.70s

---

## FFI (Embedded Mode) Tests

- **Total:** 44
- **Passed:** 44
- **Failed:** 0
- **Success Rate:** 100.0%

### FFI Test Results

- ✓ `test_ffi_01_database_open_close.py` (744ms)
- ✓ `test_ffi_02_kv_put_get.py` (778ms)
- ✓ `test_ffi_03_kv_delete.py` (817ms)
- ✓ `test_ffi_04_kv_path_operations.py` (536ms)
- ✓ `test_ffi_05_scan_prefix.py` (453ms)
- ✓ `test_ffi_06_stats_checkpoint.py` (426ms)
- ✓ `test_ffi_07_transaction_context_manager.py` (435ms)
- ✓ `test_ffi_08_transaction_rollback.py` (416ms)
- ✓ `test_ffi_09_namespace_create.py` (423ms)
- ✓ `test_ffi_09_transaction_scan.py` (426ms)
- ✓ `test_ffi_10_namespace_operations.py` (441ms)
- ✓ `test_ffi_11_vector_search_real.py` (1736ms)
- ✓ `test_ffi_12_query_builder_basic.py` (17ms)
- ✓ `test_ffi_13_query_builder_filters.py` (18ms)
- ✓ `test_ffi_14_sql_create_table.py` (412ms)
- ✓ `test_ffi_15_sql_crud.py` (419ms)
- ✓ `test_ffi_16_sql_prepared.py` (421ms)
- ✓ `test_ffi_17_table_schema.py` (436ms)
- ✓ `test_ffi_18_index_policies.py` (422ms)
- ✓ `test_ffi_19_collection_create.py` (430ms)
- ✓ `test_ffi_20_collection_insert.py` (988ms)
- ✓ `test_ffi_21_collection_search.py` (1162ms)
- ✓ `test_ffi_22_hybrid_search_bm25.py` (431ms)
- ✓ `test_ffi_23_hybrid_search_combined.py` (1229ms)
- ✓ `test_ffi_24_graph_node_properties.py` (421ms)
- ✓ `test_ffi_25_graph_get_neighbors.py` (433ms)
- ✓ `test_ffi_26_graph_find_path.py` (437ms)
- ✓ `test_ffi_27_temporal_query_range.py` (434ms)
- ✓ `test_ffi_28_temporal_end_edge.py` (435ms)
- ✓ `test_ffi_29_cache_ttl.py` (988ms)
- ✓ `test_ffi_30_cache_stats.py` (434ms)
- ✓ `test_ffi_31_context_query_builder.py` (435ms)
- ✓ `test_ffi_32_context_truncation.py` (428ms)
- ✓ `test_ffi_33_wal_checkpoint.py` (439ms)
- ✓ `test_ffi_34_wal_recovery.py` (446ms)
- ✓ `test_ffi_35_format_toon.py` (430ms)
- ✓ `test_ffi_36_format_json.py` (435ms)
- ✓ `test_ffi_37_tracing_start.py` (418ms)
- ✓ `test_ffi_38_tracing_span.py` (428ms)
- ✓ `test_ffi_39_compression.py` (423ms)
- ✓ `test_ffi_40_error_handling_txn.py` (437ms)
- ✓ `test_ffi_41_error_handling_db.py` (448ms)
- ✓ `test_ffi_42_vector_index_batch.py` (1073ms)
- ✓ `test_ffi_43_vector_index_search_params.py` (1008ms)

---

## gRPC (Server Mode) Tests

- **Total:** 15
- **Passed:** 15
- **Failed:** 0
- **Success Rate:** 100.0%

### gRPC Test Results

- ✓ `test_grpc_01_grpc_connect.py` (422ms)
- ✓ `test_grpc_02_grpc_create_index.py` (419ms)
- ✓ `test_grpc_03_grpc_insert_vectors.py` (416ms)
- ✓ `test_grpc_04_grpc_search.py` (448ms)
- ✓ `test_grpc_05_grpc_create_collection.py` (446ms)
- ✓ `test_grpc_06_grpc_add_documents.py` (415ms)
- ✓ `test_grpc_07_grpc_search_collection.py` (421ms)
- ✓ `test_grpc_08_grpc_graph_node.py` (401ms)
- ✓ `test_grpc_09_grpc_graph_edge.py` (409ms)
- ✓ `test_grpc_10_grpc_traverse.py` (404ms)
- ✓ `test_grpc_11_grpc_cache_put.py` (412ms)
- ✓ `test_grpc_12_grpc_cache_get.py` (412ms)
- ✓ `test_grpc_13_grpc_context_query.py` (414ms)
- ✓ `test_grpc_14_grpc_trace.py` (404ms)
- ✓ `test_grpc_15_grpc_error_handling.py` (408ms)
