import os
import uuid
import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration & Mobile Support
st.set_page_config(
    page_title="Metaverse AI - Gemini Pro Edition",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="auto"
)

# 2. Neon Gemini Pro UI Styling & Mobile Responsiveness
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at center, #070913, #0f1225, #040508);
        color: #e2e8f0;
    }
    h1 {
        color: #a78bfa !important;
        text-shadow: 0 0 15px rgba(167, 139, 250, 0.5);
        font-family: 'Inter', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #090b14;
        border-right: 1px solid rgba(167, 139, 250, 0.2);
    }
    .stButton button {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        color: #ffffff;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        box-shadow: 0 0 12px rgba(139, 92, 246, 0.4);
    }
    @media screen and (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.75rem !important;
            max-width: 100% !important;
        }
        h1 {
            font-size: 1.5rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# 3. Google Sign-In Gate
is_logged_in = True
user_name = "Pro Matrix Creator"

try:
    is_logged_in = st.user.is_logged_in
    user_name = getattr(st.user, "name", "User")
except Exception:
    pass 

if not is_logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🧠 Metaverse AI: Gemini Pro")
        st.markdown("Sign in securely with your Google account to access advanced reasoning and deep context analysis.")
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
            "title": "New Pro Chat",
            "messages": []
        }
    }
    st.session_state.active_session = init_id

if "active_session" not in st.session_state or st.session_state.active_session not in st.session_state.sessions:
    st.session_state.active_session = list(st.session_state.sessions.keys())[0]

# --- SIDEBAR: NAVIGATION & CHAT MANAGEMENT ---
st.sidebar.title("🧠 Metaverse AI")
st.sidebar.markdown(f"👤 **User:** {user_name}")
st.sidebar.caption("Engine: Gemini 2.5 Pro")

try:
    if st.sidebar.button("🚪 Log out", use_container_width=True):
        st.logout()
except Exception:
    pass

st.sidebar.markdown("---")

# New Chat Button
if st.sidebar.button("➕ New Pro Chat", use_container_width=True):
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {
        "title": "New Pro Chat",
        "messages": []
    }
    st.session_state.active_session = new_id
    st.rerun()

st.sidebar.markdown("### 💬 Conversations")

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
            "title": "New Pro Chat",
            "messages": []
        }
        st.session_state.active_session = fallback_id
    else:
        st.session_state.active_session = list(st.session_state.sessions.keys())[0]
    st.rerun()

st.sidebar.markdown("---")
app_mode = st.sidebar.radio("Core Engine Mode", [
    "🧠 Gemini Pro Neural Chat", 
    "👁️ Vision Analyzer Pro"
])

if not api_key:
    st.error("⚠️ Please configure your `GEMINI_API_KEY` in Streamlit Secrets or via the sidebar.")
    st.stop()

# --- MODE 1: GEMINI PRO NEURAL CHAT ---
if app_mode == "🧠 Gemini Pro Neural Chat":
    current_session = st.session_state.sessions[st.session_state.active_session]
    st.title("🧠 Metaverse AI: Gemini Pro Brain")
    st.caption(f"Active Session: {current_session['title']} (Powered by Gemini 2.5 Pro)")

    # Render chat history on screen
    for msg in current_session["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle user prompt input
    if prompt := st.chat_input("Ask Gemini Pro anything (coding, math, reasoning)..."):
        # 1. Append user message to state
        current_session["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Set automatic title based on first message
        if current_session["title"] == "New Pro Chat":
            current_session["title"] = prompt[:22] + ("..." if len(prompt) > 22 else "")

        # 2. Generate response securely using Gemini Pro model & stateless history formatting
        with st.chat_message("assistant"):
            with st.spinner("Processing deep reasoning pathways with Gemini Pro..."):
                try:
                    formatted_contents = []
                    for m in current_session["messages"]:
                        role = "user" if m["role"] == "user" else "model"
                        formatted_contents.append({
                            "role": role,
                            "parts": [{"text": m["content"]}]
                        })

                    response = client.models.generate_content(
                        model="gemini-2.5-pro",
                        contents=formatted_contents
                    )
                    
                    reply = response.text if hasattr(response, 'text') and response.text else "No response generated."
                    st.markdown(reply)
                    
                    # Append assistant reply to history
                    current_session["messages"].append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"⚠️ Gemini Pro API Error: {str(e)}")
        st.rerun()

# --- MODE 2: VISION ANALYZER PRO ---
elif app_mode == "👁️ Vision Analyzer Pro":
    st.title("👁️ Vision Matrix Pro")
    st.caption("Upload images or diagrams for high-precision multimodal analysis via Gemini Pro.")
    
    uploaded_image = st.file_uploader("Upload visual specimen", type=["jpg", "jpeg", "png", "webp"])
    v_prompt = st.text_input("Visual Query:", "Perform an in-depth analytical breakdown of this image.")
    
    if uploaded_image:
        st.image(uploaded_image, caption="Loaded Specimen", width=450)
        if st.button("Analyze with Gemini Pro", use_container_width=True):
            with st.spinner("Scanning visual patterns and running multi-modal reasoning..."):
                try:
                    resp = client.models.generate_content(
                        model="gemini-2.5-pro",
                        contents=[
                            v_prompt, 
                            types.Part.from_bytes(
                                data=uploaded_image.getvalue(), 
                                mime_type=uploaded_image.type
                            )
                        ]
                    )
                    st.markdown("### Pro Analysis Report:")
                    st.markdown(resp.text)
                except Exception as e:
                    st.error(f"Vision error: {e}")
