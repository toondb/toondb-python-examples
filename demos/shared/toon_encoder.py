"""TOON format encoder for tabular data.

TOON (Tabular Object Oriented Notation) is a compact format for representing
tabular data in prompts. Format: name[count]{fields}:\nrow1\nrow2...

Example:
    users[2]{id,name,email}:
    1,Alice,alice@example.com
    2,Bob,bob@example.com
"""

from typing import Any, List, Dict, Optional


def rows_to_toon(
    table_name: str,
    rows: List[Dict[str, Any]],
    fields: Optional[List[str]] = None,
    null_placeholder: str = "∅"
) -> str:
    """Convert rows to TOON format.
    
    Args:
        table_name: Name of the table/collection
        rows: List of dictionaries representing rows
        fields: Optional list of field names to include. If None, uses all fields from first row
        null_placeholder: Character to use for missing/null values
        
    Returns:
        TOON-formatted string
        
    Examples:
        >>> rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        >>> print(rows_to_toon("users", rows))
        users[2]{id,name}:
        1,Alice
        2,Bob
    """
    if not rows:
        return f"{table_name}[0]{{}}:\n"
    
    # Determine fields
    if fields is None:
        fields = list(rows[0].keys())
    
    # Build header: name[count]{fields}:
    header = f"{table_name}[{len(rows)}]{{{','.join(fields)}}}:\n"
    
    # Build rows
    row_strs = []
    for row in rows:
        values = []
        for field in fields:
            val = row.get(field)
            if val is None:
                values.append(null_placeholder)
            else:
                # Escape commas in values
                val_str = str(val).replace(",", "\\,")
                values.append(val_str)
        row_strs.append(",".join(values))
    
    body = "\n".join(row_strs)
    return header + body + ("\n" if body else "")


class ToonEncoder:
    """Stateful TOON encoder with formatting options."""
    
    def __init__(self, null_placeholder: str = "∅", escape_commas: bool = True):
        """Initialize encoder.
        
        Args:
            null_placeholder: Character for null values
            escape_commas: Whether to escape commas in values
        """
        self.null_placeholder = null_placeholder
        self.escape_commas = escape_commas
    
    def encode(
        self,
        table_name: str,
        rows: List[Dict[str, Any]],
        fields: Optional[List[str]] = None
    ) -> str:
        """Encode rows to TOON format."""
        return rows_to_toon(table_name, rows, fields, self.null_placeholder)
    
    def encode_multiple(self, tables: Dict[str, List[Dict[str, Any]]]) -> str:
        """Encode multiple tables into a single TOON document.
        
        Args:
            tables: Dictionary mapping table names to row lists
            
        Returns:
            Combined TOON string
        """
        parts = []
        for table_name, rows in tables.items():
            parts.append(self.encode(table_name, rows))
        return "\n".join(parts)
