
import random
import uuid
import numpy as np
import time
from typing import List, Dict
from .config import NUM_EVENTS, START_TIME, ONE_DAY, STATES, ERROR_CODES, DEVICE_ID, VECTOR_DIM

class DataGenerator:
    def __init__(self):
        # Mock embeddings for error codes
        self.error_vectors = {}
        for code in ERROR_CODES:
            vec = np.random.randn(VECTOR_DIM)
            vec /= np.linalg.norm(vec)
            self.error_vectors[code] = vec

    def generate_telemetry(self) -> List[Dict]:
        """Generate high frequency KV logs."""
        print(f"Generating {NUM_EVENTS} telemetry events...")
        logs = []
        # Spread over 24 hours
        interval = ONE_DAY / NUM_EVENTS
        for i in range(NUM_EVENTS):
            ts = int(START_TIME + (i * interval))
            val = random.gauss(120, 5) # Voltage
            logs.append((ts, {
                "id": str(uuid.uuid4()),
                "ts": ts,
                "voltage": val,
                "temp": random.gauss(60, 10),
                "device": DEVICE_ID
            }))
        return logs

    def generate_states(self) -> List[Dict]:
        """Generate state transitions over time."""
        print("Generating state transitions...")
        transitions = []
        current_ts = START_TIME
        current_state = "IDLE"
        
        while current_ts < START_TIME + ONE_DAY:
            duration = random.randint(300, 3600) # 5 min to 1 hour
            next_ts = current_ts + duration
            if next_ts > START_TIME + ONE_DAY:
                next_ts = START_TIME + ONE_DAY
                
            transitions.append({
                "state": current_state,
                "start": int(current_ts),
                "end": int(next_ts)
            })
            
            # Pick next state
            if current_state == "RUNNING":
                current_state = random.choice(["IDLE", "ERROR"])
            elif current_state == "ERROR":
                current_state = "MAINTENANCE"
            elif current_state == "MAINTENANCE":
                current_state = "IDLE"
            else: # IDLE
                current_state = "RUNNING"
                
            current_ts = next_ts
            
        return transitions

    def generate_manuals(self) -> List[Dict]:
        """Generate manual chunks with error vectors."""
        print("Generating manual chunks...")
        chunks = []
        for code, meaning in ERROR_CODES.items():
            # Create a chunk for the exact code
            # Vector = code_vector
            chunks.append({
                "id": f"man_{code}",
                "text": f"Error {code}: {meaning} Action: Check cables.",
                "vector": self.error_vectors[code].tolist(),
                "metadata": {"type": "manual", "code": code}
            })
            
            # Create a paraphrase chunk
            # Vector = code_vector + noise
            noise = np.random.randn(VECTOR_DIM) * 0.1
            p_vec = self.error_vectors[code] + noise
            p_vec /= np.linalg.norm(p_vec)
            
            chunks.append({
                "id": f"man_{code}_para",
                "text": f"Troubleshooting {code}: If system overheats or fails voltage check...",
                "vector": p_vec.tolist(),
                "metadata": {"type": "guide", "code": code}
            })
        return chunks
