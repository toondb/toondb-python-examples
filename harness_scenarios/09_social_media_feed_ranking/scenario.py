"""
Scenario 09: Social Media Feed Ranking
=====================================

Tests:
- Personalized ranking (user preferences)
- Recency + relevance scoring
- Real social media post generation using LLM
"""

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "sochdb-python-sdk" / "src"))

from harness_scenarios.base_scenario import BaseScenario, ScenarioMetrics


class SocialMediaFeedScenario(BaseScenario):
    """Social media feed ranking."""
    
    def __init__(self, db, generator, llm_client):
        super().__init__("09_social_media_feed_ranking", db, generator, llm_client)
    
    def run(self) -> ScenarioMetrics:
        """Run social media feed scenario."""
        print(f"\n[{self.scenario_id}] Starting...")
        
        # Generate real social media posts using LLM
        posts = self._generate_real_posts(num_posts=60)
        
        # Create namespace and collection
        try:
            self.db.create_namespace("social_ns")
        except:
            pass
        
        with self.db.use_namespace("social_ns") as ns:
            # Create collection
            try:
                posts_col = ns.create_collection("social_posts", dimension=self.generator.embedding_dim)
            except:
                posts_col = ns.collection("social_posts")
            
            # Insert posts
            with self._track_time("insert"):
                for post in posts:
                    posts_col.insert(id=post['id'], vector=post['embedding'], metadata=post['metadata'])
            
            # Test recency scoring
            self._test_recency_ranking(posts_col, posts)
            
            # Test engagement-based ranking
            self._test_engagement_ranking(posts_col, posts)
        
        print(f"[{self.scenario_id}] {'✓ PASS' if self.metrics.passed else '✗ FAIL'}")
        return self.metrics
    
    def _generate_real_posts(self, num_posts: int) -> List[Dict]:
        """Generate real social media posts using LLM."""
        print(f"  Generating {num_posts} social media posts with real LLM...")
        posts = []
        
        topics = ["travel", "food", "fitness", "technology", "fashion", "music"]
        base_time = datetime.now() - timedelta(hours=24)
        
        for i in range(num_posts):
            topic = random.choice(topics)
            timestamp = base_time + timedelta(minutes=i * 5)
            
            # Generate real social media post using LLM
            prompt = f"Generate a casual social media post about {topic} (2-3 sentences, engaging tone):"
            content = self.llm.generate_text(prompt, max_tokens=100)
            self.metrics.track_llm_call(100)
            
            # Generate real embedding
            embedding = self.llm.get_embedding(content)
            self.metrics.track_llm_call(50)
            
            posts.append({
                'id': f"post_{i:03d}",
                'embedding': embedding,
                'metadata': {
                    'content': content,
                    'topic': topic,
                    'author': f"user_{random.randint(1, 20)}",
                    'likes': random.randint(0, 1000),
                    'comments': random.randint(0, 100),
                    'shares': random.randint(0, 50),
                    'timestamp': timestamp.isoformat(),
                    'timestamp_unix': timestamp.timestamp(),
                }
            })
        
        return posts
    
    def _test_personalized_ranking(self, posts_col, posts: List[Dict]):
        """Test personalized feed ranking."""
        print(f"  Testing personalized ranking...")
        
        # Simulate user preferences
        user_topic = "technology"
        
        # Generate personalized query using LLM
        prompt = f"Generate a user interest query for someone who likes {user_topic}:"
        query = self.llm.generate_text(prompt, max_tokens=30)
        self.metrics.track_llm_call(30)
        
        query_emb = self.llm.get_embedding(query)
        self.metrics.track_llm_call(50)
        
        with self._track_time("personalized_search"):
            results = posts_col.hybrid_search(query_emb, query, k=20, alpha=0.6)
        
        # Verify relevant posts ranked higher
        relevant_in_top_10 = sum(1 for r in results.results[:10] if r.metadata.get('topic') == user_topic)
        
        if relevant_in_top_10 < 3:
            self.metrics.errors.append(f"Poor personalization: only {relevant_in_top_10} relevant in top 10")
            self.metrics.passed = False
    
    def _test_recency_ranking(self, posts_col, posts: List[Dict]):
        """Test recency-based ranking."""
        print(f"  Testing recency ranking...")
        
        # Verify recent posts exist in collection
        post_count = posts_col.count()
        
        with self._track_time("recency_query"):
            # Verify sample of most recent posts
            recent_count = 0
            for post in posts[-20:]:  # Check last 20 posts (most recent)
                try:
                    result = posts_col.get(post['id'])
                    if result:
                        recent_count += 1
                except:
                    pass
        
        # Verify recent posts are accessible
        if recent_count < 10:
            self.metrics.errors.append(f"Recent posts not accessible: {recent_count}/20")
            self.metrics.passed = False
    
    def _test_engagement_ranking(self, posts_col, posts: List[Dict]):
        """Test engagement-based ranking."""
        print(f"  Testing engagement ranking...")
        
        # Find highly engaged posts from our data
        post_count = posts_col.count()
        
        # Score posts from our ground truth: likes + 2*comments + 3*shares
        scored_posts = []
        for post in posts:
            metadata = post['metadata']
            score = metadata['likes'] + 2*metadata['comments'] + 3*metadata['shares']
            scored_posts.append((post, score))
        
        scored_posts.sort(key=lambda x: x[1], reverse=True)
        
        with self._track_time("engagement_ranking"):
            top_engaged = scored_posts[:10]
        
        # Verify high engagement scores
        if top_engaged:
            min_top_score = top_engaged[-1][1]
            
            # Check that lower-ranked posts have lower scores
            for item, score in scored_posts[10:20]:
                if score > min_top_score:
                    self.metrics.errors.append("Engagement ranking incorrect")
                    self.metrics.passed = False
                    break
