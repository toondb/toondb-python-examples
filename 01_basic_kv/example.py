"""
Basic Key-Value Operations with SochDB Python SDK

Demonstrates:
- Opening a database
- Put/Get/Delete operations
- Scanning with prefix
- Database statistics
"""

from sochdb import Database

def main():
    print("=== SochDB Python SDK - Basic Key-Value Operations ===\n")

    # Open database in embedded mode
    db = Database.open("./data/basic_kv_db")
    print("✅ Database opened successfully\n")

    try:
        # Example 1: PUT operations
        print("1. PUT Operations")
        print("-----------------")
        
        db.put(b"user:1001", b'{"name": "Alice", "email": "alice@example.com"}')
        print("Stored: user:1001")

        # Store multiple keys
        users = {
            b"user:1002": b'{"name": "Bob", "email": "bob@example.com"}',
            b"user:1003": b'{"name": "Charlie", "email": "charlie@example.com"}',
            b"product:2001": b'{"name": "Laptop", "price": 999}',
            b"product:2002": b'{"name": "Mouse", "price": 25}',
        }

        for key, value in users.items():
            db.put(key, value)
        print("✅ Stored multiple key-value pairs\n")

        # Example 2: GET operations
        print("2. GET Operations")
        print("-----------------")
        
        user = db.get(b"user:1001")
        print(f"Retrieved: user:1001 = {user.decode()}")

        # Get non-existent key
        missing = db.get(b"user:9999")
        if missing is None:
            print("Key not found: user:9999 (expected)\n")

        # Example 3: SCAN operations
        print("3. SCAN Operations")
        print("------------------")
        print('Scanning keys with prefix "user:"')
        
        count = 0
        for key, value in db.scan_prefix(b"user:"):
            print(f"  {key.decode()} = {value.decode()}")
            count += 1
        print(f"✅ Scanned {count} keys\n")

        # Example 4: DELETE operations
        print("4. DELETE Operations")
        print("--------------------")
        
        db.delete(b"user:1001")
        print("Deleted: user:1001")

        # Verify deletion
        deleted = db.get(b"user:1001")
        if deleted is None:
            print("✅ Key successfully deleted\n")

        # Example 5: Database statistics
        print("5. Database Statistics")
        print("----------------------")
        
        stats = db.stats()
        print(f"Keys count: {stats.get('keys_count', 0)}")
        print(f"Bytes written: {stats.get('bytes_written', 0)} bytes")
        print(f"Transactions committed: {stats.get('transactions_committed', 0)}")

        print("\n=== Example Complete ===")

    finally:
        db.close()

if __name__ == "__main__":
    main()
