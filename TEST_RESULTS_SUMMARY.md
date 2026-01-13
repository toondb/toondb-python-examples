
# SochDB Comprehensive Test Harness - Results Summary

## Run Configuration

| Setting | Value |
|---------|-------|
| Seed | `1337` |
| Scale | `small` |
| Mode | `embedded` |
| SDK Version | `0.3.3` |
| Duration | `3.75s` |
| Timestamp | `2026-01-09T16:01:16.734330` |

## Overall Results

| Metric | Value |
|--------|-------|
| **Status** | **❌ FAIL** |
| **Score** | **80.0/100** |
| Passed Scenarios | 8/10 |
| Failed Checks | 2 |

## Scenario Results

| # | Scenario | Status | NDCG@10 | Recall@10 | Leakage | Atomicity |
|---|----------|--------|---------|-----------|---------|-----------|
| 1 | 01 Multi Tenant Support | ✅ PASS | 0.171 | 0.400 | 0.0% | 0 |
| 2 | 02 Sales Crm | ✅ PASS | N/A | N/A | 0.0% | 0 |
| 3 | 03 Secops Triage | ✅ PASS | N/A | N/A | 0.0% | 0 |
| 4 | 04 Oncall Runbook | ❌ FAIL | N/A | 0.100 | 0.0% | 0 |
| 5 | 05 Memory Crash Safe | ✅ PASS | N/A | N/A | 0.0% | 0 |
| 6 | 06 Finance Close | ✅ PASS | N/A | N/A | 0.0% | 0 |
| 7 | 07 Compliance | ✅ PASS | N/A | N/A | 0.0% | 0 |
| 8 | 08 Procurement | ❌ FAIL | N/A | 0.300 | 0.0% | 0 |
| 9 | 09 Edge Field Tech | ✅ PASS | N/A | N/A | 0.0% | 0 |
| 10 | 10 Mcp Tool | ✅ PASS | N/A | N/A | 0.0% | 0 |

## Performance Metrics (P95 Latencies)

| Operation | P95 Latency | Target | Status |
|-----------|-------------|--------|--------|
| Vector Search | 5.06ms | <20ms | ✅ |
| Hybrid Search | 9.62ms | <50ms | ✅ |
| Txn Commit | 5.02ms | <10ms | ✅ |
| Ledger Commit | 7.77ms | <10ms | ✅ |

## Failed Checks

- ❌ 04_onCall_runbook: Top-1 accuracy below threshold: 10.00%
- ❌ 08_procurement: Recall below threshold: 30.00%

## Success Criteria

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Zero Leakage | 0% | 0.0% | ✅ |
| Zero Atomicity Failures | 0 | 0 | ✅ |
| Zero Consistency Failures | 0 | 0 | ✅ |
| Overall Pass Rate | ≥90% | 80.0% | ⚠️ |

---

**Generated**: 1768003276.7372248
**Harness Version**: 1.0.0
