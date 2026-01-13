"""Process C: Incident commander agent.

Monitors metrics, retrieves runbooks via hybrid search, and manages incident state.
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from sochdb import IpcClient, ContextQuery, DeduplicationStrategy
from shared.llm_client import LLMClient
from shared.embeddings import EmbeddingClient


class IncidentCommander:
    """Incident commander agent with hybrid retrieval and state management."""
    
    def __init__(self, socket_path: str):
        """Initialize commander."""
        self.socket_path = socket_path
        self.client = IpcClient.connect(socket_path)
        self.llm = LLMClient(model="gpt-4-turbo-preview")
        self.embedding_client = EmbeddingClient()
        self.incident_state = "NONE"
    
    def monitor_loop(self):
        """Monitor metrics and respond to incidents."""
        print("👀 Monitoring metrics for incidents...\n")
        
        while True:
            # Check for active incidents
            severity = self.client.get(b"incidents/current/severity")
            
            if severity and severity.decode() != "NONE" and self.incident_state == "NONE":
                print("\n" + "🚨" * 30)
                print("INCIDENT DETECTED!")
                print("🚨" * 30 + "\n")
                
                self.handle_incident()
            
            # Status update
            if self.incident_state == "NONE":
                latency = self.client.get(b"metrics/latest/latency_p99")
                error_rate = self.client.get(b"metrics/latest/error_rate")
                if latency and error_rate:
                    print(f"  [OK] Latency: {latency.decode()}ms | Error Rate: {error_rate.decode()}%", end="\r")
            
            time.sleep(3)
    
    def handle_incident(self):
        """Handle detected incident."""
        # Get incident details
        latency = self.client.get(b"incidents/current/latency")
        error_rate = self.client.get(b"incidents/current/error_rate")
        trigger_time = self.client.get(b"incidents/current/trigger_time")
        
        latency_val = latency.decode() if latency else "unknown"
        error_rate_val = error_rate.decode() if error_rate else "unknown"
        trigger_time_val = trigger_time.decode() if trigger_time else datetime.now().isoformat()
        
        print(f"📊 Incident Details:")
        print(f"   Latency P99: {latency_val}ms")
        print(f"   Error Rate: {error_rate_val}%")
        print(f"   Triggered: {trigger_time_val}")
        
        # Update state to OPEN
        self._update_incident_state("OPEN", "Incident detected, analyzing...")
        
        # Retrieve relevant runbooks
        print(f"\n🔍 Retrieving relevant runbooks (hybrid search)...")
        
        query = f"latency spike high error rate {latency_val}ms {error_rate_val}%"
        query_embedding = self.embedding_client.embed(query)
        
        ns = self.client.namespace("incident_ops")
        collection = ns.collection("runbooks")
        
        # Hybrid search with RRF
        ctx = (
            ContextQuery(collection)
            .add_vector_query(query_embedding, weight=0.6)
            .add_keyword_query("latency spike deployment rollback database", weight=0.4)
            .with_token_budget(2000)
            .with_deduplication(DeduplicationStrategy.SEMANTIC)
            .execute()
        )
        
        print(f"   Retrieved {len(ctx.documents)} runbook chunks")
        print(f"   Token budget used: ~{ctx.total_tokens} tokens")
        
        # Generate mitigation plan
        print(f"\n💡 Generating mitigation plan...")
        
        system_message = """You are an incident commander. Analyze the metrics and runbook guidance.
Suggest concrete mitigation actions in priority order. Be specific and actionable."""
        
        prompt = f"""Incident Details:
- Latency P99: {latency_val}ms (threshold: 1000ms)
- Error Rate: {error_rate_val}% (threshold: 5%)
- Time: {trigger_time_val}

Relevant Runbooks:
{ctx.as_markdown()}

Provide:
1. Most likely root cause
2. Immediate mitigation actions (priority order)
3. Next steps after mitigation
"""
        
        response = self.llm.complete(prompt, system_message=system_message)
        
        print(f"\n{'='*60}")
        print("MITIGATION PLAN")
        print('='*60)
        print(response)
        print('='*60)
        
        # Update state to MITIGATING
        self._update_incident_state("MITIGATING", response[:200])
        
        # Simulate mitigation actions
        print(f"\n⚡ Executing mitigation actions...")
        time.sleep(3)
        
        # Check if resolved
        print(f"\n🔬 Checking metrics...")
        time.sleep(2)
        
        # Simulate resolution
        self._update_incident_state("RESOLVED", "Metrics returned to normal")
        
        # Reset incident
        self.client.put(b"incidents/current/severity", b"NONE")
        
        print(f"\n✅ Incident resolved!\n")
        print(f"{'='*60}\n")
    
    def _update_incident_state(self, state: str, details: str):
        """Update incident state with ACID transaction."""
        timestamp = datetime.now().isoformat()
        
        print(f"\n📝 State transition: {self.incident_state} → {state}")
        
        # Store state transition (in real system, would use SQL transaction)
        self.client.put(b"incidents/current/state", state.encode())
        self.client.put(b"incidents/current/last_update", timestamp.encode())
        self.client.put(f"incidents/history/{timestamp}".encode(), 
                       f"{state}: {details}".encode())
        
        self.incident_state = state


def main():
    """Run incident commander."""
    socket_path = "./ops_db/sochdb.sock"
    
    print("="*60)
    print("PROCESS C: INCIDENT COMMANDER")
    print("="*60)
    print(f"Connecting to SochDB IPC socket: {socket_path}\n")
    
    try:
        commander = IncidentCommander(socket_path)
        print("✅ Connected to shared SochDB!\n")
        
        commander.monitor_loop()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Incident commander stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
