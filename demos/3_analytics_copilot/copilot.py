"""Analytics copilot with spreadsheet data, SQL queries, and vector search.

Showcases:
- CSV ingestion to SQL tables
- TOON encoding for query results (40-67% token savings)
- Vector search for semantic analysis
- Token-budgeted context assembly
"""

import sys
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from toondb import Database, ContextQuery, DeduplicationStrategy
from shared.toon_encoder import rows_to_toon
from shared.llm_client import LLMClient
from shared.embeddings import EmbeddingClient


class AnalyticsCopilot:
    """Analytics copilot with SQL, TOON, and vector search."""
    
    def __init__(self, db_path: str = "./analytics_db"):
        """Initialize copilot."""
        self.db_path = db_path
        self.llm = LLMClient(model="gpt-4-turbo-preview")
        self.embedding_client = EmbeddingClient()
    
    def setup_database(self, csv_path: str):
        """Load CSV data into SQL table and index notes."""
        print(f"📥 Loading data from {csv_path}...")
        
        with Database.open(self.db_path) as db:
            # Create customers table
            db.execute_sql("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    account_value REAL NOT NULL,
                    contract_end TEXT NOT NULL,
                    monthly_active_days INTEGER,
                    support_tickets_30d INTEGER,
                    last_login_days_ago INTEGER,
                    feature_usage_score REAL,
                    notes TEXT
                )
            """)
            
            # Load CSV data
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            for row in rows:
                db.execute_sql(f"""
                    INSERT OR REPLACE INTO customers VALUES (
                        {row['id']},
                        '{row['name']}',
                        '{row['email']}',
                        {row['account_value']},
                        '{row['contract_end']}',
                        {row['monthly_active_days']},
                        {row['support_tickets_30d']},
                        {row['last_login_days_ago']},
                        {row['feature_usage_score']},
                        '{row['notes'].replace("'", "''")}'
                    )
                """)
            
            print(f"  ✓ Loaded {len(rows)} customers into SQL table")
            
            # Index customer notes into vector collection
            print(f"🔍 Indexing customer notes for semantic search...")
            
            ns = db.namespace("analytics")
            dimension = self.embedding_client.dimension
            collection = ns.create_collection("customer_notes", dimension=dimension)
            
            for row in rows:
                if row['notes'].strip():
                    embedding = self.embedding_client.embed(row['notes'])
                    collection.add_document(
                        id=f"customer_{row['id']}",
                        embedding=embedding,
                        text=row['notes'],
                        metadata={
                            "customer_id": row['id'],
                            "customer_name": row['name']
                        }
                    )
            
            print(f"  ✓ Indexed {len(rows)} customer notes")
        
        print(f"✅ Database setup complete!\n")
    
    def analyze_churn_risk(self, query: str) -> Dict[str, Any]:
        """Analyze churn risk using SQL, TOON, and vector search.
        
        Args:
            query: User's analytical question
            
        Returns:
            Analysis results with response and debug info
        """
        print(f"{'='*70}")
        print(f"QUERY: {query}")
        print(f"{'='*70}\n")
        
        with Database.open(self.db_path) as db:
            # 1. SQL: Find at-risk customers
            print("📊 Querying at-risk customers (SQL)...")
            
            sql_query = """
                SELECT id, name, account_value, contract_end,
                       monthly_active_days, support_tickets_30d,
                       last_login_days_ago, feature_usage_score
                FROM customers
                WHERE (
                    monthly_active_days < 15
                    OR support_tickets_30d > 5
                    OR last_login_days_ago > 7
                    OR feature_usage_score < 50
                )
                ORDER BY feature_usage_score ASC, support_tickets_30d DESC
                LIMIT 10
            """
            
            result = db.execute_sql(sql_query)
            at_risk_customers = result.rows if result else []
            
            print(f"  Found {len(at_risk_customers)} at-risk customers")
            
            # 2. TOON: Encode results compactly
            print("🔧 Encoding to TOON format...")
            
            fields = [
                "id", "name", "account_value", "contract_end",
                "monthly_active_days", "support_tickets_30d",
                "last_login_days_ago", "feature_usage_score"
            ]
            
            customers_toon = rows_to_toon(
                "at_risk_customers",
                at_risk_customers,
                fields=fields
            )
            
            # Count tokens saved
            import json
            import tiktoken
            
            json_version = json.dumps(at_risk_customers)
            enc = tiktoken.encoding_for_model("gpt-4")
            json_tokens = len(enc.encode(json_version))
            toon_tokens = len(enc.encode(customers_toon))
            tokens_saved = json_tokens - toon_tokens
            percent_saved = (tokens_saved / json_tokens * 100) if json_tokens > 0 else 0
            
            print(f"  TOON tokens: {toon_tokens} | JSON tokens: {json_tokens}")
            print(f"  Saved: {tokens_saved} tokens ({percent_saved:.1f}%)")
            
            # 3. Vector search: Find relevant customer notes
            print("🔍 Searching customer notes (vector semantic search)...")
            
            query_embedding = self.embedding_client.embed(query)
            
            ns = db.namespace("analytics")
            collection = ns.collection("customer_notes")
            
            ctx = (
                ContextQuery(collection)
                .add_vector_query(query_embedding, weight=0.8)
                .add_keyword_query("churn risk support tickets low engagement", weight=0.2)
                .with_token_budget(1000)
                .with_deduplication(DeduplicationStrategy.SEMANTIC)
                .execute()
            )
            
            print(f"  Retrieved {len(ctx.documents)} relevant notes")
            print(f"  Token budget used: ~{ctx.total_tokens} tokens")
            
            # 4. Generate analysis
            print("💡 Generating churn risk analysis...")
            
            system_message = """You are a customer success data analyst.
Analyze customer data to identify churn risks and provide actionable recommendations.
Base your analysis on the SQL data and customer notes provided."""
            
            prompt = f"""Question: {query}

At-Risk Customers (TOON format):
{customers_toon}

Customer Notes (semantic search results):
{ctx.as_markdown()}

Provide:
1. Summary of top churn risks (list top 3-5 customers with reasons)
2. Common patterns across at-risk customers
3. Recommended interventions (priority order)
"""
            
            response = self.llm.complete(prompt, system_message=system_message)
            
            return {
                "query": query,
                "at_risk_count": len(at_risk_customers),
                "toon_tokens": toon_tokens,
                "json_tokens": json_tokens,
                "tokens_saved": tokens_saved,
                "percent_saved": percent_saved,
                "notes_retrieved": len(ctx.documents),
                "response": response,
                "customers_toon": customers_toon
            }


def main():
    """Run analytics copilot demo."""
    csv_path = Path(__file__).parent / "sample_data" / "customers.csv"
    
    if not csv_path.exists():
        print(f"❌ Error: {csv_path} not found")
        return
    
    copilot = AnalyticsCopilot()
    
    # Setup database
    copilot.setup_database(csv_path)
    
    # Example queries
    queries = [
        "Which customers are most at risk of churn, and why?",
        "What patterns do you see in customers with high support ticket counts?",
        "Which accounts should we prioritize for retention calls?"
    ]
    
    print("="*70)
    print("ANALYTICS COPILOT DEMO")
    print("="*70)
    print("\nAvailable queries:")
    for i, q in enumerate(queries, 1):
        print(f"  {i}. {q}")
    print(f"  {len(queries) + 1}. Custom query")
    print(f"  0. Exit")
    
    while True:
        print("\n" + "-"*70)
        choice = input(f"\nSelect query (0-{len(queries) + 1}): ")
        
        if choice == "0":
            print("\nExiting demo.")
            break
        
        try:
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(queries):
                query = queries[choice_num - 1]
            elif choice_num == len(queries) + 1:
                query = input("Enter your query: ")
            else:
                print("Invalid choice. Try again.")
                continue
            
            # Run analysis
            result = copilot.analyze_churn_risk(query)
            
            # Display results
            print("\n" + "="*70)
            print("ANALYSIS RESULTS")
            print("="*70)
            print(result["response"])
            
            print(f"\n📊 Statistics:")
            print(f"  At-risk customers: {result['at_risk_count']}")
            print(f"  Notes retrieved: {result['notes_retrieved']}")
            print(f"  TOON vs JSON: {result['toon_tokens']} vs {result['json_tokens']} tokens")
            print(f"  Token savings: {result['tokens_saved']} ({result['percent_saved']:.1f}%)")
            
        except ValueError:
            print("Invalid input. Try again.")
        except KeyboardInterrupt:
            print("\n\nExiting demo.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
