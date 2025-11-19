from .tool_server import ToolServer

def run_tool_generate(instruction: str, test_name: str = None):
    """
    Synchronous wrapper that mimics a tool call.
    Returns (message, code).
    """
    server = ToolServer()
    msg, code = server.generate_playwright_test(instruction=instruction, test_name=test_name)
    return msg, code
