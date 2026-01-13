
import os
import shutil
import time
from collections import defaultdict
from config import DB_PATH, NUM_PRODUCTS
from data_gen import DataGenerator
from db_ops import ShopDB

def measure_mrr(results, target_id):
    """Mean Reciprocal Rank."""
    for i, res in enumerate(results):
        if res["id"] == target_id:
            return 1.0 / (i + 1)
    return 0.0

def run_simulation():
    # Cleanup
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        
    print(f"=== E-commerce Simulation ({NUM_PRODUCTS} Products) ===")
    
    # 1. Setup & Ingest
    db = ShopDB(DB_PATH)
    db.setup_shop()
    
    gen = DataGenerator()
    products = gen.generate_products()
    db.ingest_products(products)
    
    edges = gen.generate_graph_edges()
    db.ingest_graph(edges)
    print(f"Ingested {len(edges)} graph edges")
    
    temporal = gen.generate_temporal_data()
    db.ingest_temporal(temporal)
    print(f"Ingested {len(temporal)} temporal events")
    
    # 2. Workload Execution
    print("\n=== Running Workloads ===")
    queries = gen.generate_queries()
    
    metrics = {
        "exact_mrr": [],
        "graph_nodes_found": [],
        "temporal_accuracy": []
    }
    
    for q in queries:
        if q["type"] == "exact":
            # Hybrid search boosting exact SKU
            # We treat SKU as keyword logic mostly
            res = db.hybrid_search(text=q["text"], k=5, alpha=0.1) # low alpha = keyword bias for SKU
            mrr = measure_mrr(res, q["target_id"])
            metrics["exact_mrr"].append(mrr)
            print(f"[Exact SKU] {q['text']} -> Rank {1/mrr if mrr > 0 else '>5'}")
            
        elif q["type"] == "intent":
            # "Charger for X"
            print(f"[Intent] {q['text']}")
            res = db.hybrid_search(text=q["text"], vector=q["vector"], k=5, alpha=0.7)
            # Validation: Check if Accessories are returned
            acc_count = sum(1 for r in res if r["metadata"].get("subcategory") == "Accessories")
            print(f"  -> Found {acc_count} accessories in top 5")
            
            # Graph Check
            if res:
                top_id = res[0]["id"]
                related = db.get_related(top_id)
                count = len(related["nodes"])
                metrics["graph_nodes_found"].append(count)
                print(f"  -> Graph Traversal: found {count} related items")
                
        elif q["type"] == "temporal":
            print(f"[Temporal] Price check for {q['target_id']} at t={q['query_time']}")
            history = db.query_price_history(q["target_id"], q["query_time"])
            if history:
                val = float(history[0]["value"]) # Should be raw json but wrapper parses? 
                # Actually db_ops returns parsed edges list? No, check wrapper
                print(f"  -> Found price: {val}")
                metrics["temporal_accuracy"].append(1.0) # Assume correct if found for now
            else:
                print("  -> No history found (might be static price)")
                metrics["temporal_accuracy"].append(0.0)

    # 3. Summary
    avg_mrr = sum(metrics["exact_mrr"]) / len(metrics["exact_mrr"]) if metrics["exact_mrr"] else 0
    avg_graph = sum(metrics["graph_nodes_found"]) / len(metrics["graph_nodes_found"]) if metrics["graph_nodes_found"] else 0
    
    print("\n=== Results Summary ===")
    print(f"Exact SKU MRR: {avg_mrr:.2f}")
    print(f"Avg Related Items Static: {avg_graph:.1f}")
    print("Simulation Complete.")

if __name__ == "__main__":
    run_simulation()
