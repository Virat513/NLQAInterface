import streamlit as st
import os
from code_generator import generate_code

os.makedirs("generated_tests", exist_ok=True)

st.set_page_config(page_title="Playwright Test Generator", layout="centered")
st.title("Playwright Test Generator")

nl_input = st.text_area("Enter test instruction (natural language)", height=200)

# Session variable to hold generated code temporarily
if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""

if st.button("Generate Code"):
    if not nl_input.strip():
        st.error("Please enter a test instruction.")
    else:
        with st.spinner("Generating test code..."):
            code = generate_code(nl_input)
            st.session_state.generated_code = code

if st.session_state.generated_code:
    st.subheader("Generated Test Code")
    st.code(st.session_state.generated_code, language="python")

    if st.button("Save Code"):
        file_path = os.path.join("generated_tests", "generated_test.py")

        with open(file_path, "a", encoding="utf-8") as f:
            f.write("\n\n# -------------------- New Test Case --------------------\n")
            f.write(st.session_state.generated_code)
        st.success(f"Code appended to {file_path}")
