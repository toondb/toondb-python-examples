"""
SochDB RAG System - Package Init
"""
from rag import SochDBRAG, create_rag
from documents import Document, Chunk, DocumentLoader
from vector_store import SochDBVectorStore, SearchResult
from embeddings import AzureEmbeddings, get_embeddings
from generation import RAGResponse, AzureLLMGenerator
from config import get_azure_config, get_sochdb_config, get_rag_config

__version__ = "0.1.0"
__all__ = [
    "SochDBRAG",
    "create_rag",
    "Document",
    "Chunk",
    "DocumentLoader",
    "SochDBVectorStore",
    "SearchResult",
    "AzureEmbeddings",
    "get_embeddings",
    "RAGResponse",
    "AzureLLMGenerator",
    "get_azure_config",
    "get_sochdb_config",
    "get_rag_config"
]
