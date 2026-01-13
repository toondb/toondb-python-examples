"""
SochDB Comprehensive Test Harness v2.0
======================================

Refactored architecture:
- Separate folders for each scenario
- Real Azure OpenAI LLM integration (no mocking)
- Synthetic ground-truth for validation
- Professional reporting

Each scenario is independent and uses real LLM API calls.
"""

import json
import os
import shutil
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np
from dotenv import load_dotenv

# Add SDK path
sdk_path = Path(__file__).parent.parent / "sochdb-python-sdk" / "src"
sys.path.insert(0, str(sdk_path))

from sochdb import Database

# Load environment
load_dotenv()

# Import harness components
from harness_scenarios.llm_client import get_llm_client, get_embedding_dimension
from harness_scenarios.base_scenario import BaseScenario, ScenarioMetrics

# Import synthetic generator from old harness
from comprehensive_harness import SyntheticGenerator


def load_scenario(scenario_id: str, db, generator, llm_client) -> BaseScenario:
    """
    Dynamically load a scenario module.
    
    Args:
        scenario_id: Scenario ID (e.g., "01_multi_tenant")
        db: Database instance
        generator: Synthetic data generator
        llm_client: Real LLM client
        
    Returns:
        Scenario instance
    """
    try:
        # Import scenario module
        module_path = f"harness_scenarios.{scenario_id}.scenario"
        module = __import__(module_path, fromlist=[''])
        
        # Find scenario class (should inherit from BaseScenario)
        for name in dir(module):
            obj = getattr(module, name)
            if (isinstance(obj, type) and 
                issubclass(obj, BaseScenario) and 
                obj is not BaseScenario):
                return obj(db, generator, llm_client)
        
        raise ImportError(f"No scenario class found in {module_path}")
        
    except Exception as e:
        print(f"  ⚠️ Could not load scenario {scenario_id}: {e}")
        return None


class ScorecardAggregator:
    """Aggregates metrics and produces final scorecard."""
    
    def __init__(self, scenarios: Dict[str, ScenarioMetrics], run_meta: Dict):
        self.scenarios = scenarios
        self.run_meta = run_meta
    
    def generate_scorecard(self) -> Dict:
        """Generate comprehensive scorecard."""
        scenario_scores = {}
        
        for scenario_id, metrics in self.scenarios.items():
            scenario_scores[scenario_id] = {
                "pass": metrics.passed,
                "metrics": metrics.to_dict()
            }
        
        # Compute global metrics
        all_latencies = defaultdict(list)
        total_llm_calls = 0
        total_llm_tokens = 0
        
        for metrics in self.scenarios.values():
            for op_type, latencies in metrics.latencies.items():
                all_latencies[op_type].extend(latencies)
            total_llm_calls += metrics.llm_calls
            total_llm_tokens += metrics.llm_tokens
        
        p95_latencies = {}
        for op_type, latencies in all_latencies.items():
            if latencies:
                p95_latencies[op_type] = float(np.percentile(latencies, 95))
        
        # Compute overall pass/fail
        total_scenarios = len(self.scenarios)
        passed_scenarios = sum(1 for m in self.scenarios.values() if m.passed)
        overall_pass = passed_scenarios == total_scenarios
        score = (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0.0
        
        failed_checks = []
        for scenario_id, metrics in self.scenarios.items():
            if not metrics.passed:
                failed_checks.extend([f"{scenario_id}: {err}" for err in metrics.errors])
        
        scorecard = {
            "run_meta": self.run_meta,
            "scenario_scores": scenario_scores,
            "global_metrics": {
                "p95_latency_ms": p95_latencies,
                "error_rate": 1 - (passed_scenarios / total_scenarios) if total_scenarios > 0 else 0.0,
                "llm_usage": {
                    "total_calls": total_llm_calls,
                    "total_tokens": total_llm_tokens,
                }
            },
            "overall": {
                "pass": overall_pass,
                "score_0_100": score,
                "passed_scenarios": passed_scenarios,
                "total_scenarios": total_scenarios,
                "failed_checks": failed_checks,
            }
        }
        
        return scorecard
    
    def print_summary_table(self, scorecard: Dict):
        """Print summary table."""
        print(f"\n{'='*80}")
        print(f"SCORECARD SUMMARY (Real LLM Mode)")
        print(f"{'='*80}\n")
        
        print(f"Run Meta:")
        print(f"  Seed: {scorecard['run_meta']['seed']}")
        print(f"  Scale: {scorecard['run_meta']['scale']}")
        print(f"  Mode: {scorecard['run_meta']['mode']}")
        print(f"  Duration: {scorecard['run_meta']['duration_s']:.2f}s")
        
        print(f"\nOverall Score: {scorecard['overall']['score_0_100']:.1f}/100")
        print(f"  Passed: {scorecard['overall']['passed_scenarios']}/{scorecard['overall']['total_scenarios']}")
        print(f"  Status: {'✓ PASS' if scorecard['overall']['pass'] else '✗ FAIL'}")
        
        print(f"\nLLM Usage:")
        llm_usage = scorecard['global_metrics']['llm_usage']
        print(f"  Total API calls: {llm_usage['total_calls']}")
        print(f"  Total tokens: {llm_usage['total_tokens']:,}")
        
        print(f"\n{'Scenario':<40} {'Status':<10} {'LLM Calls':<12} {'Tokens':<10}")
        print(f"{'-'*72}")
        
        for scenario_id, score in scorecard['scenario_scores'].items():
            status = '✓ PASS' if score['pass'] else '✗ FAIL'
            llm_calls = score['metrics']['llm']['calls']
            llm_tokens = score['metrics']['llm']['tokens']
            
            print(f"{scenario_id:<40} {status:<10} {llm_calls:<12} {llm_tokens:<10}")
        
        if scorecard['overall']['failed_checks']:
            print(f"\nFailed Checks:")
            for check in scorecard['overall']['failed_checks']:
                print(f"  ✗ {check}")
        
        print(f"\nGlobal P95 Latencies (ms):")
        for op_type, latency in scorecard['global_metrics']['p95_latency_ms'].items():
            print(f"  {op_type}: {latency:.2f}ms")
        
        print(f"\n{'='*80}\n")


def main():
    """Run comprehensive test harness with real LLM."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SochDB Comprehensive Test Harness v2.0 (Real LLM)")
    parser.add_argument("--seed", type=int, default=1337, help="Random seed")
    parser.add_argument("--scale", choices=["small", "medium", "large"], default="small", help="Test scale")
    parser.add_argument("--mode", choices=["embedded", "server"], default="embedded", help="DB mode")
    parser.add_argument("--output", default="scorecard_real_llm.json", help="Output JSON file")
    parser.add_argument("--scenarios", nargs="+", help="Specific scenarios to run (e.g., 01_multi_tenant)")
    
    args = parser.parse_args()
    
    # Clean up old test data
    test_db_path = Path("./test_harness_real_llm_db")
    if test_db_path.exists():
        shutil.rmtree(test_db_path)
    
    # Initialize components
    print("=" * 80)
    print("SochDB Comprehensive Test Harness v2.0")
    print("Using REAL Azure OpenAI (no mocking)")
    print("=" * 80)
    
    print("\nInitializing...")
    start_time = time.time()
    
    # Get embedding dimension from LLM
    embedding_dim = get_embedding_dimension()
    print(f"  Embedding dimension: {embedding_dim}")
    
    # Initialize LLM client (REAL Azure OpenAI)
    try:
        llm_client = get_llm_client()
        print(f"  ✓ Azure OpenAI client initialized")
        print(f"    Endpoint: {llm_client.endpoint}")
        print(f"    Embedding model: {llm_client.embedding_deployment}")
    except Exception as e:
        print(f"  ✗ Failed to initialize LLM client: {e}")
        print(f"  Make sure AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT are set in .env")
        return 1
    
    # Initialize synthetic generator (but use real LLM for content)
    generator = SyntheticGenerator(seed=args.seed, scale=args.scale)
    generator.embedding_dim = embedding_dim  # Override with real dimension
    print(f"  Synthetic ground-truth generator: {generator.num_topics} topics")
    
    # Initialize database
    db = Database.open(str(test_db_path))
    print(f"  Database opened: {test_db_path}")
    
    # Discover available scenarios
    scenarios_dir = Path(__file__).parent / "harness_scenarios"
    available_scenarios = []
    
    for item in sorted(scenarios_dir.iterdir()):
        if item.is_dir() and item.name.startswith(("01_", "02_", "03_", "04_", "05_",
                                                     "06_", "07_", "08_", "09_", "10_",
                                                     "11_", "12_", "13_", "14_", "15_")):
            available_scenarios.append(item.name)
    
    # Filter scenarios if specified
    if args.scenarios:
        scenarios_to_run = [s for s in available_scenarios if s in args.scenarios]
    else:
        scenarios_to_run = available_scenarios
    
    print(f"\n{'='*80}")
    print(f"Running {len(scenarios_to_run)} Scenarios in {args.mode} mode")
    print(f"{'='*80}\n")
    
    # Run scenarios
    results = {}
    
    for scenario_id in scenarios_to_run:
        scenario = load_scenario(scenario_id, db, generator, llm_client)
        
        if scenario is None:
            print(f"[{scenario_id}] ⚠️ SKIPPED (could not load)")
            continue
        
        try:
            metrics = scenario.run()
            results[scenario_id] = metrics
        except Exception as e:
            print(f"[{scenario_id}] ✗ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            
            # Create error metrics
            metrics = ScenarioMetrics(scenario_id=scenario_id)
            metrics.passed = False
            metrics.errors.append(str(e))
            results[scenario_id] = metrics
    
    duration_s = time.time() - start_time
    
    # Generate scorecard
    run_meta = {
        "seed": args.seed,
        "scale": args.scale,
        "mode": args.mode,
        "llm_mode": "real",
        "sdk_version": "0.3.3",
        "started_at": datetime.now().isoformat(),
        "duration_s": duration_s,
    }
    
    aggregator = ScorecardAggregator(results, run_meta)
    scorecard = aggregator.generate_scorecard()
    
    # Save scorecard
    output_path = Path(args.output)
    with open(output_path, "w") as f:
        json.dump(scorecard, f, indent=2)
    
    print(f"\n✓ Scorecard saved to: {output_path}")
    
    # Print summary table
    aggregator.print_summary_table(scorecard)
    
    # Cleanup
    db.close()
    shutil.rmtree(test_db_path)
    
    return 0 if scorecard['overall']['pass'] else 1


if __name__ == "__main__":
    sys.exit(main())
