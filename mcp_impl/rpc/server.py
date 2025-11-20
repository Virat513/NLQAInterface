"""JSON-RPC-like MCP-compatible server (lightweight, protocol-compatible implementation).

Supports methods:
- initialize -> returns server metadata
- tools.list -> returns list of tools
- tools.call -> call a registered tool
- shutdown -> exit

Communicates via JSON lines over stdio using simple request/response objects with an "id" field.
"""
import json
import sys
import traceback

# Ensure project root is on sys.path so package imports work when this script
# is executed as `python mcp_impl/rpc/server.py` (which sets sys.path[0]
# to the `mcp_impl/rpc` directory). Insert the repository root at the front.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from mcp_impl.tools.playwright_generator import generate_playwright_test

TOOLS = {
    "generate_playwright_test": {
        "name": "generate_playwright_test",
        "description": "Generate Playwright test code from natural language instructions",
        "input_schema": {
            "type": "object",
            "properties": {
                "instruction": {"type": "string", "description": "Natural language test scenario"}
            },
            "required": ["instruction"]
        }
    }
}

METADATA = {
    "name": "playwright-jsonrpc-server",
    "version": "0.1",
    "description": "Lightweight JSON-RPC-compatible server exposing Playwright code generation tools",
}


def _send(resp: dict):
    sys.stdout.write(json.dumps(resp, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def _handle_request(req: dict) -> dict:
    try:
        method = req.get("method")
        params = req.get("params", {})
        if method == "initialize":
            # log to stderr for observability
            print(f"[RPC server] initialize called", file=sys.stderr)
            return {"result": {"metadata": METADATA}}
        if method == "tools.list":
            print(f"[RPC server] tools.list called", file=sys.stderr)
            return {"result": {"tools": list(TOOLS.values())}}
        if method == "tools.call":
            tool = params.get("tool")
            arguments = params.get("args", {})
            print(f"[RPC server] tools.call {tool}", file=sys.stderr)
            if tool == "generate_playwright_test":
                instruction = arguments.get("instruction", "")
                if not instruction:
                    return {"error": "instruction is required"}
                # Call the generator (may raise)
                result = generate_playwright_test(instruction)
                return {"result": {"text": result}}
            return {"error": f"Unknown tool: {tool}"}
        if method == "shutdown":
            print(f"[RPC server] shutdown requested", file=sys.stderr)
            return {"result": "shutting down"}
        return {"error": f"Unknown method: {method}"}
    except Exception as e:
        tb = traceback.format_exc()
        return {"error": str(e), "trace": tb}


def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            _send({"id": None, "error": "invalid json"})
            continue
        req_id = req.get("id")
        resp = _handle_request(req)
        # Wrap with id
        out = {"id": req_id}
        out.update(resp)
        _send(out)
        # handle shutdown
        if req.get("method") == "shutdown":
            break


if __name__ == "__main__":
    main()
