import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class SochDBConfig:
    db_path: str = os.getenv("TOONDB_PATH", "./sochdb_langgraph_data")
    
@dataclass
class AzureConfig:
    api_key: str = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    embedding_deployment: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")

def get_sochdb_config() -> SochDBConfig:
    return SochDBConfig()

def get_azure_config() -> AzureConfig:
    return AzureConfig()
