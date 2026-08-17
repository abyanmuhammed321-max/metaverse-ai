import streamlit as st
import os
from google import genai

# Page configuration
st.set_page_config(
    page_title="Metaverse AI",
    page_icon="🌌",
    layout="wide"
)

# Initialize Gemini Client safely
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # Allow user to input key via sidebar if not set in environment
    with st.sidebar:
        st.subheader("🔑 Authentication Required")
        api_key = st.text_input("Enter your Gemini API Key", type="password")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key

try:
    client = genai.Client(api_key=api_key) if api_key else genai.Client()
except Exception as e:
    st.error(f"Failed to initialize Gemini Client: {e}")
    client = None

# Initialize session state for multi-chat support
if "sessions" not in st.session_state:
    st.session_state.sessions = {
        "Default Chat": {
            "title": "Default Chat",
            "messages": []
        }
    }

if "active_session" not in st.session_state:
    st.session_state.active_session = "Default Chat"

# Sidebar for managing chats
with st.sidebar:
    st.title("🌌 Metaverse AI")
    st.markdown("---")
    
    if st.button("➕ New Chat", use_container_width=True):
        new_title = f"Chat {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_title] = {"title": new_title, "messages": []}
        st.session_state.active_session = new_title
        st.rerun()
        
    st.subheader("Your Conversations")
    selected_chat = st.radio(
        "Select Chat",
        list(st.session_state.sessions.keys()),
        index=list(st.session_state.sessions.keys()).index(st.session_state.active_session),
        label_visibility="collapsed"
    )
    
    if selected_chat != st.session_state.active_session:
        st.session_state.active_session = selected_chat
        st.rerun()

# Main Chat Interface
current_session = st.session_state.sessions[st.session_state.active_session]

st.title(f"💬 {current_session['title']}")

# Render existing chat history
for msg in current_session["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask your neon AI anything..."):
    if not client:
        st.error("❌ Gemini API Key is missing. Please provide it in the sidebar or set your `GEMINI_API_KEY` environment variable.")
    else:
        # 1. Append and display user message immediately
        current_session["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Update chat title if it's the first message
        if current_session["title"].startswith("Chat ") or current_session["title"] == "Default Chat":
            current_session["title"] = prompt[:22] + ("..." if len(prompt) > 22 else "")

        # 2. Generate response from Gemini using stateless history formatting
        with st.chat_message("assistant"):
            with st.spinner("Thinking through neural pathways..."):
                try:
                    # Format previous messages for the Gemini API structure
                    formatted_contents = []
                    for m in current_session["messages"]:
                        role = "user" if m["role"] == "user" else "model"
                        formatted_contents.append({
                            "role": role,
                            "parts": [{"text": m["content"]}]
                        })

                    # Call Gemini 2.5 Flash model
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=formatted_contents
                    )
                    
                    reply = response.text if hasattr(response, 'text') and response.text else "No response generated."
                    st.markdown(reply)
                    
                    # Append assistant response to history
                    current_session["messages"].append({"role": "assistant", "content": reply})
                    
                except Exception as e:
                    st.error(f"⚠️ API Error: {str(e)}")
        
        st.rerun()
