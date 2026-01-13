"""
Instrumented Runner for llama_index.py Example with Metrics Collection
Runs the Multi-Agent Learning System and collects comprehensive metrics
"""

import asyncio
import logging
import time
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from metrics_collector import MetricsCollector
from azure_llm_config import configure_llama_index_azure, load_azure_config

# LlamaIndex imports
from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.azure_openai import AzureOpenAI

# Memory integration
from llama_index.memory.mem0 import Mem0Memory

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("learning_system_metrics.log")],
)
logger = logging.getLogger(__name__)


class InstrumentedMultiAgentLearningSystem:
    """
    Multi-Agent Architecture with Metrics Collection:
    - TutorAgent: Main teaching and explanations
    - PracticeAgent: Exercises and skill reinforcement
    - Shared Memory: Both agents learn from student interactions
    - MetricsCollector: Tracks all operations and performance
    """

    def __init__(self, student_id: str, metrics_collector: MetricsCollector):
        self.student_id = student_id
        self.metrics = metrics_collector
        
        # Configure Azure OpenAI
        logger.info("Configuring Azure OpenAI...")
        config = load_azure_config()
        
        # Create Azure OpenAI LLM
        self.llm = AzureOpenAI(
            model=config['chat_deployment'],
            deployment_name=config['chat_deployment'],
            api_key=config['api_key'],
            azure_endpoint=config['endpoint'],
            api_version=config['api_version'],
            temperature=0.2,
        )
        logger.info(f"✓ Azure OpenAI LLM configured: {config['chat_deployment']}")

        # Memory context for this student
        self.memory_context = {"user_id": student_id, "app": "learning_assistant"}
        
        # Initialize Mem0 memory with explicit Azure OpenAI configuration
        logger.info("Initializing Mem0 memory with explicit Azure OpenAI config...")
        
        # Import Memory class
        from mem0 import Memory
        
        op_id = f"mem0_init_{time.time()}"
        self.metrics.start_operation(op_id)
        try:
            # Explicit Azure OpenAI configuration for both LLM and embedder
            # Based on https://docs.mem0.ai/components/embedders/models/azure_openai
            mem0_config = {
                "llm": {
                    "provider": "azure_openai",
                    "config": {
                        "model": config['chat_deployment'],
                        "temperature": 0.1,
                        "max_tokens": 2000,
                        "azure_kwargs": {
                            "api_version": config['api_version'],
                            "azure_deployment": config['chat_deployment'],
                            "azure_endpoint": config['endpoint'],
                            "api_key": config['api_key'],
                        }
                    }
                },
                "embedder": {
                    "provider": "azure_openai",
                    "config": {
                        "model": config['embedding_deployment'],
                        "azure_kwargs": {
                            "api_version": config['api_version'],
                            "azure_deployment": config['embedding_deployment'],
                            "azure_endpoint": config['endpoint'],
                            "api_key": config['api_key'],
                        }
                    }
                }
            }
            
            # Initialize self-hosted Mem0 with explicit Azure config
            self.memory_instance = Memory.from_config(mem0_config)
            
            self.metrics.end_operation(op_id, "memory_init", {
                "student_id": student_id,
                "type": "self-hosted",
                "llm_provider": "azure_openai",
                "embedder_provider": "azure_openai"
            })
            logger.info("✓ Mem0 memory initialized with Azure OpenAI")
        except Exception as e:
            logger.error(f"Memory initialization error: {e}")
            self.metrics.record_error("memory_init", str(e))
            raise

        self._setup_agents()

    def _setup_agents(self):
        """Setup note: Using direct Mem0 operations for better metrics tracking"""
        # Agent workflow removed for metrics-focused implementation
        # We're using direct LLM and Mem0 calls to accurately track all operations
        pass

    async def start_learning_session(self, topic: str, student_message: str = "") -> str:
        """
        Start a learning session with memory tracking
        """
        op_id = f"session_{time.time()}"
        self.metrics.start_operation(op_id)

        try:
            if student_message:
                request = f"I want to learn about {topic}. {student_message}"
            else:
                request = f"I want to learn about {topic}."

            logger.info(f"Starting learning session: {topic}")
            
            # Add conversation to memory
            add_op_id = f"mem_add_{time.time()}"
            self.metrics.start_operation(add_op_id)
            
            conversation = [
                {"role": "user", "content": request}
            ]
            
            # Use Mem0 directly to add memory
            add_result = self.memory_instance.add(conversation, user_id=self.student_id)
            self.metrics.end_operation(add_op_id, "memory_add", {
                "memories_added": len(add_result.get('results', [])) if isinstance(add_result, dict) else 0
            })
            
            # Search for relevant memories
            search_op_id = f"mem_search_{time.time()}"
            self.metrics.start_operation(search_op_id)
            
            search_results = self.memory_instance.search(query=request, user_id=self.student_id, limit=5)
            memories_found = len(search_results.get('results', [])) if isinstance(search_results, dict) else 0
            
            self.metrics.end_operation(search_op_id, "memory_search", {
                "query": topic,
                "memories_count": memories_found,
            })
            
            # Generate LLM response using Azure OpenAI
            llm_op_id = f"llm_{time.time()}"
            self.metrics.start_operation(llm_op_id)
            
            # Build context from memories
            memory_context = ""
            if search_results and 'results' in search_results:
                memory_context = "\\n".join([f"- {m.get('memory', '')}" for m in search_results['results']])
            
            system_prompt = f"""You are a patient, adaptive programming tutor.
            
Previous context about the student:
{memory_context if memory_context else 'No previous context'}

Provide a helpful, personalized response."""
            
            # Import ChatMessage for proper message formatting
            from llama_index.core.base.llms.types import ChatMessage, MessageRole
            
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
                "total_tokens": total_tokens,
            })
            
            # Add assistant response to memory
            add_resp_op_id = f"mem_add_resp_{time.time()}"
            self.metrics.start_operation(add_resp_op_id)
            
            conversation.append({"role": "assistant", "content": response_text})
            add_result2 = self.memory_instance.add(conversation, user_id=self.student_id)
            
            self.metrics.end_operation(add_resp_op_id, "memory_add", {
                "memories_added": len(add_result2.get('results', [])) if isinstance(add_result2, dict) else 0
            })
            
            self.metrics.end_operation(op_id, "learning_session", {"topic": topic})
            logger.info(f"✓ Session completed: {topic}")
            
            return response_text
            
        except Exception as e:
            self.metrics.record_error("learning_session", str(e), {"topic": topic})
            logger.error(f"✗ Session failed: {e}")
            raise

    async def get_learning_history(self) -> str:
        """Show what the system remembers about this student"""
        op_id = f"history_{time.time()}"
        self.metrics.start_operation(op_id)
        
        try:
            # Search memory for learning patterns
            search_op_id = f"search_{time.time()}"
            self.metrics.start_operation(search_op_id)
            
            search_results = self.memory_instance.search(
                query="learning machine learning",
                user_id=self.student_id,
                limit=10
            )
            
            memories_count = len(search_results.get('results', [])) if isinstance(search_results, dict) else 0
            self.metrics.end_operation(search_op_id, "memory_search", {
                "query": "learning machine learning",
                "memories_count": memories_count,
            })

            if memories_count > 0:
                history = "\\n".join(f"- {m.get('memory', '')}" for m in search_results['results'])
                result = history
            else:
                result = "No learning history found yet. Let's start building your profile!"
            
            self.metrics.end_operation(op_id, "get_history", {"memories_count": memories_count})
            return result

        except Exception as e:
            self.metrics.record_error("get_history", str(e))
            return f"Memory retrieval error: {str(e)}"


async def run_learning_agent_with_metrics():
    """Run the learning agent with comprehensive metrics collection"""
    
    with MetricsCollector("llama_index_multi_agent_learning") as metrics:
        logger.info("=" * 80)
        logger.info("Multi-agent Learning System powered by LlamaIndex and Mem0")
        logger.info("Running with metrics collection...")
        logger.info("=" * 80)
        
        try:
            learning_system = InstrumentedMultiAgentLearningSystem(
                student_id="Alexander",
                metrics_collector=metrics
            )

            # First session
            logger.info("\\n" + "=" * 80)
            logger.info("SESSION 1: Vision Language Models")
            logger.info("=" * 80)
            response = await learning_system.start_learning_session(
                "Vision Language Models",
                "I'm new to machine learning but I have good hold on Python and have 4 years of work experience.",
            )
            logger.info(f"Response: {response}")

            # Second session - multi-agent memory will remember the first
            logger.info("\\n" + "=" * 80)
            logger.info("SESSION 2: Machine Learning Recap")
            logger.info("=" * 80)
            response2 = await learning_system.start_learning_session(
                "Machine Learning",
                "what all did I cover so far?"
            )
            logger.info(f"Response: {response2}")

            # Show what the multi-agent system remembers
            logger.info("\\n" + "=" * 80)
            logger.info("LEARNING HISTORY")
            logger.info("=" * 80)
            history = await learning_system.get_learning_history()
            logger.info(f"History: {history}")
            
            logger.info("\\n" + "=" * 80)
            logger.info("✓ All sessions completed successfully!")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"✗ Error running learning agent: {e}")
            metrics.record_error("main_execution", str(e))
            raise
        
        # Metrics are automatically finalized when exiting context manager
        
        # Save metrics to JSON
        metrics_file = "llama_index_metrics.json"
        metrics.save_to_file(metrics_file)
        logger.info(f"\\n✓ Metrics saved to: {metrics_file}")
        
        # Print summary
        stats = metrics.get_statistics()
        logger.info("\\n" + "=" * 80)
        logger.info("METRICS SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Duration: {stats['execution']['total_duration_seconds']} seconds")
        logger.info(f"Memory Operations: {stats['memory_operations']['total_count']}")
        logger.info(f"LLM Calls: {stats['llm_operations']['call_count']}")
        logger.info(f"Success Rate: {stats['reliability']['success_rate']}%")
        logger.info(f"Total Memories Retrieved: {stats['recall']['total_memories_retrieved']}")
        logger.info("=" * 80)
        
        return stats


if __name__ == "__main__":
    """Run the instrumented example"""
    asyncio.run(run_learning_agent_with_metrics())
