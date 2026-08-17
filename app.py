import os
import uuid
import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration & Mobile Support
st.set_page_config(
    page_title="Metaverse AI - Gemini Edition",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="auto"
)

# 2. Modern Neon Styling & Mobile Responsiveness
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at center, #0a0b10, #121420, #06070b);
        color: #e2e8f0;
    }
    h1 {
        color: #00f2fe !important;
        text-shadow: 0 0 12px rgba(0, 242, 254, 0.6);
        font-family: 'Inter', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #0d0f17;
        border-right: 1px solid rgba(0, 242, 254, 0.2);
    }
    .stButton button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: #0a0b10;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
    }
    @media screen and (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.75rem !important;
            max-width: 100% !important;
        }
        h1 {
            font-size: 1.6rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# 3. Google Sign-In Gate
is_logged_in = True
user_name = "Matrix Creator"

try:
    is_logged_in = st.user.is_logged_in
    user_name = getattr(st.user, "name", "User")
except Exception:
    pass 

if not is_logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("✨ Welcome to Metaverse AI")
        st.markdown("Sign in securely with your Google account to access your personal AI matrix.")
        try:
            if st.button("🔐 Log in with Google", use_container_width=True):
                st.login()
        except Exception:
            st.error("Google OAuth is not configured in your Streamlit secrets block.")
    st.stop()

# 4. API Key Configuration
api_key = ""
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY", "")

if not api_key:
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

# 5. Multi-Chat Session State Initialization
if "sessions" not in st.session_state:
    init_id = str(uuid.uuid4())
    st.session_state.sessions = {
        init_id: {
            "title": "New Chat",
            "messages": []
        }
    }
    st.session_state.active_session = init_id

if "active_session" not in st.session_state or st.session_state.active_session not in st.session_state.sessions:
    st.session_state.active_session = list(st.session_state.sessions.keys())[0]

# --- SIDEBAR: NAVIGATION & CHAT MANAGEMENT ---
st.sidebar.title("✨ Metaverse AI")
st.sidebar.markdown(f"👤 **User:** {user_name}")

try:
    if st.sidebar.button("🚪 Log out", use_container_width=True):
        st.logout()
except Exception:
    pass

st.sidebar.markdown("---")

# New Chat Button
if st.sidebar.button("➕ New Chat", use_container_width=True):
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {
        "title": "New Chat",
        "messages": []
    }
    st.session_state.active_session = new_id
    st.rerun()

st.sidebar.markdown("### 💬 Recent Chats")

# Chat List & Deletion Logic
sessions_to_delete = []
for s_id, s_data in list(st.session_state.sessions.items()):
    col_chat, col_del = st.sidebar.columns([4, 1])
    label = f"💬 {s_data['title']}"
    if s_id == st.session_state.active_session:
        label = f"👉 {s_data['title']}"

    with col_chat:
        if st.button(label, key=f"select_{s_id}", use_container_width=True):
            st.session_state.active_session = s_id
            st.rerun()
    with col_del:
        if st.button("🗑️", key=f"del_{s_id}", use_container_width=True):
            sessions_to_delete.append(s_id)

# Handle Deletions Safely
if sessions_to_delete:
    for s_id in sessions_to_delete:
        del st.session_state.sessions[s_id]
    if len(st.session_state.sessions) == 0:
        fallback_id = str(uuid.uuid4())
        st.session_state.sessions[fallback_id] = {
            "title": "New Chat",
            "messages": []
        }
        st.session_state.active_session = fallback_id
    else:
        st.session_state.active_session = list(st.session_state.sessions.keys())[0]
    st.rerun()

st.sidebar.markdown("---")
app_mode = st.sidebar.radio("Core Engine Mode", [
    "💬 Gemini Neural Chat", 
    "👁️ Vision Analyzer"
])

if not api_key:
    st.error("⚠️ Please configure your `GEMINI_API_KEY` in Streamlit Secrets or via the sidebar.")
    st.stop()

# --- MODE 1: GEMINI NEURAL CHAT ---
if app_mode == "💬 Gemini Neural Chat":
    current_session = st.session_state.sessions[st.session_state.active_session]
    st.title("✨ Metaverse AI: Gemini Core")
    st.caption(f"Active Session: {current_session['title']}")

    # Render chat history on screen
    for msg in current_session["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle user prompt input
    if prompt := st.chat_input("Ask your neon AI anything..."):
        # 1. Append user message to state
        current_session["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Set automatic title based on first message
        if current_session["title"] == "New Chat":
            current_session["title"] = prompt[:22] + ("..." if len(prompt) > 22 else "")

        # 2. Generate response securely using fresh chat session creation
        with st.chat_message("assistant"):
            with st.spinner("Thinking through neural pathways..."):
                try:
                    # Build history up to the latest prompt
                    history = []
                    for m in current_session["messages"][:-1]:
                        role = "user" if m["role"] == "user" else "model"
                        history.append({
                            "role": role,
                            "parts": [{"text": m["content"]}]
                        })
                    
                    # Create a fresh chat session and send message
                    chat = client.chats.create(
                        model="gemini-2.5-flash",
                        history=history
                    )
                    response = chat.send_message(prompt)
                    
                    reply = response.text if hasattr(response, 'text') and response.text else "No response generated."
                    st.markdown(reply)
                    
                    # Append assistant reply to history
                    current_session["messages"].append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"⚠️ API Error: {str(e)}")
        st.rerun()

# --- MODE 2: VISION ANALYZER ---
elif app_mode == "👁️ Vision Analyzer":
    st.title("👁️ Vision Matrix")
    st.caption("Upload visual specimens for deep multi-modal analysis.")
    uploaded_image = st.file_uploader("Upload visual specimen", type=["jpg", "jpeg", "png"])
    v_prompt = st.text_input("Visual Query:", "Analyze this image and list key details.")
    if uploaded_image:
        st.image(uploaded_image, caption="Loaded Specimen", width=400)
        if st.button("Analyze Specimen", use_container_width=True):
            with st.spinner("Scanning visual patterns..."):
                try:
                    resp = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[v_prompt, types.Part.from_bytes(data=uploaded_image.getvalue(), mime_type=uploaded_image.type)]
                    )
                    st.markdown("### Analysis Report:")
                    st.markdown(resp.text)
                except Exception as e:
                    st.error(f"Vision error: {e}")
