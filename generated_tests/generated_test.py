

# -------------------- New Test Case --------------------
```python
from playwright.sync_api import sync_playwright

def test_search_with_invalid_string():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        page.goto("https://example.com")
        page.fill("input[name='search']", "invalid_string")
        page.click("button[type='submit']")
        
        assert page.locator("text=No results found").is_visible()  # Assuming an element appears when there are no results

        browser.close()
```