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

# Initialize session state variables for settings
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

if "language" not in st.session_state:
    st.session_state.language = "English"

# 2. Handle Authentication Flow
if not st.user.is_logged_in:
    st.markdown("""
    <style>
        .stApp { background-color: #000000; color: #ffffff; font-family: 'Inter', sans-serif; }
        .login-box { text-align: center; margin-top: 20vh; }
        .metaverse-login-header {
            background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 700;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<p class="metaverse-login-header">Metaverse_AI</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #a0a0a0; font-size: 1.1rem; margin-bottom: 30px;">Sign in with your Google account to start chatting.</p>', unsafe_allow_html=True)
    
    if st.button("🔵 Sign in with Google", use_container_width=True):
        st.login()
        
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 3. Dynamic Theme Styling (True Dark vs Light Mode Opposites)
if st.session_state.theme == "Dark":
    bg_color = "#000000"
    text_color = "#ffffff"
    sidebar_bg = "#121212"
    user_bubble_bg = "#1e1f20"
    border_col = "#333537"
    sub_text = "#a0a0a0"
else:
    bg_color = "#ffffff"
    text_color = "#000000"
    sidebar_bg = "#f0f4f9"
    user_bubble_bg = "#f8f9fa"
    border_col = "#d1d5db"
    sub_text = "#5f6368"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; font-family: 'Inter', sans-serif; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; color: {text_color} !important; border-right: 1px solid {border_col}; }}
    [data-testid="stSidebar"] * {{ color: {text_color} !important; }}
    .stChatMessage {{ background-color: transparent !important; border-radius: 12px; padding: 10px; margin-bottom: 10px; color: {text_color} !important; }}
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] span, [data-testid="stChatMessage"] li {{ color: {text_color} !important; }}
    [data-testid="stChatMessage"]:nth-child(odd) {{ background-color: {user_bubble_bg} !important; border: 1px solid {border_col}; }}
    .stChatInput input {{ color: {text_color} !important; background-color: {sidebar_bg} !important; }}
    .metaverse-header {{
        text-align: center;
        background: linear-gradient(90deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0px;
    }}
    .metaverse-subheader {{ text-align: center; color: {sub_text}; font-size: 1.2rem; margin-bottom: 30px; }}
</style>
""", unsafe_allow_html=True)

# Initialize Multi-Chat Session Storage State
if "sessions" not in st.session_state:
    first_sid = str(uuid.uuid4())
    st.session_state.sessions = {first_sid: {"title": "New Chat", "messages": []}}
    st.session_state.current_session_id = first_sid

if st.session_state.current_session_id not in st.session_state.sessions:
    st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]

# 4. Sidebar Configuration
with st.sidebar:
    st.markdown("### 👤 User Profile")
    if hasattr(st.user, "picture") and st.user.picture:
        st.image(st.user.picture, width=50)
    st.write(f"**{getattr(st.user, 'name', 'User')}**")
    st.write(f"<span style='font-size: 0.8rem; color: {sub_text};'>{getattr(st.user, 'email', '')}</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- NEW CHAT BUTTON ---
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        new_sid = str(uuid.uuid4())
        st.session_state.sessions[new_sid] = {"title": "New Chat", "messages": []}
        st.session_state.current_session_id = new_sid
        st.rerun()
        
    st.markdown("### 💬 Chat History")
    
    # --- RENDER CHAT LIST WITH SELECT & DELETE BUTTONS ---
    for sid, sdata in list(st.session_state.sessions.items()):
        col1, col2 = st.columns([0.75, 0.25])
        with col1:
            btn_type = "primary" if sid == st.session_state.current_session_id else "secondary"
            display_title = sdata["title"][:18] + ("..." if len(sdata["title"]) > 18 else "")
            if st.button(display_title, key=f"sel_{sid}", use_container_width=True, type=btn_type):
                st.session_state.current_session_id = sid
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{sid}", help="Delete chat"):
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
        ["gemini-3.6-flash", "gemini-3.1-pro-preview"],
        index=0
    )
    
    # --- THEME SWITCHER ---
    theme_choice = st.selectbox(
        "Theme",
        ["Dark", "Light"],
        index=0 if st.session_state.theme == "Dark" else 1
    )
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

    # --- LANGUAGE SELECTOR ---
    languages = ["English", "Spanish", "French", "German", "Hindi", "Japanese", "Chinese", "Portuguese", "Arabic"]
    lang_choice = st.selectbox(
        "Response Language",
        languages,
        index=languages.index(st.session_state.language) if st.session_state.language in languages else 0
    )
    if lang_choice != st.session_state.language:
        st.session_state.language = lang_choice
        st.rerun()
    
    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True):
        st.logout()

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing! Please configure it in your secrets.")
    st.stop()

# 5. Main UI Layout
user_first_name = getattr(st.user, 'name', 'human').split()[0]
st.markdown(f'<p class="metaverse-header">Metaverse_AI</p>', unsafe_allow_html=True)
st.markdown(f'<p class="metaverse-subheader">Welcome back, {user_first_name}! (Language: {st.session_state.language})</p>', unsafe_allow_html=True)

current_sid = st.session_state.current_session_id
current_messages = st.session_state.sessions[current_sid]["messages"]

# Display Prior Chat Messages for Current Session
for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Handle Prompt Submission & Streaming
if prompt := st.chat_input("Enter a prompt here..."):
    if len(current_messages) == 0:
        st.session_state.sessions[current_sid]["title"] = prompt[:25]

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
            
            # Configure Gemini to respond in the user's selected language
            system_instruction = f"You are Metaverse_AI, a helpful AI assistant. Always respond in {st.session_state.language}."
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
