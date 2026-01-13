#!/usr/bin/env python3
"""
Shared Test Utilities for SochDB Testing Suite

Provides common functions for:
- Azure OpenAI client initialization
- Embedding generation
- Database setup/cleanup
- Test result logging
"""

import os
import shutil
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

# Singleton Azure client
_azure_client = None


def get_azure_client() -> AzureOpenAI:
    """Get configured Azure OpenAI client (singleton)"""
    global _azure_client
    if _azure_client is None:
        _azure_client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    return _azure_client


def get_embedding(text: str, client: Optional[AzureOpenAI] = None) -> List[float]:
    """
    Get real embedding from Azure OpenAI
    
    Args:
        text: Text to embed
        client: Optional Azure OpenAI client (will create if None)
    
    Returns:
        1536-dimensional embedding vector
    """
    if client is None:
        client = get_azure_client()
    
    response = client.embeddings.create(
        input=text,
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    )
    return response.data[0].embedding


def get_embeddings_batch(texts: List[str], client: Optional[AzureOpenAI] = None) -> List[List[float]]:
    """
    Get embeddings for multiple texts in one API call
    
    Args:
        texts: List of texts to embed
        client: Optional Azure OpenAI client
    
    Returns:
        List of embedding vectors
    """
    if client is None:
        client = get_azure_client()
    
    response = client.embeddings.create(
        input=texts,
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    )
    return [item.embedding for item in response.data]


def setup_test_db(path: str = "./test_db") -> str:
    """
    Setup test database directory, clean if exists
    
    Args:
        path: Database path
    
    Returns:
        Absolute path to database
    """
    # Clean up if exists
    if os.path.exists(path):
        shutil.rmtree(path)
    
    # Create directory
    os.makedirs(path, exist_ok=True)
    
    return os.path.abspath(path)


def cleanup_test_db(path: str):
    """
    Cleanup test database directory
    
    Args:
        path: Database path to remove
    """
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f"Warning: Failed to cleanup {path}: {e}")


def log_test_result(
    test_name: str,
    passed: bool,
    message: str = "",
    execution_time_ms: float = 0
) -> Dict[str, Any]:
    """
    Create test result dictionary
    
    Args:
        test_name: Name of the test
        passed: Whether test passed
        message: Optional message/error
        execution_time_ms: Execution time in milliseconds
    
    Returns:
        Test result dictionary
    """
    return {
        "test": test_name,
        "passed": passed,
        "message": message,
        "execution_time_ms": execution_time_ms,
        "timestamp": datetime.now().isoformat()
    }


def print_test_result(result: Dict[str, Any]):
    """
    Print test result to console
    
    Args:
        result: Test result dictionary
    """
    status = "✓ PASS" if result["passed"] else "✗ FAIL"
    message = f" - {result['message']}" if result["message"] else ""
    time_info = f" ({result['execution_time_ms']:.1f}ms)" if result.get("execution_time_ms", 0) > 0 else ""
    print(f"{status}: {result['test']}{time_info}{message}")


def save_test_results(results: List[Dict[str, Any]], output_file: str):
    """
    Save test results to JSON file
    
    Args:
        results: List of test result dictionaries
        output_file: Path to output JSON file
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)


def load_test_results(input_file: str) -> List[Dict[str, Any]]:
    """
    Load test results from JSON file
    
    Args:
        input_file: Path to input JSON file
    
    Returns:
        List of test result dictionaries
    """
    if not os.path.exists(input_file):
        return []
    
    with open(input_file, 'r') as f:
        return json.load(f)


class TestBase:
    """Base class for all tests"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.results = []
        self.start_time = None
    
    def setup(self):
        """Override in subclass"""
        pass
    
    def teardown(self):
        """Override in subclass"""
        pass
    
    def add_result(self, test_name: str, passed: bool, message: str = ""):
        """Add a test result"""
        result = log_test_result(test_name, passed, message)
        self.results.append(result)
        print_test_result(result)
    
    def run(self) -> List[Dict[str, Any]]:
        """
        Run all tests
        
        Returns:
            List of test results
        """
        import time
        
        print(f"\n{'='*70}")
        print(f"Test: {self.test_name}")
        print(f"{'='*70}\n")
        
        try:
            self.start_time = time.time()
            self.setup()
            self.execute_tests()
            self.teardown()
        except Exception as e:
            self.add_result(
                f"{self.test_name} - Setup/Teardown",
                False,
                f"Fatal error: {str(e)}"
            )
        
        # Print summary
        passed = sum(1 for r in self.results if r["passed"])
        failed = len(self.results) - passed
        
        print(f"\n{'-'*70}")
        print(f"Results: {passed} passed, {failed} failed out of {len(self.results)} tests")
        print(f"{'-'*70}\n")
        
        return self.results
    
    def execute_tests(self):
        """Override in subclass to run actual tests"""
        raise NotImplementedError("Subclass must implement execute_tests()")


# Test data for common use cases
SAMPLE_TEXTS = [
    "Python is a high-level programming language",
    "Machine learning is a subset of artificial intelligence",
    "Database systems store and retrieve data efficiently",
    "Vector search enables semantic similarity matching",
    "Graph databases excel at relationship queries"
]

SAMPLE_QUERIES = [
    "What is Python?",
    "Tell me about ML",
    "How do databases work?",
    "What is vector search?",
    "Explain graph databases"
]
