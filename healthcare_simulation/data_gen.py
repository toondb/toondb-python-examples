
import random
import uuid
import numpy as np
from typing import List, Dict
from .config import ACRONYMS, NUM_GUIDELINES, CHUNKS_PER_DOC, VECTOR_DIM

class DataGenerator:
    def __init__(self):
        # Create a mock vector for each acronym to simulate semantic clusters
        self.acronym_vectors = {}
        for acr in ACRONYMS:
            vec = np.random.randn(VECTOR_DIM)
            vec /= np.linalg.norm(vec)
            self.acronym_vectors[acr] = vec

    def generate_guidelines(self) -> List[Dict]:
        print(f"Generating {NUM_GUIDELINES * CHUNKS_PER_DOC} guideline chunks...")
        chunks = []
        
        for i in range(NUM_GUIDELINES):
            doc_id = f"doc_{i}"
            # Pick a primary topic
            topic_acr = random.choice(list(ACRONYMS.keys()))
            topic_full = ACRONYMS[topic_acr]
            
            base_vec = self.acronym_vectors[topic_acr]
            
            for c in range(CHUNKS_PER_DOC):
                chunk_id = f"{doc_id}_c{c}"
                
                # Mix of full term and acronym
                text = f"Guideline {doc_id} (v{random.randint(1,3)}): "
                if random.random() < 0.5:
                    text += f"Management of {topic_full} includes... "
                else:
                     text += f"Protocol for {topic_acr} patients... "
                
                text += "titration of meds. monitor renal function."
                
                # Vector = Base + Noise
                noise = np.random.randn(VECTOR_DIM) * 0.1
                vec = base_vec + noise
                vec /= np.linalg.norm(vec)
                
                chunks.append({
                    "id": chunk_id,
                    "text": text,
                    "vector": vec.tolist(),
                    "metadata": {
                        "topic": topic_acr,
                        "doc_id": doc_id,
                        "chunk_idx": c
                    }
                })
                
        return chunks
