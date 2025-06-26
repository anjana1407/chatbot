import streamlit as st
from assistant_core import setup_assistant, get_response
import os

st.set_page_config(page_title="Context AI Bot", layout="centered")
st.title("Context-Based Chatbot")

# Initialize session state
if "context" not in st.session_state:
    st.session_state.context = ""
if "email_list" not in st.session_state:
    st.session_state.email_list = []
if "assistant_ready" not in st.session_state:
    st.session_state.assistant_ready = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# Training Content Section
st.header("Training Content")
context_input = st.text_area("Paste training content below:", height=200, value=st.session_state.context)

if st.button("Save Context"):
    if context_input.strip():
        try:
            # Save context to file
            with open("context.txt", "w", encoding="utf-8") as f:
                f.write(context_input.strip())
            
            # Setup assistant
            with st.spinner("Setting up assistant..."):
                success = setup_assistant(context_input.strip())
            
            if success:
                st.session_state.context = context_input.strip()
                st.session_state.assistant_ready = True
                st.success("Context saved and assistant created successfully!")
            else:
                st.error("Failed to create assistant. Please check your API key.")
                
        except Exception as e:
            st.error(f"Error saving context: {str(e)}")
    else:
        st.warning("Please provide some training content.")

# Display current context status
if st.session_state.context:
    st.info(f"Training content loaded ({len(st.session_state.context)} characters)")

# Email Section
st.header("Your Email")
email = st.text_input("Enter your email")

if st.button("Save Email"):
    if email and "@" in email:
        if email not in st.session_state.email_list:
            st.session_state.email_list.append(email)
            st.success(f"Email saved: {email}")
        else:
            st.info("Email already saved.")
    else:
        st.error("Please enter a valid email address.")

# Display saved emails
if st.session_state.email_list:
    st.write("Saved emails:", ", ".join(st.session_state.email_list))

# Chat Section
st.header("Chat with the Assistant")

# Check if assistant is ready
if not st.session_state.assistant_ready:
    st.warning("Please save training content first to activate the assistant.")
elif not st.session_state.context:
    st.warning("No training content available. Please add training content.")
else:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question based on the training content"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_response(prompt, st.session_state.email_list)
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar info
with st.sidebar:
    st.header("System Status")
    st.write(f"Assistant Status: {'Ready' if st.session_state.assistant_ready else 'Not Ready'}")
    st.write(f"Training Content: {'Loaded' if st.session_state.context else 'Empty'}")
    st.write(f"Saved Emails: {len(st.session_state.email_list)}")
    
    if st.button("Reset All"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        # Clear context file
        if os.path.exists("context.txt"):
            os.remove("context.txt")
        st.rerun()