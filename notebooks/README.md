# ToonDB Demo Notebooks

Interactive Jupyter notebooks for learning ToonDB features through hands-on examples.

## 📚 Notebooks

### [1. Support Agent](./1_support_agent.ipynb)
**RAG + SQL + Transactions**

Learn how to build an AI support agent with:
- SQL queries for order data
- KV storage for user preferences
- Vector RAG with policy retrieval
- TOON encoding (40-67% token savings)
- ACID transactions

**Key Concepts**: `execute_sql()`, KV storage, vector collections, `ContextQuery`, TOON format, transactions

---

### [2. Incident Response](./2_incident_response.ipynb)
**Multi-Agent IPC**

Learn how to build coordinated multi-process systems with:
- IPC mode (Unix socket)
- Shared state across processes
- Namespace isolation
- Hybrid retrieval (vector + keyword with RRF)
- ACID state machines

**Key Concepts**: IPC mode, `IpcClient`, namespaces, hybrid search, state transitions

---

### [3. Analytics Copilot](./3_analytics_copilot.ipynb)
**Spreadsheet + AI Analysis**

Learn how to build data analysis agents with:
- CSV ingestion to SQL
- TOON vs JSON token comparison (with proof!)
- Vector search over text fields
- Token-budgeted context assembly
- Churn prediction analysis

**Key Concepts**: CSV → SQL, TOON encoding, token savings measurement, semantic search

---

## 🚀 Getting Started

### Prerequisites

```bash
# Install dependencies
pip install toondb openai tiktoken jupyter

# Set API key
export OPENAI_API_KEY="your-api-key-here"
```

### Run Notebooks

```bash
cd demos/notebooks
jupyter notebook
```

Then open any notebook and run cells sequentially.

---

## 📖 Learning Path

**Beginner**: Start with Notebook 1 (Support Agent)
- Learn core ToonDB concepts
- Understand SQL, KV, and vector features
- See TOON encoding in action

**Intermediate**: Move to Notebook 3 (Analytics Copilot)
- Practical data analysis workflow
- Measure real token savings
- Build production-ready pipelines

**Advanced**: Finish with Notebook 2 (Incident Response)
- Multi-process coordination
- IPC architecture
- Complex state management

---

## 💡 What Makes These Notebooks Special

### ✅ Educational & Hands-On

- **Concept blocks** explain the "why" behind each feature
- **How-To sections** show practical implementation
- **Real code** you can run and modify
- **Visual results** with token counts, comparisons, metrics

### ✅ Production-Ready Patterns

Not toy examples:
- Real SQL schemas
- Actual vector search
- Measured token savings
- Error handling
- Best practices

### ✅ Interactive Learning

- Modify queries and see results change
- Experiment with token budgets
- Try different embeddings
- Upload your own data

---

## 📊 Key Insights from Notebooks

### TOON Token Savings (Proven!)

From Notebook 3:
- **Simple data** (3 rows): 54% savings
- **Customer data** (10 rows): 58% savings
- **Large datasets** (50+ rows): 60-67% savings

**Real cost impact**: At 1000 queries/day with 20 rows each:
- Save ~600,000 tokens/day
- ~$6/day at GPT-4 pricing
- **~$2,190/year**

### No Glue Code Needed

Traditional stack:
```
CSV → Postgres → Pinecone → LLM
```

ToonDB stack:
```
CSV → ToonDB → LLM
```

### ACID Everywhere

All demos show atomic operations:
- Notebook 1: Update 3 tables atomically
- Notebook 2: State transitions across processes
- Notebook 3: Consistent analytics queries

---

## 🎯 Use Cases Demonstrated

| Notebook | Use Case | Features |
|----------|----------|----------|
| 1 | Customer support automation | SQL, KV, RAG, transactions |
| 2 | Ops automation & monitoring | IPC, multi-process, state machines |
| 3 | Data analytics & BI | CSV ingestion, TOON, semantic search |

---

## 🔧 Customization Ideas

### Notebook 1 (Support Agent)
- Add more policy documents
- Implement refund/replacement logic
- Add multi-language support
- Track customer satisfaction

### Notebook 2 (Incident Response)
- Add more incident types
- Implement auto-remediation
- Add alerting integrations
- Track MTTR metrics

### Notebook 3 (Analytics Copilot)
- Upload your own CSV data
- Add more BI metrics
- Build dashboards
- Automate reports

---

## 📚 Additional Resources

- [Main Demo READMEs](../) - Full Python implementations
- [ToonDB Documentation](https://github.com/toondb/toondb)
- [Python SDK](https://github.com/toondb/toondb-python-sdk)
- [TOON Format Spec](https://github.com/toondb/toondb#toon-format)

---

## 💬 Feedback & Questions

These notebooks are designed to be educational. If you find:
- Unclear explanations
- Missing concepts
- Bugs or errors
- Ideas for improvements

Please open an issue or contribute!

---

## Requirements

All notebooks use:
```
toondb>=0.3.3
openai>=1.0.0
tiktoken>=0.5.0
jupyter>=1.0.0
```

Install with:
```bash
pip install -r ../requirements.txt jupyter
```
