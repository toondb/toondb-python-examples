"""
Scenario 08: Academic Paper Citations
====================================

Tests:
- Graph-like relationships (citations)
- Metadata updates (citation count)
- Real academic paper generation using LLM
"""

import random
import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "sochdb-python-sdk" / "src"))

from harness_scenarios.base_scenario import BaseScenario, ScenarioMetrics


class AcademicCitationsScenario(BaseScenario):
    """Academic paper citations."""
    
    def __init__(self, db, generator, llm_client):
        super().__init__("08_academic_paper_citations", db, generator, llm_client)
    
    def run(self) -> ScenarioMetrics:
        """Run academic citations scenario."""
        print(f"\n[{self.scenario_id}] Starting...")
        
        try:
            # Generate real academic papers using LLM
            papers = self._generate_real_papers(num_papers=30)
        except Exception as e:
            self.metrics.errors.append(f"Failed to generate papers: {e}")
            self.metrics.passed = False
            print(f"[{self.scenario_id}] ✗ FAIL")
            return self.metrics
        
        # Create namespace and collection
        try:
            self.db.create_namespace("papers_ns")
        except:
            pass  # Already exists
        
        with self.db.use_namespace("papers_ns") as ns:
            papers_col = ns.create_collection(
                "academic_papers",
                dimension=self.generator.embedding_dim
            )
            
            # Insert papers
            with self._track_time("insert"):
                for paper in papers:
                    papers_col.insert(id=paper['id'], vector=paper['embedding'], metadata=paper['metadata'])
            
            # Create citation relationships
            self._create_citations(papers_col, papers)
            
            # Test citation search
            self._test_citation_search(papers_col, papers)
            
            # Test citation count updates
            self._test_citation_updates(papers_col, papers)
        
        print(f"[{self.scenario_id}] {'✓ PASS' if self.metrics.passed else '✗ FAIL'}")
        return self.metrics
    
    def _generate_real_papers(self, num_papers: int) -> List[Dict]:
        """Generate real academic papers using LLM."""
        print(f"  Generating {num_papers} academic papers with real LLM...")
        papers = []
        
        fields = ["Machine Learning", "Quantum Computing", "Bioinformatics", "Robotics", "Cryptography"]
        
        for i in range(num_papers):
            field = random.choice(fields)
            
            # Generate real abstract using LLM
            prompt = f"Generate a realistic academic paper abstract in {field} (4-5 sentences):"
            abstract = self.llm.generate_text(prompt, max_tokens=200)
            self.metrics.track_llm_call(200)
            
            # Generate real embedding
            embedding = self.llm.get_embedding(abstract)
            self.metrics.track_llm_call(50)
            
            papers.append({
                'id': f"paper_{i:03d}",
                'embedding': embedding,
                'metadata': {
                    'title': f"{field} Research {i}",
                    'field': field,
                    'abstract': abstract,
                    'year': random.randint(2018, 2024),
                    'authors': f"Author {random.randint(1, 10)}",
                    'citations': [],
                    'citation_count': 0,
                }
            })
        
        return papers
    
    def _create_citations(self, papers_col, papers: List[Dict]):
        """Create citation relationships."""
        print(f"  Creating citation relationships...")
        
        # Older papers get cited by newer ones
        for i, paper in enumerate(papers):
            # Randomly cite 1-3 older papers
            if i > 0:
                num_citations = random.randint(1, min(3, i))
                cited_papers = random.sample(papers[:i], num_citations)
            else:
                cited_papers = []
            
            paper['metadata']['citations'] = [p['id'] for p in cited_papers]
            
            # Update citation counts
            for cited in cited_papers:
                cited['metadata']['citation_count'] += 1
        
        # Update all papers in database (delete + insert)
        with self._track_time("citation_update"):
            for paper in papers:
                papers_col.delete(paper['id'])
                papers_col.insert(id=paper['id'], vector=paper['embedding'], metadata=paper['metadata'])
    
    def _test_citation_search(self, papers_col, papers: List[Dict]):
        """Test finding papers by citations."""
        print(f"  Testing citation search...")
        
        # Find highly cited papers
        item_count = papers_col.count()
        if not papers:
            self.metrics.errors.append("No papers to test")
            self.metrics.passed = False
            return
        
        highly_cited = [p for p in papers if p['metadata']['citation_count'] >= 2]
        
        if not highly_cited:
            # Acceptable if no papers have enough citations
            return
        
        # Verify citation counts
        for paper in highly_cited:
            paper_id = paper['id']
            expected_count = paper['metadata']['citation_count']
            
            # Get from database
            retrieved = papers_col.get(paper_id)
            
            if retrieved['metadata']['citation_count'] != expected_count:
                self.metrics.errors.append(f"Citation count mismatch for {paper_id}")
                self.metrics.passed = False
    
    def _test_citation_updates(self, papers_col, papers: List[Dict]):
        """Test updating citation counts."""
        print(f"  Testing citation count updates...")
        
        # Add new citation to a paper
        target_paper = papers[0]
        new_count = target_paper['metadata']['citation_count'] + 1
        
        new_metadata = target_paper['metadata'].copy()
        new_metadata['citation_count'] = new_count
        
        with self._track_time("update_citation"):
            papers_col.delete(target_paper['id'])
            papers_col.insert(id=target_paper['id'], vector=target_paper['embedding'], metadata=new_metadata)
        
        # Verify update
        updated = papers_col.get(target_paper['id'])
        
        if updated['metadata']['citation_count'] != new_count:
            self.metrics.errors.append(f"Citation count update failed: {updated['metadata']['citation_count']} != {new_count}")
            self.metrics.passed = False
