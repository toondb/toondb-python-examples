"""
Scenario 11: Financial Ledger with Double-Post Prevention
========================================================

Tests:
- G3: Double-post rate (GATE - must be 0)
- Idempotent invoice posting
- Ledger consistency
- Real financial data generation using LLM
"""

import random
import sys
from pathlib import Path
from typing import List, Dict, Set

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "sochdb-python-sdk" / "src"))

from harness_scenarios.base_scenario import BaseScenario, ScenarioMetrics


class FinancialLedgerScenario(BaseScenario):
    """Financial ledger testing double-post prevention."""
    
    def __init__(self, db, generator, llm_client):
        super().__init__("11_financial_ledger", db, generator, llm_client)
    
    def run(self) -> ScenarioMetrics:
        """Run financial ledger scenario."""
        print(f"\n[{self.scenario_id}] Starting...")
        
        # Generate real invoices using LLM
        invoices = self._generate_real_invoices(num_invoices=50)
        
        # Create namespace and collections
        try:
            self.db.create_namespace("ledger_ns")
        except:
            pass
        
        with self.db.use_namespace("ledger_ns") as ns:
            # Create collections
            invoices_col = ns.create_collection("invoices", dimension=self.generator.embedding_dim)
            ledger_col = ns.create_collection("ledger_entries", dimension=self.generator.embedding_dim)
            
            # Insert invoices
            with self._track_time("insert"):
                for invoice in invoices:
                    invoices_col.insert(id=invoice['id'], vector=invoice['embedding'], metadata=invoice['metadata'])
                    self.metrics.log_audit_event("system", "insert", f"invoice:{invoice['id']}")
            
            # Test idempotent posting
            self._test_idempotent_posting(invoices_col, ledger_col, invoices)
            
            # Test double-post prevention (G3)
            self._test_double_post_prevention(invoices_col, ledger_col, invoices)
        
        # Test ledger consistency
        self._test_ledger_consistency(invoices_col, ledger_col, invoices)
        
        print(f"[{self.scenario_id}] {'✓ PASS' if self.metrics.passed else '✗ FAIL'}")
        return self.metrics
    
    def _generate_real_invoices(self, num_invoices: int) -> List[Dict]:
        """Generate real invoice data using LLM."""
        print(f"  Generating {num_invoices} invoices with real LLM...")
        invoices = []
        
        vendors = ["Acme Corp", "TechSupply Inc", "Global Services", "Premier Solutions"]
        
        for i in range(num_invoices):
            vendor = random.choice(vendors)
            amount = round(random.uniform(100.0, 50000.0), 2)
            
            # Generate real invoice description using LLM
            prompt = f"Generate a realistic invoice description for {vendor}, amount ${amount} (1 sentence):"
            description = self.llm.generate_text(prompt, max_tokens=50)
            self.metrics.track_llm_call(50)
            
            # Generate real embedding
            embedding = self.llm.get_embedding(description)
            self.metrics.track_llm_call(50)
            
            invoices.append({
                'id': f"inv_{i:05d}",
                'embedding': embedding,
                'metadata': {
                    'invoice_id': f"INV-{i:05d}",
                    'vendor': vendor,
                    'amount': amount,
                    'description': description,
                    'status': 'pending',
                    'posted_to_ledger': False,
                }
            })
        
        return invoices
    
    def _test_idempotent_posting(self, invoices_col, ledger_col, invoices: List[Dict]):
        """Test idempotent invoice posting."""
        print(f"  Testing idempotent posting...")
        
        # Post first batch
        for invoice in invoices[:10]:
            self._post_to_ledger(invoice, ledger_col)
            self.metrics.log_audit_event("accountant", "post_ledger", invoice['id'])
        
        # Attempt to post same invoices again (should be idempotent)
        for invoice in invoices[:10]:
            self._post_to_ledger(invoice, ledger_col)
    
    def _post_to_ledger(self, invoice: Dict, ledger_col) -> bool:
        """Post invoice to ledger (idempotent)."""
        invoice_id = invoice['metadata']['invoice_id']
        entry_id = f"ledger_{invoice_id}"
        
        # Check if already posted
        try:
            existing = ledger_col.get(entry_id)
            if existing:
                return False  # Already posted
        except:
            pass  # Not found, can post
        
        # Create ledger entry
        ledger_entry = {
            'invoice_id': invoice_id,
            'amount': invoice['metadata']['amount'],
            'vendor': invoice['metadata']['vendor'],
            'status': 'posted',
        }
        
        ledger_col.insert(
            id=entry_id,
            vector=invoice['embedding'],
            metadata=ledger_entry
        )
        self.metrics.log_audit_event("accountant", "post_ledger", invoice_id, "success")
        
        return True  # Successfully posted
    
    def _test_double_post_prevention(self, invoices_col, ledger_col, invoices: List[Dict]):
        """Test G3: Double-post rate (must be 0)."""
        print(f"  Testing double-post prevention (G3)...")
        
        # Post all invoices, track successes
        successful_posts = 0
        for invoice in invoices:
            if self._post_to_ledger(invoice, ledger_col):
                successful_posts += 1
        
        print(f"    Posted {successful_posts} unique invoices")
        
        # Try to post again (should all be rejected)
        duplicate_attempts = 0
        rejected_posts = 0
        for invoice in invoices[:10]:  # Test first 10
            duplicate_attempts += 1
            if not self._post_to_ledger(invoice, ledger_col):
                rejected_posts += 1
        
        # G3: double_post_rate should be 0 (all duplicates rejected)
        double_post_rate = ((duplicate_attempts - rejected_posts) / duplicate_attempts * 100) if duplicate_attempts > 0 else 0.0
        self.metrics.double_post_rate = double_post_rate
        
        print(f"    Duplicate rejections: {rejected_posts}/{duplicate_attempts}")
        
        if self.metrics.double_post_rate > 0:
            self.metrics.errors.append(f"G3 FAIL: Double-post rate = {self.metrics.double_post_rate:.1f}% (must be 0)")
            self.metrics.passed = False
        else:
            print(f"    ✓ G3 PASS: Double-post rate = 0.0%")
    
    def _test_ledger_consistency(self, invoices_col, ledger_col, invoices: List[Dict]):
        """Test ledger consistency."""
        print(f"  Testing ledger consistency...")
        
        # Verify ledger count matches posted invoices
        ledger_count = ledger_col.count()
        expected_count = len(invoices)
        
        if ledger_count != expected_count:
            self.metrics.errors.append(f"Ledger count mismatch: {ledger_count} vs {expected_count}")
            self.metrics.passed = False
        else:
            # Verify sample entries match invoices
            sample_size = min(10, len(invoices))
            for invoice in invoices[:sample_size]:
                invoice_id = invoice['metadata']['invoice_id']
                entry_id = f"ledger_{invoice_id}"
                
                try:
                    entry = ledger_col.get(entry_id)
                    if entry:
                        # Verify amounts match
                        if abs(entry['metadata']['amount'] - invoice['metadata']['amount']) > 0.01:
                            self.metrics.errors.append(f"Amount mismatch for {invoice_id}")
                            self.metrics.passed = False
                except:
                    self.metrics.errors.append(f"Ledger entry not found: {invoice_id}")
                    self.metrics.passed = False
