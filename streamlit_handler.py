import streamlit as st
from code_generator import generate_code
import os

os.makedirs("generated_tests", exist_ok=True)

st.title("Playwright Test Code Generator")

# Keep generated code between reruns
if "generated_code" not in st.session_state:
    st.session_state.generated_code = None

nl_input = st.text_area("Enter your test instruction:")

# --- Generate Button ---
if st.button("Generate Code", key="generate_btn"):
    if nl_input.strip():
        with st.spinner("Generating Playwright test..."):
            code = generate_code(nl_input)
        # Store this once, do NOT lose it during rerun
        st.session_state.generated_code = code
    else:
        st.error("Please enter an instruction.")

# --- Show Generated Code Only If Exists ---
if st.session_state.generated_code:
    st.subheader("Generated Playwright Test Code")
    st.code(st.session_state.generated_code, language="python")

    # Save button
    if st.button("Save Code", key="save_btn"):
        file_path = "generated_tests/generated_test.py"

        # APPEND CORRECTLY — write a separator and then append
        with open(file_path, "a", encoding="utf-8") as f:
            f.write("\n\n# ---- New Test Case ----\n")
            f.write(st.session_state.generated_code)
            f.write("\n")

        st.success(f"Saved to {file_path}")
