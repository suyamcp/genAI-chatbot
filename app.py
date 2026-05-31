import streamlit as st

# Configure the browser interface
st.set_page_config(page_title="Accenture Helpdesk Bot", page_icon="🛡️")
st.title("🛡️ Enterprise IT Helpdesk Copilot")
st.caption("A Capstone Prototype for Cloud Elite")

# --- MOCK ENTERPRISE DATABASE ---
# This dictionary replaces your Cloud Storage documents during local testing
KNOWLEDGE_BASE = {
    "vpn": "Baguio Office Network Policy: To connect to the secure local VPN after the June 2026 M365 migration, employees must use the Cisco AnyConnect client pointed to client.baguio.accenture.local. Do not use the old global portal gateway.",
    "allowance": "Accenture Academy Track Intern Benefits: Active interns under the Cloud Elite track are allocated a monthly data connectivity allowance of PHP 1,500 to support virtual training modules.",
    "password": "M365 Authentication Protocol: Standard enterprise domain passwords must be changed every 90 days. Passwords must contain at least 14 characters, including upper case, lower case, numbers, and symbols."
}

# Initialize session chat history tracking
if "messages" not in st.session_state:
    st.session_state.messages = []
#yes daddy
# Display previous conversation streams
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process live user queries
if user_query := st.chat_input("Ask me about Accenture policies..."):
    # Render user query
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # --- RETRIEVAL PHASE (RAG Simulation) ---
    # Scan the question for keywords to pull context from our knowledge base
    context_found = "No relevant enterprise document context was discovered for this prompt."
    query_lower = user_query.lower()
    
    if "vpn" in query_lower or "network" in query_lower or "connect" in query_lower:
        context_found = KNOWLEDGE_BASE["vpn"]
    elif "allowance" in query_lower or "intern" in query_lower or "money" in query_lower:
        context_found = KNOWLEDGE_BASE["allowance"]
    elif "password" in query_lower or "m365" in query_lower or "account" in query_lower:
        context_found = KNOWLEDGE_BASE["password"]

    # --- GENERATION PHASE ---
    with st.chat_message("assistant"):
        # Construct response displaying the fetched reference doc
        response_text = f"### 🔍 Verified Document Source:\n> {context_found}\n\n"
        
        if context_found != "No relevant enterprise document context was discovered for this prompt.":
            response_text += "### 🤖 AI Summary:\nBased on current internal protocols, follow those explicit instructions to resolve your issue."
        else:
            response_text += "### 🤖 AI Summary:\nI cannot find an official internal document to reference for this query. Please check with an HR manager."
            
        st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
