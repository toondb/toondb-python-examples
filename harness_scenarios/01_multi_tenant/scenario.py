"""
Scenario 1: Multi-tenant Support Agent

Tests:
- Namespace isolation (leakage rate = 0)
- Hybrid search quality (NDCG@10)
- Real LLM embeddings and text generation
- Cache effectiveness with real paraphrases

This scenario uses REAL Azure OpenAI API calls:
- Real embeddings for documents and queries
- Real text generation for support articles
- Real paraphrases for cache testing
"""

import json
import numpy as np
from typing import List, Dict, Any

from ..base_scenario import BaseScenario, ScenarioMetrics


class MultiTenantSupportScenario(BaseScenario):
    """Multi-tenant support agent with RAG + memory + cost control."""
    
    def get_id(self) -> str:
        return "01_multi_tenant_support"
    
    def get_name(self) -> str:
        return "Multi-tenant Support Agent"
    
    def get_description(self) -> str:
        return (
            "Tests namespace isolation, hybrid search with real LLM embeddings, "
            "and semantic cache with real paraphrases"
        )
    
    def run(self) -> ScenarioMetrics:
        """Run the multi-tenant support scenario."""
        print(f"\n[{self.get_id()}] Starting...")
        print(f"  Using REAL Azure OpenAI for embeddings and text generation")
        
        # Generate tenants
        tenants = self.generator.generate_tenants()
        print(f"  Created {len(tenants)} tenants")
        
        # Setup: Create namespaces and collections with REAL LLM
        collections = {}
        all_docs = {}
        ground_truth_topics = {}  # Map doc_id -> topic_id for validation
        
        for tenant_id in tenants:
            print(f"  Setting up tenant: {tenant_id}")
            
            # Create namespace
            try:
                self.db.create_namespace(tenant_id)
            except:
                pass
            
            with self.db.use_namespace(tenant_id) as ns:
                # Create support docs collection
                try:
                    collection = ns.create_collection(
                        "support_docs",
                        dimension=self.generator.embedding_dim,
                        enable_hybrid_search=True,
                        content_field="content"
                    )
                except:
                    collection = ns.collection("support_docs")
                
                collections[tenant_id] = collection
                
                # Generate documents with REAL LLM
                docs = self._generate_real_documents(tenant_id, num_docs=20)
                all_docs[tenant_id] = docs
                
                # Track ground truth
                for doc in docs:
                    ground_truth_topics[doc["id"]] = doc["topic_id"]
                
                # Insert documents
                print(f"    Inserting {len(docs)} documents with real embeddings...")
                for doc in docs:
                    collection.insert(
                        id=doc["id"],
                        vector=doc["embedding"],
                        metadata=doc["metadata"],
                        content=doc["content"]
                    )
        
        # Test 1: Namespace isolation (leakage check)
        print(f"  Test 1: Namespace isolation...")
        cross_tenant_hits = 0
        total_queries = 0
        
        for tenant_id in tenants:
            with self.db.use_namespace(tenant_id) as ns:
                collection = ns.collection("support_docs")
                
                # Generate real queries with LLM
                queries = self._generate_real_queries(tenant_id, num_queries=5)
                
                for query in queries:
                    with self.measure_time("vector_search"):
                        results = collection.vector_search(query["embedding"], k=10)
                    
                    # Check for leakage
                    for result in results:
                        if not result.id.startswith(tenant_id):
                            cross_tenant_hits += 1
                            print(f"      ⚠️ LEAKAGE: {result.id} in {tenant_id} query")
                    
                    total_queries += 1
        
        self.metrics.leakage_rate = cross_tenant_hits / total_queries if total_queries > 0 else 0.0
        
        if self.metrics.leakage_rate > 0:
            self.metrics.passed = False
            self.metrics.errors.append(f"Namespace leakage detected: {self.metrics.leakage_rate:.2%}")
        
        print(f"    Leakage rate: {self.metrics.leakage_rate:.4f}")
        
        # Test 2: Hybrid search quality
        print(f"  Test 2: Hybrid search quality...")
        tenant_id = tenants[0]
        with self.db.use_namespace(tenant_id) as ns:
            collection = ns.collection("support_docs")
            queries = self._generate_real_queries(tenant_id, num_queries=5)
            
            ndcg_scores = []
            recall_scores = []
            
            for query in queries:
                # Ground truth: docs with same topic
                ground_truth = [
                    doc["id"] for doc in all_docs[tenant_id]
                    if doc["topic_id"] == query["topic_id"]
                ]
                
                # Hybrid search with real embeddings
                with self.measure_time("hybrid_search"):
                    results = collection.hybrid_search(
                        vector=query["embedding"],
                        text_query=query["text"],
                        k=10,
                        alpha=0.5
                    )
                
                results_list = [{"id": r.id, "score": r.score} for r in results]
                
                ndcg = self.compute_ndcg(results_list, ground_truth, k=10)
                recall = self.compute_recall(results_list, ground_truth, k=10)
                
                ndcg_scores.append(ndcg)
                recall_scores.append(recall)
            
            self.metrics.ndcg_at_10 = np.mean(ndcg_scores) if ndcg_scores else 0.0
            self.metrics.recall_at_10 = np.mean(recall_scores) if recall_scores else 0.0
        
        print(f"    NDCG@10: {self.metrics.ndcg_at_10:.3f}")
        print(f"    Recall@10: {self.metrics.recall_at_10:.3f}")
        
        # Test 3: Semantic cache with real paraphrases
        print(f"  Test 3: Semantic cache with real paraphrases...")
        cache_hits, cache_total = self._test_semantic_cache(tenant_id, collection)
        
        self.metrics.cache_hit_rate = cache_hits / cache_total if cache_total > 0 else 0.0
        print(f"    Cache hit rate: {self.metrics.cache_hit_rate:.2%}")
        
        # Summary
        status = "✓ PASSED" if self.metrics.passed else "✗ FAILED"
        print(f"[{self.get_id()}] {status}")
        print(f"  LLM calls: {self.metrics.llm_calls}, Tokens: {self.metrics.llm_tokens}")
        
        return self.metrics
    
    def _generate_real_documents(self, tenant_id: str, num_docs: int = 20) -> List[Dict[str, Any]]:
        """Generate documents using REAL LLM."""
        docs = []
        
        for doc_id in range(num_docs):
            # Get topic keywords from generator
            topic_id = (hash(f"{tenant_id}_support_{doc_id}") % self.generator.num_topics)
            keywords = self.generator.topic_keywords.get(topic_id, ["general", "support", "help"])
            
            # Generate REAL content using LLM
            print(f"      Generating doc {doc_id+1}/{num_docs} with LLM...", end="\r")
            content = self.llm.generate_support_doc(keywords, doc_type="support")
            self.metrics.track_llm_call(tokens=len(content.split()))
            
            # Generate REAL embedding using LLM
            embedding = self.llm.get_embedding(content)
            self.metrics.track_llm_call(tokens=len(content.split()))
            
            docs.append({
                "id": f"{tenant_id}_support_{doc_id}",
                "topic_id": topic_id,
                "embedding": embedding,
                "content": content,
                "metadata": {
                    "tenant": tenant_id,
                    "collection": "support",
                    "topic": topic_id,
                    "keywords": keywords,
                }
            })
        
        print(f"      Generated {num_docs} docs with real LLM" + " " * 20)
        return docs
    
    def _generate_real_queries(self, tenant_id: str, num_queries: int = 5) -> List[Dict[str, Any]]:
        """Generate queries using REAL LLM."""
        queries = []
        
        for query_id in range(num_queries):
            # Get topic keywords
            topic_id = (hash(f"query_{tenant_id}_support_{query_id}") % self.generator.num_topics)
            keywords = self.generator.topic_keywords.get(topic_id, ["support", "help"])
            
            # Generate REAL query text using LLM
            query_text = self.llm.generate_query(keywords, query_type="support")
            self.metrics.track_llm_call(tokens=len(query_text.split()))
            
            # Generate REAL embedding
            query_embedding = self.llm.get_embedding(query_text)
            self.metrics.track_llm_call(tokens=len(query_text.split()))
            
            queries.append({
                "id": f"query_{query_id}",
                "topic_id": topic_id,
                "embedding": query_embedding,
                "text": query_text,
                "tenant": tenant_id,
            })
        
        return queries
    
    def _test_semantic_cache(self, tenant_id: str, collection) -> tuple:
        """Test semantic cache with real paraphrases."""
        # Generate a base query
        topic_id = 0
        keywords = self.generator.topic_keywords.get(topic_id, ["support", "help"])
        base_query = self.llm.generate_query(keywords, query_type="support")
        self.metrics.track_llm_call(tokens=len(base_query.split()))
        
        # Generate REAL paraphrases using LLM
        print(f"      Generating paraphrases with LLM...")
        paraphrases = self.llm.generate_paraphrases(base_query, num_paraphrases=3)
        self.metrics.track_llm_call(tokens=len(base_query.split()) * 4)
        
        # First query (cache miss)
        base_embedding = self.llm.get_embedding(base_query)
        self.metrics.track_llm_call(tokens=len(base_query.split()))
        
        with self.measure_time("cache_miss"):
            base_results = collection.vector_search(base_embedding, k=10)
        base_ids = [r.id for r in base_results]
        
        # Paraphrase queries (should have high overlap = cache hit)
        cache_hits = 0
        cache_total = len(paraphrases)
        
        for paraphrase in paraphrases:
            para_embedding = self.llm.get_embedding(paraphrase)
            self.metrics.track_llm_call(tokens=len(paraphrase.split()))
            
            with self.measure_time("cache_check"):
                para_results = collection.vector_search(para_embedding, k=10)
            para_ids = [r.id for r in para_results]
            
            # Check overlap (>50% = cache hit)
            overlap = len(set(base_ids) & set(para_ids))
            if overlap >= 5:  # 50% of top-10
                cache_hits += 1
        
        return cache_hits, cache_total
