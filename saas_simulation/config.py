
import os
from dotenv import load_dotenv

load_dotenv()

# Simulation Parameters
NUM_TENANTS = 50
DOCS_PER_TENANT = 1000  # As per requirements
CHUNKS_PER_DOC = 10    # As per requirements
TOTAL_CHUNKS_PER_TENANT = DOCS_PER_TENANT * CHUNKS_PER_DOC

TICKETS_PER_TENANT = 5000
MEMORIES_PER_USER = 50
USERS_PER_TENANT = 500

# Vector Dimension (Simulated)
VECTOR_DIM = 1536 

# SochDB Config
DB_PATH = "./sochdb_data_saas_sim"

# Topics for Synthetic Data
TOPICS = [
    "onboarding", "billing", "SSO", "SAML", "RBAC", 
    "API rate limits", "webhooks", "known issues", 
    "SCIM", "Okta", "JWT", "security", "GDPR", 
    "compliance", "audit logs", "user management",
    "integrations", "slack", "discord", "email setup",
    "notifications", "webhooks", "mobile app", "desktop app",
    "API keys", "authentication", "authorization", "roles",
    "permissions", "groups", "teams", "workspaces"
]

# Lexical Traps (Exact terms)
LEXICAL_TRAPS = [
    "SCIM", "Okta", "SAML 2.0", "SOC 2 Type II", 
    "JWT", "X-Request-ID", "409 Conflict", "500 Internal Server Error"
]

# Evaluation Config
RECALL_K = 5
PRECISION_K = 5
NDCG_K = 10
ALPHA_VALUES = [0.2, 0.5, 0.8] # Vector weight
