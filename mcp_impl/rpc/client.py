"""Client for the JSON-RPC-compatible MCP server under mcp_impl/rpc.

Spawns the server as a subprocess and sends JSON requests with incremental ids.
Waits for responses and returns the result. Logs server stderr to a file.
"""
import json
import subprocess
import threading
import queue
import time
import os
from typing import Any, Optional


class RPCPlaywrightClient:
    def __init__(self, server_command: list = None):
        self.server_command = server_command or ["python", "mcp_impl/rpc/server.py"]
        self.process: Optional[subprocess.Popen] = None
        self._resp_q = queue.Queue()
        self._reader_thread = None
        self.log_file = ".rpc_server.log"
        self._stderr_thread = None
        self._next_id = 1
    
    def _reader(self):
        assert self.process is not None
        for line in self.process.stdout:
            if not line:
                break
            try:
                obj = json.loads(line)
            except Exception:
                continue
            self._resp_q.put(obj)

    def _stderr_logger(self):
        """Log server stderr to a file to avoid blocking/stderr-related errors on Windows."""
        assert self.process is not None
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                for line in self.process.stderr:
                    if not line:
                        break
                    f.write(line)
                    f.flush()
        except Exception:
            pass
    
    async def __aenter__(self):
        # start process
        self.process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        # start reader thread
        self._reader_thread = threading.Thread(target=self._reader, daemon=True)
        self._reader_thread.start()
        # start stderr logger thread to avoid blocked stderr on Windows
        self._stderr_thread = threading.Thread(target=self._stderr_logger, daemon=True)
        self._stderr_thread.start()
        # small boot wait
        time.sleep(0.05)
        if self.process.poll() is not None:
            stderr = self.process.stderr.read() if self.process.stderr else ""
            raise RuntimeError(f"Server failed to start: {stderr}")
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        try:
            await self._call_method("shutdown", {})
        except Exception:
            pass
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except Exception:
                self.process.kill()

    
    def _send(self, payload: dict):
        if not self.process or not self.process.stdin:
            raise RuntimeError("Server process not running")
        self.process.stdin.write(json.dumps(payload) + "\n")
        self.process.stdin.flush()
    
    def _wait_for_id(self, req_id: int, timeout: float = 60.0) -> dict:
        start = time.time()
        while time.time() - start < timeout:
            try:
                obj = self._resp_q.get(timeout=timeout)
            except queue.Empty:
                continue
            if obj.get("id") == req_id:
                return obj
            # else, put it back for other waiters
            # but to avoid losing responses, requeue
            self._resp_q.put(obj)
        raise RuntimeError("Timeout waiting for response")
    
    async def _call_method(self, method: str, params: dict) -> Any:
        req_id = self._next_id
        self._next_id += 1
        payload = {"id": req_id, "method": method, "params": params}
        self._send(payload)
        resp = self._wait_for_id(req_id)
        if "error" in resp:
            raise RuntimeError(resp.get("error"))
        return resp.get("result")
    
    async def generate_test(self, instruction: str) -> str:
        res = await self._call_method("tools.call", {"tool": "generate_playwright_test", "args": {"instruction": instruction}})
        # result expected as {"text": "..."}
        if isinstance(res, dict) and "text" in res:
            return res["text"]
        return str(res)


class SyncRPCClient:
    """Synchronous client for the RPC server. Useful for synchronous callers like Streamlit.

    Usage:
        client = SyncRPCClient()
        client.start()
        try:
            code = client.generate_test("...")
        finally:
            client.stop()
    
    Server stderr is logged to `.rpc_server.log` in the current working directory.
    """
    def __init__(self, server_command: list = None, log_file: str = ".rpc_server.log"):
        self.server_command = server_command or ["python", "mcp_impl/rpc/server.py"]
        self.process: Optional[subprocess.Popen] = None
        self._resp_q = queue.Queue()
        self._reader_thread = None
        self._next_id = 1
        self.log_file = log_file
        self._stderr_thread = None

    def _reader(self):
        assert self.process is not None
        for line in self.process.stdout:
            if not line:
                break
            try:
                obj = json.loads(line)
            except Exception:
                continue
            self._resp_q.put(obj)

    def _stderr_logger(self):
        """Log server stderr to a file to avoid blocking/stderr-related errors on Windows."""
        assert self.process is not None
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                for line in self.process.stderr:
                    if not line:
                        break
                    f.write(line)
                    f.flush()
        except Exception:
            # Swallow errors — this logger is best-effort
            pass


    def start(self):
        if self.process is not None:
            return
        self.process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._reader_thread = threading.Thread(target=self._reader, daemon=True)
        self._reader_thread.start()
        self._stderr_thread = threading.Thread(target=self._stderr_logger, daemon=True)
        self._stderr_thread.start()
        time.sleep(0.05)
        if self.process.poll() is not None:
            stderr = self.process.stderr.read() if self.process.stderr else ""
            raise RuntimeError(f"Server failed to start: {stderr}")

    def stop(self):
        if not self.process:
            return
        try:
            # ask server to shutdown
            self._send({"id": -1, "method": "shutdown", "params": {}})
        except Exception:
            pass
        try:
            self.process.terminate()
            self.process.wait(timeout=3)
        except Exception:
            try:
                self.process.kill()
            except Exception:
                pass
        self.process = None

    def _send(self, payload: dict):
        if not self.process or not self.process.stdin:
            raise RuntimeError("Server process not running")
        self.process.stdin.write(json.dumps(payload) + "\n")
        self.process.stdin.flush()

    def _wait_for_id(self, req_id: int, timeout: float = 60.0) -> dict:
        start = time.time()
        while time.time() - start < timeout:
            try:
                obj = self._resp_q.get(timeout=timeout)
            except queue.Empty:
                continue
            if obj.get("id") == req_id:
                return obj
            # otherwise, requeue
            self._resp_q.put(obj)
        raise RuntimeError("Timeout waiting for response")

    def _call_method(self, method: str, params: dict, timeout: float = 120.0) -> Any:
        if not self.process:
            raise RuntimeError("Server not started. Call start() first.")
        req_id = self._next_id
        self._next_id += 1
        payload = {"id": req_id, "method": method, "params": params}
        self._send(payload)
        resp = self._wait_for_id(req_id, timeout=timeout)
        if "error" in resp:
            raise RuntimeError(resp.get("error"))
        return resp.get("result")

    def generate_test(self, instruction: str) -> str:
        res = self._call_method("tools.call", {"tool": "generate_playwright_test", "args": {"instruction": instruction}})
        if isinstance(res, dict) and "text" in res:
            return res["text"]
        return str(res)
