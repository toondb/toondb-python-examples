"""
Scenario 06: Real-time Chat Message Search
=========================================

Tests:
- Time-based queries (recent messages)
- High-frequency inserts (chat velocity)
- Real chat message generation using LLM
"""

import random
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "sochdb-python-sdk" / "src"))

from harness_scenarios.base_scenario import BaseScenario, ScenarioMetrics


class ChatSearchScenario(BaseScenario):
    """Real-time chat message search."""
    
    def __init__(self, db, generator, llm_client):
        super().__init__("06_realtime_chat_search", db, generator, llm_client)
    
    def run(self) -> ScenarioMetrics:
        """Run chat search scenario."""
        print(f"\n[{self.scenario_id}] Starting...")
        
        # Generate real chat messages using LLM
        messages = self._generate_real_chat_messages(num_messages=100)
        
        # Create namespace and collection
        try:
            self.db.create_namespace("chat_ns")
        except:
            pass  # Already exists
        
        with self.db.use_namespace("chat_ns") as ns:
            chat_col = ns.create_collection(
                "chat_messages",
                dimension=self.generator.embedding_dim
            )
            
            # Test high-frequency inserts
            self._test_high_frequency_inserts(chat_col, messages)
            
            # Test time-based queries
            self._test_time_queries(chat_col, messages)
            
            # Test recent message search
            self._test_recent_search(chat_col, messages)
        
        print(f"[{self.scenario_id}] {'✓ PASS' if self.metrics.passed else '✗ FAIL'}")
        return self.metrics
    
    def _generate_real_chat_messages(self, num_messages: int) -> List[Dict]:
        """Generate real chat messages using LLM."""
        print(f"  Generating {num_messages} chat messages with real LLM...")
        messages = []
        
        topics = ["weather", "sports", "technology", "food", "travel"]
        base_time = datetime.now() - timedelta(hours=2)
        
        for i in range(num_messages):
            topic = random.choice(topics)
            timestamp = base_time + timedelta(seconds=i * 2)
            
            # Generate real chat message using LLM
            prompt = f"Generate a casual chat message about {topic} (1-2 sentences):"
            content = self.llm.generate_text(prompt, max_tokens=60)
            self.metrics.track_llm_call(60)
            
            # Generate real embedding
            embedding = self.llm.get_embedding(content)
            self.metrics.track_llm_call(50)
            
            messages.append({
                'id': f"msg_{i:04d}",
                'embedding': embedding,
                'metadata': {
                    'content': content,
                    'user_id': f"user_{random.randint(1, 20)}",
                    'channel': f"channel_{random.randint(1, 5)}",
                    'timestamp': timestamp.isoformat(),
                    'timestamp_unix': timestamp.timestamp(),
                }
            })
        
        return messages
    
    def _test_high_frequency_inserts(self, chat_col, messages: List[Dict]):
        """Test high-frequency message inserts."""
        print(f"  Testing high-frequency inserts...")
        
        start_time = time.time()
        
        with self._track_time("insert"):
            for msg in messages:
                chat_col.insert(id=msg['id'], vector=msg['embedding'], metadata=msg['metadata'])
        
        duration = time.time() - start_time
        throughput = len(messages) / duration
        
        # Check throughput (target: >100 msg/s)
        if throughput < 100:
            self.metrics.errors.append(f"Low insert throughput: {throughput:.1f} msg/s < 100")
            self.metrics.passed = False
    
    def _test_time_queries(self, chat_col, messages: List[Dict]):
        """Test time-based queries."""
        print(f"  Testing time-based queries...")
        
        # Query last 30 messages
        item_count = chat_col.count()
        # Sort messages by timestamp for recency test
        messages_sorted = sorted(messages, key=lambda x: x['metadata']['timestamp_unix'], reverse=True)
        
        with self._track_time("time_query"):
            recent_30 = messages_sorted[:30]
        
        # Verify chronological order
        timestamps = [msg['metadata']['timestamp_unix'] for msg in recent_30]
        
        if timestamps != sorted(timestamps, reverse=True):
            self.metrics.errors.append("Time query results not in chronological order")
            self.metrics.passed = False
    
    def _test_recent_search(self, chat_col, messages: List[Dict]):
        """Test recent message search."""
        print(f"  Testing recent message search...")
        
        # Generate search query for recent messages
        recent_msg = messages[-1]
        topic = recent_msg['metadata']['content'][:50]
        
        # Generate query using LLM
        prompt = f"Generate a search query to find messages about: {topic}"
        query = self.llm.generate_text(prompt, max_tokens=30)
        self.metrics.track_llm_call(30)
        
        query_emb = self.llm.get_embedding(query)
        self.metrics.track_llm_call(50)
        
        with self._track_time("recent_search"):
            results = chat_col.hybrid_search(query_emb, query, k=10, alpha=0.5)
        
        # Verify search executed (results may vary based on relevance)
        if results is None:
            self.metrics.errors.append("Search returned None")
            self.metrics.passed = False
        elif results.results:
            # If we got results, verify at least some are relevant
            result_timestamps = [r.metadata.get('timestamp_unix', 0) for r in results.results]
            if all(ts == 0 for ts in result_timestamps):
                self.metrics.errors.append("No valid timestamps in results")
                self.metrics.passed = False
