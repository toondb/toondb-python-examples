# SochDB Python Examples

Official Python examples for SochDB - the high-performance embedded database for AI applications. This repository showcases integration patterns with popular agent frameworks and demonstrates SochDB's unique features.

## 📂 Repository Structure

```
sochdb-python-examples/
├── agent_memory/          # Production agent memory system with HNSW index
├── azure_openai/          # Azure OpenAI integration examples
├── complete_examples/     # Framework integrations (LangGraph, AutoGen, CrewAI)
├── context_builder/       # Token-budget aware context assembly
├── ecommerce/             # eCommerce product catalog RAG
├── langgraph/             # LangGraph checkpointer and memory
├── podcast/               # Podcast transcript search
├── rag/                   # Complete RAG pipeline
├── wizard_of_oz/          # Long-form text ingestion
└── zep/                   # Zep-compatible examples
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+ installed
- SochDB Python SDK: `sochdb`

### Installation

```bash
pip install sochdb
```

## 📚 Examples by Category

### 🧠 Agent Memory & State

#### 1. Agent Memory (`agent_memory/`)

**Production-ready agent memory system** with vector search and HNSW index.

**Features**:
- Long-term memory with semantic search
- Session-based memory management  
- Time-weighted retrieval
- Performance tracking and metrics
- HNSW vector index for fast similarity search

**Use Cases**: Multi-turn conversations, customer support agents, research assistants

```bash
cd agent_memory
pip install -r requirements.txt
python main.py
```

---

#### 2. LangGraph Integration (`langgraph/`)

**Best for**: Building stateful LangGraph agents with persistent memory.

**Features**:
- Custom SochDB checkpointer for graph state
- Long-term memory store for user interactions
- Time-weighted context retrieval
- Seamless LangGraph integration

```bash
cd langgraph
pip install -r requirements.txt  
python agent_with_sochdb.py
```

---

#### 3. Context Query Builder (`context_builder/`)

**Best for**: Managing LLM context under strict token budgets.

**Features**:
- Priority-based content truncation
- Token budget management
- Intelligent context assembly
- System + user + history + retrieval

**Demonstrated Scenarios**:
- Ample budget (4000 tokens)
- Tight budget (500 tokens)
- SochDB integration with TOON format

```bash
cd context_builder
pip install -r requirements.txt
python runner.py
```

---

### 🔍 RAG & Retrieval Examples

#### 4. RAG Pipeline (`rag/`)

**Complete production RAG system** with document ingestion, chunking, and query pipeline.

**Features**:
- Document ingestion and chunking
- Azure OpenAI embeddings
- Vector search with SochDB
- Generation with context

```bash
cd rag
pip install -r requirements.txt
python main.py
```

---

#### 5. eCommerce RAG (`ecommerce/`)

**Best for**: Product catalogs, shopping assistants, recommendation systems.

**Features**:
- Hybrid search (semantic + metadata filtering)
- TOON format for compact results
- Structured product data ingestion
- **100% accuracy** on test queries

```bash
cd ecommerce
pip install -r requirements.txt
python runner.py
```

---

#### 6. Azure OpenAI ("California Politics") (`azure_openai/`)

**Best for**: Fact retrieval systems with Azure OpenAI.

**Features**:
- Entity-focused retrieval (Kamala Harris, Gavin Newsom)
- High-precision fact extraction
- Azure OpenAI embeddings and chat
- **100% accuracy** on political facts

```bash
cd azure_openai
pip install -r requirements.txt
python runner.py
```

---

### 📖 Document & Text Processing

#### 7. Wizard of Oz (`wizard_of_oz/`)

**Best for**: Long-context narrative understanding, book ingestion.

**Features**:
- Paragraph-based chunking
- Semantic search over narrative text
- Character and plot retrieval
- **100% accuracy** on story queries

```bash
cd wizard_of_oz
pip install -r requirements.txt
python runner.py
```

---

#### 8. Podcast Search (`podcast/`)

**Best for**: Audio transcripts, meeting notes, multi-speaker dialogue.

**Features**:
- Speaker attribution parsing
- Timestamp preservation
- Turn-based segmentation
- **100% accuracy** on speaker/topic queries

```bash
cd podcast
pip install -r requirements.txt
python runner.py
```

---

### 🛠️ Framework Integrations

#### 9. Complete Examples (`complete_examples/`)

**Multi-framework integrations** showing SochDB with various agent frameworks.

**Included**:
- LangGraph agent with SochDB memory
- AutoGen multi-agent with SochDB
- Chat history management
- Graph-based examples

```bash
cd complete_examples
pip install -r requirements.txt
# Run individual examples
python langgraph_agent_with_sochdb.py
```

---

#### 10. Zep Port (`zep/`)

**Best for**: Users migrating from Zep or needing entity-centric memory.

**Features**:
- Entity extraction and storage
- User profile management
- Conversation thread tracking
- Zep-compatible API patterns

```bash
cd zep
pip install -r requirements.txt
python sochdb_simple.py
```

# SochDB Demo Notebooks

Interactive Jupyter notebooks for learning SochDB features through hands-on examples.

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

## 🔑 Key SochDB Features Demonstrated

- **TOON Format**: Token-efficient output format (`Database.to_toon()`)
- **Vector Search**: Built-in HNSW index for semantic similarity
- **ACID Transactions**: Group commits with Snapshot Isolation
- **Columnar Storage**: Efficient projection-based reads
- **SQL Support**: Optional SQL interface via IPC mode
- **Embedded Mode**: Zero-config, file-based database

## 📖 Documentation

- [SochDB Documentation](https://sochdb.io)
- [Python SDK (PyPI)](https://pypi.org/project/sochdb-client/)
- [API Reference](https://sochdb.io/docs/python-sdk)

## ✅ Accuracy Testing

All examples include `accuracy_test.py` scripts with verified results:

| Example | Accuracy | Test Cases |
|---------|----------|------------|
| eCommerce | 100% | 4/4 |
| Azure OpenAI | 100% | 4/4 |
| Wizard of Oz | 100% | 3/3 |
| Podcast | 100% | 4/4 |

## 🤝 Contributing

We welcome contributions! Please submit Pull Requests with:
- New example implementations
- Improvements to existing examples  
- Documentation enhancements
- Bug fixes

## 📄 License

Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Repositories

- [sochdb/sochdb](https://github.com/sochdb/sochdb) - Main SochDB repository
- [sochdb/sochdb-go](https://github.com/sochdb/sochdb-go) - Go SDK
- [sochdb/sochdb-golang-examples](https://github.com/sochdb/sochdb-golang-examples) - Go examples
- [sochdb/sochdb-examples](https://github.com/sochdb/sochdb-examples) - Multi-language examples

## Acknowledgements

Some of the agent memory examples (Wizard of Oz, Podcast, Zep ports) are referenced and adapted from the following projects:
- [Zep](https://github.com/getzep/zep)
- [Graphiti](https://github.com/getzep/graphiti)
git a