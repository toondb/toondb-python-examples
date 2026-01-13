# SochDB Zep Migration Examples

This directory contains examples of how to migrate from Zep Memory to SochDB. These scripts replicate the functionality of standard Zep examples using SochDB's native Key-Value and hierarchy primitives.

## Examples Provided

| Zep Example | SochDB Port | Description |
|-------------|-------------|-------------|
| `simple.py` | `sochdb_simple.py` | Basic user, thread, and message management. Shows how to structure conversation data hierarchically. |
| `user_example.py` | `sochdb_user_management.py` | Full CRUD operations for Users. Demonstrates metadata storage, updates, and soft deletion. |
| `advanced.py` | `sochdb_entities.py` | Advanced Entity & Relationship storage (Knowledge Graph). Shows how to model graph data using KV pairs and manual indexes. |

## Key Concepts Mapped

| Concept | Zep Implementation | SochDB Implementation |
|---------|--------------------|-----------------------|
| **User** | `client.user.add(...)` | `db.put(f"users.{id}.name", ...)` |
| **Thread** | `client.thread.create(...)` | `db.put(f"threads.{id}.created_at", ...)` |
| **Message** | `client.thread.add_messages(...)` | `db.put(f"threads.{id}.messages.{i}.content", ...)` |
| **Entity** | `EntityModel` (Pydantic) | `entities.{type}.{id}.{field}` |
| **Edge** | `EdgeModel` (Pydantic) | `relationships.{type}.{id}` + `indexes.source.{id}` |

## Usage

Run any example to see SochDB in action:

```bash
# Basic conversation storge
python3 sochdb_simple.py

# User management (CRUD)
python3 sochdb_user_management.py

# Advanced Knowledge Graph (Entities & Relationships)
python3 sochdb_entities.py
```

## Data Location

Each example creates a local database directory:
- `./sochdb_simple_data`
- `./sochdb_user_data`
- `./sochdb_entity_data`

To reset, simply delete these directories.
