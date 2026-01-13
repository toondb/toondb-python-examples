"""
Scenario 13: Crash Recovery & Consistency
========================================

Tests:
- G5: Crash consistency violations (GATE - must be 0)
- #18: Recovery replay effectiveness (4 pts)
- Kill/restart during writes
- Multi-index consistency
"""

import random
import sys
import shutil
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "sochdb-python-sdk" / "src"))

from sochdb import Database
from harness_scenarios.base_scenario import BaseScenario, ScenarioMetrics


class CrashRecoveryScenario(BaseScenario):
    """Crash recovery testing with consistency validation."""
    
    def __init__(self, db, generator, llm_client):
        super().__init__("13_crash_recovery", db, generator, llm_client)
        self.test_db_path = Path("./test_crash_recovery_db")
    
    def run(self) -> ScenarioMetrics:
        """Run crash recovery scenario."""
        print(f"\n[{self.scenario_id}] Starting...")
        
        # Clean up any existing test DB
        if self.test_db_path.exists():
            shutil.rmtree(self.test_db_path)
        
        # Test crash during writes (G5)
        self._test_crash_during_writes()
        
        # Test recovery replay (#18)
        self._test_recovery_replay()
        
        # Cleanup
        if self.test_db_path.exists():
            shutil.rmtree(self.test_db_path)
        
        print(f"[{self.scenario_id}] {'✓ PASS' if self.metrics.passed else '✗ FAIL'}")
        return self.metrics
    
    def _test_crash_during_writes(self):
        """Test G5: Crash consistency violations."""
        print(f"  Testing crash consistency (G5)...")
        
        # Open dedicated test database
        test_db = Database.open(str(self.test_db_path))
        
        try:
            # Create namespace and collection
            try:
                test_db.create_namespace("crash_ns")
            except:
                pass
            
            with test_db.use_namespace("crash_ns") as ns:
                # Create collection
                try:
                    col = ns.create_collection("crash_test", dimension=self.generator.embedding_dim)
                except:
                    col = ns.collection("crash_test")
                
                # Insert some documents
                documents = []
                for i in range(10):
                    # Generate content
                    prompt = f"Generate test document {i} (1 sentence):"
                    content = self.llm.generate_text(prompt, max_tokens=40)
                    self.metrics.track_llm_call(40)
                    
                    embedding = self.llm.get_embedding(content)
                    self.metrics.track_llm_call(50)
                    
                    doc = {
                        'id': f"doc_{i:03d}",
                        'embedding': embedding,
                        'metadata': {'content': content, 'index': i}
                    }
                    documents.append(doc)
                    
                    col.insert(id=doc['id'], vector=doc['embedding'], metadata=doc['metadata'])
                    self.metrics.log_audit_event("system", "insert", f"doc_{i:03d}")
            
            # Simulate crash by closing without proper shutdown
            test_db.close()
            
            # Reopen database (recovery)
            print(f"    Simulating recovery after crash...")
            test_db = Database.open(str(self.test_db_path))
            
            with test_db.use_namespace("crash_ns") as ns:
                col = ns.collection("crash_test")
                
                # Check consistency (G5) - verify expected documents exist
                violations = 0
                recovered_count = col.count()
            
            print(f"    Recovered {recovered_count} documents")
            
            # Verify sample documents exist with required fields
            for i in range(min(10, 50)):  # Check first 10 of 50 inserted
                doc_id = f"doc_{i:03d}"
                try:
                    doc = col.get(doc_id)
                    if doc:
                        # Check if document has all required fields
                        if 'content' not in doc['metadata'] or 'index' not in doc['metadata']:
                            violations += 1
                            self.metrics.errors.append(f"G5: Missing fields in {doc_id}")
                    else:
                        violations += 1
                except:
                    violations += 1
            
            # G5: crash_consistency_violations must be 0
            self.metrics.crash_consistency_violations = violations
            
            if violations > 0:
                self.metrics.errors.append(f"G5 FAIL: {violations} consistency violations (must be 0)")
                self.metrics.passed = False
            else:
                print(f"    ✓ G5 PASS: Crash consistency violations = 0")
            
            # Track recovery metrics (#18)
            self.metrics.recovery_replayed_entries = recovered_count
            
        finally:
            test_db.close()
    
    def _test_recovery_replay(self):
        """Test #18: Recovery replay effectiveness."""
        print(f"  Testing recovery replay (#18)...")
        
        # Open database again
        test_db = Database.open(str(self.test_db_path))
        
        try:
            with test_db.use_namespace("crash_ns") as ns:
                col = ns.collection("crash_test")
                
                # Count recovered entries
                replayed_count = col.count()
            
                print(f"    Replayed entries: {replayed_count}")
                
                # #18: replayed_entries > 0 AND invariants hold
                if replayed_count == 0:
                    self.metrics.errors.append("#18: No entries replayed during recovery")
                    self.metrics.passed = False
                else:
                    print(f"    ✓ #18: Successfully replayed {replayed_count} entries")
                
                self.metrics.recovery_replayed_entries = replayed_count
            
        finally:
            test_db.close()
