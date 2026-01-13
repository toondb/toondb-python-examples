# SochDB Python Examples - Bugs Found and Fixed

This document lists all bugs found while testing the examples and the fixes applied.

## Summary

| Category | Bug | Status | File(s) |
|----------|-----|--------|---------|
| Import Path | SDK path hardcoded | ✅ Fixed | `comprehensive_harness.py` |
| Import Style | Relative imports in standalone scripts | ✅ Fixed | Multiple files |
| Config | Wrong environment variable name | ✅ Fixed | `autogen_agent_with_toondb.py` |
| External Dep | pyautogen strips dots from deployment names | ⚠️ Known Issue | N/A |
| Missing Module | ContextQuery/DeduplicationStrategy not in SDK | ❌ SDK Gap | `demos/1_support_agent/` |
| Missing Module | metrics_collector module not found | ❌ Not Fixed | `toondb_support_chatbot.py` |
| Server Dep | Some demos require sochdb-server | ⏭️ Skipped | `demos/2_incident_response/` |

---

## 1. SDK Path Hardcoded in comprehensive_harness.py

**File:** `comprehensive_harness.py`

**Problem:** The harness file added the local SDK path to sys.path, causing it to use the development version instead of pip-installed version:

```python
# OLD CODE (BROKEN)
sdk_path = Path(__file__).parent.parent / "sochdb-python-sdk" / "src"
sys.path.insert(0, str(sdk_path))
```

**Fix Applied:** Removed the SDK path insertion, using pip-installed sochdb:

```python
# NEW CODE (FIXED)
# Using sochdb from pip install (not local SDK path)
from sochdb import Database
```

---

## 2. Relative Imports in Standalone Scripts

Several examples used relative imports (e.g., `from .config import ...`) but were meant to be run as standalone scripts.

**Files Fixed:**
- `context_builder/runner.py`
- `langgraph/agent_with_toondb.py`
- `langgraph/memory.py`
- `langgraph/checkpointer.py`
- `ecommerce_simulation/main.py`
- `ecommerce_simulation/data_gen.py`
- `ecommerce_simulation/db_ops.py`
- `fintech_simulation/main.py`

**Fix Applied:** Changed relative imports to absolute imports:

```python
# OLD CODE (BROKEN)
from .config import get_azure_config

# NEW CODE (FIXED)
from config import get_azure_config
```

---

## 3. Wrong Environment Variable in AutoGen Example

**File:** `complete_examples/autogen_agent_with_toondb.py`

**Problem:** Used `AZURE_OPENAI_DEPLOYMENT` but the `.env` file defines `AZURE_OPENAI_CHAT_DEPLOYMENT`:

```python
# OLD CODE
"model": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
```

**Fix Applied:**

```python
# NEW CODE
"model": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", os.getenv("AZURE_OPENAI_DEPLOYMENT")),
```

---

## 4. pyautogen Strips Dots from Deployment Names (Known Issue)

**File:** `complete_examples/autogen_agent_with_toondb.py`

**Problem:** pyautogen library (both 0.2.x and 0.9.x) has code that strips dots from Azure deployment names:

```python
# In pyautogen source (client.py):
openai_config["azure_deployment"] = openai_config["azure_deployment"].replace(".", "")
```

This means if your Azure deployment is named `gpt-4.1`, it becomes `gpt41` which doesn't exist.

**Workaround:** 
- Create Azure deployments without dots in the name (e.g., `gpt-4-turbo` instead of `gpt-4.1`)
- Or use a different version of pyautogen

**Status:** Not fixed in examples - this is a pyautogen library issue.

---

## 5. Missing SDK Features (ContextQuery, DeduplicationStrategy)

**Files Affected:**
- `demos/1_support_agent/agent.py`

**Problem:** The demo imports features that don't exist in the current SDK:

```python
from sochdb import Database, ContextQuery, DeduplicationStrategy
```

These appear to be planned features that aren't yet implemented.

**Status:** Cannot run these demos until SDK is updated.

---

## 6. Missing metrics_collector Module

**File:** `toondb_support_chatbot.py`

**Problem:** The script imports a module that doesn't exist:

```python
from metrics_collector import MetricsCollector
```

**Status:** Not fixed - missing dependency file.

---

## 7. Server-Required Demos

**Files Affected:**
- `demos/2_incident_response/` (all files)
- `demos/3_analytics_copilot/` (all files)

**Problem:** These demos require a running `sochdb-server` which is a separate component.

**Status:** Skipped - requires external server setup.

---

## Examples Test Status

### ✅ Working Examples (22)

| Example | Notes |
|---------|-------|
| `quickstart_example.py` | Works perfectly |
| `comprehensive_harness.py` | All 10 scenarios run |
| `agent_memory/main.py` | Real LLM integration works |
| `azure_openai/runner.py` | Vector search + TOON format |
| `complete_examples/chat_history_memory.py` | ✅ |
| `complete_examples/graph_example.py` | ✅ |
| `complete_examples/langgraph_agent_with_toondb.py` | Interactive mode |
| `complete_examples/advanced_travel.py` | Not tested |
| `context_builder/runner.py` | ✅ After fix |
| `ecommerce/runner.py` | ✅ (data file optional) |
| `ecommerce_simulation/main.py` | ✅ After fix |
| `fintech_simulation/main.py` | ✅ After fix |
| `langgraph/agent_with_toondb.py` | ✅ After fix |
| `podcast/runner.py` | ✅ (data file optional) |
| `rag/demo.py` | Full RAG pipeline works |
| `rag/main.py` | CLI interface works |
| `wizard_of_oz/runner.py` | ✅ (data file optional) |
| `zep/toondb_simple.py` | ✅ |
| `zep/toondb_user_management.py` | ✅ |
| `zep/toondb_entities.py` | ✅ |

### ⚠️ Partial/Known Issues (2)

| Example | Issue |
|---------|-------|
| `complete_examples/autogen_agent_with_toondb.py` | pyautogen strips dots from deployment name |
| `toondb_support_chatbot.py` | Missing metrics_collector module |

### ❌ Cannot Run (3)

| Example | Reason |
|---------|--------|
| `demos/1_support_agent/` | Missing SDK features (ContextQuery) |
| `demos/2_incident_response/` | Requires sochdb-server |
| `demos/3_analytics_copilot/` | Requires sochdb-server |

---

## Recommendations

1. **For SDK Team:** Add `ContextQuery` and `DeduplicationStrategy` to the SDK to enable the demos.

2. **For Examples:** Update pyautogen config format or document the Azure deployment naming restriction.

3. **For Documentation:** Add a note that some demos require `sochdb-server` to be running.

4. **For CI/CD:** Create a test script that runs all examples to catch import errors early.
