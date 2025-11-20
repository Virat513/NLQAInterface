# NLQAInterface — MCP Integration

This project demonstrates integrating an MCP-style tool server with a Streamlit UI using a JSON-RPC-based MCP implementation.

## Architecture

- **`mcp_impl/rpc/`** — The primary implementation: a lightweight JSON-RPC-compatible server and client with persistent subprocess connection, stderr logging, and synchronous/asynchronous wrapper support.
- **`mcp_impl/tools/`** — Core code generation logic (OpenAI API integration for Playwright test generation).
- **`streamlit_handler.py`** — Streamlit UI with integrated RPC client, server health indicator, and log viewer.

## Prerequisites

- Python 3.10+ (your environment)
- Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

- `OPENAI_API_KEY` must be set in the environment:

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

## Run Instructions

### 1) Start Streamlit UI

```powershell
streamlit run streamlit_handler.py
# Open http://localhost:8501
```

Features:
- ✓ RPC Server Running / ○ RPC Server Idle indicator
- Stop RPC Server button
- View server logs link
- Generate Playwright test code from natural language
- Save generated tests to `generated_tests/`

### 2) Run RPC E2E Test (Manual)

```powershell
python -m mcp_impl.rpc.test_e2e
```

This validates that the RPC server can be spawned, initialized, and can generate code correctly.

