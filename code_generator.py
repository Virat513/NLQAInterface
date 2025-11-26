from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def generate_code(nl_input):
    prompt = f"""
        You are an expert Playwright automation engineer.
        Convert the following natural language test scenario into a complete Python Playwright test script.

        RULES:
        - Output ONLY valid Python code.
        - Use Playwright sync API (not async).
        - Include imports ONLY if they are not already present.
        - The test name must start with test_ and be descriptive.
        - The code must be runnable directly by pytest.
        - Do not include any extra text or code fences.
        - Use stable and recommended selectors for www.saucedemo.com

        Here are the correct element selectors for https://www.saucedemo.com:

        Login Page:
        - Username input:  #user-name
        - Password input:  #password
        - Login button:    #login-button
        - Error message:   data-test="error"

        Inventory Page:
        - Inventory items: .inventory_item
        - Add to cart:     button[data-test='add-to-cart-<item-name>']
        - Cart badge:      .shopping_cart_badge
        - Cart button:     .shopping_cart_link

        Cart Page:
        - Checkout button: data-test="checkout"

        Checkout Step 1:
        - First Name:  #first-name
        - Last Name:   #last-name
        - Postal Code: #postal-code
        - Continue:    #continue

        Checkout Step 2:
        - Finish:       #finish
        - Cancel:       #cancel

        Order Complete Page:
        - Order message: .complete-header

        Scenario:
        {nl_input}
        """


    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    return response.output_text
