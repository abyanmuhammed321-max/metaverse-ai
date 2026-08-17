import os
import uuid
import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration & Mobile Viewport Support
st.set_page_config(
    page_title="Metaverse AI - Gemini Edition",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="auto"
)

# 2. Neon Gemini UI Styling & Mobile Responsive CSS Injection
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
    
    /* --- MOBILE RESPONSIVE MEDIA QUERIES --- */
    @media screen and (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.75rem !important;
            max-width: 100% !important;
        }
        h1 {
            font-size: 1.6rem !important;
        }
        .stTextInput input, .stTextArea textarea, .stSelectbox {
            font-size: 16px !important;
        }
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
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

# 4. Secure API Key Configuration
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_ACTUAL_GEMINI_API_KEY")

if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_ACTUAL_GEMINI_API_KEY":
    st.error("⚠️ Please configure your GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()
else:
    @st.cache_resource
    def get_gemini_client(api_key):
        return genai.Client(api_key=api_key)

    client = get_gemini_client(GEMINI_API_KEY)

    # 5. Multi-Chat Session Storage Initialization
    if "sessions" not in st.session_state:
        st.session_state.sessions = {}
    if "current_session_id" not in st.session_state:
        init_id = str(uuid.uuid4())
        st.session_state.sessions[init_id] = {
            "title": "New Chat",
            "messages": [],
            "chat_obj": client.chats.create(model="gemini-2.5-flash")
        }
        st.session_state.current_session_id = init_id

    # --- SIDEBAR ---
    st.sidebar.title("✨ Metaverse AI")
    st.sidebar.markdown(f"👤 **User:** {user_name}")
    
    try:
        if st.sidebar.button("🚪 Log out", use_container_width=True):
            st.logout()
    except Exception:
        pass

    st.sidebar.markdown("---")
    
    if st.sidebar.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {
            "title": "New Chat",
            "messages": [],
            "chat_obj": client.chats.create(model="gemini-2.5-flash")
        }
        st.session_state.current_session_id = new_id
        st.rerun()

    st.sidebar.markdown("### 💬 Recent Chats")

    sessions_to_delete = []
    for s_id, s_data in list(st.session_state.sessions.items()):
        col_chat, col_del = st.sidebar.columns([4, 1])
        label = f"💬 {s_data['title']}"
        if s_id == st.session_state.current_session_id:
            label = f"👉 {s_data['title']}"
        
        with col_chat:
            if st.button(label, key=f"select_{s_id}", use_container_width=True):
                st.session_state.current_session_id = s_id
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"del_{s_id}", use_container_width=True):
                sessions_to_delete.append(s_id)

    if sessions_to_delete:
        for s_id in sessions_to_delete:
            del st.session_state.sessions[s_id]
        if len(st.session_state.sessions) == 0:
            fallback_id = str(uuid.uuid4())
            st.session_state.sessions[fallback_id] = {
                "title": "New Chat",
                "messages": [],
                "chat_obj": client.chats.create(model="gemini-2.5-flash")
            }
            st.session_state.current_session_id = fallback_id
        else:
            st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
        st.rerun()

    st.sidebar.markdown("---")
    app_mode = st.sidebar.radio("Core Engine Mode", [
        "💬 Gemini Neural Chat", 
        "👁️ Vision Analyzer"
    ])

    curr_id = st.session_state.current_session_id
    if curr_id not in st.session_state.sessions:
        curr_id = list(st.session_state.sessions.keys())[0]
        st.session_state.current_session_id = curr_id

    current_session = st.session_state.sessions[curr_id]

    # --- MODE 1: GEMINI NEURAL CHAT ---
    if app_mode == "💬 Gemini Neural Chat":
        st.title("✨ Metaverse AI: Gemini Core")
        st.caption(f"Active Session: {current_session['title']}")

        for msg in current_session["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask your neon AI anything..."):
            current_session["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if current_session["title"] == "New Chat":
                current_session["title"] = prompt[:22] + ("..." if len(prompt) > 22 else "")

            with st.chat_message("assistant"):
                with st.spinner("Thinking through neural pathways..."):
                    try:
                        response = current_session["chat_obj"].send_message(prompt)
                        reply = response.text
                    except Exception:
                        current_session["chat_obj"] = client.chats.create(model="gemini-2.5-flash")
                        response = current_session["chat_obj"].send_message(prompt)
                        reply = response.text

                    st.markdown(reply)
                    current_session["messages"].append({"role": "assistant", "content": reply})
            st.rerun()

    # --- MODE 2: VISION ANALYZER ---
    elif app_mode == "👁️ Vision Analyzer":
        st.title("👁️ Vision Matrix")
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
