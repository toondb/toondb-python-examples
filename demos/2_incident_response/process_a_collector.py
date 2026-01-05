"""Process A: Metrics and events collector.

Simulates collecting metrics and deployment events, writing to shared ToonDB via IPC.
"""

import sys
import time
import random
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from toondb import IpcClient


def collect_metrics(client: IpcClient):
    """Simulate metrics collection and write to shared DB."""
    print("🔄 Process A: Metrics Collector")
    print("  Writing metrics to shared ToonDB via IPC...\n")
    
    iteration = 0
    
    while True:
        iteration += 1
        timestamp = datetime.now().isoformat()
        
        # Simulate metrics
        latency_p99 = random.randint(200, 1500) if iteration < 20 else random.randint(800, 3000)
        error_rate = round(random.uniform(0.1, 2.5), 2) if iteration < 20 else round(random.uniform(2.0, 8.0), 2)
        cpu_usage = round(random.uniform(30, 85), 1)
        
        # Write metrics to KV paths
        client.put(f"metrics/latency_p99/{timestamp}".encode(), str(latency_p99).encode())
        client.put(f"metrics/error_rate/{timestamp}".encode(), str(error_rate).encode())
        client.put(f"metrics/cpu_usage/{timestamp}".encode(), str(cpu_usage).encode())
        
        # Write latest metrics for quick access
        client.put(b"metrics/latest/latency_p99", str(latency_p99).encode())
        client.put(b"metrics/latest/error_rate", str(error_rate).encode())
        client.put(b"metrics/latest/cpu_usage", str(cpu_usage).encode())
        client.put(b"metrics/latest/timestamp", timestamp.encode())
        
        print(f"  [{timestamp}] Latency P99: {latency_p99}ms | Error Rate: {error_rate}% | CPU: {cpu_usage}%")
        
        # Simulate deployment event occasionally
        if iteration % 30 == 0:
            deploy_event = f"Deployment v1.{iteration // 30}.0 to production"
            client.put(f"events/deployments/{timestamp}".encode(), deploy_event.encode())
            print(f"  📦 {deploy_event}")
        
        # Simulate incident trigger
        if latency_p99 > 1000 and error_rate > 5.0:
            incident_key = b"incidents/current/severity"
            existing = client.get(incident_key)
            if not existing or existing == b"NONE":
                print(f"\n  🚨 HIGH LATENCY + HIGH ERROR RATE DETECTED!")
                print(f"     Triggering incident response...\n")
                client.put(b"incidents/current/severity", b"HIGH")
                client.put(b"incidents/current/trigger_time", timestamp.encode())
                client.put(b"incidents/current/latency", str(latency_p99).encode())
                client.put(b"incidents/current/error_rate", str(error_rate).encode())
        
        time.sleep(5)  # Collect metrics every 5 seconds


def main():
    """Run metrics collector."""
    socket_path = "./ops_db/toondb.sock"
    
    print("="*60)
    print("PROCESS A: METRICS COLLECTOR")
    print("="*60)
    print(f"Connecting to ToonDB IPC socket: {socket_path}\n")
    
    try:
        client = IpcClient.connect(socket_path)
        print("✅ Connected to shared ToonDB!\n")
        
        # Initialize metrics
        client.put(b"metrics/latest/latency_p99", b"0")
        client.put(b"metrics/latest/error_rate", b"0.0")
        client.put(b"metrics/latest/cpu_usage", b"0.0")
        client.put(b"incidents/current/severity", b"NONE")
        
        collect_metrics(client)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Metrics collector stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
