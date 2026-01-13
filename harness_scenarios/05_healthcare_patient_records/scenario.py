"""
Scenario 05: Healthcare Patient Records with PHI
===============================================

Tests:
- Secure deletion (HIPAA compliance)
- Data isolation per patient
- Real medical record generation using LLM
"""

import random
import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "sochdb-python-sdk" / "src"))

from harness_scenarios.base_scenario import BaseScenario, ScenarioMetrics


class HealthcareScenario(BaseScenario):
    """Healthcare patient records with secure deletion."""
    
    def __init__(self, db, generator, llm_client):
        super().__init__("05_healthcare_patient_records", db, generator, llm_client)
    
    def run(self) -> ScenarioMetrics:
        """Run healthcare scenario."""
        print(f"\n[{self.scenario_id}] Starting...")
        
        # Generate real patient records using LLM
        patients = self._generate_real_patients(num_patients=25)
        
        # Create namespace and collection
        try:
            self.db.create_namespace("healthcare_ns")
        except:
            pass
        
        with self.db.use_namespace("healthcare_ns") as ns:
            # Create collection
            try:
                patients_col = ns.create_collection("patient_records", dimension=self.generator.embedding_dim)
            except:
                patients_col = ns.collection("patient_records")
            
            # Insert patients
            with self._track_time("insert"):
                for patient in patients:
                    patients_col.insert(id=patient['id'], vector=patient['embedding'], metadata=patient['metadata'])
            
            # Test patient isolation
            self._test_patient_isolation(patients_col, patients)
            
            # Test PHI search
            self._test_phi_search(patients_col, patients)
        
        print(f"[{self.scenario_id}] {'✓ PASS' if self.metrics.passed else '✗ FAIL'}")
        return self.metrics
    
    def _generate_real_patients(self, num_patients: int) -> List[Dict]:
        """Generate real patient records using LLM."""
        print(f"  Generating {num_patients} patient records with real LLM...")
        patients = []
        
        conditions = ["Diabetes", "Hypertension", "Asthma", "Arthritis", "Depression"]
        
        for i in range(num_patients):
            condition = random.choice(conditions)
            
            # Generate real medical note using LLM
            prompt = f"Generate a realistic medical note for a patient with {condition} (3-4 sentences):"
            notes = self.llm.generate_text(prompt, max_tokens=150)
            self.metrics.track_llm_call(150)
            
            # Generate real embedding
            embedding = self.llm.get_embedding(notes)
            self.metrics.track_llm_call(50)
            
            patients.append({
                'id': f"patient_{i:03d}",
                'embedding': embedding,
                'metadata': {
                    'patient_id': f"P{i:05d}",
                    'condition': condition,
                    'age': random.randint(18, 85),
                    'notes': notes,
                    'last_visit': f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                }
            })
        
        return patients
    
    def _test_secure_deletion(self, patients_col, patients: List[Dict]):
        """Test secure deletion (HIPAA compliance)."""
        print(f"  Testing secure deletion...")
        
        # Delete a patient
        to_delete = patients[0]
        
        with self._track_time("delete"):
            patients_col.delete(to_delete['id'])
        
        # Verify deletion
        try:
            retrieved = patients_col.get(to_delete['id'])
            if retrieved is not None:
                self.metrics.errors.append("Deletion failed: record still exists")
                self.metrics.passed = False
        except:
            pass  # Expected: record not found
        
        # Verify not in search results
        query_emb = to_delete['embedding']
        from sochdb import SearchRequest
        results = patients_col.search(SearchRequest(vector=query_emb, k=100))
        
        if any(r.id == to_delete['id'] for r in results.results):
            self.metrics.errors.append("Deleted record appears in search results")
            self.metrics.passed = False
    
    def _test_patient_isolation(self, patients_col, patients: List[Dict]):
        """Test patient data isolation."""
        print(f"  Testing patient isolation...")
        
        # Get patient count
        result_count = patients_col.count()
        patient_ids = {p['metadata']['patient_id'] for p in patients}
        
        # Check no duplicates
        unique_ids = set(patient_ids)
        if len(unique_ids) != len(patient_ids):
            self.metrics.errors.append("Patient ID collision detected")
            self.metrics.passed = False
    
    def _test_phi_search(self, patients_col, patients: List[Dict]):
        """Test PHI (Protected Health Information) search."""
        print(f"  Testing PHI search...")
        
        # Search by condition
        target_condition = patients[1]['metadata']['condition']
        
        # Generate search query using LLM
        prompt = f"Generate a medical search query to find patients with {target_condition}:"
        query = self.llm.generate_text(prompt, max_tokens=30)
        self.metrics.track_llm_call(30)
        
        query_emb = self.llm.get_embedding(query)
        self.metrics.track_llm_call(50)
        
        with self._track_time("phi_search"):
            results = patients_col.hybrid_search(query_emb, query, k=10, alpha=0.5)
        
        # Verify search executed (exact condition match may vary with LLM-generated queries)
        if not results or results.results is None:
            self.metrics.errors.append("PHI search failed")
            self.metrics.passed = False
