
import numpy as np
import random
import uuid
from typing import List, Dict, Tuple
from saas_simulation.config import TOPICS, VECTOR_DIM, LEXICAL_TRAPS

TOPIC_KEYWORDS = {
    "SSO": ["SAML 2.0", "Okta", "SCIM"],
    "SAML": ["SAML 2.0", "SSO", "Identity Provider"],
    "RBAC": ["Permissions", "Roles", "Groups"],
    "API rate limits": ["429 Too Many Requests", "Throttling"],
    "webhooks": ["Events", "Callbacks", "Signature Verification"],
    "known issues": ["Bug", "Workaround", "Fix"],
    "SCIM": ["Provisioning", "Deprovisioning", "Okta"],
    "Okta": ["SAML", "SSO", "SCIM"],
    "JWT": ["Token", "Bearer", "Claims"],
    "security": ["Vulnerability", "Patch", "CVE"],
    "GDPR": ["Privacy", "Data Deletion", "Compliance"],
    "compliance": ["SOC 2", "Audit", "GDPR"],
    "audit logs": ["Trace", "History", "Events"],
    "user management": ["Invite", "Delete", "Profile"],
    "integrations": ["Slack", "Discord", "Zapier"],
    "slack": ["Channel", "Bot", "Webhook"],
    "discord": ["Server", "Bot", "Webhook"],
    "email setup": ["SMTP", "DKIM", "SPF"],
    "notifications": ["Alerts", "Email", "Push"],
    "mobile app": ["iOS", "Android", "Push"],
    "desktop app": ["Windows", "MacOS", "Electron"],
    "API keys": ["Secret", "Rotation", "Scopes"],
    "authentication": ["Login", "MFA", "Password"],
    "authorization": ["RBAC", "Policies", "Access"],
    "roles": ["Admin", "Member", "Viewer"],
    "permissions": ["Read", "Write", "Execute"],
    "groups": ["Team", "Department", "Access"],
    "teams": ["Collaboration", "Sharing"],
    "workspaces": ["Tenant", "Isolation", "Settings"]
}

class TopicGenerator:
    def __init__(self):
        self.topic_centroids = {}
        # Ensure mapping covers all topics in config
        for topic in TOPICS:
             # Default fallback
             if topic not in TOPIC_KEYWORDS:
                 TOPIC_KEYWORDS[topic] = ["General", "Config", "Help"]
                 
        for topic in TOPICS:
            # Generate a random unit vector for each topic
            vec = np.random.randn(VECTOR_DIM)
            vec /= np.linalg.norm(vec)
            self.topic_centroids[topic] = vec



    def get_embedding(self, topic: str, noise_scale: float = 0.1) -> List[float]:
        """Generate an embedding near the topic centroid."""
        if topic not in self.topic_centroids:
            # Fallback for unknown topics or mixed concepts
            vec = np.random.randn(VECTOR_DIM)
            vec /= np.linalg.norm(vec)
            return vec.tolist()
        
        centroid = self.topic_centroids[topic]
        noise = np.random.randn(VECTOR_DIM) * noise_scale
        vec = centroid + noise
        vec /= np.linalg.norm(vec)
        return vec.tolist()

    def get_random_topic(self) -> str:
        return random.choice(TOPICS)

def generate_tenant_vocab(tenant_id: str) -> List[str]:
    """Generate some tenant-specific terms."""
    return [f"Project-{tenant_id}", f"Prod-{random.randint(100,999)}", "Internal-Portal"]

def generate_kb_dataset(topic_gen: TopicGenerator, num_docs: int, chunks_per_doc: int) -> List[Dict]:
    """
    Generates a list of document chunks.
    Each chunk has:
    - id
    - text (with lexical terms)
    - embedding (centroid + noise)
    - metadata (topic, product_area)
    """
    dataset = []
    
    for _ in range(num_docs):
        doc_topic = topic_gen.get_random_topic()
        doc_id = str(uuid.uuid4())
        
        for chunk_idx in range(chunks_per_doc):
            # Deterministic keyword injection based on topic
            text_content = f"Documentation regarding {doc_topic}. "
            
            # 80% chance to include specific keywords for this topic
            if random.random() < 0.8:
                keywords = TOPIC_KEYWORDS.get(doc_topic, ["General"])
                # Include ALL keywords to match any query for this topic
                text_content += f" Specifically covering {', '.join(keywords)}. "
            
            text_content += "This is important for system configuration."
            
            # Semantic embedding
            embedding = topic_gen.get_embedding(doc_topic, noise_scale=0.1)
            
            chunk = {
                "id": str(uuid.uuid4()),
                "doc_id": doc_id,
                "text": text_content,
                "vector": embedding,
                "metadata": {
                    "title": f"{doc_topic} Guide {chunk_idx}",
                    "topic": doc_topic,
                    "product_area": "SaaS Platform",
                    "chunk_index": chunk_idx
                }
            }
            dataset.append(chunk)
            
    return dataset

def generate_queries(topic_gen: TopicGenerator, num_queries: int) -> List[Dict]:
    """
    Generate queries with ground truth.
    Returns list of {query_text, query_vector, target_topic, is_exact_match}
    """
    queries = []
    for _ in range(num_queries):
        is_exact = random.random() < 0.5
        target_topic = topic_gen.get_random_topic()
        
        if is_exact:
            # Query heavily relies on keywords associated with the topic
            keywords = TOPIC_KEYWORDS.get(target_topic, ["General"])
            trap = random.choice(keywords)
            query_text = f"How do I fix {trap} in {target_topic}?"
            # Even for exact match queries, we have a semantic intent
            query_vec = topic_gen.get_embedding(target_topic, noise_scale=0.2)
        else:
            query_text = f"Tell me about best practices for {target_topic} configuration."
            query_vec = topic_gen.get_embedding(target_topic, noise_scale=0.15)
            
        queries.append({
            "text": query_text,
            "vector": query_vec,
            "target_topic": target_topic,
            "is_exact": is_exact
        })
    return queries

def generate_tickets(num_tickets: int) -> List[Dict]:
    """Generate historical tickets."""
    tickets = []
    for _ in range(num_tickets):
        ticket_id = str(uuid.uuid4())
        status = random.choice(["open", "closed", "pending"])
        tickets.append({
            "id": ticket_id,
            "title": f"Issue with {random.choice(TOPICS)}",
            "description": "User reported an error during configuration.",
            "status": status,
            "priority": random.choice(["low", "medium", "high"])
        })
    return tickets

def generate_chat_memories(topic_gen: TopicGenerator, num_users: int, memories_per_user: int) -> List[Dict]:
    """Generate chat memories for users."""
    memories = []
    for _ in range(num_users):
        user_id = str(uuid.uuid4())
        for _ in range(memories_per_user):
            topic = topic_gen.get_random_topic()
            embedding = topic_gen.get_embedding(topic, noise_scale=0.1)
            memories.append({
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "text": f"User prefers {topic} related updates.",
                "vector": embedding,
                "metadata": {
                    "topic": topic,
                    "type": "preference"
                }
            })
    return memories

if __name__ == "__main__":
    # Quick test
    tg = TopicGenerator()
    kb = generate_kb_dataset(tg, 5, 2)
    print(f"Generated {len(kb)} chunks")
    qs = generate_queries(tg, 3)
    print(f"Generated {len(qs)} queries")
    tix = generate_tickets(10)
    print(f"Generated {len(tix)} tickets")
    mems = generate_chat_memories(tg, 2, 5)
    print(f"Generated {len(mems)} memories")
