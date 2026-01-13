
from sochdb import Database
import os

DB_PATH = "./test_crash_db"
if os.path.exists(DB_PATH):
    import shutil
    shutil.rmtree(DB_PATH)

print("Opening DB...")
db = Database.open(DB_PATH)

print("Add Node...")
db.add_node("test", "A", "person", {})
db.add_node("test", "B", "person", {})

print("Add Edge...")
db.add_edge("test", "A", "knows", "B", {})

print("Traverse...")
nodes, edges = db.traverse("test", "A")
print(f"Nodes: {len(nodes)}, Edges: {len(edges)}")

print("Temporal Query Check...")
# Try the temporal query that crashed?
try:
    edges = db.query_temporal_graph("test", "A", mode="point_in_time", timestamp=100)
    print("Temporal Query OK", edges)
except Exception as e:
    print("Temporal Query Failed", e)

print("Done")
