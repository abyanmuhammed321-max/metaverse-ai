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

# Persistent Chat History Storage across sessions
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

# 2. Dynamic Gemini-Inspired Theme Styling (Deep Tech Dark/Light)
if st.session_state.theme == "Dark":
    bg_color = "#0b0c10"
    text_color = "#f1f3f4"
    sidebar_bg = "#13151b"
    user_bubble = "#1e212b"
    model_bubble = "#13151b"
    border_col = "#2d313d"
    sub_text = "#9aa0a6"
    accent_glow = "rgba(155, 114, 203, 0.1)"
else:
    bg_color = "#f8f9fa"
    text_color = "#202124"
    sidebar_bg = "#f1f3f4"
    user_bubble = "#e8f0fe"
    model_bubble = "#ffffff"
    border_col = "#dadce0"
    sub_text = "#5f6368"
    accent_glow = "rgba(66, 133, 244, 0.08)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
        font-family: 'Inter', sans-serif;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {border_col};
    }}
    
    [data-testid="stSidebar"] * {{
        color: {text_color} !important;
    }}

    /* Chat bubble container styling mimicking modern LLMs */
    .stChatMessage {{
        background-color: transparent !important;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 14px;
        border: 1px solid {border_col};
        box-shadow: 0 4px 20px {accent_glow};
    }}

    /* Header Styling */
    .metaverse-header {{
        text-align: center;
        background: linear-gradient(135deg, #4285F4 0%, #9B72CB 50%, #D96570 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0px;
    }}
    
    .metaverse-subheader {{
        text-align: center;
        color: {sub_text};
        font-size: 1.05rem;
        margin-bottom: 35px;
        font-weight: 400;
    }}

    /* Custom futuristic buttons */
    .stButton button {{
        border-radius: 12px;
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    
    .stButton button:hover {{
        border-color: #4285F4;
        box-shadow: 0 0 12px rgba(66, 133, 244, 0.3);
    }}
</style>
""", unsafe_allow_html=True)

# 3. Sidebar Configuration (Authentication, History & Model Parameters)
with st.sidebar:
    st.markdown("### 🌐 Gemini Account")
    
    try:
        is_logged_in = getattr(st.user, "is_logged_in", False)
    except Exception:
        is_logged_in = False

    if not is_logged_in:
        st.write(f"<span style='font-size: 0.85rem; color: {sub_text};'>Link your Google profile for cloud continuity.</span>", unsafe_allow_html=True)
        st.button("Sign in with Google", on_click=st.login, use_container_width=True, type="primary")
    else:
        user_name = getattr(st.user, "name", "Google User")
        user_email = getattr(st.user, "email", "user@gmail.com")
        st.success(f"**{user_name}**")
        st.write(f"<span style='font-size: 0.75rem; color: {sub_text};'>{user_email}</span>", unsafe_allow_html=True)
        st.button("Sign Out", on_click=st.logout, use_container_width=True)
            
    st.markdown("---")
    
    if st.button("✨ New Chat Workspace", use_container_width=True):
        new_sid = str(uuid.uuid4())
        st.session_state.sessions[new_sid] = {"title": "New Chat", "messages": []}
        st.session_state.current_session_id = new_sid
        st.rerun()
        
    st.markdown("### 💬 Recent Threads")
    
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
    st.markdown("### ⚙️ Engine Settings")
    
    selected_model = st.selectbox(
        "Model Tier",
        ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.1-flash-lite"],
        index=0,
        help="Powered by high-speed free tier flash models."
    )
    
    theme_choice = st.selectbox(
        "Interface Theme",
        ["Dark", "Light"],
        index=0 if st.session_state.theme == "Dark" else 1
    )
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

    languages = ["English", "Malayalam", "Spanish", "French", "German", "Hindi", "Japanese", "Chinese", "Portuguese", "Arabic"]
    lang_choice = st.selectbox(
        "Response Language",
        languages,
        index=languages.index(st.session_state.language) if st.session_state.language in languages else 0
    )
    if lang_choice != st.session_state.language:
        st.session_state.language = lang_choice
        st.rerun()

if not api_key:
    st.error("⚠️ GEMINI_API_KEY configuration is missing inside your `.streamlit/secrets.toml` file.")
    st.stop()

# 4. Main Canvas Display
st.markdown(f'<p class="metaverse-header">Metaverse_AI</p>', unsafe_allow_html=True)
st.markdown(f'<p class="metaverse-subheader">Neural Workspace • Language: {st.session_state.language}</p>', unsafe_allow_html=True)

current_sid = st.session_state.current_session_id
current_messages = st.session_state.sessions[current_sid]["messages"]

# Render Conversation Stream
for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Handle Realtime Streaming Prompts
if prompt := st.chat_input("Ask, code, brainstorm or analyze..."):
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
            
            system_instruction = f"You are Metaverse_AI, a state-of-the-art neural assistant. Always reply natively in {st.session_state.language}."
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
