import uuid
import streamlit as st
from google import genai
from google.genai import errors
from google.genai import types

# 1. Page Configuration
st.set_page_config(
    page_title="Metaverse_AI",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Load Gemini API Key from secrets
api_key = st.secrets.get("GEMINI_API_KEY")

# Initialize session state variables
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

if "language" not in st.session_state:
    st.session_state.language = "English"

if "sessions" not in st.session_state:
    first_sid = str(uuid.uuid4())
    st.session_state.sessions = {
        first_sid: {
            "title": "New Chat",
            "messages": []
        }
    }
    st.session_state.current_session_id = first_sid

if st.session_state.current_session_id not in st.session_state.sessions:
    st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]

# Check native Streamlit OIDC login status
try:
    is_logged_in = getattr(st.user, "is_logged_in", False)
except Exception:
    is_logged_in = False

# 2. Dynamic Gemini-Inspired UI Theme & Responsive Opening Animation Engine
if st.session_state.theme == "Dark":
    bg_color = "#131314"
    text_color = "#e3e3e3"
    sidebar_bg = "#1e1f20"
    user_bubble = "#2b2c2f"
    model_bubble = "#131314"
    border_col = "#333538"
    sub_text = "#c4c7c5"
    accent_glow = "rgba(138, 180, 248, 0.08)"
else:
    bg_color = "#ffffff"
    text_color = "#1f1f1f"
    sidebar_bg = "#f0f4f9"
    user_bubble = "#f0f4f9"
    model_bubble = "#ffffff"
    border_col = "#e0e2e0"
    sub_text = "#444746"
    accent_glow = "rgba(26, 115, 232, 0.06)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Inter:wght@400;500;600&display=swap');

    .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
        font-family: 'Google Sans', 'Inter', sans-serif;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {border_col};
    }}
    
    [data-testid="stSidebar"] * {{
        color: {text_color} !important;
    }}

    /* --- RESPONSIVE OPENING ANIMATION FOR LAPTOP & MOBILE --- */
    @keyframes geminiEntrance {{
        0% {{
            opacity: 0;
            transform: translateY(20px) scale(0.98);
        }}
        100% {{
            opacity: 1;
            transform: translateY(0) scale(1);
        }}
    }}

    .stApp, .block-container {{
        animation: geminiEntrance 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}

    /* Modern Gemini Style Message Bubbles */
    .stChatMessage {{
        background-color: transparent !important;
        border-radius: 20px;
        padding: 18px;
        margin-bottom: 14px;
        border: 1px solid {border_col};
        box-shadow: 0 2px 12px {accent_glow};
    }}

    /* Google Gemini Signature Multi-Color Gradient Title */
    .gemini-title {{
        text-align: center;
        background: linear-gradient(135deg, #4285F4 0%, #9B72CB 50%, #EA4335 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: -0.8px;
        margin-bottom: 0px;
        padding-top: 10px;
    }}
    
    .gemini-subtitle {{
        text-align: center;
        color: {sub_text};
        font-size: 1.05rem;
        margin-bottom: 30px;
        font-weight: 400;
    }}

    /* Custom Input and Button Styles */
    .stButton button {{
        border-radius: 24px;
        font-weight: 500;
        border: 1px solid {border_col};
        background-color: {sidebar_bg};
        transition: all 0.2s ease-in-out;
    }}
    
    .stButton button:hover {{
        border-color: #4285F4;
        background-color: {user_bubble};
        box-shadow: 0 0 8px rgba(66, 133, 244, 0.2);
    }}
</style>
""", unsafe_allow_html=True)

# 3. Sidebar Configuration (Authentication, History & Model Parameters)
with st.sidebar:
    st.markdown("### ✨ Google Account")
    
    if not is_logged_in:
        st.write(f"<span style='font-size: 0.85rem; color: {sub_text};'>Please sign in with Google to start chatting with Metaverse_AI.</span>", unsafe_allow_html=True)
        st.button("🌐 Sign in with Google", on_click=st.login, use_container_width=True, type="primary")
    else:
        user_name = getattr(st.user, "name", "Google User")
        user_email = getattr(st.user, "email", "user@gmail.com")
        st.success(f"**{user_name}**")
        st.write(f"<span style='font-size: 0.75rem; color: {sub_text};'>{user_email}</span>", unsafe_allow_html=True)
        st.button("Sign Out", on_click=st.logout, use_container_width=True)
            
    st.markdown("---")
    
    if st.button("➕ New Chat", use_container_width=True):
        new_sid = str(uuid.uuid4())
        st.session_state.sessions[new_sid] = {"title": "New Chat", "messages": []}
        st.session_state.current_session_id = new_sid
        st.rerun()
        
    st.markdown("### 💬 Recent Chats")
    
    for sid, sdata in list(st.session_state.sessions.items()):
        col1, col2 = st.columns([0.78, 0.22])
        with col1:
            btn_type = "primary" if sid == st.session_state.current_session_id else "secondary"
            display_title = sdata["title"][:16] + ("..." if len(sdata["title"]) > 16 else "")
            if st.button(display_title, key=f"sel_{sid}", use_container_width=True, type=btn_type):
                st.session_state.current_session_id = sid
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{sid}", help="Delete chat thread"):
                del st.session_state.sessions[sid]
                if not st.session_state.sessions:
                    fresh_sid = str(uuid.uuid4())
                    st.session_state.sessions[fresh_sid] = {"title": "New Chat", "messages": []}
                    st.session_state.current_session_id = fresh_sid
                else:
                    st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
                st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    
    selected_model = st.selectbox(
        "Choose Model",
        ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-flash-lite"],
        index=0
    )
    
    theme_choice = st.selectbox(
        "Appearance",
        ["Dark", "Light"],
        index=0 if st.session_state.theme == "Dark" else 1
    )
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

    languages = ["English", "Malayalam", "Spanish", "French", "German", "Hindi", "Japanese", "Chinese", "Portuguese", "Arabic"]
    lang_choice = st.selectbox(
        "Language",
        languages,
        index=languages.index(st.session_state.language) if st.session_state.language in languages else 0
    )
    if lang_choice != st.session_state.language:
        st.session_state.language = lang_choice
        st.rerun()

if not api_key:
    st.error("⚠️ GEMINI_API_KEY configuration is missing inside your `.streamlit/secrets.toml` file.")
    st.stop()

# 4. Main Canvas Interface Layout
st.markdown(f'<p class="gemini-title">Metaverse_AI</p>', unsafe_allow_html=True)
st.markdown(f'<p class="gemini-subtitle">Explore, create, and chat • ({st.session_state.language})</p>', unsafe_allow_html=True)

# Strict Authentication Gate: Require Google Sign In before chatting
if not is_logged_in:
    st.info("🔒 **Authentication Required:** Please click **'Sign in with Google'** in the sidebar to unlock Metaverse_AI chat.")
    st.stop()

current_sid = st.session_state.current_session_id
current_messages = st.session_state.sessions[current_sid]["messages"]

# Render Conversation Stream
for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Handle Realtime Streaming Prompts
if prompt := st.chat_input("Enter a prompt here..."):
    if len(current_messages) == 0:
        st.session_state.sessions[current_sid]["title"] = prompt[:24]

    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            client = genai.Client(api_key=api_key)
            
            chat_history_formatted = [
                {"role": m["role"], "parts": [{"text": m["content"]}]} 
                for m in current_messages
            ]
            
            system_instruction = f"You are Metaverse_AI, built with Google's advanced architecture. Always reply natively in {st.session_state.language}."
            config = types.GenerateContentConfig(
                system_instruction=system_instruction
            )
            
            response_stream = client.models.generate_content_stream(
                model=selected_model,
                contents=chat_history_formatted,
                config=config
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

        current_messages.append({"role": "model", "content": full_response})
