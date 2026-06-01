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
            
            try:
                # Call the live generative model using your custom persona
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=grounded_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.3, # Low temperature ensures it sticks strictly to the PDF text
                    )
                )
                response_text = response.text
                
            except Exception as e:
                response_text = f"⚠️ **API Connection Error:** Unable to reach Gemini. Technical details: {e}"
            
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})