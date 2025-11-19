import os
from typing import Tuple
from code_generator import generate_code

ROOT_TESTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_tests")
os.makedirs(ROOT_TESTS_DIR, exist_ok=True)
TEST_FILE = os.path.join(ROOT_TESTS_DIR, "generated_test.py")

class ToolServer:
    def generate_playwright_test(self, instruction: str, test_name: str = None) -> Tuple[str, str]:
        code = generate_code(instruction)
        with open(TEST_FILE, "a", encoding="utf-8") as f:
            f.write(code)
            f.write("\n")
        message = f"Added new test to {TEST_FILE}"
        return message, code
