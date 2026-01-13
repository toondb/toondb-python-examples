# SochDB Comprehensive Test Harness

Unified test harness covering all SochDB Python SDK features with synthetic data generation, 10 real-world scenarios, metrics collection, and scorecard reporting.

## Features Tested

### Core SDK Features
- ✅ **Namespaces** - Multi-tenant isolation with use_namespace()
- ✅ **Hybrid Search** - Vector + keyword search with alpha blending
- ✅ **Semantic Cache** - Cache hit/miss tracking and paraphrase groups
- ✅ **Context Builder** - Token budgeting with STRICT/LENIENT modes
- ✅ **SSI Transactions** - Atomicity, rollback, conflict handling
- ✅ **Temporal Graph** - POINT_IN_TIME and RANGE queries
- ✅ **Atomic Writes** - WAL-based recovery and consistency
- ✅ **Sessions/Audit** - Complete audit trail logging
- ✅ **MCP/Server Mode** - Tool provider integration

## Architecture

### 1. SyntheticGenerator
Deterministically creates test data:
- **Topic centroids** - 200 unit-normalized vectors for ground-truth
- **Keyword mapping** - Topic-specific keywords for BM25 signal
- **Paraphrase groups** - Controlled query variants for cache testing
- **Graph structures** - Incident clusters with temporal edges
- **Ground-truth labels** - Expected doc IDs, relevance scores

### 2. ScenarioRunner
Runs 10 comprehensive scenarios:
1. **Multi-tenant Support Agent** - RAG + memory + cost control
2. **Sales/CRM Agent** - Lead enrichment with atomic updates
3. **SecOps Triage Agent** - Entity graph + incident timelines
4. **On-call Runbook Agent** - Hybrid search + context budgets
5. **Memory-building Agent** - Crash-safe atomic writes
6. **Finance Close Agent** - Ledger integrity + conflict resolution
7. **Compliance Agent** - Policy evaluation + explainability
8. **Procurement Agent** - Contract search + clause linking
9. **Edge Field-Tech Agent** - Offline time-travel diagnostics
10. **Tool-using Agent** - MCP integration testing

### 3. MetricsRecorder
Computes comprehensive metrics:
- **Correctness** (70%) - Leakage, atomicity, consistency
- **Retrieval** (15%) - NDCG@10, Recall@10, MRR
- **Performance** (10%) - P95 latencies per operation
- **Cost Proxies** (5%) - Cache hit rates, token budgets

### 4. ScorecardAggregator
Produces final reports:
- **JSON scorecard** - Structured results with all metrics
- **Summary table** - Human-readable pass/fail report
- **CSV export** - Optional tabular format

## Installation

```bash
# Install dependencies
pip install -r harness_requirements.txt

# Install SochDB SDK
cd ../sochdb-python-sdk
pip install -e .
cd ../sochdb_py_temp_test
```

## Usage

### Basic Run
```bash
python comprehensive_harness.py
```

### With Options
```bash
# Small scale, custom seed
python comprehensive_harness.py --scale small --seed 42

# Large scale, server mode
python comprehensive_harness.py --scale large --mode server

# Custom output file
python comprehensive_harness.py --output results/scorecard_v1.json
```

### Command-line Arguments
- `--seed` - Random seed for reproducibility (default: 1337)
- `--scale` - Test scale: small/medium/large (default: medium)
- `--mode` - DB mode: embedded/server (default: embedded)
- `--output` - Output JSON file (default: scorecard.json)

## Test Scales

| Scale  | Tenants | Docs/Collection | Queries | Duration |
|--------|---------|-----------------|---------|----------|
| Small  | 3       | 50              | 20      | ~30s     |
| Medium | 5       | 200             | 50      | ~2min    |
| Large  | 10      | 1000            | 100     | ~10min   |

## Scorecard Schema

```json
{
  "run_meta": {
    "seed": 1337,
    "scale": "medium",
    "mode": "embedded",
    "sdk_version": "0.3.3",
    "started_at": "2026-01-09T...",
    "duration_s": 123.4
  },
  "scenario_scores": {
    "01_multi_tenant_support": {
      "pass": true,
      "metrics": {
        "correctness": {
          "leakage_rate": 0.0,
          "atomicity_failures": 0,
          "consistency_failures": 0
        },
        "retrieval": {
          "ndcg_at_10": 0.875,
          "recall_at_10": 0.923,
          "mrr": 0.891
        },
        "cache": {
          "hit_rate": 0.67
        },
        "performance": {
          "p95_latencies_ms": {
            "vector_search": 12.3,
            "hybrid_search": 18.7
          }
        }
      }
    }
  },
  "global_metrics": {
    "p95_latency_ms": {
      "vector_search": 12.3,
      "hybrid_search": 18.7,
      "txn_commit": 4.1
    },
    "error_rate": 0.0
  },
  "overall": {
    "pass": true,
    "score_0_100": 95.8,
    "passed_scenarios": 10,
    "total_scenarios": 10,
    "failed_checks": []
  }
}
```

## Metrics Details

### Correctness (70% weight)
- **Leakage rate** - Cross-tenant data access (must be 0)
- **Atomicity failures** - Partial updates after rollback (must be 0)
- **Consistency failures** - Post-crash invariant violations (must be 0)
- **Time-travel correctness** - Temporal query accuracy (must be 100%)

### Retrieval Quality (15% weight)
- **NDCG@10** - Normalized Discounted Cumulative Gain
- **Recall@10** - Fraction of relevant docs in top-10
- **MRR** - Mean Reciprocal Rank

### Performance (10% weight)
- **P95 latencies** - 95th percentile per operation type
- **Thresholds** - hybrid_search <50ms, txn_commit <10ms

### Cost Proxies (5% weight)
- **Cache hit rate** - After paraphrase warmup (target: ≥60%)
- **Token budgets** - STRICT mode compliance (must be 100%)
- **LLM calls avoided** - Via cache hits

## Expected Thresholds

| Scenario | Metric | Threshold |
|----------|--------|-----------|
| 01 Multi-tenant | Leakage rate | 0% |
| 01 Multi-tenant | NDCG@10 | ≥0.70 |
| 01 Multi-tenant | Cache hit rate | ≥60% |
| 02 CRM | Atomicity failures | 0 |
| 02 CRM | Audit coverage | 100% |
| 03 SecOps | Cluster F1 | ≥90% |
| 03 SecOps | Temporal correctness | 100% |
| 04 Runbook | Top-1 accuracy | ≥70% |
| 04 Runbook | Top-3 accuracy | ≥90% |
| 05 Memory | Consistency after crash | 100% |
| 06 Finance | Double-post rate | 0% |
| 06 Finance | Retry success | ≥99% |
| 07 Compliance | Policy accuracy | 100% |
| 07 Compliance | Explainability | 100% |
| 08 Procurement | Recall@10 | ≥85% |
| 09 Field-Tech | Time-travel accuracy | 100% |
| 10 MCP | Tool call success | ≥99.9% |

## Deterministic Ground-Truth

### 1. Topic-Based Embeddings
```python
# 200 topic centroids (unit-normalized)
centroids = normalize(random.randn(200, 384))

# Document embedding = centroid + small noise
doc_vector = normalize(centroid[topic_id] + noise)

# Query embedding uses same centroid
# → Known relevant docs = docs with same topic_id
```

### 2. Controlled Keyword Signal
```python
# Each topic has 3-5 keywords
topic_keywords = {
  0: ["authentication", "security", "login"],
  1: ["performance", "latency", "throughput"],
  ...
}

# 70% of docs for topic include its keywords
# 5% of other docs include as noise
# → BM25 signal with controlled collisions
```

### 3. Paraphrase Groups
```python
# Same topic embedding, different text
paraphrases = [
  "How do I fix authentication issues?",
  "What's the solution for auth problems?",
  "Help with authentication errors",
]
# → Cache hit test with known equivalence
```

## Output Examples

### Console Summary
```
================================================================================
SCORECARD SUMMARY
================================================================================

Run Meta:
  Seed: 1337
  Scale: medium
  Mode: embedded
  Duration: 127.34s

Overall Score: 95.8/100
  Passed: 10/10
  Status: ✓ PASS

Scenario                                 Status     NDCG@10    Recall@10
----------------------------------------------------------------------
01_multi_tenant_support                  ✓ PASS     0.875      0.923
02_sales_crm                             ✓ PASS     N/A        N/A
03_secops_triage                         ✓ PASS     N/A        N/A
04_oncall_runbook                        ✓ PASS     N/A        0.912
05_memory_crash_safe                     ✓ PASS     N/A        N/A
06_finance_close                         ✓ PASS     N/A        N/A
07_compliance                            ✓ PASS     N/A        N/A
08_procurement                           ✓ PASS     N/A        0.887
09_edge_field_tech                       ✓ PASS     N/A        N/A
10_mcp_tool                              ✓ PASS     N/A        N/A

Global P95 Latencies (ms):
  vector_search: 11.23ms
  hybrid_search: 17.89ms
  txn_commit: 3.87ms
  ledger_commit: 4.21ms

================================================================================
```

## Integration with CI/CD

```bash
#!/bin/bash
# .github/workflows/sdk-integration-test.yml

set -e

# Run harness
python comprehensive_harness.py \
  --scale medium \
  --seed 1337 \
  --output ci_scorecard.json

# Check exit code
if [ $? -ne 0 ]; then
  echo "❌ SDK integration tests FAILED"
  exit 1
fi

# Extract score
score=$(jq '.overall.score_0_100' ci_scorecard.json)
echo "📊 Integration test score: $score/100"

# Fail if score < 90
if (( $(echo "$score < 90" | bc -l) )); then
  echo "❌ Score below threshold (90)"
  exit 1
fi

echo "✅ SDK integration tests PASSED"
```

## Troubleshooting

### Common Issues

1. **Import errors**
   ```bash
   # Ensure SDK is installed
   pip install -e ../sochdb-python-sdk
   ```

2. **Permission errors**
   ```bash
   # Clean up old test data
   rm -rf test_harness_db/
   ```

3. **Low scores**
   ```bash
   # Check specific scenario failures
   jq '.scenario_scores[] | select(.pass == false)' scorecard.json
   ```

4. **Slow execution**
   ```bash
   # Use smaller scale for quick validation
   python comprehensive_harness.py --scale small
   ```

## Extending the Harness

### Adding New Scenarios

```python
def scenario_11_custom(self, metrics: ScenarioMetrics):
    """Custom scenario description."""
    
    # 1. Setup
    with self.db.use_namespace("custom") as ns:
        collection = ns.create_collection("test", dimension=384)
    
    # 2. Execute operations
    start = time.time()
    # ... your test logic ...
    duration_ms = (time.time() - start) * 1000
    metrics.add_latency("custom_op", duration_ms)
    
    # 3. Validate correctness
    if failures > 0:
        metrics.passed = False
        metrics.errors.append(f"Validation failed: {failures}")
    
    # 4. Record metrics
    metrics.ndcg_at_10 = compute_ndcg(...)
    
    print(f"  → Custom metric: {value}")
```

### Adding Custom Metrics

```python
@dataclass
class ScenarioMetrics:
    # ... existing fields ...
    
    # Add your custom metric
    custom_metric: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["custom"] = {"metric": self.custom_metric}
        return result
```

## License

Apache 2.0 - See LICENSE file

## Contributors

- Sushanth (@sushanthpy)

## References

- [SochDB Python SDK Documentation](../sochdb-python-sdk/README.md)
- [Feature Comparison v0.3.3](../SDK_COMPARISON_v0.3.3.md)
- [Quick Reference v0.3.3](../QUICK_REFERENCE_v0.3.3.md)
