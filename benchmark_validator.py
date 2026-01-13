"""
SochDB Agentic Benchmark Validator
===================================

Validates scorecard against SochDB Agentic Benchmark Rubric:
- 7 GATE metrics (must ALL pass or automatic FAIL)
- 21 scored metrics (100 points total)
- Pass: ≥70 points, Strong: ≥85 points

Usage:
    python benchmark_validator.py scorecard_real_llm.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class BenchmarkValidator:
    """Validates scorecard against SochDB Agentic Benchmark Rubric."""
    
    # GATE metrics (must ALL pass)
    GATE_METRICS = {
        'G1': {'name': 'conflict_rate', 'threshold': 0, 'op': '==', 'desc': 'Conflict rate must be 0%'},
        'G2': {'name': 'data_loss_incidents', 'threshold': 0, 'op': '==', 'desc': 'Data loss incidents must be 0'},
        'G3': {'name': 'double_post_rate', 'threshold': 0, 'op': '==', 'desc': 'Double-post rate must be 0%'},
        'G4': {'name': 'time_travel_mismatches', 'threshold': 0, 'op': '==', 'desc': 'Time-travel mismatches must be 0'},
        'G5': {'name': 'crash_consistency_violations', 'threshold': 0, 'op': '==', 'desc': 'Crash consistency violations must be 0'},
        'G6': {'name': 'audit_coverage', 'threshold': 100, 'op': '==', 'desc': 'Audit coverage must be 100%'},
        'G7': {'name': 'schema_validation_failures', 'threshold': 0, 'op': '==', 'desc': 'Schema validation failures must be 0'},
    }
    
    # Scored metrics (100 points total)
    SCORED_METRICS = [
        # Quality (35 points)
        {'id': '#1', 'name': 'avg_ndcg', 'weight': 10, 'threshold': 0.90, 'category': 'quality'},
        {'id': '#2', 'name': 'avg_recall_at_k', 'weight': 8, 'threshold': 0.85, 'category': 'quality'},
        {'id': '#3', 'name': 'semantic_accuracy', 'weight': 7, 'threshold': 0.80, 'category': 'quality'},
        {'id': '#4', 'name': 'mrr_at_10', 'weight': 5, 'threshold': 0.75, 'category': 'quality'},
        {'id': '#5', 'name': 'graph_consistency', 'weight': 5, 'threshold': 1.00, 'category': 'quality'},
        
        # Context/Token Management (11 points)
        {'id': '#7', 'name': 'context_budget_violations', 'weight': 5, 'threshold': 0, 'category': 'context', 'inverse': True},
        {'id': '#8', 'name': 'strict_truncation_failures', 'weight': 3, 'threshold': 0, 'category': 'context', 'inverse': True},
        {'id': '#9', 'name': 'token_reduction_pct', 'weight': 3, 'threshold': 25, 'category': 'context'},
        
        # Transactions (11 points)
        {'id': '#10', 'name': 'txn_abort_rate', 'weight': 4, 'threshold': 0.05, 'category': 'transactions', 'inverse': True},
        {'id': '#11', 'name': 'avg_retries_on_conflict', 'weight': 3, 'threshold': 2.0, 'category': 'transactions', 'inverse': True},
        {'id': '#12', 'name': 'conflict_rate', 'weight': 4, 'threshold': 0.10, 'category': 'transactions', 'inverse': True},
        
        # Performance (19 points)
        {'id': '#13', 'name': 'p95_hybrid_search_latency_ms', 'weight': 5, 'threshold': 100, 'category': 'performance', 'inverse': True},
        {'id': '#14', 'name': 'p95_graph_query_latency_ms', 'weight': 4, 'threshold': 150, 'category': 'performance', 'inverse': True},
        {'id': '#15', 'name': 'p95_temporal_query_latency_ms', 'weight': 4, 'threshold': 120, 'category': 'performance', 'inverse': True},
        {'id': '#16', 'name': 'throughput_ops_per_sec', 'weight': 3, 'threshold': 500, 'category': 'performance'},
        {'id': '#17', 'name': 'batch_speedup_vs_single', 'weight': 3, 'threshold': 3.0, 'category': 'performance'},
        
        # Operational (18 points)
        {'id': '#18', 'name': 'recovery_replayed_entries', 'weight': 4, 'threshold': 1, 'category': 'operational'},
        {'id': '#19', 'name': 'policy_accuracy', 'weight': 4, 'threshold': 1.00, 'category': 'operational'},
        {'id': '#20', 'name': 'deny_with_explanation_pct', 'weight': 2, 'threshold': 100, 'category': 'operational'},
        {'id': '#21', 'name': 'namespace_isolation_violations', 'weight': 4, 'threshold': 0, 'category': 'operational', 'inverse': True},
        {'id': '#22', 'name': 'tool_call_success_rate', 'weight': 4, 'threshold': 0.95, 'category': 'operational'},
        
        # Concurrency (6 points)
        {'id': '#6', 'name': 'hybrid_search_concurrency', 'weight': 6, 'threshold': 10, 'category': 'concurrency'},
    ]
    
    def __init__(self, scorecard: Dict):
        self.scorecard = scorecard
        self.gate_results = {}
        self.scored_results = {}
        self.total_score = 0.0
        self.passed_gates = 0
        self.total_points = 0.0
    
    def validate(self) -> Tuple[bool, Dict]:
        """Validate scorecard against benchmark rubric."""
        # Collect all metrics from scenarios
        all_metrics = self._collect_metrics()
        
        # Validate GATE metrics
        gate_pass = self._validate_gate_metrics(all_metrics)
        
        # Calculate scored metrics
        score = self._calculate_scored_metrics(all_metrics)
        
        # Determine overall result
        overall_pass = gate_pass and score >= 70.0
        
        result = {
            'gate_pass': gate_pass,
            'gate_results': self.gate_results,
            'score': score,
            'scored_results': self.scored_results,
            'overall_pass': overall_pass,
            'grade': self._get_grade(score, gate_pass),
        }
        
        return overall_pass, result
    
    def _collect_metrics(self) -> Dict:
        """Collect all metrics from scorecard."""
        metrics = {}
        
        for scenario_id, scenario_data in self.scorecard['scenario_scores'].items():
            scenario_metrics = scenario_data['metrics']
            
            # Flatten all categories
            for category in ['gate_metrics', 'quality', 'context', 'transactions', 'performance', 'operational', 'concurrency']:
                if category in scenario_metrics:
                    for key, value in scenario_metrics[category].items():
                        # Aggregate metrics (max, avg, etc.)
                        if key in metrics:
                            # For violations/errors, sum them
                            if 'violations' in key or 'failures' in key or 'incidents' in key:
                                metrics[key] += value
                            # For rates/percentages, average them
                            elif 'rate' in key or 'pct' in key or 'coverage' in key or 'accuracy' in key:
                                if isinstance(metrics[key], list):
                                    metrics[key].append(value)
                                else:
                                    metrics[key] = [metrics[key], value]
                            # For counts, sum them
                            else:
                                if isinstance(value, (int, float)):
                                    metrics[key] = metrics.get(key, 0) + value
                        else:
                            metrics[key] = value
        
        # Average list values
        for key, value in metrics.items():
            if isinstance(value, list):
                metrics[key] = sum(value) / len(value) if value else 0
        
        return metrics
    
    def _validate_gate_metrics(self, metrics: Dict) -> bool:
        """Validate GATE metrics (ALL must pass)."""
        print("\n" + "="*80)
        print("GATE METRICS (must ALL pass)")
        print("="*80)
        
        passed_count = 0
        
        for gate_id, gate_spec in self.GATE_METRICS.items():
            metric_name = gate_spec['name']
            threshold = gate_spec['threshold']
            desc = gate_spec['desc']
            
            value = metrics.get(metric_name, None)
            
            if value is None:
                status = '✗ MISSING'
                passed = False
            else:
                if gate_spec['op'] == '==':
                    passed = value == threshold
                elif gate_spec['op'] == '<=':
                    passed = value <= threshold
                elif gate_spec['op'] == '>=':
                    passed = value >= threshold
                else:
                    passed = False
                
                status = '✓ PASS' if passed else '✗ FAIL'
                if passed:
                    passed_count += 1
            
            self.gate_results[gate_id] = {
                'metric': metric_name,
                'value': value,
                'threshold': threshold,
                'passed': passed if value is not None else False,
                'desc': desc,
            }
            
            print(f"{gate_id}: {status:10} {metric_name} = {value} (must be {threshold}) - {desc}")
        
        gate_pass = (passed_count == len(self.GATE_METRICS))
        print(f"\nGATE Summary: {passed_count}/{len(self.GATE_METRICS)} passed {'✓ PASS' if gate_pass else '✗ FAIL (auto-FAIL)'}")
        
        return gate_pass
    
    def _calculate_scored_metrics(self, metrics: Dict) -> float:
        """Calculate score from scored metrics."""
        print("\n" + "="*80)
        print("SCORED METRICS (100 points total)")
        print("="*80)
        
        score = 0.0
        
        for metric_spec in self.SCORED_METRICS:
            metric_id = metric_spec['id']
            metric_name = metric_spec['name']
            weight = metric_spec['weight']
            threshold = metric_spec['threshold']
            category = metric_spec['category']
            inverse = metric_spec.get('inverse', False)
            
            value = metrics.get(metric_name, None)
            
            if value is None:
                points = 0.0
                status = 'MISSING'
            else:
                # Calculate points
                if inverse:
                    # Lower is better (violations, failures, latency)
                    if value <= threshold:
                        points = weight
                        status = 'FULL'
                    elif value <= threshold * 1.5:
                        points = weight * 0.5
                        status = 'PARTIAL'
                    else:
                        points = 0.0
                        status = 'FAIL'
                else:
                    # Higher is better (accuracy, throughput)
                    if value >= threshold:
                        points = weight
                        status = 'FULL'
                    elif value >= threshold * 0.7:
                        points = weight * 0.5
                        status = 'PARTIAL'
                    else:
                        points = 0.0
                        status = 'FAIL'
            
            score += points
            
            self.scored_results[metric_id] = {
                'metric': metric_name,
                'value': value,
                'threshold': threshold,
                'weight': weight,
                'points': points,
                'category': category,
            }
            
            print(f"{metric_id:5} {status:10} {metric_name:35} = {str(value):8} (threshold: {threshold:8}) [{points}/{weight} pts]")
        
        print(f"\nTotal Score: {score:.1f}/100")
        
        return score
    
    def _get_grade(self, score: float, gate_pass: bool) -> str:
        """Get grade based on score and gate pass."""
        if not gate_pass:
            return 'F (GATE FAIL)'
        elif score >= 85:
            return 'A (Strong)'
        elif score >= 70:
            return 'B (Pass)'
        else:
            return 'C (Weak)'
    
    def print_summary(self, result: Dict):
        """Print validation summary."""
        print("\n" + "="*80)
        print("BENCHMARK VALIDATION SUMMARY")
        print("="*80)
        
        print(f"\nGATE Metrics: {result['gate_pass']:5} {'✓ ALL PASS' if result['gate_pass'] else '✗ FAIL'}")
        print(f"Score:        {result['score']:5.1f}/100")
        print(f"Grade:        {result['grade']}")
        print(f"Overall:      {'✓ PASS' if result['overall_pass'] else '✗ FAIL'}")
        
        if not result['gate_pass']:
            print(f"\n⚠️  GATE metrics failed - automatic FAIL regardless of point score")
            print(f"    Failed GATE metrics:")
            for gate_id, gate_result in result['gate_results'].items():
                if not gate_result['passed']:
                    print(f"      {gate_id}: {gate_result['metric']} = {gate_result['value']} (must be {gate_result['threshold']})")
        
        print("\n" + "="*80 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python benchmark_validator.py <scorecard.json>")
        return 1
    
    scorecard_path = Path(sys.argv[1])
    
    if not scorecard_path.exists():
        print(f"Error: Scorecard file not found: {scorecard_path}")
        return 1
    
    # Load scorecard
    with open(scorecard_path) as f:
        scorecard = json.load(f)
    
    # Validate
    validator = BenchmarkValidator(scorecard)
    overall_pass, result = validator.validate()
    validator.print_summary(result)
    
    # Save validation result
    output_path = scorecard_path.parent / f"{scorecard_path.stem}_validation.json"
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✓ Validation result saved to: {output_path}")
    
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
