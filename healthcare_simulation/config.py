
import os

# Data Scale
NUM_GUIDELINES = 500 # Scaled down
CHUNKS_PER_DOC = 10
NUM_CHUNKS = NUM_GUIDELINES * CHUNKS_PER_DOC

# Constants
DB_PATH = "./sochdb_data_healthcare"
VECTOR_DIM = 1536

# Medical Terminology
ACRONYMS = {
    "COPD": "Chronic Obstructive Pulmonary Disease",
    "HTN": "Hypertension",
    "CKD": "Chronic Kidney Disease",
    "MI": "Myocardial Infarction",
    "CHF": "Congestive Heart Failure",
    "T2DM": "Type 2 Diabetes Mellitus"
}

# Queries to correct/expand
TEST_QUERIES = [
    {"q": "COPD exacerbation steroid dosing", "target": "COPD"},
    {"q": "HTN management in elderly", "target": "HTN"},
    {"q": "renal impairment dosing for metformin", "target": "CKD"}, # "renal" ~ "kidney"
]

# Cache Test
CACHE_PAIRS = [
    ("What is the dosing for amoxicillin?", "Amoxicillin dosing protocol?"),
    ("Contraindications for beta blockers", "When to avoid beta blockers?"),
]
