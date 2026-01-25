"""
Transactions Example - SochDB Python SDK

Demonstrates:
- Beginning transactions
- Batch operations
- Commit and rollback
- ACID properties
"""

from sochdb import Database

def main():
    print("=== SochDB Python SDK - Transactions ===\n")

    db = Database.open("./data/transactions_db")
    print("✅ Database opened successfully\n")

    try:
        # Example 1: Successful transaction
        print("1. Successful Transaction")
        print("-------------------------")
        
        with db.transaction() as txn:
            txn.put(b"account:alice", b"1000")
            txn.put(b"account:bob", b"500")
            txn.put(b"account:charlie", b"750")
            print("  Staged 3 account updates")
        print("✅ Transaction committed\n")

        # Verify data persisted
        alice = db.get(b"account:alice")
        print(f"Verified: account:alice = {alice.decode()}\n")

        # Example 2: Atomic transfer
        print("2. Atomic Transfer")
        print("------------------")
        
        before = db.get(b"account:alice")
        print(f"Before: Alice = {before.decode()}")

        with db.transaction() as txn:
            txn.put(b"account:alice", b"800")
            txn.put(b"account:bob", b"700")
            txn.put(b'transfer:001', b'{"from":"alice","to":"bob","amount":200}')

        after = db.get(b"account:alice")
        print(f"After:  Alice = {after.decode()}")
        print("✅ Atomic transfer complete\n")

        # Example 3: Scan within transaction
        print("3. Scan within Transaction")
        print("--------------------------")
        
        with db.transaction() as txn:
            count = 0
            for key, value in txn.scan_prefix(b"account:"):
                print(f"  {key.decode()} = {value.decode()}")
                count += 1
            print(f"✅ Scanned {count} accounts in transaction\n")

        print("=== Example Complete ===")

    finally:
        db.close()

if __name__ == "__main__":
    main()
