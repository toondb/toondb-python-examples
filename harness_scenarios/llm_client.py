"""
Real LLM Client for SochDB Test Harness

Uses Azure OpenAI for real embeddings and text generation.
No mocking - actual API calls with synthetic ground-truth for validation.
"""

import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AzureOpenAIClient:
    """Real Azure OpenAI client for embeddings and text generation."""
    
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
        self.embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
        
        if not self.api_key or not self.endpoint:
            raise ValueError(
                "Azure OpenAI credentials not found. "
                "Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in .env"
            )
        
        # Import here to avoid dependency if not using real LLM
        try:
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
        except ImportError:
            raise ImportError(
                "openai package not installed. "
                "Run: pip install openai"
            )
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get real embedding from Azure OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (1536-dim for text-embedding-3-small)
        """
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_deployment
        )
        return response.data[0].embedding
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts in one call.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        response = self.client.embeddings.create(
            input=texts,
            model=self.embedding_deployment
        )
        return [item.embedding for item in response.data]
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate text using Azure OpenAI chat completion.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_prompt: Optional system prompt
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    def generate_support_doc(self, topic_keywords: List[str], doc_type: str = "support") -> str:
        """
        Generate realistic support document using LLM.
        
        Args:
            topic_keywords: Keywords related to the document topic
            doc_type: Type of document (support, runbook, contract, log)
            
        Returns:
            Generated document text
        """
        templates = {
            "support": (
                "You are a technical support specialist. "
                "Write a brief support article (50-100 words) about troubleshooting issues with: "
                f"{', '.join(topic_keywords)}. "
                "Include common symptoms, diagnostic steps, and solutions."
            ),
            "runbook": (
                "You are a DevOps engineer. "
                "Write a runbook entry (50-100 words) for handling incidents related to: "
                f"{', '.join(topic_keywords)}. "
                "Include detection, diagnosis, and remediation steps."
            ),
            "contract": (
                "You are a legal contract specialist. "
                "Write a contract clause (50-100 words) regarding: "
                f"{', '.join(topic_keywords)}. "
                "Include obligations, terms, and conditions."
            ),
            "log": (
                "You are a system engineer. "
                "Write a log entry (30-50 words) about an issue with: "
                f"{', '.join(topic_keywords)}. "
                "Include severity, affected components, and error details."
            ),
        }
        
        prompt = templates.get(doc_type, templates["support"])
        return self.generate_text(prompt, max_tokens=150, temperature=0.7)
    
    def generate_query(self, topic_keywords: List[str], query_type: str = "support") -> str:
        """
        Generate realistic user query using LLM.
        
        Args:
            topic_keywords: Keywords the query should be about
            query_type: Type of query (support, runbook, contract)
            
        Returns:
            Generated query text
        """
        templates = {
            "support": (
                "Write a brief user question (10-20 words) asking how to fix or troubleshoot: "
                f"{', '.join(topic_keywords)}"
            ),
            "runbook": (
                "Write a brief incident description (10-20 words) about an issue with: "
                f"{', '.join(topic_keywords)}"
            ),
            "contract": (
                "Write a brief legal query (10-20 words) about contract terms regarding: "
                f"{', '.join(topic_keywords)}"
            ),
        }
        
        prompt = templates.get(query_type, templates["support"])
        return self.generate_text(prompt, max_tokens=50, temperature=0.7)
    
    def generate_paraphrases(self, original_text: str, num_paraphrases: int = 3) -> List[str]:
        """
        Generate paraphrases of a query for cache testing.
        
        Args:
            original_text: Original query text
            num_paraphrases: Number of paraphrases to generate
            
        Returns:
            List of paraphrased queries
        """
        prompt = (
            f"Generate {num_paraphrases} different ways to ask this same question. "
            f"Each should have the same meaning but different wording.\n\n"
            f"Original: {original_text}\n\n"
            f"Output only the {num_paraphrases} paraphrases, one per line, without numbering."
        )
        
        response = self.generate_text(prompt, max_tokens=200, temperature=0.8)
        
        # Parse paraphrases from response
        paraphrases = [line.strip() for line in response.split('\n') if line.strip()]
        return paraphrases[:num_paraphrases]


# Singleton instance
_llm_client = None


def get_llm_client() -> AzureOpenAIClient:
    """Get singleton LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = AzureOpenAIClient()
    return _llm_client


def get_embedding_dimension() -> int:
    """Get the embedding dimension for the configured model."""
    # text-embedding-3-small = 1536 dimensions
    # text-embedding-3-large = 3072 dimensions
    embedding_model = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
    
    if "small" in embedding_model.lower():
        return 1536
    elif "large" in embedding_model.lower():
        return 3072
    elif "ada" in embedding_model.lower():
        return 1536
    else:
        return 1536  # Default
