from openai import OpenAI
client = OpenAI()

def generate_code(nl_input):
    prompt = f"""
You are an expert Playwright automation engineer.
Convert the following natural language test scenario into a complete Python Playwright test script.

The output MUST follow these rules:
- Output ONLY valid Python code
- involve imports
- Must include sync Playwright  code
- Must be executable as-is
- Do not provide any additional text outside the code like '''python''' or explanations
- Make the name of test with test_ prefix and descriptive
- No need to create a main function

Scenario:
{nl_input}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )

    return response.choices[0].message.content

