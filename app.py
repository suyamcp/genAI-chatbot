import streamlit as st
import os
from pypdf import PdfReader
from google import genai
from google.genai import types

# Configure the browser interface
st.set_page_config(page_title="Accenture Helpdesk Bot", page_icon="🛡️")
st.title("🛡️ Enterprise IT Helpdesk Copilot")
st.caption("A Capstone Prototype for Cloud Elite")

# 1. Initialize the live Gemini client
# (Ensure your GEMINI_API_KEY environment variable is set up in your system)
client = genai.Client()

# 2. Define your AI's custom persona instructions
SYSTEM_INSTRUCTION = """
You are the Enterprise IT Helpdesk Copilot, an elite, highly professional, 
and supportive AI assistant for corporate employees. 
Your persona is knowledgeable, empathetic, clear, and slightly witty.

CRITICAL RULE: You must ONLY answer questions using the verified document context provided. 
If the context does not contain the answer, politely state that you cannot find an 
official internal document and advise them to check with an HR manager. Do not make up profiles or data.
"""

# 3. Helper function to read all PDFs in your local documents folder
def load_local_documents():
    docs_folder = "./documents"
    combined_text = ""
    
    if os.path.exists(docs_folder):
        for filename in os.listdir(docs_folder):
            if filename.endswith(".pdf"):
                path = os.path.join(docs_folder, filename)
                try:
                    reader = PdfReader(path)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            combined_text += f"\n--- Source: {filename} ---\n" + text
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
    return combined_text

# Initialize session chat history tracking
if "messages" not in st.session_state:
    st.session_state.messages = []

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

    with st.chat_message("assistant"):
        with st.spinner("Searching internal document repositories..."):
            # Execute text extraction from your sidebar 'documents' folder
            document_context = load_local_documents()
            
            # If the folder is empty or text extraction failed entirely
            if not document_context.strip():
                document_context = "No internal reference documents found in system storage."

            # Construct the grounded prompt pairing the document with the query
            grounded_prompt = f"""
            User Question: {user_query}
            
            Verified Reference Document Context:
            {document_context}
            """
            
            # --- GENERATION PHASE WITH AUTOMATIC RETRY ---
            import time

            response_text = ""
            max_retries = 3
            retry_delay = 2  # wait 2 seconds before retrying

            for attempt in range(max_retries):
                try:
                    # Pointing cleanly back to the main 2.5 flash model
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=grounded_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            temperature=0.3,
                        )
                    )
                    response_text = response.text
                    break  # Success! Break out of the retry loop
                    
                except Exception as e:
                    # Check if it's a 503 server congestion error
                    if "503" in str(e) and attempt < max_retries - 1:
                        with st.spinner(f"Server is busy (503). Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})"):
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                    else:
                        # If it's a different error (like 404) or we ran out of retries
                        response_text = f"⚠️ **API Connection Error:** Unable to reach Gemini. Technical details: {e}"
                        break
            
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})