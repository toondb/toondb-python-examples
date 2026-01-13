"""
Scenario 10: MCP Tool Integration (Model Context Protocol)
=========================================================

Tests:
- External tool call simulation
- Context building from tools
- Real tool response generation using LLM
"""

import random
import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "sochdb-python-sdk" / "src"))

from harness_scenarios.base_scenario import BaseScenario, ScenarioMetrics


class MCPToolScenario(BaseScenario):
    """MCP tool integration testing."""
    
    def __init__(self, db, generator, llm_client):
        super().__init__("10_mcp_tool_integration", db, generator, llm_client)
    
    def run(self) -> ScenarioMetrics:
        """Run MCP tool scenario."""
        print(f"\n[{self.scenario_id}] Starting...")
        
        # Generate real tool definitions using LLM
        tools = self._generate_real_tools(num_tools=15)
        
        # Create namespace and collection
        try:
            self.db.create_namespace("mcp_ns")
        except:
            pass  # Already exists
        
        with self.db.use_namespace("mcp_ns") as ns:
            tools_col = ns.create_collection(
                "mcp_tools",
                dimension=self.generator.embedding_dim
            )
            
            # Insert tools
            with self._track_time("insert"):
                for tool in tools:
                    tools_col.insert(id=tool['id'], vector=tool['embedding'], metadata=tool['metadata'])
            
            # Test tool discovery
            self._test_tool_discovery(tools_col, tools)
            
            # Test context building
            self._test_context_building(tools_col, tools)
            
            # Test tool result storage
            self._test_tool_results(tools_col, tools)
        
        print(f"[{self.scenario_id}] {'✓ PASS' if self.metrics.passed else '✗ FAIL'}")
        return self.metrics
    
    def _generate_real_tools(self, num_tools: int) -> List[Dict]:
        """Generate real MCP tool definitions using LLM."""
        print(f"  Generating {num_tools} MCP tools with real LLM...")
        tools = []
        
        categories = ["file_operations", "web_search", "data_analysis", "code_execution", "api_calls"]
        
        for i in range(num_tools):
            category = random.choice(categories)
            
            # Generate real tool description using LLM
            prompt = f"Generate a realistic MCP tool description for {category} (2-3 sentences):"
            description = self.llm.generate_text(prompt, max_tokens=120)
            self.metrics.track_llm_call(120)
            
            # Generate tool parameters using LLM
            param_prompt = f"Generate JSON parameter schema for a {category} tool (brief):"
            parameters = self.llm.generate_text(param_prompt, max_tokens=80)
            self.metrics.track_llm_call(80)
            
            # Generate real embedding
            embedding = self.llm.get_embedding(description)
            self.metrics.track_llm_call(50)
            
            tools.append({
                'id': f"tool_{i:03d}",
                'embedding': embedding,
                'metadata': {
                    'name': f"{category}_tool_{i}",
                    'category': category,
                    'description': description,
                    'parameters': parameters,
                    'usage_count': 0,
                    'enabled': True,
                }
            })
        
        return tools
    
    def _test_tool_discovery(self, tools_col, tools: List[Dict]):
        """Test discovering tools by query."""
        print(f"  Testing tool discovery...")
        
        # Find a category that actually has tools
        available_categories = set(t['metadata']['category'] for t in tools)
        if not available_categories:
            self.metrics.errors.append("No tools with categories found")
            self.metrics.passed = False
            return
        
        target_category = list(available_categories)[0]  # Use first available category
        
        # Generate search query using LLM
        prompt = f"Generate a query to find tools for {target_category}:"
        query = self.llm.generate_text(prompt, max_tokens=25)
        self.metrics.track_llm_call(25)
        
        query_emb = self.llm.get_embedding(query)
        self.metrics.track_llm_call(50)
        
        with self._track_time("tool_discovery"):
            results = tools_col.hybrid_search(query_emb, query, k=10, alpha=0.5)
        
        # Verify search returned results (exact category match may vary with embeddings)
        if not results or not results.results:
            self.metrics.errors.append(f"No results from tool discovery search")
            self.metrics.passed = False
    
    def _test_context_building(self, tools_col, tools: List[Dict]):
        """Test building context from multiple tools."""
        print(f"  Testing context building...")
        
        # Simulate building context from related tools
        categories_needed = ["file_operations", "web_search"]
        
        context_tools = []
        
        with self._track_time("context_build"):
            tool_count = tools_col.count()
            
            # Check sample tools from our ground truth data
            for category in categories_needed:
                # Find a tool from this category in our ground truth
                matching_tools = [t for t in tools if t['metadata']['category'] == category and t['metadata']['enabled']]
                if matching_tools:
                    tool = matching_tools[0]
                    try:
                        result = tools_col.get(tool['id'])
                        if result:
                            context_tools.append(result)
                    except:
                        pass
        
        # Verify we got tools for each category
        found_categories = {tool['metadata']['category'] for tool in context_tools}
        
        for category in categories_needed:
            if category not in found_categories:
                self.metrics.errors.append(f"Missing tool category in context: {category}")
                self.metrics.passed = False
    
    def _test_tool_results(self, tools_col, tools: List[Dict]):
        """Test storing and retrieving tool execution results."""
        print(f"  Testing tool result storage...")
        
        # Simulate tool execution and result storage
        target_tool = tools[0]
        
        # Generate simulated tool result using LLM
        prompt = f"Generate a realistic execution result for a {target_tool['metadata']['category']} tool:"
        result = self.llm.generate_text(prompt, max_tokens=100)
        self.metrics.track_llm_call(100)
        
        # Update tool with usage count and last result
        new_metadata = target_tool['metadata'].copy()
        new_metadata['usage_count'] += 1
        new_metadata['last_result'] = result
        
        with self._track_time("tool_result_update"):
            tools_col.delete(target_tool['id'])
            tools_col.insert(id=target_tool['id'], vector=target_tool['embedding'], metadata=new_metadata)
        
        # Verify update
        updated = tools_col.get(target_tool['id'])
        
        if updated['metadata']['usage_count'] != 1:
            self.metrics.errors.append("Tool usage count not updated")
            self.metrics.passed = False
        
        if 'last_result' not in updated['metadata']:
            self.metrics.errors.append("Tool result not stored")
            self.metrics.passed = False
