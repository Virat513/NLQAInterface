import streamlit as st
from code_generator import generate_code
import os
import subprocess

# Ensure tests folder exists
os.makedirs("generated_tests", exist_ok=True)

st.title("Playwright Test Code Generator")

# Helper: Check if at least one test file exists
def has_tests():
    test_files = [f for f in os.listdir("generated_tests") if f.endswith(".py")]
    return len(test_files) > 0

# Keep generated code between reruns
if "generated_code" not in st.session_state:
    st.session_state.generated_code = None

nl_input = st.text_area("Enter your test instruction:")

# --- Generate Button ---
if st.button("Generate Code", key="generate_btn"):
    if nl_input.strip():
        with st.spinner("Generating Playwright test..."):
            code = generate_code(nl_input)
        st.session_state.generated_code = code
    else:
        st.error("Please enter an instruction.")

# --- Show Generated Code Only If Exists ---
if st.session_state.generated_code:
    st.subheader("Generated Playwright Test Code")
    st.code(st.session_state.generated_code, language="python")

    # NEW: File name input
    file_name = st.text_input(
        "Enter file name (optional):",
        placeholder="example: login_test.py"
    )

    # Save button
    if st.button("Save Code", key="save_btn"):

        # If user provides a file name, use it
        if file_name.strip():
            if not file_name.endswith(".py"):
                file_name += ".py"
            file_path = f"generated_tests/{file_name}"

        # Else auto-generate
        else:
            base = "test_case"
            i = 1
            while os.path.exists(f"generated_tests/{base}_{i}.py"):
                i += 1
            file_path = f"generated_tests/{base}_{i}.py"

        # Write the new file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(st.session_state.generated_code)
            f.write("\n")

        st.success(f"Saved to {file_path}")

# ---------------------------------------------------------
# ---- Run Tests Button (only when at least 1 test exists)
# ---------------------------------------------------------
st.write("---")

if has_tests():
    st.subheader("Run Your Tests")

    if st.button("Run Tests"):
        report_file = "test-report.html"
        command = [
            "pytest",
            "generated_tests",
            f"--html={report_file}",
            "--self-contained-html"
        ]

        with st.spinner("Running Playwright tests..."):
            result = subprocess.run(
                command, capture_output=True, text=True, shell=True
            )

        st.subheader("Pytest Output")
        st.code(result.stdout)

        if result.stderr:
            st.error("Errors:")
            st.code(result.stderr)

        if os.path.exists(report_file):
            st.success("HTML Test Report Generated!")
            with open(report_file, "r", encoding="utf-8") as f:
                html = f.read()
            st.components.v1.html(html, height=800, scrolling=True)
else:
    st.info("Add at least one test before running.")
