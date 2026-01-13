
import os

# Data Scale
NUM_DISPUTES = 1000 # Scaled down for interactive simulation (targeting concurrency mainly)
NUM_LEDGER_ENTRIES = 5000
NUM_CUSTOMERS = 200

# Constants
DB_PATH = "./sochdb_data_fintech"
VECTOR_DIM = 1536 # For policy doc embeddings

# Business Logic
DISPUTE_REASONS = ["fraud", "duplicate", "goods_not_received", "unrecognized"]
KYC_STATUSES = ["unverified", "pending", "verified", "flagged"]

# Policy Docs (Mock)
POLICY_DOCS = [
    {"id": "pol_1", "text": "Fraud claims under $50 are auto-approved if customer score > 80.", "vector": [0.1]*VECTOR_DIM},
    {"id": "pol_2", "text": "Requires manager approval for disputes > $1000.", "vector": [0.2]*VECTOR_DIM},
    {"id": "pol_3", "text": "Goods not received requires tracking number verification.", "vector": [0.3]*VECTOR_DIM},
]
