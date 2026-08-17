import streamlit as st
from google import genai
from google.genai import errors

# 1. Page Configuration
st.set_page_config(
    page_title="Gemini Clone",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. Securely Load API Key (Checks Streamlit Secrets first, then Environment Variables)
api_key = None
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    import os
    api_key = os.environ.get("GEMINI_API_KEY")

# 3. Inject Custom CSS to Match Gemini's Dark UI Style
st.markdown("""
<style>
    .stApp {
        background-color: #131314;
        color: #e3e3e3;
        font-family: 'Inter', sans-serif;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stChatMessage {
        background-color: transparent !important;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
    }
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1e1f20 !important;
        border: 1px solid #333537;
    }
    .stChatInput input {
        color: #e3e3e3 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #1e1f20;
        border-right: 1px solid #333537;
    }
    .gemini-header {
        text-align: center;
        background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .gemini-subheader {
        text-align: center;
        color: #8e918f;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# 4. Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    selected_model = st.selectbox(
        "Choose Model",
        ["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0
    )
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #8e918f; font-size: 0.8rem;'>Built with Python & Google GenAI SDK</p>", unsafe_allow_html=True)

# 5. Main UI Layout
st.markdown('<p class="gemini-header">Hello, human</p>', unsafe_allow_html=True)
st.markdown('<p class="gemini-subheader">How can I help you today?</p>', unsafe_allow_html=True)

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing! Please set it in your local environment variables or Streamlit secrets.")
    st.stop()

# Initialize Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages onto the UI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Handle User Input & API Generation
if prompt := st.chat_input("Enter a prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            client = genai.Client(api_key=api_key)
            
            chat_history_formatted = [
                {"role": m["role"], "parts": [{"text": m["content"]}]} 
                for m in st.session_state.messages
            ]
            
            response_stream = client.models.generate_content_stream(
                model=selected_model,
                contents=chat_history_formatted
            )
            
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except errors.APIError as e:
            full_response = f"❌ **API Error:** {e}"
            message_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"❌ **Error:** {str(e)}"
            message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "model", "content": full_response})
