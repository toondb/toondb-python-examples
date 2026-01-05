"""LLM client wrapper for agent responses."""

import os
from typing import Optional, List, Dict, Any
import tiktoken
from openai import OpenAI


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text using tiktoken.
    
    Args:
        text: Text to count tokens for
        model: Model name for tokenizer selection
        
    Returns:
        Number of tokens
    """
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


class LLMClient:
    """OpenAI client wrapper with token counting and error handling."""
    
    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None
    ):
        """Initialize LLM client.
        
        Args:
            model: OpenAI model name
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    def complete(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate completion for prompt.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            
        Returns:
            Generated text response
        """
        messages: List[Dict[str, str]] = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens
        )
        
        return response.choices[0].message.content or ""
    
    def count_prompt_tokens(self, prompt: str, system_message: Optional[str] = None) -> int:
        """Count tokens in a prompt.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            
        Returns:
            Total token count
        """
        total = count_tokens(prompt, self.model)
        if system_message:
            total += count_tokens(system_message, self.model)
        return total
