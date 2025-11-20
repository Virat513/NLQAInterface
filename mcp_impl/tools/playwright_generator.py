"""Playwright test generator using OpenAI.

Provides a single function `generate_playwright_test(instruction: str) -> str`
that returns Python test code (Playwright sync API) generated from a
natural-language instruction.

This is intentionally small and dependency-light: it expects the `openai`
package to be installed and `OPENAI_API_KEY` to be set in the environment.
"""
from __future__ import annotations

import os
from typing import Any

try:
    import openai
    from openai import OpenAI
except Exception as e:  # pragma: no cover - descriptive runtime error
    raise RuntimeError("openai package is required. Install via `pip install openai`") from e


def _get_openai_client() -> Any:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment")
    openai.api_key = api_key
    return openai


def generate_playwright_test(instruction: str) -> str:
    """Generate Playwright test code from `instruction` using OpenAI.

    Returns a string containing a complete Python test function using
    `playwright.sync_api.sync_playwright`.
    """
    if not instruction or not instruction.strip():
        raise ValueError("instruction is required")

    oai = _get_openai_client()

    system = (
        "You are a helpful assistant that outputs a single Python Playwright "
        "test using the synchronous Playwright API. ONLY output valid Python code. "
        "Do not include commentary or markdown fences. The test should use "
        "`from playwright.sync_api import sync_playwright` and define a single "
        "function named `test_generated` that implements the requested steps. "
        "Keep imports minimal and the test deterministic (avoid randomness)."
    )

    user = f"Write a Playwright test that {instruction}."

    # Use new OpenAI client interface (OpenAI >=1.0.0)
    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=800,
        temperature=0,
    )

    choices = getattr(resp, "choices", None)
    if not choices:
        raise RuntimeError("OpenAI returned no completion choices")

    # New response object typically has .message.content
    first = choices[0]
    text = None
    if hasattr(first, "message") and hasattr(first.message, "content"):
        text = first.message.content
    else:
        # fallback to dict-like access
        text = getattr(first, "text", None) or (
            first.get("message", {}).get("content") if isinstance(first, dict) else None
        )

    if not text:
        raise RuntimeError("OpenAI returned empty response")

    return text.strip()
