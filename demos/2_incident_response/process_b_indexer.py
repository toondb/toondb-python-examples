"""Process B: Runbook indexer.

Indexes runbook documents into vector collection via IPC.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from toondb import IpcClient
from shared.embeddings import EmbeddingClient


def index_runbooks(client: IpcClient):
    """Index runbook documents into vector collection."""
    print("📚 Indexing runbooks into vector collection...\n")
    
    embedding_client = EmbeddingClient()
    dimension = embedding_client.dimension
    
    # Get or create namespace
    ns = client.namespace("incident_ops")
    
    # Create collection for runbooks
    try:
        collection = ns.create_collection("runbooks", dimension=dimension)
        print(f"  ✓ Created 'runbooks' collection (dimension={dimension})")
    except Exception as e:
        # Collection might already exist
        collection = ns.collection("runbooks")
        print(f"  ✓ Using existing 'runbooks' collection")
    
    # Index runbook files
    runbooks_dir = Path(__file__).parent / "runbooks"
    
    for runbook_file in sorted(runbooks_dir.glob("*.txt")):
        print(f"\n  Indexing: {runbook_file.name}")
        
        with open(runbook_file, "r") as f:
            content = f.read()
        
        # Split into chunks (by section)
        chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
        
        for i, chunk in enumerate(chunks):
            if len(chunk) < 50:  # Skip very short chunks
                continue
            
            # Generate embedding
            embedding = embedding_client.embed(chunk)
            
            doc_id = f"{runbook_file.stem}_chunk_{i}"
            metadata = {
                "source": runbook_file.name,
                "type": "runbook",
                "chunk_index": i
            }
            
            # Add to collection
            collection.add_document(
                id=doc_id,
                embedding=embedding,
                text=chunk,
                metadata=metadata
            )
            
            print(f"    ✓ Indexed chunk {i+1}: {chunk[:60]}...")
    
    print(f"\n✅ Runbook indexing complete!")
    return collection


def main():
    """Run runbook indexer."""
    socket_path = "./ops_db/toondb.sock"
    
    print("="*60)
    print("PROCESS B: RUNBOOK INDEXER")
    print("="*60)
    print(f"Connecting to ToonDB IPC socket: {socket_path}\n")
    
    try:
        client = IpcClient.connect(socket_path)
        print("✅ Connected to shared ToonDB!\n")
        
        # Index runbooks
        index_runbooks(client)
        
        # Keep process running to maintain connection
        print("\n👀 Watching for runbook updates (Ctrl+C to stop)...\n")
        while True:
            time.sleep(60)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Runbook indexer stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
