"""Simple Graph Example - v0.4.0

Demonstrates SochDB graph operations using the new API.
Based on the sochdb v0.4.0 documentation.
"""
from sochdb import Database

print("=== SochDB Graph Example (Python) v0.4.0 ===\n")

# Open database
db = Database.open("./test_graph_db")
print("✓ Database opened")

# Add nodes using db.add_node()
db.add_node(
    namespace="demo",
    node_id="alice",
    node_type="person",
    properties={"name": "Alice", "role": "developer"}
)
db.add_node("demo", "bob", "person", {"name": "Bob", "role": "engineer"})
db.add_node("demo", "sochdb", "project", {"name": "SochDB", "status": "active"})
print("✓ 3 nodes added")

# Add edges using db.add_edge()
db.add_edge("demo", "alice", "works_on", "sochdb", {"role": "lead"})
db.add_edge("demo", "bob", "works_on", "sochdb")
db.add_edge("demo", "alice", "knows", "bob")
print("✓ 3 edges added")

# Traverse graph using db.traverse()
nodes, edges = db.traverse(
    namespace="demo",
    start_node="alice",
    max_depth=2,
    order="bfs"
)
print(f"✓ BFS traversal from 'alice':")
print(f"  Visited {len(nodes)} nodes:")
for node in nodes:
    print(f"    - {node['id']} ({node['node_type']})")
print(f"  Found {len(edges)} edges:")
for edge in edges:
    print(f"    - {edge['from_id']} --{edge['edge_type']}--> {edge['to_id']}")

db.close()
print("\n✓✓✓ SUCCESS: Graph operations work perfectly! ✓✓✓")
