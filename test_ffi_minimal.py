import ctypes
import os

def test_minimal():
    lib_path = "/Users/sushanth/sochdb_v2/sochdb/target/release/libsochdb_storage_DEBUG.dylib"
    print(f"Loading {lib_path}")
    lib = ctypes.CDLL(lib_path)
    
    print("Connecting to function...")
    try:
        fn = lib.sochdb_collection_keyword_search
        print("Function found!")
    except AttributeError:
        print("Function NOT found!")
        return

    # Call it with nulls to trigger panic (panic check is before null check? No, panic is AFTER null check currently)
    # Wait, I put panic AFTER null check in step 1041.
    # So I must pass valid pointers or hit null check return -1.
    # To hit panic, I must pass valid non-null pointers.
    
    # Actually, pass dummy pointers.
    dummy = ctypes.c_char_p(b"dummy")
    
    try:
        print("Calling function...")
        # (ptr, ns, col, query, k, results)
        res = fn(
            ctypes.c_void_p(1), # Fake ptr
            dummy, dummy, dummy,
            ctypes.c_size_t(1),
            ctypes.c_void_p(1) # Fake results ptr
        )
        print(f"Result: {res}")
    except OSError as e:
        print(f"OSError: {e}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_minimal()
