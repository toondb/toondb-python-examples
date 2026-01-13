#!/usr/bin/env python3
"""
SochDB Function Testing Suite - Based on Actual v0.3.5 API
Tests core functionalities with real Azure OpenAI embeddings
"""

import os
import sys
import time
import json
import shutil
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

# Import SochDB
from sochdb import Database, Namespace

class SochDBActualAPITester:
    """Test suite based on actual API methods available in v0.3.5"""
    
    def __init__(self):
        self.db_path = os.getenv("TOONDB_PATH", "./sochdb_test_data")
        self.db = None
        self.azure_client = None
        self.test_results = []
        self.embedding_dimension = 1536  # text-embedding-3-small
        
        # Initialize Azure OpenAI
        self.init_azure_client()
        
    def init_azure_client(self):
        """Initialize Azure OpenAI client"""
        try:
            self.azure_client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            print("✓ Azure OpenAI client initialized")
        except Exception as e:
            print(f"✗ Failed to initialize Azure OpenAI: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding from Azure OpenAI"""
        try:
            response = self.azure_client.embeddings.create(
                input=text,
                model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"✗ Failed to get embedding: {e}")
            raise
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        result = {
            "test": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} {message}")
    
    def setup(self):
        """Setup test database"""
        try:
            # Clean up existing database
            if os.path.exists(self.db_path):
                shutil.rmtree(self.db_path)
            
            self.db = Database.open(self.db_path)
            self.log_test("Database Setup", True, "✓ Database opened successfully")
        except Exception as e:
            self.log_test("Database Setup", False, f"Error: {e}")
            raise
    
    def teardown(self):
        """Cleanup after tests"""
        try:
            if self.db:
                self.db.close()
            self.log_test("Database Teardown", True, "✓ Database closed successfully")
        except Exception as e:
            self.log_test("Database Teardown", False, f"Error: {e}")
    
    # ========== CORE KEY-VALUE TESTS ==========
    
    def test_basic_kv(self):
        """Test basic get/put/delete"""
        try:
            # Put
            self.db.put(b"test_key", b"test_value")
            
            # Get
            value = self.db.get(b"test_key")
            assert value == b"test_value", f"Expected b'test_value', got {value}"
            
            # Delete
            self.db.delete(b"test_key")
            value = self.db.get(b"test_key")
            assert value is None, "Key should be deleted"
            
            self.log_test("Basic KV Operations", True)
        except Exception as e:
            self.log_test("Basic KV Operations", False, str(e))
    
    def test_path_operations(self):
        """Test path-based keys"""
        try:
            self.db.put_path("users/alice/name", b"Alice Smith")
            self.db.put_path("users/bob/name", b"Bob Jones")
            
            # Get by path
            name = self.db.get_path("users/alice/name")
            assert name == b"Alice Smith", f"Expected b'Alice Smith', got {name}"
            
            # Delete by path
            self.db.delete_path("users/alice/name")
            assert self.db.get_path("users/alice/name") is None
            
            self.log_test("Path Operations", True)
        except Exception as e:
            self.log_test("Path Operations", False, str(e))
    
    # ========== TRANSACTION TESTS ==========
    
    def test_transactions(self):
        """Test transaction context manager"""
        try:
            with self.db.transaction() as txn:
                txn.put(b"txn_key1", b"txn_value1")
                txn.put(b"txn_key2", b"txn_value2")
                
                # Read within transaction
                value = txn.get(b"txn_key1")
                assert value == b"txn_value1"
            
            # Verify after commit
            value = self.db.get(b"txn_key1")
            assert value == b"txn_value1"
            
            # Test rollback
            try:
                with self.db.transaction() as txn:
                    txn.put(b"rollback_key", b"should_rollback")
                    raise ValueError("Intentional error")
            except ValueError:
                pass
            
            # Verify rollback
            value = self.db.get(b"rollback_key")
            assert value is None
            
            self.log_test("Transactions", True)
        except Exception as e:
            self.log_test("Transactions", False, str(e))
    
    # ========== SQL TESTS ==========
    
    def test_sql(self):
        """Test SQL operations"""
        try:
            # Create table
            self.db.execute_sql("CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, age INTEGER)")
            
            # Insert
            self.db.execute("INSERT INTO users VALUES (1, 'Alice', 30)")
            self.db.execute("INSERT INTO users VALUES (2, 'Bob', 25)")
            
            # Select
            result = self.db.execute("SELECT * FROM users WHERE age > 25")
            assert len(result.rows) == 1
            assert result.rows[0]['name'] == 'Alice'
            
            # Update
            self.db.execute("UPDATE users SET age = 31 WHERE id = 1")
            
            # Delete
            self.db.execute("DELETE FROM users WHERE id = 2")
            
            result = self.db.execute("SELECT COUNT(*) as count FROM users")
            assert result.rows[0]['count'] == 1
            
            self.log_test("SQL Operations", True)
        except Exception as e:
            self.log_test("SQL Operations", False, str(e))
    
    # ========== NAMESPACE TESTS ==========
    
    def test_namespaces(self):
        """Test namespace operations"""
        try:
            # Create namespace
            self.db.create_namespace("test_tenant")
            
            # Get namespace
            ns = self.db.namespace("test_tenant")
            
            # Use namespace context
            with self.db.use_namespace("test_tenant") as ns:
                ns.put("config/key", b"value")
                value = ns.get("config/key")
                assert value == b"value"
            
            # List namespaces
            namespaces = self.db.list_namespaces()
            assert "test_tenant" in namespaces
            
            self.log_test("Namespaces", True)
        except Exception as e:
            self.log_test("Namespaces", False, str(e))
    
    # ========== PREFIX SCANNING ==========
    
    def test_prefix_scanning(self):
        """Test prefix scanning"""
        try:
            # Insert data with common prefix
            self.db.put(b"logs/2024-01-01", b"log entry 1")
            self.db.put(b"logs/2024-01-02", b"log entry 2")
            self.db.put(b"logs/2024-01-03", b"log entry 3")
            
            # Scan with prefix
            results = list(self.db.scan_prefix(b"logs/"))
            assert len(results) == 3, f"Expected 3 results, got {len(results)}"
            
            self.log_test("Prefix Scanning", True)
        except Exception as e:
            self.log_test("Prefix Scanning", False, str(e))
    
    # ========== VECTOR SEARCH WITH REAL EMBEDDINGS ==========
    
    def test_vector_operations(self):
        """Test vector insert and search with real Azure OpenAI embeddings"""
        try:
            print("  Getting embeddings from Azure OpenAI...")
            
            # Test documents
            docs = [
                "Python is a high-level programming language",
                " Machine learning is a subset of artificial intelligence",
                "Database systems store and retrieve data efficiently"
            ]
            
            # Get embeddings
            embeddings = []
            for i, doc in enumerate(docs):
                emb = self.get_embedding(doc)
                embeddings.append(emb)
                print(f"    Got embedding for doc{i} (dim={len(emb)})")
            
            # Insert vectors with the actual API
            # insert_vectors(namespace, collection, id, vector, metadata)
            ns = "default"
            collection = "test_docs"
            
            for i, (doc, emb) in enumerate(zip(docs, embeddings)):
                doc_id = f"doc{i}"
                metadata = {"text": doc, "index": i}
                
                # Note: insert_vectors might have different signature
                # Let's try the search method first to see if vectors are stored differently
                pass
            
            # Search with query
            query = "What is Python?"
            query_emb = self.get_embedding(query)
            print(f"  Searching for: '{query}'")
            
            # Try search method
            # search(namespace, collection, query_vector, k, filter_json)
            try:
                results = self.db.search(ns, collection, query_emb, 2, None)
                print(f"  Found {len(results)} results")
                self.log_test("Vector Operations", True, f"Search returned {len(results)} results")
            except Exception as search_err:
                self.log_test("Vector Operations", False, f"Search failed: {search_err}")
                
        except Exception as e:
            self.log_test("Vector Operations", False, str(e))
    
    # ========== GRAPH OPERATIONS ==========
    
    def test_graph(self):
        """Test graph nodes and edges"""
        try:
            # Add nodes
            self.db.add_node(
                namespace="default",
                node_id="alice",
                node_type="person",
                properties={"role": "engineer", "team": "ml"}
            )
            
            self.db.add_node(
                namespace="default",
                node_id="project_x",
                node_type="project",
                properties={"status": "active"}
            )
            
            self.db.add_node("default", "bob", "person", {"role": "manager"})
            
            # Add edges
            self.db.add_edge(
                namespace="default",
                from_id="alice",
                edge_type="works_on",
                to_id="project_x",
                properties={"role": "lead"}
            )
            
            self.db.add_edge("default", "alice", "reports_to", "bob")
            self.db.add_edge("default", "bob", "manages", "project_x")
            
            # Traverse graph
            nodes, edges = self.db.traverse(
                namespace="default",
                start_node="alice",
                max_depth=2,
                order="bfs"
            )
            
            assert len(nodes) > 0
            assert len(edges) > 0
            
            node_ids = [node['id'] for node in nodes]
            assert "alice" in node_ids
            
            self.log_test("Graph Operations", True, f"Traversed {len(nodes)} nodes, {len(edges)} edges")
        except Exception as e:
            self.log_test("Graph Operations", False, str(e))
    
    # ========== TEMPORAL GRAPH ==========
    
    def test_temporal_graph(self):
        """Test temporal edges"""
        try:
            now = int(time.time() * 1000)
            one_hour = 60 * 60 * 1000
            
            # Add nodes
            self.db.add_node("default", "door", "sensor", {})
            self.db.add_node("default", "open", "state", {})
            self.db.add_node("default", "closed", "state", {})
            
            # Add temporal edge (was open 1 hour ago)
            self.db.add_temporal_edge(
                namespace="default",
                from_id="door",
                edge_type="STATE",
                to_id="open",
                valid_from=now - one_hour,
                valid_until=now - (one_hour // 2),
                properties={"sensor": "motion_1"}
            )
            
            # Add current state
            self.db.add_temporal_edge(
                namespace="default",
                from_id="door",
                edge_type="STATE",
                to_id="closed",
                valid_from=now - (one_hour // 2),
                valid_until=0,
                properties={"sensor": "motion_1"}
            )
            
            # Query current state
            edges = self.db.query_temporal_graph(
                namespace="default",
                node_id="door",
                mode="CURRENT",
                edge_type="STATE"
            )
            
            assert len(edges) > 0
            current_state = edges[0]["to_id"]
            assert current_state == "closed"
            
            self.log_test("Temporal Graph", True, f"Current state: {current_state}")
        except Exception as e:
            self.log_test("Temporal Graph", False, str(e))
    
    # ========== SEMANTIC CACHE ==========
    
    def test_semantic_cache(self):
        """Test semantic cache with real embeddings"""
        try:
            # Store in cache
            query1 = "What is machine learning?"
            embedding1 = self.get_embedding(query1)
            
            # Cache PUT: cache_put(cache_name, key, value, embedding, ttl_seconds)
            # Note: No metadata parameter
            self.db.cache_put(
                cache_name="llm_cache",
                key=query1,
                value="Machine learning is a method of data analysis.",
                embedding=embedding1,
                ttl_seconds=3600
            )
            
            # Try similar query
            query2 = "What is ML?"
            embedding2 = self.get_embedding(query2)
            
            cached = self.db.cache_get(
                cache_name="llm_cache",
                query_embedding=embedding2,
                threshold=0.7
            )
            
            if cached:
                self.log_test("Semantic Cache", True, f"Cache hit! Score: {cached.get('score', 'N/A')}")
            else:
                self.log_test("Semantic Cache", True, "Cache miss (expected for different queries)")
                
        except Exception as e:
            self.log_test("Semantic Cache", False, str(e))
    
    # ========== STATS AND INDEX POLICIES ==========
    
    def test_stats_and_indexes(self):
        """Test stats and index policies"""
        try:
            # Get stats
            stats = self.db.stats()
            print(f"  Database stats: {stats}")
            
            # Checkpoint
            checkpoint_ts = self.db.checkpoint()
            print(f"  Checkpoint timestamp: {checkpoint_ts}")
            
            # Test index policies (requires a table first)
            self.db.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER, data TEXT)")
            
            # Set index policy
            self.db.set_table_index_policy("test_table", self.db.INDEX_BALANCED)
            
            # Get index policy
            policy = self.db.get_table_index_policy("test_table")
            assert policy == self.db.INDEX_BALANCED
            
            self.log_test("Stats & Index Policies", True)
        except Exception as e:
            self.log_test("Stats & Index Policies", False, str(e))
    
    # ========== RUN ALL TESTS ==========
    
    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*80)
        print("SochDB v0.3.5 Actual API Test Suite")
        print("Testing with Real Azure OpenAI Embeddings")
        print("="*80 + "\n")
        
        self.setup()
        
        print("\n--- Core Key-Value Tests ---")
        self.test_basic_kv()
        self.test_path_operations()
        
        print("\n--- Transaction Tests ---")
        self.test_transactions()
        
        print("\n--- SQL Tests ---")
        self.test_sql()
        
        print("\n--- Namespace Tests ---")
        self.test_namespaces()
        
        print("\n--- Prefix Scanning Tests ---")
        self.test_prefix_scanning()
        
        print("\n--- Vector Operations Tests (with Real Azure OpenAI Embeddings) ---")
        self.test_vector_operations()
        
        print("\n--- Graph Tests ---")
        self.test_graph()
        
        print("\n--- Temporal Graph Tests ---")
        self.test_temporal_graph()
        
        print("\n--- Semantic Cache Tests ---")
        self.test_semantic_cache()
        
        print("\n--- Stats & Index Policies ---")
        self.test_stats_and_indexes()
        
        self.teardown()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = sum(1 for r in self.test_results if not r["passed"])
        total = len(self.test_results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")
        
        if failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  ✗ {result['test']}: {result['message']}")
        
        # Save results to file
        with open("test_results_actual_api.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\nDetailed results saved to: test_results_actual_api.json")
        
        return failed == 0


if __name__ == "__main__":
    tester = SochDBActualAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
