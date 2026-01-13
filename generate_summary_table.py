#!/usr/bin/env python3
"""
Generate a markdown summary table from scorecard JSON.
Usage: python3 generate_summary_table.py test_scorecard.json
"""

import json
import sys
from pathlib import Path

def generate_table(scorecard_path):
    with open(scorecard_path) as f:
        data = json.load(f)
    
    print("\n# SochDB Comprehensive Test Harness - Results Summary\n")
    
    # Run Meta
    print("## Run Configuration\n")
    meta = data['run_meta']
    print(f"| Setting | Value |")
    print(f"|---------|-------|")
    print(f"| Seed | `{meta['seed']}` |")
    print(f"| Scale | `{meta['scale']}` |")
    print(f"| Mode | `{meta['mode']}` |")
    print(f"| SDK Version | `{meta['sdk_version']}` |")
    print(f"| Duration | `{meta['duration_s']:.2f}s` |")
    print(f"| Timestamp | `{meta['started_at']}` |")
    
    # Overall
    print("\n## Overall Results\n")
    overall = data['overall']
    status_emoji = "✅" if overall['pass'] else "❌"
    print(f"| Metric | Value |")
    print(f"|--------|-------|")
    print(f"| **Status** | **{status_emoji} {'PASS' if overall['pass'] else 'FAIL'}** |")
    print(f"| **Score** | **{overall['score_0_100']:.1f}/100** |")
    print(f"| Passed Scenarios | {overall['passed_scenarios']}/{overall['total_scenarios']} |")
    print(f"| Failed Checks | {len(overall['failed_checks'])} |")
    
    # Scenario Breakdown
    print("\n## Scenario Results\n")
    print("| # | Scenario | Status | NDCG@10 | Recall@10 | Leakage | Atomicity |")
    print("|---|----------|--------|---------|-----------|---------|-----------|")
    
    for i, (scenario_id, score) in enumerate(data['scenario_scores'].items(), 1):
        status = "✅ PASS" if score['pass'] else "❌ FAIL"
        metrics = score['metrics']
        
        ndcg = metrics['retrieval']['ndcg_at_10']
        ndcg_str = f"{ndcg:.3f}" if ndcg is not None else "N/A"
        
        recall = metrics['retrieval']['recall_at_10']
        recall_str = f"{recall:.3f}" if recall is not None else "N/A"
        
        leakage = metrics['correctness']['leakage_rate']
        leakage_str = f"{leakage:.1%}"
        
        atomicity = metrics['correctness']['atomicity_failures']
        
        name = scenario_id.replace('_', ' ').title()
        print(f"| {i} | {name} | {status} | {ndcg_str} | {recall_str} | {leakage_str} | {atomicity} |")
    
    # Performance
    print("\n## Performance Metrics (P95 Latencies)\n")
    p95 = data['global_metrics']['p95_latency_ms']
    if p95:
        print("| Operation | P95 Latency | Target | Status |")
        print("|-----------|-------------|--------|--------|")
        
        thresholds = {
            'vector_search': 20,
            'hybrid_search': 50,
            'txn_commit': 10,
            'ledger_commit': 10,
        }
        
        for op_type, latency in p95.items():
            threshold = thresholds.get(op_type, 50)
            status = "✅" if latency < threshold else "⚠️"
            print(f"| {op_type.replace('_', ' ').title()} | {latency:.2f}ms | <{threshold}ms | {status} |")
    
    # Failed Checks
    if overall['failed_checks']:
        print("\n## Failed Checks\n")
        for check in overall['failed_checks']:
            print(f"- ❌ {check}")
    
    # Success Criteria
    print("\n## Success Criteria\n")
    print("| Criterion | Target | Actual | Status |")
    print("|-----------|--------|--------|--------|")
    
    # Calculate aggregate correctness
    total_leakage = 0
    total_atomicity = 0
    total_consistency = 0
    count = 0
    
    for score in data['scenario_scores'].values():
        metrics = score['metrics']
        total_leakage += metrics['correctness']['leakage_rate']
        total_atomicity += metrics['correctness']['atomicity_failures']
        total_consistency += metrics['correctness']['consistency_failures']
        count += 1
    
    avg_leakage = total_leakage / count if count > 0 else 0
    
    print(f"| Zero Leakage | 0% | {avg_leakage:.1%} | {'✅' if avg_leakage == 0 else '❌'} |")
    print(f"| Zero Atomicity Failures | 0 | {total_atomicity} | {'✅' if total_atomicity == 0 else '❌'} |")
    print(f"| Zero Consistency Failures | 0 | {total_consistency} | {'✅' if total_consistency == 0 else '❌'} |")
    print(f"| Overall Pass Rate | ≥90% | {overall['score_0_100']:.1f}% | {'✅' if overall['score_0_100'] >= 90 else '⚠️'} |")
    
    print("\n---\n")
    print(f"**Generated**: {Path(scorecard_path).stat().st_mtime}")
    print(f"**Harness Version**: 1.0.0")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_summary_table.py <scorecard.json>")
        sys.exit(1)
    
    generate_table(sys.argv[1])
