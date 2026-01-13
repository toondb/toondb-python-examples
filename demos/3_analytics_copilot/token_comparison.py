"""Token comparison utility: TOON vs JSON.

Demonstrates token savings when using TOON format for tabular data.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

import tiktoken
from shared.toon_encoder import rows_to_toon


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens using tiktoken."""
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def compare_formats(
    rows: List[Dict[str, Any]],
    table_name: str = "data",
    fields: List[str] = None,
    model: str = "gpt-4"
) -> Dict[str, Any]:
    """Compare token counts for JSON vs TOON formats.
    
    Args:
        rows: Data rows as list of dictionaries
        table_name: Table name for TOON format
        fields: Optional field list (defaults to all fields)
        model: Model name for tokenizer
        
    Returns:
        Dictionary with comparison results
    """
    # JSON format
    json_payload = json.dumps(rows, indent=2)
    json_tokens = count_tokens(json_payload, model)
    
    # TOON format
    toon_payload = rows_to_toon(table_name, rows, fields)
    toon_tokens = count_tokens(toon_payload, model)
    
    # Calculate savings
    tokens_saved = json_tokens - toon_tokens
    percent_saved = (tokens_saved / json_tokens * 100) if json_tokens > 0 else 0
    
    return {
        "json_payload": json_payload,
        "json_tokens": json_tokens,
        "toon_payload": toon_payload,
        "toon_tokens": toon_tokens,
        "tokens_saved": tokens_saved,
        "percent_saved": percent_saved,
        "model": model
    }


def print_comparison(comparison: Dict[str, Any]):
    """Pretty print comparison results."""
    print("="*70)
    print("TOKEN COMPARISON: JSON vs TOON")
    print("="*70)
    
    print(f"\nModel: {comparison['model']}\n")
    
    print("JSON FORMAT:")
    print("-"*70)
    print(comparison['json_payload'][:500])
    if len(comparison['json_payload']) > 500:
        print("... (truncated)")
    print(f"\nTokens: {comparison['json_tokens']}")
    
    print("\n" + "="*70 + "\n")
    
    print("TOON FORMAT:")
    print("-"*70)
    print(comparison['toon_payload'][:500])
    if len(comparison['toon_payload']) > 500:
        print("... (truncated)")
    print(f"\nTokens: {comparison['toon_tokens']}")
    
    print("\n" + "="*70 + "\n")
    
    print("RESULTS:")
    print(f"  JSON tokens:      {comparison['json_tokens']}")
    print(f"  TOON tokens:      {comparison['toon_tokens']}")
    print(f"  Tokens saved:     {comparison['tokens_saved']}")
    print(f"  Percent saved:    {comparison['percent_saved']:.1f}%")
    
    print("\n" + "="*70)


def main():
    """Run token comparison demo."""
    
    # Example data from SochDB README
    example_rows = [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 28},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 34},
        {"id": 3, "name": "Carol", "email": "carol@example.com", "age": 42}
    ]
    
    print("\n🔍 Example 1: Simple User Table (from SochDB README)")
    comparison = compare_formats(example_rows, "users", model="gpt-4")
    print_comparison(comparison)
    
    # Load customer data
    csv_path = Path(__file__).parent / "sample_data" / "customers.csv"
    
    if csv_path.exists():
        print("\n\n🔍 Example 2: Customer Analytics Data")
        
        import csv
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            customer_rows = list(reader)
        
        # Take first 5 customers
        sample_customers = customer_rows[:5]
        
        # Use subset of fields for cleaner comparison
        fields = ["id", "name", "account_value", "contract_end", "support_tickets_30d"]
        
        comparison = compare_formats(
            sample_customers,
            "customers",
            fields=fields,
            model="gpt-4"
        )
        print_comparison(comparison)
        
        # Full table comparison
        print("\n\n🔍 Example 3: Full Customer Table (15 rows)")
        full_comparison = compare_formats(
            customer_rows,
            "customers",
            model="gpt-4"
        )
        
        print("="*70)
        print(f"Full table comparison ({len(customer_rows)} rows):")
        print(f"  JSON tokens:      {full_comparison['json_tokens']}")
        print(f"  TOON tokens:      {full_comparison['toon_tokens']}")
        print(f"  Tokens saved:     {full_comparison['tokens_saved']}")
        print(f"  Percent saved:    {full_comparison['percent_saved']:.1f}%")
        print("="*70)
    
    print("\n✅ Token comparison complete!")
    print("\nKey Takeaway:")
    print("  TOON format typically saves 40-67% tokens for tabular data,")
    print("  allowing you to fit more context in prompts and reduce API costs.\n")


if __name__ == "__main__":
    main()
