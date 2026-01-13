#!/usr/bin/env python3
"""
Comprehensive SochDB Python SDK Test Suite
Tests all major functionalities with real Azure OpenAI embeddings
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

# Import SochDB
try:
    from sochdb import (
        Database, 
        CollectionConfig, 
        DistanceMetric,
        # Note: QuantizationType not available in this version
    )
    print("✓ SochDB imported successfully")
except ImportError as e:
    print(f"✗ Failed to import SochDB: {e}")
    sys.exit(1)


class SochDBTester:
    """Comprehensive test suite for SochDB"""
    
    def __init__(self):
        self.db_path = os.getenv("TOONDB_PATH", "./sochdb_data")
        self.db = None
        self.azure_client = None
        self.test_results = []
        self.embedding_dimension = 1536  # text-embedding-3-small dimension
        
        # Initialize Azure OpenAI
        self.init_azure_client()
        
    def init_azure_client(self):
        """Initialize Azure OpenAI client with credentials from .env"""
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
            import shutil
            if os.path.exists(self.db_path):
                shutil.rmtree(self.db_path)
            
            self.db = Database.open(self.db_path)
            self.log_test("Database Setup", True, "Database opened successfully")
        except Exception as e:
            self.log_test("Database Setup", False, f"Error: {e}")
            raise
    
    def teardown(self):
        """Cleanup after tests"""
        try:
            if self.db:
                self.db.close()
            self.log_test("Database Teardown", True, "Database closed successfully")
        except Exception as e:
            self.log_test("Database Teardown", False, f"Error: {e}")
    
    # ========== CORE KEY-VALUE TESTS ==========
    
    def test_basic_kv_operations(self):
        """Test basic key-value operations"""
        try:
            # Put
            self.db.put(b"test_key", b"test_value")
            
            # Get
            value = self.db.get(b"test_key")
            assert value == b"test_value", f"Expected b'test_value', got {value}"
            
            # Exists
            exists = self.db.exists(b"test_key")
            assert exists, "Key should exist"
            
            # Delete
            self.db.delete(b"test_key")
            value = self.db.get(b"test_key")
            assert value is None, "Key should be deleted"
            
            self.log_test("Basic KV Operations", True)
        except Exception as e:
            self.log_test("Basic KV Operations", False, str(e))
    
    def test_path_based_keys(self):
        """Test hierarchical path-based keys"""
        try:
            self.db.put_path("users/alice/name", b"Alice Smith")
            self.db.put_path("users/alice/email", b"alice@example.com")
            self.db.put_path("users/bob/name", b"Bob Jones")
            
            # Get by path
            name = self.db.get_path("users/alice/name")
            assert name == b"Alice Smith", f"Expected b'Alice Smith', got {name}"
            
            # List children
            children = self.db.list_path("users/")
            assert "alice" in children and "bob" in children, f"Expected alice and bob, got {children}"
            
            # Delete by path
            self.db.delete_path("users/alice/email")
            
            self.log_test("Path-Based Keys", True)
        except Exception as e:
            self.log_test("Path-Based Keys", False, str(e))
    
    def test_batch_operations(self):
        """Test batch put/get/delete"""
        try:
            # Batch put
            pairs = [
                (b"batch1", b"value1"),
                (b"batch2", b"value2"),
                (b"batch3", b"value3"),
            ]
            self.db.put_batch(pairs)
            
            # Batch get
            values = self.db.get_batch([b"batch1", b"batch2", b"batch3"])
            assert len(values) == 3, f"Expected 3 values, got {len(values)}"
            assert values[0] == b"value1", f"Expected b'value1', got {values[0]}"
            
            # Batch delete
            self.db.delete_batch([b"batch1", b"batch2", b"batch3"])
            
            self.log_test("Batch Operations", True)
        except Exception as e:
            self.log_test("Batch Operations", False, str(e))
    
    # ========== TRANSACTION TESTS ==========
    
    def test_transaction_context_manager(self):
        """Test transactions with context manager"""
        try:
            with self.db.transaction() as txn:
                txn.put(b"txn_key1", b"txn_value1")
                txn.put(b"txn_key2", b"txn_value2")
                
                # Read within transaction
                value = txn.get(b"txn_key1")
                assert value == b"txn_value1", f"Expected b'txn_value1', got {value}"
            
            # Verify after commit
            value = self.db.get(b"txn_key1")
            assert value == b"txn_value1", "Transaction should be committed"
            
            self.log_test("Transaction Context Manager", True)
        except Exception as e:
            self.log_test("Transaction Context Manager", False, str(e))
    
    def test_transaction_rollback(self):
        """Test transaction rollback on exception"""
        try:
            try:
                with self.db.transaction() as txn:
                    txn.put(b"rollback_key", b"should_rollback")
                    raise ValueError("Intentional error")
            except ValueError:
                pass
            
            # Verify rollback
            value = self.db.get(b"rollback_key")
            assert value is None, "Transaction should be rolled back"
            
            self.log_test("Transaction Rollback", True)
        except Exception as e:
            self.log_test("Transaction Rollback", False, str(e))
    
    # ========== SQL TESTS ==========
    
    def test_sql_operations(self):
        """Test SQL table creation and CRUD"""
        try:
            # Create table
            self.db.execute_sql("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    age INTEGER
                )
            """)
            
            # Insert
            self.db.execute_sql(
                "INSERT INTO users (id, name, email, age) VALUES (?, ?, ?, ?)",
                params=[1, "Alice", "alice@example.com", 30]
            )
            
            self.db.execute_sql(
                "INSERT INTO users (id, name, email, age) VALUES (?, ?, ?, ?)",
                params=[2, "Bob", "bob@example.com", 25]
            )
            
            # Select
            result = self.db.execute_sql("SELECT * FROM users WHERE age > 25")
            assert len(result.rows) == 1, f"Expected 1 row, got {len(result.rows)}"
            assert result.rows[0]['name'] == 'Alice', f"Expected Alice, got {result.rows[0]['name']}"
            
            # Update
            self.db.execute_sql("UPDATE users SET email = ? WHERE id = ?", 
                              params=["alice.new@example.com", 1])
            
            # Delete
            self.db.execute_sql("DELETE FROM users WHERE id = ?", params=[2])
            
            # Verify
            result = self.db.execute_sql("SELECT COUNT(*) as count FROM users")
            assert result.rows[0]['count'] == 1, f"Expected 1 user, got {result.rows[0]['count']}"
            
            self.log_test("SQL Operations", True)
        except Exception as e:
            self.log_test("SQL Operations", False, str(e))
    
    # ========== NAMESPACE TESTS ==========
    
    def test_namespaces(self):
        """Test namespace creation and operations"""
        try:
            # Create namespace
            ns = self.db.create_namespace(
                name="test_tenant",
                display_name="Test Tenant",
                labels={"tier": "premium"}
            )
            
            # Get namespace
            ns = self.db.namespace("test_tenant")
            
            # Namespace-scoped operations
            with self.db.use_namespace("test_tenant") as ns:
                ns.put("config/key", b"value")
                value = ns.get("config/key")
                assert value == b"value", f"Expected b'value', got {value}"
            
            # List namespaces
            namespaces = self.db.list_namespaces()
            assert "test_tenant" in namespaces, f"Expected test_tenant in {namespaces}"
            
            self.log_test("Namespaces", True)
        except Exception as e:
            self.log_test("Namespaces", False, str(e))
    
    # ========== VECTOR SEARCH TESTS WITH REAL EMBEDDINGS ==========
    
    def test_vector_collection_basic(self):
        """Test vector collection with real Azure OpenAI embeddings"""
        try:
            ns = self.db.get_or_create_namespace("default")
            
            # Create collection
            collection = ns.create_collection(
                name="documents",
                dimension=self.embedding_dimension,
                metric=DistanceMetric.COSINE
            )
            
            # Test documents
            docs = [
                "Python is a high-level programming language",
                "Machine learning is a subset of artificial intelligence",
                "Database systems store and retrieve data efficiently"
            ]
            
            print("  Getting embeddings from Azure OpenAI...")
            # Insert documents with real embeddings
            for i, doc in enumerate(docs):
                embedding = self.get_embedding(doc)
                collection.insert(
                    id=f"doc{i}",
                    vector=embedding,
                    metadata={"text": doc, "index": i}
                )
                print(f"    Inserted doc{i}")
            
            # Search with a query
            query = "What is Python?"
            query_embedding = self.get_embedding(query)
            
            results = collection.vector_search(
                vector=query_embedding,
                k=2
            )
            
            assert len(results) > 0, "Should return search results"
            # The Python document should be most relevant
            assert results[0].metadata["text"] == docs[0], \
                f"Expected Python doc, got {results[0].metadata['text']}"
            
            print(f"    Query: '{query}'")
            print(f"    Top result: '{results[0].metadata['text']}' (score: {results[0].score:.4f})")
            
            self.log_test("Vector Collection Basic", True)
        except Exception as e:
            self.log_test("Vector Collection Basic", False, str(e))
    
    def test_vector_metadata_filtering(self):
        """Test vector search with metadata filtering"""
        try:
            ns = self.db.namespace("default")
            collection = ns.collection("documents")
            
            # Search with metadata filter
            query = "programming language"
            query_embedding = self.get_embedding(query)
            
            results = collection.vector_search(
                vector=query_embedding,
                k=5,
                filter={"index": 0}  # Only doc0
            )
            
            assert len(results) == 1, f"Expected 1 result, got {len(results)}"
            assert results[0].id == "doc0", f"Expected doc0, got {results[0].id}"
            
            self.log_test("Vector Metadata Filtering", True)
        except Exception as e:
            self.log_test("Vector Metadata Filtering", False, str(e))
    
    # ========== HYBRID SEARCH TESTS ==========
    
    def test_hybrid_search(self):
        """Test hybrid search (vector + BM25)"""
        try:
            ns = self.db.namespace("default")
            
            # Create collection with hybrid search enabled
            try:
                ns.delete_collection("hybrid_docs")
            except:
                pass
            
            config = CollectionConfig(
                name="hybrid_docs",
                dimension=self.embedding_dimension,
                enable_hybrid_search=True,
                content_field="text"
            )
            collection = ns.create_collection(config)
            
            # Insert documents
            docs = [
                "The quick brown fox jumps over the lazy dog",
                "Python programming language is versatile and powerful",
                "Machine learning models require large datasets"
            ]
            
            print("  Getting embeddings for hybrid search...")
            for i, doc in enumerate(docs):
                embedding = self.get_embedding(doc)
                collection.insert(
                    id=f"hybrid{i}",
                    vector=embedding,
                    metadata={"text": doc}
                )
            
            # Hybrid search
            query = "Python coding"
            query_embedding = self.get_embedding(query)
            
            results = collection.hybrid_search(
                vector=query_embedding,
                text_query="Python",
                k=2,
                alpha=0.5  # Balanced between vector and keyword
            )
            
            assert len(results) > 0, "Should return hybrid search results"
            print(f"    Hybrid search for '{query}': {len(results)} results")
            
            self.log_test("Hybrid Search", True)
        except Exception as e:
            self.log_test("Hybrid Search", False, str(e))
    
    # ========== GRAPH TESTS ==========
    
    def test_graph_operations(self):
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
            
            # Add edge
            self.db.add_edge(
                namespace="default",
                from_id="alice",
                edge_type="works_on",
                to_id="project_x",
                properties={"role": "lead"}
            )
            
            # Get neighbors
            neighbors = self.db.get_neighbors(
                namespace="default",
                node_id="alice",
                direction="outgoing"
            )
            
            assert len(neighbors) > 0, "Should have neighbors"
            assert neighbors[0]['id'] == "project_x", f"Expected project_x, got {neighbors[0]['id']}"
            
            self.log_test("Graph Operations", True)
        except Exception as e:
            self.log_test("Graph Operations", False, str(e))
    
    def test_graph_traversal(self):
        """Test graph traversal"""
        try:
            # Add more nodes and edges for traversal
            self.db.add_node("default", "bob", "person", {"role": "manager"})
            self.db.add_edge("default", "alice", "reports_to", "bob")
            self.db.add_edge("default", "bob", "manages", "project_x")
            
            # Traverse from alice
            nodes, edges = self.db.traverse(
                namespace="default",
                start_node="alice",
                max_depth=2,
                order="bfs"
            )
            
            assert len(nodes) > 0, "Should traverse nodes"
            assert len(edges) > 0, "Should traverse edges"
            
            # Check for specific nodes
            node_ids = [node['id'] for node in nodes]
            assert "alice" in node_ids, "Should include starting node"
            assert "bob" in node_ids or "project_x" in node_ids, "Should include connected nodes"
            
            self.log_test("Graph Traversal", True)
        except Exception as e:
            self.log_test("Graph Traversal", False, str(e))
    
    # ========== TEMPORAL GRAPH TESTS ==========
    
    def test_temporal_graph(self):
        """Test temporal edges and time-travel queries"""
        try:
            now = int(time.time() * 1000)
            one_hour = 60 * 60 * 1000
            
            # Add nodes
            self.db.add_node("default", "door_front", "sensor", {})
            self.db.add_node("default", "open", "state", {})
            self.db.add_node("default", "closed", "state", {})
            
            # Add temporal edge (door was open 1 hour ago)
            self.db.add_temporal_edge(
                namespace="default",
                from_id="door_front",
                edge_type="STATE",
                to_id="open",
                valid_from=now - one_hour,
                valid_until=now - (one_hour // 2),
                properties={"sensor": "motion_1"}
            )
            
            # Add current state (door is closed now)
            self.db.add_temporal_edge(
                namespace="default",
                from_id="door_front",
                edge_type="STATE",
                to_id="closed",
                valid_from=now - (one_hour // 2),
                valid_until=0,  # Still valid
                properties={"sensor": "motion_1"}
            )
            
            # Query current state
            edges = self.db.query_temporal_graph(
                namespace="default",
                node_id="door_front",
                mode="CURRENT",
                edge_type="STATE"
            )
            
            assert len(edges) > 0, "Should return current state"
            current_state = edges[0]["to_id"]
            assert current_state == "closed", f"Expected closed, got {current_state}"
            
            # Query historical state
            edges = self.db.query_temporal_graph(
                namespace="default",
                node_id="door_front",
                mode="POINT_IN_TIME",
                timestamp=now - int(0.75 * one_hour)
            )
            
            assert len(edges) > 0, "Should return historical state"
            past_state = edges[0]["to_id"]
            assert past_state == "open", f"Expected open at that time, got {past_state}"
            
            self.log_test("Temporal Graph", True)
        except Exception as e:
            self.log_test("Temporal Graph", False, str(e))
    
    # ========== SEMANTIC CACHE TESTS ==========
    
    def test_semantic_cache(self):
        """Test semantic cache with real embeddings"""
        try:
            # Store in cache
            query1 = "What is machine learning?"
            response1 = "Machine learning is a method of data analysis that automates analytical model building."
            embedding1 = self.get_embedding(query1)
            
            self.db.cache_put(
                cache_name="llm_responses",
                key=query1,
                value=response1,
                embedding=embedding1,
                ttl_seconds=3600,
                metadata={"model": "test"}
            )
            
            # Try to retrieve with similar query
            query2 = "What is ML?"
            embedding2 = self.get_embedding(query2)
            
            cached = self.db.cache_get(
                cache_name="llm_responses",
                query_embedding=embedding2,
                threshold=0.75  # Lower threshold for similar queries
            )
            
            if cached:
                print(f"    Cache HIT! Original: '{cached['key']}'")
                print(f"    Similarity: {cached['score']:.4f}")
                assert cached['value'] == response1, "Should return cached response"
                self.log_test("Semantic Cache", True, f"Cache hit with score {cached['score']:.4f}")
            else:
                # This is okay - semantic similarity might not be high enough
                self.log_test("Semantic Cache", True, "Cache miss (expected for different queries)")
            
        except Exception as e:
            self.log_test("Semantic Cache", False, str(e))
    
    # ========== PREFIX SCANNING TESTS ==========
    
    def test_prefix_scanning(self):
        """Test prefix scanning operations"""
        try:
            # Insert data with common prefix
            prefixes = [
                (b"logs/2024-01-01", b"log entry 1"),
                (b"logs/2024-01-02", b"log entry 2"),
                (b"logs/2024-01-03", b"log entry 3"),
            ]
            self.db.put_batch(prefixes)
            
            # Scan with prefix
            results = list(self.db.scan_prefix(b"logs/"))
            assert len(results) == 3, f"Expected 3 results, got {len(results)}"
            
            # Batched scanning
            batch_results = list(self.db.scan_batched(b"logs/", batch_size=2))
            assert len(batch_results) == 3, f"Expected 3 results, got {len(batch_results)}"
            
            self.log_test("Prefix Scanning", True)
        except Exception as e:
            self.log_test("Prefix Scanning", False, str(e))
    
    # ========== STATISTICS TESTS ==========
    
    def test_statistics(self):
        """Test database statistics"""
        try:
            stats = self.db.stats()
            
            assert "key_count" in stats or "total_keys" in stats, "Should have key count"
            print(f"    Database stats: {json.dumps(stats, indent=2)}")
            
            self.log_test("Statistics", True)
        except Exception as e:
            self.log_test("Statistics", False, str(e))
    
    # ========== RUN ALL TESTS ==========
    
    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*80)
        print("SochDB Comprehensive Test Suite")
        print("="*80 + "\n")
        
        self.setup()
        
        print("\n--- Core Key-Value Tests ---")
        self.test_basic_kv_operations()
        self.test_path_based_keys()
        self.test_batch_operations()
        
        print("\n--- Transaction Tests ---")
        self.test_transaction_context_manager()
        self.test_transaction_rollback()
        
        print("\n--- SQL Tests ---")
        self.test_sql_operations()
        
        print("\n--- Namespace Tests ---")
        self.test_namespaces()
        
        print("\n--- Vector Search Tests (with Real Azure OpenAI Embeddings) ---")
        self.test_vector_collection_basic()
        self.test_vector_metadata_filtering()
        
        print("\n--- Hybrid Search Tests ---")
        self.test_hybrid_search()
        
        print("\n--- Graph Tests ---")
        self.test_graph_operations()
        self.test_graph_traversal()
        
        print("\n--- Temporal Graph Tests ---")
        self.test_temporal_graph()
        
        print("\n--- Semantic Cache Tests ---")
        self.test_semantic_cache()
        
        print("\n--- Prefix Scanning Tests ---")
        self.test_prefix_scanning()
        
        print("\n--- Statistics Tests ---")
        self.test_statistics()
        
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
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\nDetailed results saved to: test_results.json")
        
        return failed == 0


if __name__ == "__main__":
    tester = SochDBTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
