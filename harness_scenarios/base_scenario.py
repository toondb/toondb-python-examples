"""
Base Scenario Class

All scenarios inherit from this base class.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time


@dataclass
class ScenarioMetrics:
    """Metrics for a single scenario - aligned with SochDB Agentic Benchmark."""
    scenario_id: str
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    
    # GATE Metrics (must all be 0 or 100%)
    leakage_rate: float = 0.0  # G1: Must be 0
    atomicity_failures: int = 0  # G2: Must be 0
    double_post_rate: float = 0.0  # G3: Must be 0
    time_travel_mismatches: int = 0  # G4: Must be 0
    crash_consistency_violations: int = 0  # G5: Must be 0
    audit_coverage: float = 0.0  # G6: Must be 100%
    schema_validation_failures: int = 0  # G7: Must be 0
    
    # Quality Metrics (scored)
    ndcg_scores: List[float] = field(default_factory=list)  # #1: NDCG@10
    recall_scores: List[float] = field(default_factory=list)  # #2: Recall@10
    precision_scores: List[float] = field(default_factory=list)  # #3: Precision@10
    mrr_scores: List[float] = field(default_factory=list)  # #4: MRR@10
    cache_hit_rate: Optional[float] = None  # #5
    cache_false_hit_rate: float = 0.0  # #6: Must be 0
    
    # Context & Token Metrics (scored)
    context_budget_violations: int = 0  # #7: Must be 0
    strict_truncation_failures: int = 0  # #8: Must be 0
    token_reduction_pct: Optional[float] = None  # #9: TOON vs JSON
    
    # Transaction Metrics (scored)
    txn_recovery_success_rate: Optional[float] = None  # #10
    avg_retries_on_conflict: Optional[float] = None  # #11
    conflict_rate: Optional[float] = None  # #12
    
    # Performance Metrics (scored)
    latencies: Dict[str, List[float]] = field(default_factory=lambda: {})  # #13-16
    throughput_ops_per_sec: Optional[float] = None  # #17
    
    # Operational Metrics (scored)
    recovery_replayed_entries: int = 0  # #18
    policy_accuracy: Optional[float] = None  # #19
    deny_with_explanation_pct: Optional[float] = None  # #20
    tool_call_success_rate: Optional[float] = None  # #21
    
    # Audit tracking
    audit_events: List[Dict[str, Any]] = field(default_factory=list)
    
    # LLM usage tracking
    llm_calls: int = 0
    llm_tokens: int = 0
    
    def add_latency(self, op_type: str, duration_ms: float):
        """Record operation latency."""
        if op_type not in self.latencies:
            self.latencies[op_type] = []
        self.latencies[op_type].append(duration_ms)
    
    def track_llm_call(self, tokens: int = 0):
        """Track LLM API call."""
        self.llm_calls += 1
        self.llm_tokens += tokens
    
    def log_audit_event(self, actor: str, action: str, resource: str, result: str = "success"):
        """Log audit event (G6 requirement)."""
        import datetime
        self.audit_events.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "actor": actor,
            "action": action,
            "resource": resource,
            "result": result
        })
        # Update coverage
        self.audit_coverage = 100.0 if len(self.audit_events) > 0 else 0.0
    
    def get_p95_latency(self, op_type: str) -> Optional[float]:
        """Get p95 latency for operation type."""
        if op_type not in self.latencies or not self.latencies[op_type]:
            return None
        import numpy as np
        return float(np.percentile(self.latencies[op_type], 95))
    
    def compute_avg_ndcg(self) -> Optional[float]:
        """Compute average NDCG@10."""
        if not self.ndcg_scores:
            return None
        return sum(self.ndcg_scores) / len(self.ndcg_scores)
    
    def compute_avg_recall(self) -> Optional[float]:
        """Compute average Recall@10."""
        if not self.recall_scores:
            return None
        return sum(self.recall_scores) / len(self.recall_scores)
    
    def compute_avg_mrr(self) -> Optional[float]:
        """Compute average MRR@10."""
        if not self.mrr_scores:
            return None
        return sum(self.mrr_scores) / len(self.mrr_scores)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for scorecard."""
        p95_latencies = {}
        for op_type in self.latencies:
            p95 = self.get_p95_latency(op_type)
            if p95 is not None:
                p95_latencies[op_type] = p95
        
        return {
            "passed": self.passed,
            "errors": self.errors,
            "gate_metrics": {
                "G1_leakage_rate": self.leakage_rate,
                "G2_atomicity_failures": self.atomicity_failures,
                "G3_double_post_rate": self.double_post_rate,
                "G4_time_travel_mismatches": self.time_travel_mismatches,
                "G5_crash_consistency_violations": self.crash_consistency_violations,
                "G6_audit_coverage": self.audit_coverage,
                "G7_schema_validation_failures": self.schema_validation_failures,
            },
            "quality": {
                "ndcg_scores": self.ndcg_scores,
                "avg_ndcg": self.compute_avg_ndcg(),
                "recall_scores": self.recall_scores,
                "avg_recall": self.compute_avg_recall(),
                "precision_scores": self.precision_scores,
                "mrr_scores": self.mrr_scores,
                "avg_mrr": self.compute_avg_mrr(),
                "cache_hit_rate": self.cache_hit_rate,
                "cache_false_hit_rate": self.cache_false_hit_rate,
            },
            "context": {
                "budget_violations": self.context_budget_violations,
                "strict_truncation_failures": self.strict_truncation_failures,
                "token_reduction_pct": self.token_reduction_pct,
            },
            "transactions": {
                "recovery_success_rate": self.txn_recovery_success_rate,
                "avg_retries": self.avg_retries_on_conflict,
                "conflict_rate": self.conflict_rate,
            },
            "performance": {
                "p95_latencies_ms": p95_latencies,
                "throughput_ops_per_sec": self.throughput_ops_per_sec,
            },
            "operational": {
                "recovery_replayed_entries": self.recovery_replayed_entries,
                "policy_accuracy": self.policy_accuracy,
                "deny_with_explanation_pct": self.deny_with_explanation_pct,
                "tool_call_success_rate": self.tool_call_success_rate,
            },
            "audit": {
                "coverage": self.audit_coverage,
                "events_count": len(self.audit_events),
            },
            "llm": {
                "calls": self.llm_calls,
                "tokens": self.llm_tokens,
            }
        }


class BaseScenario(ABC):
    """Base class for all test scenarios."""
    
    def __init__(self, scenario_id: str, db, generator, llm_client):
        """
        Initialize scenario.
        
        Args:
            scenario_id: Unique scenario identifier
            db: Database instance
            generator: SyntheticGenerator instance
            llm_client: Real LLM client instance
        """
        self.scenario_id = scenario_id
        self.db = db
        self.generator = generator
        self.llm = llm_client
        self.metrics = ScenarioMetrics(scenario_id=scenario_id)
    
    @abstractmethod
    def run(self) -> ScenarioMetrics:
        """
        Run the scenario and return metrics.
        
        Returns:
            ScenarioMetrics with results
        """
        pass
    
    def compute_ndcg(
        self, 
        results: List[Dict[str, Any]], 
        ground_truth: List[str],
        k: int = 10
    ) -> float:
        """Compute NDCG@k."""
        if not results or not ground_truth:
            return 0.0
        
        import numpy as np
        
        # Build relevance scores
        relevance = []
        for i, result in enumerate(results[:k]):
            doc_id = result.get("id")
            relevance.append(1.0 if doc_id in ground_truth else 0.0)
        
        # DCG
        dcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(relevance))
        
        # IDCG (ideal)
        ideal_relevance = sorted(relevance, reverse=True)
        idcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(ideal_relevance))
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def compute_recall(
        self,
        results: List[Dict[str, Any]],
        ground_truth: List[str],
        k: int = 10
    ) -> float:
        """Compute Recall@k."""
        if not ground_truth:
            return 0.0
        
        retrieved = set(r.get("id") for r in results[:k])
        relevant = set(ground_truth)
        
        hits = len(retrieved & relevant)
        return hits / len(relevant)
    
    def _track_time(self, op_type: str):
        """Context manager for tracking operation time."""
        return _TimeTracker(self.metrics, op_type)
    
    def measure_time(self, op_type: str):
        """Context manager for measuring operation time (alias for _track_time)."""
        return _TimeTracker(self.metrics, op_type)


class _TimeTracker:
    """Helper class for timing operations."""
    
    def __init__(self, metrics: ScenarioMetrics, op_type: str):
        self.metrics = metrics
        self.op_type = op_type
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration_ms = (time.time() - self.start_time) * 1000
            self.metrics.add_latency(self.op_type, duration_ms)
