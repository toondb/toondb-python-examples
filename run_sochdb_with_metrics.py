"""
SochDB-based Multi-Agent Learning System with Metrics Collection

Equivalent implementation to run_llama_index_with_metrics.py but using SochDB instead of mem0.
Allows direct comparison of performance metrics between SochDB and mem0.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime

# SochDB imports
from sochdb import Database, CollectionConfig, DistanceMetric, SearchRequest

# LlamaIndex imports
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.base.llms.types import ChatMessage, MessageRole

# Local imports
from metrics_collector import MetricsCollector
from azure_llm_config import load_azure_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sochdb_learning_system_metrics.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SochDBMultiAgentLearningSystem:
    """
    Multi-agent learning system using SochDB for memory instead of mem0.
    
    Uses SochDB's:
    - Collections for vector storage
    - Hybrid search for keyword + semantic matching
    - Graph operations for relationship tracking
    """
    
    def __init__(self, student_id: str, db_path: str = "./sochdb_learning"):
        self.student_id = student_id
        self.metrics = MetricsCollector(f"sochdb_{student_id}")
        
        logger.info("=" * 80)
        logger.info("Multi-agent Learning System powered by LlamaIndex and SochDB")
        logger.info("Running with metrics collection...")
        logger.info("=" * 80)
        
        # Configure Azure OpenAI
        logger.info("Configuring Azure OpenAI...")
        config = load_azure_config()
        
        self.llm = AzureOpenAI(
            model=config['chat_deployment'],
            deployment_name=config['chat_deployment'],
            api_key=config['api_key'],
            azure_endpoint=config['endpoint'],
            api_version=config['api_version'],
        )
        logger.info(f"✓ Azure OpenAI LLM configured: {config['chat_deployment']}")
        
        # Initialize SochDB
        logger.info("Initializing SochDB...")
        op_id = f"sochdb_init_{time.time()}"
        self.metrics.start_operation(op_id)
        
        try:
            # Open database
            self.db = Database.open(db_path)
            
            # Create namespace for this student
            self.namespace = self.db.get_or_create_namespace(f"student_{student_id}")
            
            # Create collection for memories with hybrid search
            collection_config = CollectionConfig(
                name="memories",
                dimension=1536,  # text-embedding-3-small dimension
                metric=DistanceMetric.COSINE,
                m=16,
                ef_construction=200,
                enable_hybrid_search=True,
                content_field="memory_text"
            )
            
            try:
                self.collection = self.namespace.create_collection(collection_config)
            except Exception as e:
                # Collection might already exist
                self.collection = self.namespace.collection("memories")
            
            # Create graph nodes for student
            self.db.add_node(
                namespace=f"student_{student_id}",
                node_id=f"student_{student_id}",
                node_type="student",
                properties={"created_at": datetime.now().isoformat()}
            )
            
            self.metrics.end_operation(op_id, "sochdb_init", {
                "student_id": student_id,
                "type": "embedded",
                "backend": "sochdb"
            })
            logger.info("✓ SochDB initialized successfully")
            
        except Exception as e:
            self.metrics.record_error("sochdb_init", str(e))
            raise
    
    async def start_learning_session(self, topic: str, student_message: str = "") -> str:
        """
        Start a learning session on a specific topic.
        """
        request = f"I want to learn about {topic}." if not student_message else f"I want to learn about {topic}. {student_message}"
        
        logger.info(f"Starting learning session: {topic}")
        
        # Build conversation for memory extraction
        conversation = [
            {"role": "user", "content": request}
        ]
        
        try:
            # 1. Add memories from conversation
            add_op_id = f"memory_add_{time.time()}"
            self.metrics.start_operation(add_op_id)
            
            # Extract facts and store as separate memories
            # For simplicity, we'll create memories based on the conversation
            memory_id = f"session_{int(time.time())}_{topic.replace(' ', '_')}"
            memory_text = request
            
            # Generate embedding using Azure OpenAI
            from openai import AzureOpenAI as OpenAIClient
            embedding_client = OpenAIClient(
                api_key=load_azure_config()['api_key'],
                api_version=load_azure_config()['api_version'],
                azure_endpoint=load_azure_config()['endpoint']
            )
            
            embedding_response = embedding_client.embeddings.create(
                input=memory_text,
                model=load_azure_config()['embedding_deployment']
            )
            embedding = embedding_response.data[0].embedding
            
            # Store in SochDB collection
            self.collection.insert(
                id=memory_id,
                vector=embedding,
                metadata={
                    "memory_text": memory_text,
                    "topic": topic,
                    "student_id": self.student_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Add graph edge to track student's learning topics
            try:
                self.db.add_edge(
                    namespace=f"student_{self.student_id}",
                    from_id=f"student_{self.student_id}",
                    edge_type="learned_about",
                    to_id=memory_id,
                    properties={"topic": topic}
                )
            except:
                pass  # Edge might already exist
            
            self.metrics.end_operation(add_op_id, "memory_add", {
                "memory_id": memory_id,
                "topic": topic
            })
            
            # 2. Search for related memories
            search_op_id = f"memory_search_{time.time()}"
            self.metrics.start_operation(search_op_id)
            
            # Search using hybrid search (vector + keyword)
            search_request = SearchRequest(
                vector=embedding,
                text_query=topic,
                k=5,
                alpha=0.7,  # 70% vector, 30% keyword
                filter={"student_id": self.student_id},
                include_metadata=True
            )
            
            search_results = self.collection.search(search_request)
            
            results_count = len(search_results.results) if hasattr(search_results, 'results') else len(search_results)
            self.metrics.end_operation(search_op_id, "memory_search", {
                "results_count": results_count,
                "memories_count": results_count,
                "query": topic[:50]
            })
            
            # 3. Generate LLM response using Azure OpenAI
            llm_op_id = f"llm_{time.time()}"
            self.metrics.start_operation(llm_op_id)
            
            # Build context from memories
            memory_context = ""
            results_list = search_results.results if hasattr(search_results, 'results') else search_results
            if results_list:
                memory_context = "\\n".join([
                    f"- {r.metadata.get('memory_text', '')}" 
                    for r in results_list
                ])
            
            system_prompt = f"""You are a patient, adaptive programming tutor.
            
Previous context about the student:
{memory_context if memory_context else 'No previous context'}

Provide a helpful, personalized response."""
            
            messages = [
                ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
                ChatMessage(role=MessageRole.USER, content=request)
            ]
            
            # Call Azure OpenAI LLM
            response = await self.llm.achat(messages)
            response_text = response.message.content
            
            # Extract token usage from response
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            
            if hasattr(response, 'raw') and response.raw:
                usage = getattr(response.raw, 'usage', None)
                if usage:
                    prompt_tokens = getattr(usage, 'prompt_tokens', 0)
                    completion_tokens = getattr(usage, 'completion_tokens', 0)
                    total_tokens = getattr(usage, 'total_tokens', 0)
            
            self.metrics.end_operation(llm_op_id, "llm_call", {
                "model": self.llm.model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            })
            
            logger.info(f"✓ Session completed: {topic}")
            logger.info(f"Response: {response_text}")
            
            return response_text
            
        except Exception as e:
            logger.error(f"✗ Session failed: {str(e)}")
            self.metrics.record_error(f"session_{topic}", str(e))
            raise
    
    async def get_learning_history(self) -> str:
        """Get a summary of what the student has learned."""
        search_op_id = f"history_search_{time.time()}"
        self.metrics.start_operation(search_op_id)
        
        try:
            # Get all memories for this student (no specific query, just filter)
            # Use a generic query vector
            dummy_embedding = [0.0] * 1536
            
            search_request = SearchRequest(
                vector=dummy_embedding,
                k=100,  # Get many results
                filter={"student_id": self.student_id},
                include_metadata=True
            )
            
            results = self.collection.search(search_request)
            results_list = results.results if hasattr(results, 'results') else results
            
            results_count = len(results_list)
            self.metrics.end_operation(search_op_id, "history_search", {
                "results_count": results_count,
                "memories_count": results_count
            })
            
            # Format history
            history_items = [r.metadata.get('memory_text', '') for r in results_list]
            history = "\\n".join([f"- {item}" for item in history_items if item])
            
            return history
            
        except Exception as e:
            self.metrics.record_error("learning_history", str(e))
            return "No learning history available"
    
    def save_metrics(self, filename: str = "sochdb_metrics.json"):
        """Save collected metrics to JSON file."""
        self.metrics.save_to_file(filename)
        logger.info(f"\\n✓ Metrics saved to: {filename}")
    
    def close(self):
        """Clean up resources."""
        if hasattr(self, 'db'):
            self.db.close()


async def run_learning_agent_with_metrics():
    """
    Run the SochDB-based learning agent with metrics collection.
    """
    # Create the learning system
    learning_system = SochDBMultiAgentLearningSystem(
        student_id="Alexander",
        db_path="./sochdb_learning"
    )
    
    # Define learning sessions (same as mem0 version)
    sessions = [
        {
            "topic": "Vision Language Models",
            "message": "I'm new to machine learning but have good hold on Python. I have 4 years of work experience."
        },
        {
            "topic": "Machine Learning",
            "message": "Can you summarize what I've covered so far?"
        }
    ]
    
    # Run each session
    for i, session in enumerate(sessions, 1):
        logger.info("\\n" + "=" * 80)
        logger.info(f"SESSION {i}: {session['topic']}")
        logger.info("=" * 80)
        
        response = await learning_system.start_learning_session(
            topic=session['topic'],
            student_message=session['message']
        )
    
    # Get learning history
    logger.info("\\n" + "=" * 80)
    logger.info("LEARNING HISTORY")
    logger.info("=" * 80)
    
    history = await learning_system.get_learning_history()
    logger.info(f"History: {history}")
    
    logger.info("\\n" + "=" * 80)
    logger.info("✓ All sessions completed successfully!")
    logger.info("=" * 80)
    
    # Save metrics
    learning_system.save_metrics()
    
    # Print summary
    stats = learning_system.metrics.get_statistics()
    logger.info("\\n" + "=" * 80)
    logger.info("METRICS SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total Duration: {stats['execution']['total_duration_seconds']:.1f} seconds")
    logger.info(f"Memory Operations: {stats['memory_operations']['total_count']}")
    logger.info(f"LLM Calls: {stats['llm_operations']['call_count']}")
    logger.info(f"Success Rate: {stats['reliability']['success_rate']:.1f}%")
    logger.info(f"Total Memories Retrieved: {stats['recall']['total_memories_retrieved']}")
    logger.info("=" * 80)
    
    # Clean up
    learning_system.close()


if __name__ == "__main__":
    asyncio.run(run_learning_agent_with_metrics())
