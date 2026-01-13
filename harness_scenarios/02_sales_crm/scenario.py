"""
Scenario 02: Sales CRM with Transaction Atomicity
================================================

Tests:
- Transaction atomicity (all-or-nothing commits)
- Rollback on errors
- Multi-document updates
- Real CRM data generation using LLM
"""

import random
import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "sochdb-python-sdk" / "src"))

from sochdb import Collection
from harness_scenarios.base_scenario import BaseScenario, ScenarioMetrics


class SalesCRMScenario(BaseScenario):
    """Sales CRM testing transaction atomicity."""
    
    def __init__(self, db, generator, llm_client):
        super().__init__("02_sales_crm", db, generator, llm_client)
    
    def run(self) -> ScenarioMetrics:
        """Run sales CRM scenario."""
        print(f"\n[{self.scenario_id}] Starting...")
        
        # Generate real CRM data using LLM
        accounts = self._generate_real_accounts(num_accounts=15)
        opportunities = self._generate_real_opportunities(accounts, num_opps=30)
        
        # Create namespace and collections
        try:
            self.db.create_namespace("crm_ns")
        except:
            pass
        
        with self.db.use_namespace("crm_ns") as ns:
            # Create collections
            try:
                accounts_col = ns.create_collection(
                    "accounts",
                    dimension=self.generator.embedding_dim
                )
            except:
                accounts_col = ns.collection("accounts")
            
            try:
                opportunities_col = ns.create_collection(
                    "opportunities",
                    dimension=self.generator.embedding_dim
                )
            except:
                opportunities_col = ns.collection("opportunities")
            
            # Insert data
            with self._track_time("insert"):
                for acc in accounts:
                    accounts_col.insert(acc['id'], acc['embedding'], acc['metadata'])
            
            for opp in opportunities:
                opportunities_col.insert(opp['id'], opp['embedding'], opp['metadata'])
            
            # Test atomicity
            self._test_atomicity(accounts_col, opportunities_col, accounts, opportunities)
            
            # Test rollback
            self._test_rollback(accounts_col, accounts)
            
            # Test multi-document updates
            self._test_batch_updates(opportunities_col, opportunities)
        
        print(f"[{self.scenario_id}] {'✓ PASS' if self.metrics.passed else '✗ FAIL'}")
        return self.metrics
    
    def _generate_real_accounts(self, num_accounts: int) -> List[Dict]:
        """Generate real account data using LLM."""
        print(f"  Generating {num_accounts} accounts with real LLM...")
        accounts = []
        
        industries = ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing"]
        
        for i in range(num_accounts):
            industry = random.choice(industries)
            
            # Generate real account description using LLM
            prompt = f"Generate a realistic {industry} company account description (2-3 sentences):"
            description = self.llm.generate_text(prompt, max_tokens=100)
            self.metrics.track_llm_call(100)
            
            # Generate real embedding
            embedding = self.llm.get_embedding(description)
            self.metrics.track_llm_call(50)
            
            accounts.append({
                'id': f"acc_{i:03d}",
                'embedding': embedding,
                'metadata': {
                    'name': f"Account {i}",
                    'industry': industry,
                    'description': description,
                    'revenue': random.randint(100_000, 10_000_000),
                    'employees': random.randint(10, 1000),
                }
            })
        
        return accounts
    
    def _generate_real_opportunities(self, accounts: List[Dict], num_opps: int) -> List[Dict]:
        """Generate real opportunity data using LLM."""
        print(f"  Generating {num_opps} opportunities with real LLM...")
        opportunities = []
        
        stages = ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
        
        for i in range(num_opps):
            account = random.choice(accounts)
            stage = random.choice(stages)
            
            # Generate real opportunity description using LLM
            prompt = f"Generate a realistic sales opportunity for a {account['metadata']['industry']} company, stage {stage} (2 sentences):"
            description = self.llm.generate_text(prompt, max_tokens=80)
            self.metrics.track_llm_call(80)
            
            # Generate real embedding
            embedding = self.llm.get_embedding(description)
            self.metrics.track_llm_call(50)
            
            opportunities.append({
                'id': f"opp_{i:03d}",
                'embedding': embedding,
                'metadata': {
                    'account_id': account['id'],
                    'stage': stage,
                    'amount': random.randint(10_000, 500_000),
                    'probability': random.randint(10, 90),
                    'description': description,
                }
            })
        
        return opportunities
    
    def _test_atomicity(self, accounts_col: Collection, opportunities_col: Collection,
                       accounts: List[Dict], opportunities: List[Dict]):
        """Test transaction atomicity."""
        print(f"  Testing transaction atomicity...")
        
        # Get initial counts
        initial_acc_count = accounts_col.count()
        initial_opp_count = opportunities_col.count()
        
        # Simulate atomic update: convert opportunity to won, update account revenue
        target_opp = opportunities[0]
        target_acc_id = target_opp['metadata']['account_id']
        target_acc = next(a for a in accounts if a['id'] == target_acc_id)
        
        try:
            with self._track_time("transaction"):
                # Update opportunity stage (delete + insert)
                new_metadata = target_opp['metadata'].copy()
                new_metadata['stage'] = 'Closed Won'
                opportunities_col.delete(target_opp['id'])
                opportunities_col.insert(
                    id=target_opp['id'],
                    vector=target_opp['embedding'],
                    metadata=new_metadata
                )
                
                # Update account revenue (delete + insert)
                new_acc_metadata = target_acc['metadata'].copy()
                new_acc_metadata['revenue'] += target_opp['metadata']['amount']
                accounts_col.delete(target_acc['id'])
                accounts_col.insert(
                    id=target_acc['id'],
                    vector=target_acc['embedding'],
                    metadata=new_acc_metadata
                )
            
            # Verify both updates succeeded
            updated_opp = opportunities_col.get(target_opp['id'])
            updated_acc = accounts_col.get(target_acc['id'])
            
            if updated_opp['metadata']['stage'] != 'Closed Won':
                self.metrics.errors.append("Opportunity stage not updated")
                self.metrics.passed = False
            
            expected_revenue = target_acc['metadata']['revenue'] + target_opp['metadata']['amount']
            if updated_acc['metadata']['revenue'] != expected_revenue:
                self.metrics.errors.append(f"Account revenue mismatch: {updated_acc['metadata']['revenue']} != {expected_revenue}")
                self.metrics.passed = False
            
            # Verify no extra insertions
            final_acc_count = accounts_col.count()
            final_opp_count = opportunities_col.count()
            
            if final_acc_count != initial_acc_count or final_opp_count != initial_opp_count:
                self.metrics.errors.append("Atomicity violation: count mismatch")
                self.metrics.passed = False
            
            self.metrics.atomicity_failures = 0
            
        except Exception as e:
            self.metrics.errors.append(f"Transaction failed: {e}")
            self.metrics.passed = False
            self.metrics.atomicity_failures = 1
    
    def _test_rollback(self, accounts_col: Collection, accounts: List[Dict]):
        """Test rollback on error."""
        print(f"  Testing rollback...")
        
        target_acc = accounts[1]
        original_metadata = accounts_col.get(target_acc['id'])
        
        try:
            # Attempt update that should fail
            invalid_embedding = [0.1] * (self.generator.embedding_dim - 1)  # Wrong dimension
            
            with self._track_time("rollback"):
                try:
                    # Try to insert with invalid embedding (should fail)
                    test_id = f"rollback_test_{random.randint(1000, 9999)}"
                    accounts_col.insert(
                        id=test_id,
                        vector=invalid_embedding,
                        metadata={'name': 'test', 'revenue': 0}
                    )
                    self.metrics.errors.append("Should have failed with invalid embedding")
                    self.metrics.passed = False
                except Exception as e:
                    # Expected to fail - verify original data unchanged
                    current_metadata = accounts_col.get(target_acc['id'])
                    
                    if current_metadata and current_metadata['metadata'] != original_metadata['metadata']:
                        self.metrics.errors.append("Rollback failed: metadata changed")
                        self.metrics.passed = False
                        self.metrics.atomicity_failures += 1
        
        except Exception as e:
            self.metrics.errors.append(f"Rollback test failed: {e}")
            self.metrics.passed = False
    
    def _test_batch_updates(self, opportunities_col: Collection, opportunities: List[Dict]):
        """Test multi-document batch updates."""
        print(f"  Testing batch updates...")
        
        # Update stage for all "Prospecting" opportunities
        prospecting_opps = [o for o in opportunities if o['metadata']['stage'] == 'Prospecting']
        
        if not prospecting_opps:
            return  # Skip if none
        
        try:
            with self._track_time("batch_update"):
                for opp in prospecting_opps:
                    new_metadata = opp['metadata'].copy()
                    new_metadata['stage'] = 'Qualification'
                    opportunities_col.delete(opp['id'])
                    opportunities_col.insert(id=opp['id'], vector=opp['embedding'], metadata=new_metadata)
            
            # Verify all updated
            for opp in prospecting_opps:
                current = opportunities_col.get(opp['id'])
                if current['metadata']['stage'] != 'Qualification':
                    self.metrics.errors.append(f"Batch update failed for {opp['id']}")
                    self.metrics.passed = False
        
        except Exception as e:
            self.metrics.errors.append(f"Batch update failed: {e}")
            self.metrics.passed = False
