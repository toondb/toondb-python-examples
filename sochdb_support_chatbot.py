"""
Support Chatbot using SochDB with Azure OpenAI
Equivalent implementation to mem0_support_chatbot.py for direct comparison
"""

import os
from typing import List, Dict
from datetime import datetime
import time

# SochDB imports
from sochdb import Database, CollectionConfig, DistanceMetric, SearchRequest

# Azure OpenAI import
from openai import AzureOpenAI

# Local imports
from metrics_collector import MetricsCollector
from azure_llm_config import load_azure_config

class SochDBSupportChatbot:
    def __init__(self, db_path: str = "./sochdb_support"):
        print("Initializing SochDB Support Chatbot with Azure OpenAI...")
        
        # Initialize metrics
        self.metrics = MetricsCollector("sochdb_support_chatbot")
        
        # Load Azure config
        config = load_azure_config()
        
        # Initialize Azure OpenAI clients
        self.llm_client = AzureOpenAI(
            api_key=config['api_key'],
            api_version=config['api_version'],
            azure_endpoint=config['endpoint']
        )
        self.llm_deployment = config['chat_deployment']
        self.embedding_deployment = config['embedding_deployment']
        
        # Initialize SochDB
        op_id = f"sochdb_init_{time.time()}"
        self.metrics.start_operation(op_id)
        
        self.db = Database.open(db_path)
        self.namespace = self.db.get_or_create_namespace("support")
        
        # Create collection for support interactions
        collection_config = CollectionConfig(
            name="interactions",
            dimension=1536,  # text-embedding-3-small
            metric=DistanceMetric.COSINE,
            m=16,
            ef_construction=200,
            enable_hybrid_search=True,
            content_field="interaction_text"
        )
        
        try:
            self.collection = self.namespace.create_collection(collection_config)
        except:
            self.collection = self.namespace.collection("interactions")
        
        self.metrics.end_operation(op_id, "memory_init", {"backend": "sochdb"})
        
        # Support context
        self.system_context = """You are a helpful customer support agent. Use the following guidelines:
- Be polite and professional
- Show empathy for customer issues
- Reference past interactions when relevant
- Maintain consistent information across conversations
- If you're unsure about something, ask for clarification
- Keep track of open issues and follow-ups"""
        
        print("✓ SochDB Support Chatbot initialized")
    
    def store_customer_interaction(self, user_id: str, message: str, response: str, metadata: Dict = None):
        """Store customer interaction in SochDB collection."""
        op_id = f"memory_add_{time.time()}"
        self.metrics.start_operation(op_id)
        
        if metadata is None:
            metadata = {}
        
        metadata["timestamp"] = datetime.now().isoformat()
        metadata["user_id"] = user_id
        metadata["type"] = metadata.get("type", "support_query")
        
        # Create compact summary for storage (not full conversation)
        # Store just the key facts/issue for token efficiency
        summary = f"{message[:100]}"  # Truncate customer message
        
        # Generate embedding from full text but store compact version
        embedding_response = self.llm_client.embeddings.create(
            input=message,  # Embed the question for search relevance
            model=self.embedding_deployment
        )
        embedding = embedding_response.data[0].embedding
        
        # Store in SochDB with compact metadata
        interaction_id = f"{user_id}_{int(time.time()*1000)}"
        metadata["summary"] = summary  # Compact summary
        metadata["message"] = message  # Full message for reference
        metadata["timestamp_short"] = datetime.now().strftime("%Y-%m-%d")  # Compact timestamp
        
        self.collection.insert(
            id=interaction_id,
            vector=embedding,
            metadata=metadata
        )
        
        self.metrics.end_operation(op_id, "memory_add", {
            "user_id": user_id,
            "message_length": len(message)
        })
        
        return interaction_id
    
    def get_relevant_history(self, user_id: str, query: str) -> List[Dict]:
        """Retrieve relevant past interactions using hybrid search."""
        op_id = f"memory_search_{time.time()}"
        self.metrics.start_operation(op_id)
        
        # Generate query embedding
        embedding_response = self.llm_client.embeddings.create(
            input=query,
            model=self.embedding_deployment
        )
        query_embedding = embedding_response.data[0].embedding
        
        # Hybrid search (vector + keyword)
        search_request = SearchRequest(
            vector=query_embedding,
            text_query=query,
            k=5,
            alpha=0.7,  # 70% vector, 30% keyword
            filter={"user_id": user_id},
            include_metadata=True
        )
        
        results = self.collection.search(search_request)
        results_list = results.results if hasattr(results, 'results') else results
       
        self.metrics.end_operation(op_id, "memory_search", {
            "user_id": user_id,
            "query_length": len(query),
            "memories_count": len(results_list)
        })
        
        return results_list
    
    def handle_customer_query(self, user_id: str, query: str) -> str:
        """Process customer query with context from past interactions."""
        # Get relevant history
        relevant_history = self.get_relevant_history(user_id, query)
        
        # Build compact context (like mem0's fact extraction)
        context = "Previous issues:\\n"
        if relevant_history:
            for result in relevant_history:
                # Use compact summary, not full text
                summary = result.metadata.get("summary", "")
                if summary:
                    context += f"- {summary}\\n"
            context += "---\\n"
        else:
            context = "No previous interactions found.\\n"
        
        # Prepare prompt
        prompt = f"""{self.system_context}

{context}

Current customer query: {query}

Provide a helpful response that takes into account any relevant past interactions."""
        
        # Generate response using Azure OpenAI
        llm_op_id = f"llm_{time.time()}"
        self.metrics.start_operation(llm_op_id)
        
        response = self.llm_client.chat.completions.create(
            model=self.llm_deployment,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.1
        )
        
        response_text = response.choices[0].message.content
        
        # Extract token usage
        usage = response.usage
        self.metrics.end_operation(llm_op_id, "llm_call", {
            "model": self.llm_deployment,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens
        })
        
        # Store interaction
        self.store_customer_interaction(
            user_id=user_id,
            message=query,
            response=response_text,
            metadata={"type": "support_query"}
        )
        
        return response_text
    
    def save_metrics(self, filename: str = "sochdb_support_metrics.json"):
        """Save collected metrics."""
        self.metrics.finalize()
        self.metrics.save_to_file(filename)
        print(f"✓ Metrics saved to {filename}")
    
    def close(self):
        """Clean up resources."""
        if hasattr(self, 'db'):
            self.db.close()


def run_test_conversation():
    """Run a test support conversation with predefined queries."""
    chatbot = SochDBSupportChatbot()
    user_id = "customer_001"
    
    # Same test conversation as mem0 version
    queries = [
        "Hi, I'm having trouble connecting my new smartwatch to the mobile app. It keeps showing a connection error.",
        "The connection issue is still happening even after trying the steps you suggested.",
        "What's the status of my previous issue with the smartwatch?"
    ]
    
    print("\n" + "=" * 80)
    print("SUPPORT CONVERSATION TEST")
    print("=" * 80 + "\n")
    
    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}:")
        print(f"Customer: {query}")
        
        response = chatbot.handle_customer_query(user_id, query)
        print(f"Support: {response[:200]}...")  # Truncate for display
        print("-" * 80)
    
    # Save metrics
    chatbot.save_metrics()
    
    # Print summary
    stats = chatbot.metrics.get_statistics()
    print("\n" + "=" * 80)
    print("METRICS SUMMARY")
    print("=" * 80)
    print(f"Memory Operations: {stats['memory_operations']['total_count']}")
    print(f"  - Adds: {stats['memory_operations']['add_count']}")
    print(f"  - Searches: {stats['memory_operations']['search_count']}")
    print(f"  - Avg Latency: {stats['memory_operations']['latency_ms']['avg']:.2f}ms")
    print(f"\nLLM Calls: {stats['llm_operations']['call_count']}")
    print(f"  - Total Tokens: {stats['llm_operations']['total_tokens']}")
    print(f"  - Avg Latency: {stats['llm_operations']['latency_ms']['avg']:.2f}ms")
    print(f"\nRecall: {stats['recall']['total_memories_retrieved']} memories retrieved")
    print(f"Success Rate: {stats['reliability']['success_rate']:.1f}%")
    print("=" * 80)
    
    # Clean up
    chatbot.close()


if __name__ == "__main__":
    run_test_conversation()
