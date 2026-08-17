import streamlit as st
from google import genai
from google.genai import errors

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="Gemini Clone",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. Inject Custom CSS to Match Gemini's Dark UI Style
st.markdown("""
<style>
    /* Main background & font styling */
    .stApp {
        background-color: #131314;
        color: #e3e3e3;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide default Streamlit header/footer elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Style chat message bubbles */
    .stChatMessage {
        background-color: transparent !important;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    /* User prompt box styling */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1e1f20 !important;
        border: 1px solid #333537;
    }

    /* Fix text color in chat input area */
    .stChatInput input {
        color: #e3e3e3 !important;
    }
    
    /* Custom Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1e1f20;
        border-right: 1px solid #333537;
    }
    
    /* Center title header styling */
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

# 3. Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key_input = st.text_input("Gemini API Key", type="password", help="Enter your Google AI Studio API Key")
    
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

# 4. Main UI Layout
st.markdown('<p class="gemini-header">Hello, human</p>', unsafe_allow_html=True)
st.markdown('<p class="gemini-subheader">How can I help you today?</p>', unsafe_allow_html=True)

# Initialize Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages onto the UI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Handle User Input & API Generation
if prompt := st.chat_input("Enter a prompt here..."):
    # Check if API key is supplied
    if not api_key_input and not "GEMINI_API_KEY" in st.secrets:
        st.error("⚠️ Please enter your Gemini API Key in the sidebar settings to proceed.")
        st.stop()
    
    # Resolve API Key source (sidebar input or deployment secrets)
    active_api_key = api_key_input if api_key_input else st.secrets.get("GEMINI_API_KEY")

    # Append and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant response with Gemini
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Initialize official GenAI client
            client = genai.Client(api_key=active_api_key)
            
            # Convert previous messages into the history structure required by the SDK if needed,
            # or use simple stateless/stream generation. Here we format contents for the stream call:
            chat_history_formatted = [
                {"role": m["role"], "parts": [{"text": m["content"]}]} 
                for m in st.session_state.messages
            ]
            
            # Request streaming content from Gemini model
            response_stream = client.models.generate_content_stream(
                model=selected_model,
                contents=chat_history_formatted
            )
            
            # Stream chunks dynamically into the UI box
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

        # Append model response to session state history
        st.session_state.messages.append({"role": "model", "content": full_response})
