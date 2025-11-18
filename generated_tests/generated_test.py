from playwright.sync_api import sync_playwright

def test_signup_with_valid_username_and_valid_password():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://example.com/signup")
        page.fill("input[name='username']", "valid_username")
        page.fill("input[name='password']", "valid_password")
        page.click("button[type='submit']")
        page.wait_for_selector("text=Signup successful", timeout=5000)
        browser.close()

def test_signup_with_valid_username_and_invalid_password():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://example.com/signup")

        # Fill in the signup form
        page.fill("input[name='username']", "valid_username")
        page.fill("input[name='password']", "invalid")

        # Submit the form
        page.click("button[type='submit']")

        # Verify the error message for invalid password
        assert page.locator("text='Invalid password'").is_visible()

        # Close the browser
        browser.close()
