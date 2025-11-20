import streamlit as st
import os

os.makedirs("generated_tests", exist_ok=True)

st.title("Playwright Test Code Generator")

if "generated_code" not in st.session_state:
    st.session_state.generated_code = None


# Health indicator for RPC server
col1, col2 = st.columns([3, 1])
with col1:
    st.write("")  # spacing
with col2:
    rpc_client = st.session_state.get("rpc_client")
    if rpc_client is not None and rpc_client.process is not None and rpc_client.process.poll() is None:
        st.success("✓ RPC Server Running")
    else:
        st.info("○ RPC Server Idle")


def generate_code_via_rpc(instruction: str) -> str:
    """Generate Playwright test code using the RPC-based MCP server."""
    from mcp_impl.rpc.client import SyncRPCClient

    client = st.session_state.get("rpc_client")
    if client is None:
        client = SyncRPCClient(server_command=["python", "mcp_impl/rpc/server.py"])
        client.start()
        st.session_state["rpc_client"] = client

    return client.generate_test(instruction)


nl_input = st.text_area("Enter your test instruction:")

# --- Generate Button ---
if st.button("Generate Code", key="generate_btn"):
    if nl_input.strip():
        with st.spinner("Generating Playwright test..."):
            try:
                code = generate_code_via_rpc(nl_input)
                st.session_state.generated_code = code
            except Exception as e:
                st.error(f"Error generating code: {str(e)}")
    else:
        st.error("Please enter an instruction.")
        
# Stop RPC server button
rpc_client = st.session_state.get("rpc_client")
if rpc_client is not None:
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("Stop RPC Server", key="stop_rpc"):
            try:
                rpc_client.stop()
            except Exception:
                pass
            del st.session_state["rpc_client"]
            st.success("RPC server stopped")
    # Show log file link if it exists
    if os.path.exists(".rpc_server.log"):
        with col3:
            st.write("")  # spacing
        st.caption("📋 [View server logs](.rpc_server.log)")

if st.session_state.generated_code:
    st.subheader("Generated Playwright Test Code")
    st.code(st.session_state.generated_code, language="python")

    # Save button
    if st.button("Save Code", key="save_btn"):
        file_path = "generated_tests/generated_test.py"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(st.session_state.generated_code)
            f.write("\n\n")

        st.info(f"Appended to {file_path}")
